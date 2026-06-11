"""
mail_client.py — Interacción con Outlook 365 via Microsoft Graph API
"""

import os
import time
import logging
import requests
import msal # Microsoft Authentication Library para obtener tokens OAuth2.
from dotenv import load_dotenv

load_dotenv()

log = logging.getLogger(__name__)

GRAPH = "https://graph.microsoft.com/v1.0"
CATEGORIA_PROCESADO = "AgenteProcesado"   # categoría que se crea en Outlook


class MailClient:
    def __init__(self, buzon: str):
        self.client_id = os.getenv("CLIENT_ID")
        self.client_secret = os.getenv("CLIENT_SECRET")
        self.tenant_id = os.getenv("TENANT_ID")
        self.buzon = buzon
        self._token = None
        self._folder_cache: dict[str, str] = {}  # nombre → folder_id

    # ── Auth ──────────────────────────────────────────────────────

    def _get_token(self) -> str:
        app = msal.ConfidentialClientApplication(
            self.client_id,
            authority=f"https://login.microsoftonline.com/{self.tenant_id}",
            client_credential=self.client_secret,
        )
        result = app.acquire_token_for_client(
            scopes=["https://graph.microsoft.com/.default"]
        )
        if "access_token" not in result:
            raise Exception(f"Auth office 365 fallida: {result.get('error_description')}")
        return result["access_token"]

    def refresh_token(self) -> None:
        """Obtiene un token fresco y lo cachea para todo el ciclo."""
        self._token = self._get_token()

    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self._token}",
            "Content-Type": "application/json",
        }

    def _request_con_retry(self, metodo: str, url: str, **kwargs) -> requests.Response:
        """
        Ejecuta un request a Graph reintentando ante errores transitorios.
        - 429 (throttling): respeta el header 'Retry-After' que envía Graph.
        - 5xx (errores de servidor): backoff exponencial (1s, 2s, 4s).
        Inyecta los headers de auth automáticamente.
        """
        for intento in range(3):
            r = requests.request(metodo, url, headers=self._headers(), **kwargs)

            if r.status_code == 429:
                espera = int(r.headers.get("Retry-After", 5))
                log.warning(f"    ⏳ Throttling (429). Esperando {espera}s...")
                time.sleep(espera)
                continue

            if 500 <= r.status_code < 600:
                espera = 2 ** intento  # 1s, 2s, 4s
                log.warning(f"    ⏳ Error {r.status_code} de Graph. Reintento en {espera}s...")
                time.sleep(espera)
                continue

            r.raise_for_status()
            return r

        # Si agotó los 3 intentos, lanza el error del último intento.
        r.raise_for_status()
        # Nota: el raise_for_status() anterior ya lanza la excepción, así que esta línea no se ejecuta.
        #return r

    # ── Leer ──────────────────────────────────────────────────────

    def leer_no_procesados(self, cantidad: int = 20) -> list[dict]:
        """
        Lee correos que NO tienen la categoría 'AgenteProcesado'.
        Así el agente nunca reprocesa el mismo mail.
        """

        # NOTA: El paréntesis en $select es solo para concatenar el string sin
        # que se rompa la línea (lo une en tiempo de compilación, no tiene costo).
        # No es parte de la sintaxis de Microsoft Graph.

        # Excluye los ya procesados por el agente. Si está seteada PROCESAR_DESDE
        # (fecha/hora ISO 8601 en UTC, ej: "2026-06-11T00:00:00Z"), excluye además los
        # correos anteriores a esa fecha: así, al arrancar en un buzón que todavía no tiene
        # la categoría 'AgenteProcesado', no se procesan los correos viejos.
        filtro = f"NOT categories/any(c:c eq '{CATEGORIA_PROCESADO}')"
        procesar_desde = os.getenv("PROCESAR_DESDE")
        if procesar_desde:
            filtro = f"receivedDateTime ge {procesar_desde} and {filtro}"

        params = {
            "$top": cantidad,
            "$select": (
                "id,"
                "internetMessageId,"
                "conversationId,"
                "subject,"
                "from,"
                "toRecipients,"
                "ccRecipients,"
                "replyTo,"
                "bodyPreview,"
                "body,"
                "receivedDateTime,"
                "isRead,"
                "sentDateTime,"
                "hasAttachments,"
                "importance,"
                "parentFolderId"
            ),
            "$orderby": "receivedDateTime asc",
            "$filter": filtro,
        }
        url = f"{GRAPH}/users/{self.buzon}/messages"
        r = self._request_con_retry("GET", url, params=params)
        resp = r.json().get("value", [])
        
        return resp

    def leer_completo(self, message_id: str) -> dict:
        """Obtiene el cuerpo completo de un correo."""
        url = f"{GRAPH}/users/{self.buzon}/messages/{message_id}"
        r = self._request_con_retry("GET", url)
        return r.json()

    # ── Acciones ──────────────────────────────────────────────────

    def responder(self, message_id: str, cuerpo_html: str) -> None:
        """Responde al correo original."""
        url = f"{GRAPH}/users/{self.buzon}/messages/{message_id}/reply"
        payload = {
            "message": {
                "body": {"contentType": "HTML", "content": cuerpo_html}
            },
            "comment": ""
        }
        self._request_con_retry("POST", url, json=payload)

    def crear_draft_respuesta(self, message_id: str, cuerpo_html: str) -> None:
        """Crea un borrador de respuesta en la carpeta Drafts sin enviarlo."""
        url = f"{GRAPH}/users/{self.buzon}/messages/{message_id}/createReply"
        payload = {
            "message": {
                "body": {"contentType": "HTML", "content": cuerpo_html}
            }
        }
        self._request_con_retry("POST", url, json=payload)

    def reenviar(self, message_id: str, destinatarios: list[str], comentario: str = "") -> None:
        """Reenvía el correo a una lista de destinatarios."""
        to_list = [{"emailAddress": {"address": e}} for e in destinatarios]
        url = f"{GRAPH}/users/{self.buzon}/messages/{message_id}/forward"
        payload = {
            "comment": comentario,
            "toRecipients": to_list,
        }
        self._request_con_retry("POST", url, json=payload)

    def enviar_nuevo(self, destinatario: str, asunto: str, cuerpo_html: str) -> None:
        """Envía un correo nuevo (no como respuesta)."""
        url = f"{GRAPH}/users/{self.buzon}/sendMail"
        payload = {
            "message": {
                "subject": asunto,
                "body": {"contentType": "HTML", "content": cuerpo_html},
                "toRecipients": [{"emailAddress": {"address": destinatario}}],
            },
            "saveToSentItems": True,
        }
        self._request_con_retry("POST", url, json=payload)

    def marcar_procesado(self, message_id: str, categorias: list[str] | None = None) -> None:
        """
        Agrega la categoría 'AgenteProcesado' al correo más las categorías de las reglas.
        Así el agente no lo vuelve a procesar en el próximo ciclo.
        """
        todas = [CATEGORIA_PROCESADO] + [c for c in (categorias or []) if c != CATEGORIA_PROCESADO]
        url = f"{GRAPH}/users/{self.buzon}/messages/{message_id}"
        payload = {"categories": todas}
        self._request_con_retry("PATCH", url, json=payload)

    def marcar_leido(self, message_id: str) -> None:
        url = f"{GRAPH}/users/{self.buzon}/messages/{message_id}"
        self._request_con_retry("PATCH", url, json={"isRead": True})

    # ── Carpetas ──────────────────────────────────────────────────

    def _get_or_create_folder(self, nombre: str) -> str:
        """Devuelve el ID de la carpeta, creándola si no existe. Soporta rutas anidadas con '/'."""
        if nombre in self._folder_cache:
            return self._folder_cache[nombre]

        segmentos = nombre.split("/")
        parent_id = None
        ruta_acumulada = ""

        for segmento in segmentos:
            ruta_acumulada = f"{ruta_acumulada}/{segmento}" if ruta_acumulada else segmento

            if ruta_acumulada in self._folder_cache:
                parent_id = self._folder_cache[ruta_acumulada]
                continue

            if parent_id is None:
                url_base = f"{GRAPH}/users/{self.buzon}/mailFolders"
            else:
                url_base = f"{GRAPH}/users/{self.buzon}/mailFolders/{parent_id}/childFolders"

            r = self._request_con_retry("GET", url_base, params={"$filter": f"displayName eq '{segmento}'"})
            carpetas = r.json().get("value", [])

            if carpetas:
                folder_id = carpetas[0]["id"]
            else:
                r = self._request_con_retry("POST", url_base, json={"displayName": segmento})
                folder_id = r.json()["id"]

            self._folder_cache[ruta_acumulada] = folder_id
            parent_id = folder_id

        return parent_id

    def mover_a_carpeta(self, message_id: str, nombre_carpeta: str) -> str:
        """Mueve el correo a la carpeta indicada. Retorna el nuevo message_id."""
        folder_id = self._get_or_create_folder(nombre_carpeta)
        url = f"{GRAPH}/users/{self.buzon}/messages/{message_id}/move"
        r = self._request_con_retry("POST", url, json={"destinationId": folder_id})
        return r.json()["id"]   # ← Graph devuelve el mensaje con su nuevo id

    # ── Escalación ────────────────────────────────────────────────

    def enviar_alerta_escalacion(
        self,
        correo_original: dict,
        red_flags: list[str],
        destinatarios: list[str],
    ) -> None:
        """Envía un email de alerta a los contactos de escalación por red flags detectados."""
        remitente    = correo_original.get("from", {}).get("emailAddress", {}).get("address", "desconocido")
        asunto       = correo_original.get("subject", "(sin asunto)")
        cuerpo_orig  = correo_original.get("body", {}).get("content", "")
        flags_html   = "".join(f"<li><b>{f}</b></li>" for f in red_flags)

        cuerpo_html = (
            f"<p>⚠️ El agente de correo detectó <b>señales de alerta</b> en el siguiente correo:</p>"
            f"<ul>{flags_html}</ul>"
            f"<hr>"
            f"<p><b>De:</b> {remitente}<br>"
            f"<b>Asunto:</b> {asunto}</p>"
            f"<blockquote>{cuerpo_orig}</blockquote>"
        )
        asunto_alerta = f"🚨 Red flag detectado: {asunto}"

        for destinatario in destinatarios:
            self.enviar_nuevo(destinatario, asunto_alerta, cuerpo_html)
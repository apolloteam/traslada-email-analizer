"""
agent.py — Agente principal de Outlook 365
Corre en loop, revisa correos nuevos, los analiza con Claude y ejecuta acciones.

Uso:
    python src/agent.py              # usa src/config/general_rules.md por defecto
    python src/agent.py --interval 5 # revisa cada 5 minutos
"""

import os
import re
import time
import json
import logging
import argparse
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

_DIR = os.path.dirname(os.path.abspath(__file__))

from mail_client import MailClient, DOMINIOS_INTERNOS
from analyzer import AnalizadorClaude, MODELO
from actions import ejecutar_accion
from models.email_decision_log import EmailDecisionLog
from utils.email_parser import extraer_texto_body
import db_logger

# ── Logging ────────────────────────────────────────────────────────
_LOG_DIR = os.path.join(_DIR, "logs")
os.makedirs(_LOG_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(os.path.join(_DIR, "logs", "agent.log"), encoding="utf-8"),
        logging.StreamHandler()
    ]
)
log = logging.getLogger(__name__)


TZ_ARGENTINA = ZoneInfo("America/Argentina/Buenos_Aires")

# Remitente y patrón de asunto que identifican un lead de formulario web.
REMITENTE_LEAD  = os.getenv("REMITENTE_LEAD", "noreply@traslada.com.ar") # Ejemplo: noreply@traslada.com.ar
LEAD_ASUNTO_PATRON = "nuevo lead - source:"


def extraer_email_de_lead(body_texto: str) -> str | None:
    """
    Extrae el email del campo 'E-mail:' de un lead de formulario web.
    Contempla variantes: 'E-mail', 'Email', 'E mail', con o sin mayúsculas.
    Devuelve el email en minúsculas, o None si no lo encuentra.
    """
    m = re.search(
        r"e[\-\s]?mail\s*:\s*([A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,})",
        body_texto or "",
        re.IGNORECASE,
    )
    return m.group(1).lower() if m else None


def _a_hora_argentina(valor) -> str | None:
    """
    Convierte un datetime o un string ISO 8601 (UTC u otro offset) a hora local de
    Argentina y lo devuelve como ISO 8601 SIN zona horaria (naive), para que la base de
    datos guarde el horario 'de pared' argentino sin reconversiones del lado del server.
    Devuelve None si el valor es vacío.
    """
    if not valor:
        return None
    if isinstance(valor, str):
        dt = datetime.fromisoformat(valor.replace("Z", "+00:00"))
    else:
        dt = valor
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)  # si viene naive, se asume UTC
    local = dt.astimezone(TZ_ARGENTINA).replace(tzinfo=None)
    resultado = local.isoformat()
    return resultado


def _direcciones(lista) -> str:
    """Aplana destinatarios de Graph a un string de direcciones separadas por ';'."""
    direcciones = [
        r.get("emailAddress", {}).get("address", "")
        for r in (lista or [])
        if r.get("emailAddress", {}).get("address")
    ]
    resultado = ";".join(direcciones)
    return resultado


def _construir_log_record(
    correo: dict,
    mail_client: MailClient,
    decision: dict | None,
    uso: dict | None,
    elapsed: float,
    error_descrip: str | None,
) -> EmailDecisionLog:
    """Arma el registro de log a partir del correo y la decisión (o el error)."""
    input_tokens  = uso["input_tokens"] if uso else 0
    output_tokens = uso["output_tokens"] if uso else 0

    # Le saca el prefijo "📢 Regla - ".
    rule_name=decision.get("nombre_regla") if decision else None
    clean_rule_name = rule_name.split("Regla -", 1)[-1].strip() if rule_name else None
    
    record = EmailDecisionLog(
        mailbox=mail_client.buzon,
        analyzed_date=_a_hora_argentina(datetime.now(timezone.utc)),
        email_id=correo.get("id", ""),
        internet_message_id=correo.get("internetMessageId"),
        conversation_id=correo.get("conversationId"),
        subject=correo.get("subject"),
        from_address=correo.get("from", {}).get("emailAddress", {}).get("address"),
        to_recipients=_direcciones(correo.get("toRecipients")),
        cc_recipients=_direcciones(correo.get("ccRecipients")),
        reply_to=_direcciones(correo.get("replyTo")),
        received_date_time=_a_hora_argentina(correo.get("receivedDateTime")),
        sent_date_time=_a_hora_argentina(correo.get("sentDateTime")),
        has_attachments=correo.get("hasAttachments"),
        rule_name=clean_rule_name,
        accion=decision.get("accion") if decision else None,
        red_flag=bool(decision.get("red_flags_detectados")) if decision else False,
        decision_json=json.dumps(decision, ensure_ascii=False) if decision else None,
        elapsed_time=elapsed,
        ai_model=MODELO,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        cost=db_logger.calcular_costo(input_tokens, output_tokens),
        error=error_descrip is not None,
        error_descrip=error_descrip,
    )
    return record


def ciclo(mail_client: MailClient, analizador: AnalizadorClaude):
    """Un ciclo completo para un buzón: leer → analizar → actuar."""
    mail_client.refresh_token()
    log.info(f"▶ Revisando correos de {mail_client.buzon}...")

    # Lee correos no procesados (sin la categoría 'AgenteProcesado')
    max_correos = int(os.getenv("MAX_CORREOS_POR_CICLO", 20))
    correos = mail_client.leer_no_procesados(cantidad=max_correos)

    if not correos:
        log.info("  Sin correos nuevos.")
        return

    log.info(f"  {len(correos)} correo(s) encontrado(s).")

    for correo in correos:
        try:
            log.info(f"  📧 Procesando: '{correo['subject']}' de {correo['from']['emailAddress']['address']}")

            # Agrega y resuelve el campo custom 'direction' (recibido vs enviado).
            remitente = correo.get("from", {}).get("emailAddress", {}).get("address", "")
            direction = 1 if remitente.lower() == mail_client.buzon.lower() else 0  # 0=recibido, 1=enviado
            correo["direction"] = direction
            dominio_remitente = remitente.split("@")[-1].lower()

            # ── Filtros previos al análisis ───────────────────────────────────────────────────────
            if correo["direction"] == 1:
                log.info(f"  ⏭ Saliente, ignorando.")
                mail_client.marcar_procesado(correo["id"])
                continue

            # Detección de lead de formulario web: viene de noreply@ interno y el asunto
            # tiene el patrón de lead. Extraemos el email del cuerpo y lo inyectamos como
            # replyTo, para que el resto del sistema lo trate igual que un correo con
            # remitente real (que la respuesta vaya al cliente del formulario, no a noreply@).
            # Ejemplo: "Nuevo lead - Source: WebClientesTraslada" con body que incluye "E-mail: cliente@example.com".
            es_lead_form = (
                bool(REMITENTE_LEAD)
                and remitente.lower() == REMITENTE_LEAD.lower()
                and LEAD_ASUNTO_PATRON in correo.get("subject", "").lower()
            )

            # Si es un lead de formulario web, extraemos el email del body y lo seteamos como replyTo.
            if es_lead_form:
                email_cliente = extraer_email_de_lead(extraer_texto_body(correo))
                if email_cliente:
                    correo["replyTo"] = [{"emailAddress": {"address": email_cliente}}]
                    log.info(f"  📨 Lead de formulario web. Cliente: {email_cliente}")
                else:
                    # Sin email no podemos responderle al cliente. No lo procesamos
                    # (responderíamos a noreply@ y se perdería); lo dejamos para revisión manual.
                    log.warning(f"  ⚠️ No se pudo extraer el email del body del lead. Asunto: '{correo.get('subject','')}'")
                    mail_client.mover_a_carpeta(correo["id"], "Errores/LeadSinEmail")
                    mail_client.marcar_procesado(correo["id"])
                    continue

            # Remitente automático (no-reply / noreply): se ignora, EXCEPTO si es un lead
            # de formulario web (esos se procesan, ya con su replyTo seteado arriba).
            if not es_lead_form and (remitente.lower().startswith("no-reply") or remitente.lower().startswith("noreply")):
                log.info(f"  ⏭ Remitente automático, ignorando.")
                mail_client.marcar_procesado(correo["id"])
                continue

            if dominio_remitente in DOMINIOS_INTERNOS:
                # Excepción: correo interno derivado. El agente setea replyTo=cliente al derivar,
                # esa señal indica que el correo debe analizarse (no ignorarse) en el buzón destino.
                reply_to_list = correo.get("replyTo", [])
                tiene_reply_to = bool(reply_to_list and reply_to_list[0].get("emailAddress", {}).get("address"))
                if not tiene_reply_to:
                    log.info(f"  ⏭ Correo interno sin replyTo ({remitente}), ignorando.")
                    mail_client.marcar_procesado(correo["id"])
                    continue
                log.info(f"  ✅ Correo interno derivado ({remitente}), pasando al análisis.")
            # ──────────────────────────────────────────────────────────────────────────────────────

            # ── A partir de acá el correo se analiza: SIEMPRE se loguea a DB ──────────
            inicio = time.monotonic()
            decision = None
            uso = None
            error_descrip = None
            try:
                # 1. Claude analiza el correo y decide qué hacer
                decision, uso = analizador.analizar(correo, mail_client.buzon)

                log.info(f"  🤖 Decisión: {decision['accion']} — {decision['razon']}")

                # 2. Marcar como procesado PRIMERO.
                # Se marca antes de ejecutar acciones para garantizar idempotencia:
                # si una acción falla más abajo, el correo ya quedó marcado y NO se
                # reprocesa en el próximo ciclo (evita responder/reenviar dos veces).
                # La categoría 'AgenteProcesado' viaja con el correo aunque luego se mueva.
                mail_client.marcar_procesado(correo["id"], decision.get("categorias", []))

                # 3. Ejecutar acción + escalar + mover, de forma protegida.
                # Si algo falla acá, el correo ya está marcado (no se duplica) y se mueve
                # a una carpeta de revisión para que nada se pierda en silencio.
                try:
                    # 3a. Ejecutar la acción decidida
                    if decision["accion"] != "ignorar":
                        ejecutar_accion(decision, correo, mail_client)

                    # 3b. Escalar si se detectaron red flags (independiente de la acción)
                    escalar_a = decision.get("escalar_a", [])
                    if escalar_a:
                        red_flags = decision.get("red_flags_detectados", [])
                        mail_client.enviar_alerta_escalacion(correo, red_flags, escalar_a)
                        log.warning(f"    🚨 Red flags: {red_flags} → Escalado a: {escalar_a}")

                    # 3c. Mover a carpeta de archivo si la conversación está cerrada
                    carpeta = decision.get("carpeta_archivo")
                    if carpeta:
                        correo["id"] = mail_client.mover_a_carpeta(correo["id"], carpeta)  # ← actualiza el id
                        log.info(f"    📁 Movido a carpeta: {carpeta}")

                except Exception as e:
                    # El correo ya fue marcado como procesado, así que no se reprocesa.
                    # Lo movemos a una carpeta de revisión manual para no perderlo.
                    error_descrip = str(e)
                    log.error(f"    ⚠️ Falló la ejecución de acciones: {e}")
                    try:
                        mail_client.mover_a_carpeta(correo["id"], "Errores/RequiereRevision")
                        log.error(f"    📁 Movido a 'Errores/RequiereRevision' para revisión manual.")
                    except Exception as e2:
                        log.error(f"    ❌ Tampoco se pudo mover a 'Errores/RequiereRevision': {e2}")

            except Exception as e:
                # Falló el análisis o el marcado: no hay decisión (o quedó incompleta).
                error_descrip = str(e)
                log.error(f"  ❌ Error analizando correo {correo['id']}: {e}")

            finally:
                # 4. Registrar en DB qué hizo el agente (decisión, tokens, costo, tiempo, error).
                elapsed = time.monotonic() - inicio
                record = _construir_log_record(
                    correo, mail_client, decision, uso, elapsed, error_descrip
                )
                db_logger.enviar_log(record)

        except Exception as e:
            log.error(f"  ❌ Error procesando correo {correo['id']}: {e}")


def main():
    parser = argparse.ArgumentParser(description="Agente Outlook 365")
    parser.add_argument("--interval", type=int, default=None, help="Intervalo en minutos")
    parser.add_argument("--config", default=None, help="Carpeta de reglas (default: src/config/)")
    parser.add_argument("--once", action="store_true", help="Correr solo una vez y salir")
    args = parser.parse_args()

    intervalo  = args.interval or int(os.getenv("INTERVALO_MINUTOS", 10))
    buzones    = [b.strip() for b in os.getenv("BUZONES", "").split(";") if b.strip()]
    analizador = AnalizadorClaude(rules_dir=args.config) if args.config else AnalizadorClaude()

    log.info("=" * 55)
    log.info("  Agente Outlook 365 iniciado")
    log.info(f"  Buzones: {', '.join(buzones)}")
    log.info(f"  Intervalo: cada {intervalo} minutos")
    log.info(f"  Reglas: {analizador.rules_dir}")
    log.info("=" * 55)

    if args.once:
        for buzon in buzones:
            ciclo(MailClient(buzon), analizador)
        return

    while True:
        try:
            for buzon in buzones:
                ciclo(MailClient(buzon), analizador)

        except Exception as e:
            log.error(f"Error en ciclo principal: {e}")

        log.info(f"  ⏳ Próxima revisión en {intervalo} minutos...")
        time.sleep(intervalo * 60)


if __name__ == "__main__":
    main()
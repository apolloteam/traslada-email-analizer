"""
actions.py — Ejecuta las acciones decididas por Claude.
"""

import logging
from mail_client import MailClient, DOMINIOS_INTERNOS

log = logging.getLogger(__name__)


def ejecutar_accion(decision: dict, correo: dict, mail: MailClient) -> None:
    """
    Recibe la decisión de Claude y ejecuta la acción correspondiente.

    Acciones posibles:
      - responder              → responde al remitente original (o al replyTo si el correo fue derivado)
      - reenviar               → reenvía a destinatarios; detecta automáticamente derivaciones internas
      - responder_y_reenviar   → hace ambas cosas
      - ignorar                → no hace nada (ya filtrado antes de llegar aquí)
    """
    accion     = decision.get("accion", "ignorar")
    remitente  = correo["from"]["emailAddress"]["address"]
    asunto     = correo.get("subject", "(sin asunto)")
    msg_id     = correo["id"]

    if accion == "responder":
        _responder(mail, msg_id, remitente, asunto, decision, correo)

    elif accion == "reenviar":
        _reenviar(mail, msg_id, decision, correo)

    elif accion == "responder_y_reenviar":
        _responder(mail, msg_id, remitente, asunto, decision, correo)
        _reenviar(mail, msg_id, decision, correo)

    else:
        log.info(f"    → Acción: ignorar (sin operación)")


def _responder(mail: MailClient, msg_id: str, remitente: str, asunto: str, decision: dict, correo: dict):
    cuerpo = decision.get("respuesta_html")
    if not cuerpo:
        log.warning("    ⚠️  Acción 'responder' sin respuesta_html. Saltando.")
        return

    # Correo derivado: el replyTo contiene al cliente original; responder a él, no al from interno.
    reply_to_list = correo.get("replyTo", [])
    reply_to_address = (
        reply_to_list[0].get("emailAddress", {}).get("address")
        if reply_to_list else None
    )

    if reply_to_address:
        mail.responder_a_reply_to(msg_id, cuerpo, reply_to_address)
        log.info(f"    ✉️  Respuesta enviada al replyTo: {reply_to_address} (correo derivado)")
    elif decision.get("responder_como_draft", False):
        mail.crear_draft_respuesta(msg_id, cuerpo)
        log.info(f"    📝  Borrador creado para: {remitente} | Asunto: {asunto}")
    else:
        mail.responder(msg_id, cuerpo)
        log.info(f"    ✉️  Respuesta enviada a: {remitente} | Asunto: {asunto}")


def _reenviar(mail: MailClient, msg_id: str, decision: dict, correo: dict):
    destinatarios = decision.get("reenviar_a", [])
    if not destinatarios:
        log.warning("    ⚠️  Acción 'reenviar' sin destinatarios. Saltando.")
        return

    comentario = decision.get("comentario_reenvio", "")

    # El cliente al que se debe poder responder: si el correo ya tiene replyTo (derivación en
    # cadena), lo propaga; si no, el from actual es el cliente original.
    reply_to_list = correo.get("replyTo", [])
    cliente_address = (
        reply_to_list[0].get("emailAddress", {}).get("address")
        if reply_to_list
        else correo["from"]["emailAddress"]["address"]
    )

    destinos_derivar  = [d for d in destinatarios if d.split("@")[-1].lower() in DOMINIOS_INTERNOS]
    destinos_reenviar = [d for d in destinatarios if d.split("@")[-1].lower() not in DOMINIOS_INTERNOS]

    if destinos_derivar:
        mail.derivar(msg_id, destinos_derivar, cliente_address, comentario)
        log.info(f"    ↪️  Derivado a: {', '.join(destinos_derivar)} (replyTo: {cliente_address})")

    if destinos_reenviar:
        mail.reenviar(msg_id, destinos_reenviar, comentario)
        log.info(f"    ↪️  Reenviado a: {', '.join(destinos_reenviar)}")

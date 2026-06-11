from typing import Optional
from pydantic import BaseModel

AGENT_ID = "email_analyzer_1"


class EmailDecisionLog(BaseModel):
    """
    Registro estructurado de la decisión del agente sobre un correo, para persistir en la
    base de datos vía API. Campos en snake_case (el API los deserializa).

    A diferencia del log local (src/logs/agent.log), que es un detalle paso a paso, este log
    guarda QUÉ hizo el agente con cada correo: la decisión, el análisis, datos del correo,
    tiempo de procesamiento, tokens consumidos, costo y errores.
    """

    agent_id: str = AGENT_ID
    mailbox: str
    analyzed_date: str  # ISO 8601 UTC

    # Identificadores del correo
    email_id: str                      # id de Graph (mutable: cambia al mover de carpeta)
    internet_message_id: Optional[str] = None  # Message-ID RFC 5322 (estable e inmutable)
    conversation_id: Optional[str] = None

    # Datos del correo
    subject: Optional[str] = None
    from_address: Optional[str] = None
    to_recipients: Optional[str] = None
    cc_recipients: Optional[str] = None
    reply_to: Optional[str] = None
    received_date_time: Optional[str] = None
    sent_date_time: Optional[str] = None
    has_attachments: Optional[bool] = None

    # Decisión y análisis
    rule_name: Optional[str] = None
    accion: Optional[str] = None
    red_flag: bool = False
    decision_json: Optional[str] = None  # JSON completo de la decisión (string)

    # Métricas
    elapsed_time: float = 0.0  # segundos
    ai_model: Optional[str] = None
    input_tokens: int = 0
    output_tokens: int = 0
    cost: float = 0.0

    # Error
    error: bool = False
    error_descrip: Optional[str] = None

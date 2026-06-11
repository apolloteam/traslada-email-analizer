"""
db_logger.py — Envía a la base de datos (vía API) el registro de la decisión del agente.

El modelo de datos vive en models/email_decision_log.py. Acá está la lógica de cálculo de
costo y el envío por POST.

El envío es resiliente: si el POST falla, se loguea localmente pero NUNCA se propaga la
excepción, para no romper el procesamiento de correos.
"""

import os
import logging
import requests
from dotenv import load_dotenv

from models.email_decision_log import EmailDecisionLog

load_dotenv()

log = logging.getLogger(__name__)

LOG_URI = "ai/agents/emailanalyzer/logs"
LOG_API_BASE_URL = os.getenv("LOG_API_BASE_URL", "https://api.traslada.com.ar")
TIMEOUT_SEGUNDOS = 10

# Precios en USD por 1M de tokens del modelo configurado (AI_MODEL en .env).
PRECIO_INPUT_USD_POR_1M  = float(os.getenv("AI_INPUT_PRICE_PER_1M", "3.00"))
PRECIO_OUTPUT_USD_POR_1M = float(os.getenv("AI_OUTPUT_PRICE_PER_1M", "15.00"))


def calcular_costo(input_tokens: int, output_tokens: int) -> float:
    """Calcula el costo en USD según los tokens consumidos y los precios del .env."""
    costo = (
        input_tokens / 1_000_000 * PRECIO_INPUT_USD_POR_1M
        + output_tokens / 1_000_000 * PRECIO_OUTPUT_USD_POR_1M
    )
    return costo


def enviar_log(record: EmailDecisionLog) -> None:
    """
    Envía el registro al API por POST. Resiliente: ante cualquier fallo loguea localmente
    y retorna sin propagar la excepción.
    """
    url = f"{LOG_API_BASE_URL.rstrip('/')}/{LOG_URI}"
    try:
        r = requests.post(url, json=record.model_dump(), timeout=TIMEOUT_SEGUNDOS)
        r.raise_for_status()
        log.info(f"    📝 Log enviado a DB ({record.email_id}).")
    except Exception as e:
        log.error(f"    ⚠️ No se pudo enviar el log a DB ({record.email_id}): {e}")

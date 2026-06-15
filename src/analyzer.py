"""
analyzer.py — Analiza correos con Claude y decide qué acción tomar.
"""

import logging
import os
import anthropic
from dotenv import load_dotenv
load_dotenv()

from models.email_decision import EmailDecision
from utils.email_parser import extraer_texto_body

logger = logging.getLogger(__name__)

MODELO = os.getenv("AI_MODEL", "claude-sonnet-4-6")
_DEFAULT_RULES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config")

_CORREO_PROMPT_TEMPLATE = """
# Correo recibido
- **Remitente:** {remitente}
- **Fecha:** {fecha}
- **Dirección:** {direccion}
- **Asunto:** {asunto}
- **Cuerpo:**
{cuerpo}
"""


class AnalizadorClaude:
    def __init__(self, rules_dir: str = _DEFAULT_RULES_DIR):
        self.client = anthropic.Anthropic(
            api_key=os.getenv("ANTHROPIC_API_KEY"),
        )

        self.rules_dir = rules_dir
        self._system_prompt_template = self._cargar_system_prompt()

    def _cargar_system_prompt(self) -> str:
        path = os.path.join(self.rules_dir, "system_prompt.md")
        with open(path, encoding="utf-8") as f:
            contenido = f.read()
        return contenido.strip()

    def _cargar_reglas_generales(self) -> str:
        path = os.path.join(self.rules_dir, "general_rules.md")
        with open(path, encoding="utf-8") as f:
            contenido = f.read()
        return contenido

    def _cargar_reglas_especificas(self, buzon: str) -> str:
        """
        Carga reglas específicas del buzón desde {local}.md en el mismo directorio 
        que rules_path. Retorna vacío si no existe.
        """
        name = buzon.split("@")[0]  # "ventas", "soporte", etc.
        path = os.path.join(self.rules_dir, f"{name}_rules.md")
        if not os.path.exists(path):
            return "(sin reglas específicas para este correo)"
        with open(path, encoding="utf-8") as f:
            contenido = f.read()
        return contenido

    def analizar(self, correo: dict, buzon: str) -> tuple[dict, dict]:
        """
        Le pasa el correo y las reglas a Claude.
        Devuelve una tupla (decision, uso):
        - decision: dict con accion, razon, nombre_regla, etc.
        - uso: dict con input_tokens, output_tokens y modelo (para el log de costos).
        """

        remitente          = correo["from"]["emailAddress"]["address"]
        asunto             = correo.get("subject", "(sin asunto)")
        cuerpo             = extraer_texto_body(correo)
        fecha              = correo.get("receivedDateTime", "")
        reglas_generales   = self._cargar_reglas_generales()
        reglas_especificas = self._cargar_reglas_especificas(buzon)

        system_prompt = (self._system_prompt_template
            .replace("{reglas_generales}", reglas_generales)
            .replace("{reglas_especificas}", reglas_especificas))
            
        correo_prompt = _CORREO_PROMPT_TEMPLATE.format_map({
            "remitente": remitente,
            "fecha": fecha,
            "direccion": "enviado" if correo.get("direction", 0) == 1 else "recibido",
            "asunto": asunto,
            "cuerpo": cuerpo,
        })

        response = self.client.messages.parse(
            model=MODELO,
            max_tokens=2048,
            system=system_prompt,
            messages=[{"role": "user", "content": correo_prompt}],
            output_format=EmailDecision,
        )

        decision = response.parsed_output.model_dump()
        uso = {
            "input_tokens": response.usage.input_tokens,
            "output_tokens": response.usage.output_tokens,
            "modelo": MODELO,
        }
        resultado = (decision, uso)
        return resultado

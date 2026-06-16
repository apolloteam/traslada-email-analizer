"""
test_enviar_lead.py — Envía un correo de prueba simulando un lead de formulario web.

Manda un mail a aiemail1@traslada.com.ar con el formato de un lead (asunto
'Nuevo lead - Source: ...' y body con el campo 'E-mail:'), para probar que el
agente lo detecte, extraiga el email del cuerpo y lo procese correctamente.

El correo se envía DESDE noreply@traslada.com.ar para simular el remitente real
de los formularios. Esto requiere que la app tenga permisos sobre ese buzón.

Uso:
    python src/test_enviar_lead.py
    python src/test_enviar_lead.py --source WebTrasladaPresupuesto --email cliente@gmail.com
"""

import os
import sys
import argparse

# Permite importar mail_client estando en src/
_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _DIR)

from mail_client import MailClient, GRAPH

# Buzón destino (el de prueba) y buzón remitente (simula el formulario)
DESTINO = "aiemail1@traslada.com.ar"
REMITENTE_LEAD = "noreply@traslada.com.ar"


def enviar_lead(source: str, email_cliente: str):
    """Envía un lead simulado desde noreply@ hacia el buzón de prueba."""
    cuerpo = f"""Empresa: Empresa de Prueba SA
Nombre: Juan
Apellido: Pérez
E-mail: {email_cliente}
Telefono: 01152298588
Notas: Quiero un presupuesto para un traslado, gracias.
Documento:
Origen: {source}

Data: {{"DatosVehiculo":"Chevrolet Cruze Premier 2021"}}
"""

    payload = {
        "message": {
            "subject": f"Nuevo lead - Source: {source}",
            "body": {"contentType": "Text", "content": cuerpo},
            "toRecipients": [
                {"emailAddress": {"address": DESTINO}}
            ],
        },
        "saveToSentItems": True,
    }

    # Usamos un MailClient apuntando al buzón remitente (noreply@) para enviar desde ahí.
    mc = MailClient(REMITENTE_LEAD)
    mc.refresh_token()

    url = f"{GRAPH}/users/{REMITENTE_LEAD}/sendMail"
    mc._request_con_retry("POST", url, json=payload)

    print(f"✓ Lead de prueba enviado:")
    print(f"    De:      {REMITENTE_LEAD}")
    print(f"    Para:    {DESTINO}")
    print(f"    Asunto:  Nuevo lead - Source: {source}")
    print(f"    E-mail en el body: {email_cliente}")
    print(f"\n  Ahora corré el agente sobre {DESTINO} y mirá el log:")
    print(f"    - Debería decir: '📨 Lead de formulario web. Cliente: {email_cliente}'")
    print(f"    - Y al responder, debería contestar a {email_cliente} (no a {REMITENTE_LEAD}).")


def main():
    parser = argparse.ArgumentParser(description="Enviar un lead de prueba")
    parser.add_argument("--source", default="WebTrasladaPresupuesto",
                        help="Source del formulario (default: WebTrasladaPresupuesto)")
    parser.add_argument("--email", default="cliente.prueba@gmail.com",
                        help="Email del cliente que irá en el body (default: cliente.prueba@gmail.com)")
    args = parser.parse_args()

    enviar_lead(args.source, args.email)


if __name__ == "__main__":
    main()
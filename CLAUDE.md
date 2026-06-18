# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Purpose

Agente autónomo que lee emails de Outlook 365 via Microsoft Graph API, los analiza con Claude, y ejecuta acciones automáticas (responder, reenviar) según reglas configurables en Markdown.

## Setup

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env_example .env   # completar con credenciales reales
```

Variables de entorno requeridas (ver `.env_example`):
- `CLIENT_ID`, `CLIENT_SECRET`, `TENANT_ID` — app registrada en Azure AD con permisos Mail.Read, Mail.Send, Mail.ReadWrite
- `BUZONES` — lista de casillas a monitorear, separadas por `;` (ej: `ventas@traslada.com.ar;admin@traslada.com.ar`)
- `ANTHROPIC_API_KEY` — clave de API de Anthropic
- `INTERVALO_MINUTOS` — intervalo del loop (por defecto 10)
- `MAX_CORREOS_POR_CICLO` — máximo de emails a procesar por ciclo (por defecto 20)

## Run Commands

```powershell
python src/agent.py                                # loop cada 10 minutos
python src/agent.py --once                         # una sola ejecución (útil para pruebas)
python src/agent.py --interval 5                   # loop cada 5 minutos
```

Logs en `src/logs/agent_YYYYMMDD.log` (un archivo por día; al pasar la medianoche abre el del día siguiente). Para seguir en tiempo real:
```powershell
Get-Content src\logs\agent_20260618.log -Wait   # ajustar la fecha al día actual
```

## Architecture

El flujo principal es: **leer → analizar → actuar → marcar**.

```
src/agent.py                    Orquestador del loop. Itera sobre cada buzón en BUZONES,
                                aplica pre-filtros (emails enviados, no-reply, dominio
                                interno), llama a mail_client → analyzer → actions en
                                secuencia. Si Claude falla en un email individual, loguea
                                y continúa con el siguiente.

src/mail_client.py              Wrapper sobre Microsoft Graph API. Autentica via MSAL
                                (OAuth2 client_credentials). Filtra emails SIN la
                                categoría "AgenteProcesado". Tras actuar, marca el email
                                con esa categoría y lo mueve a carpeta si corresponde.
                                Soporta rutas jerárquicas ("Comercial/Cerrado").

src/analyzer.py                 Integración con Claude (claude-sonnet-4-6). Carga el
                                system prompt + reglas generales + reglas específicas del
                                buzón desde archivos Markdown (hot-reload por ciclo).
                                Devuelve un EmailDecision validado por Pydantic.

src/actions.py                  Ejecuta la decisión de Claude delegando en mail_client.
                                Soporta draft mode (borrador=True) y acción
                                combinada responder_y_reenviar.

src/models/email_decision.py    Pydantic BaseModel con los campos de la decisión de
                                Claude: accion, razon, respuesta_html, reenviar_a,
                                comentario_reenvio, prioridad, categorias,
                                carpeta_archivo, borrador,
                                red_flags_detectados, escalar_a.

src/utils/email_parser.py       Convierte HTML de email a texto plano limpio. Normaliza
                                caracteres Unicode invisibles (usados por plataformas de
                                email marketing) y trunca a 4000 caracteres.
```

## Rules Configuration

Las reglas se definen en archivos Markdown en `src/config/`:

- `system_prompt.md` — prompt base del sistema; incluye `{reglas_generales}` y `{reglas_especificas}` como placeholders
- `general_rules.md` — reglas globales a todos los buzones (red flags, soporte técnico, publicidad, fallback)
- `{buzón}_rules.md` — reglas específicas de cada casilla (ej: `ventas_rules.md`, `administracion_rules.md`)

Las reglas están escritas en lenguaje natural; Claude las interpreta sin parsing en código. Se recargan en cada ciclo (hot-reload). Para aprender a escribir reglas, ver `src/config/instructivo.md`.

Acciones posibles: `responder` | `reenviar` | `responder_y_reenviar` | `ignorar`.

## Model in Use

`src/analyzer.py` usa `claude-sonnet-4-6`. Si se cambia de modelo, actualizar la constante en ese archivo.

## Git Commits

Antes de hacer un commit, leer las convenciones en `.claude/docs/commit-conventions.md`.

## Coding Style

- En los `return`, siempre asignar el resultado a una variable y retornar esa variable. Nunca encadenar llamadas directamente en el `return`.
  - ✓ `resultado = valor.strip()[:4000]` → `return resultado`
  - ✗ `return valor.strip()[:4000]`

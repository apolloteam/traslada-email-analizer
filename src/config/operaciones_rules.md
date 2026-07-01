# Buzón de Ventas

**Dirección:** operaciones@traslada.com.ar  
**Propósito:** Recibe consultas sobre operaciones a realizar sobre una reserva (consulta, modificación, cancelación) o solicitud de nuevas reservas.

### 📢 Regla - Inspección de bandeja (resumen, sin acción)

#### Condiciones
Cualquier correo que llegue a este buzón. El objetivo es registrar un resumen del motivo del correo para tener un panorama completo del buzón y analizarlo más adelante, sin tomar ninguna acción, sin responder y sin reenviar.

#### No aplica si
- El correo es publicidad o correo no solicitado → aplica la regla de publicidad de las reglas generales, que tiene prioridad. En ese caso no generes resumen.

#### Campos de decisión
- `accion`: ignorar
- `resumen`: Generá un resumen muy breve (una o dos oraciones, máximo ~30 palabras) del motivo del correo: qué pide o informa el remitente. Sé objetivo y conciso. No incluyas saludos ni datos personales, solo el motivo central.
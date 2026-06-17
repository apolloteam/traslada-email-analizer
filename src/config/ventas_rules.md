# Buzón de Ventas

**Dirección:** ventas@traslada.com.ar  
**Propósito:** Recibe consultas comerciales, leads, primeros contactos de clientes potenciales y licitaciones.

## Base de conocimiento de este buzón
### Tipos de vehículos disponibles
- Remís:
  - Sedán Estándar: 
    - Máximo pasajeros: 4.
    - Máximo equipaje: 2 valijas + 2 equipaje de mano (aproximado, según dimensiones estándares).
    - Código: `STD`
    - Descripción: Ideal para traslados corporativos.
    - Modelos: VW Nivus, Nissan Kicks, Peugeot 2008, Fiat Cronos o similares.
  - Sedán Ejecutivo: 
    - Máximo pasajeros: 4.
    - Máximo equipaje: 2 valijas + 2 equipaje de mano (aproximado, según dimensiones estándares).
    - Código: `EJE`
    - Descripción: El más elegido por ejecutivos.
    - Modelos: Toyota Corolla, VW Virtus, Nissan Versa, VW Taos o similares.
  - Monovolumen:
    - Máximo pasajeros: 4.
    - Máximo equipaje: 4 valijas + 4 equipaje de mano (aproximado, según dimensiones estándares).
    - Código: `MVL`
    - Descripción: Ideal para traslados con equipaje desde y hacia aeropuertos.
    - Modelos: Chevrolet Spin, Citroen Berlingo, Peugeot Partner, Renault Kangoo o similares.
- Remís VIP:
  - Máximo pasajeros: 3.
  - Máximo equipaje: 2 valijas + 2 equipaje de mano (aproximado, según dimensiones estándares).
  - Código: `VIP`
  - Descripción: Eventos especiales.
  - Modelos: Mercedes Benz clase "C", clase "E" y clase "E línea nueva".
- Traslados grupales y de personal:
  - Combis y Minibuses: Contamos con combis y minibuses que transportan desde 14 hasta 24 pasajeros cada unidad (cantidad de equipaje según configuración).
  - Buses: Contamos con una moderna flota de Buses de piso simple y piso doble (desde 45 hasta 58 pasajeros por unidad, cantidad de equipaje según configuración).
  - VANS VIP: Nuestras Vans VIP destacan por su calidad y excelencia. Si se trata de viajar de la mejor manera (Mercedes Benz y Hyundai, que destacan por su elegancia, confort y seguridad).

### Tipos de clientes:
- **B2C**: Persona individual (Particular) con dominio gmail|hotmail|yahoo, etc. Pedido personal. Ejemplo: María Sol González (gmail), Pedro Aguilera (hotmail), Juan.
- **B2B**: Empresa real (SRL, SA, Club, Institución). Dominio propio o pedido claramente corporativo (aunque use gmail|hotmail).
- **Agencia**: El nombre sugiere travel, viajes, turismo, eventos, productora. Intermediario que cotiza para su cliente.

### Datos mínimos requeridos para consulta de precios/presupuestos/disponibilidad
Para que el equipo comercial pueda cotizar, hacen falta:
- Razón social o nombre de la empresa
- Fecha estimada.
- Origen y destino del traslado.
- Cantidad de pasajeros.
- Cantidad de equipaje.
- Con retorno (si se debe incluir la vuelta al origen).

Datos adicionales solo para servicios Periódicos/Recurrentes:
- Días y horarios o frecuencia estimada (diaria, semanal, etc.).
- Fecha de inicio.
- Recorrido y paradas (opcional)

### Vocabulario
- Servicio Remís: Traslado en auto de hasta 4 pasajeros.
- Servicio Grupal: Traslado en vans, minibuses, buses (más de 4 pasajeros).
- Servicio Eventual: Traslado ocasional de una única vez, evento específico.
- Servicio Periódico/Recurrente: Traslado preestablecido, mismas direcciones y horario, que se repite periódicamente (diario, semanal, mensual, etc.).

## Tono para este buzón

Complementa el tono base con:
- Entusiasta y orientado a la oportunidad: el cliente potencial está considerando 
  contratarnos, tratalo como si fuera una venta que queremos ganar.
- Usá el nombre del remitente si figura en el correo.
- Evitá tecnicismos de logística — hablá en términos del beneficio para el cliente.

## Reglas

### 📢 Regla - Consulta de servicio de remís **B2C**

#### Condiciones
El correo pregunta por precios, cotizaciones, presupuestos de un traslado de remís y encaja en el perfil B2C. También aplica si el asunto contiene "Source: WebTrasladaPresupuesto" y el lead es de un particular (perfil B2C) para un servicio de remís.

#### Ejemplos que NO aplican
En caso que ya le hayas indicado que utilice los canales para B2C y haya solicitado nuevamente asesoramiento personalizado.

#### Campos de decisión
- `accion`: responder
- `instruccion_respuesta`:
  Tratá al cliente por su nombre si lo detectás en el correo. Agradecé el interés e informá los canales para reservas B2C. Usá el siguiente ejemplo como modelo de tono, estructura y formato HTML, adaptando el nombre y el contenido al correo real:

```
  <p>Hola Gonzalo,</p>
  <p>¡Gracias por contactarnos! Nos alegra que estés considerando a Traslada para tu traslado.</p>
  <p>Para reservas o consultas podés utilizar estos canales directamente:</p>
  <ul>
    <li>Nuestra web: <a href="https://clientes.traslada.com.ar/">crear una cuenta</a></li>
    <li>App Android: <a href="https://play.google.com/store/apps/details?id=com.traslada.corporativo">descargar en Google Play</a></li>
    <li>App iOS: <a href="https://itunes.apple.com/us/app/traslada-corporativo/id1250094586?l=es&ls=1&mt=8">descargar en App Store</a></li>
    <li>WhatsApp: <a href="https://wa.me/5491140504874">escribinos por WhatsApp</a></li>
    <li>Mesa operativa: 0810-112-5111</li>
  </ul>
  <p>Desde ahí podés consultar precios y hacer reservas directamente.</p>
  <p>¡Quedamos a disposición!</p>
  <p>Saludos,<br>Equipo Traslada<br>ventas@traslada.com.ar</p>
```
- `categorias`: ["Comercial", "B2C", "Remis", "Lead"]
- `borrador`: true

### 📢 Regla - Consulta de servicio Grupal **B2C**

#### Condiciones
El correo pregunta por precios, cotizaciones o presupuestos de un traslado grupal, y encaja en el perfil B2C. También aplica si el asunto contiene "Source: WebTrasladaPresupuesto" y el lead es de un particular (perfil B2C) para un traslado grupal.

#### Campos de decisión
- `accion`: responder_y_reenviar
- `reenviar_a`: vstaque@traslada.com.ar;jgomezmoreno@traslada.com.ar;rodrigosalinas@traslada.com.ar
- `categorias`: ["Comercial", "B2C", "Grupal", "Lead"]
- `instruccion_respuesta`:
  - Agradecé el interés (si no lo hiciste en un mensaje anterior del hilo).
  - **Según si están los datos mínimos requeridos** (ver la base de conocimiento del buzón):
    - **Si faltan datos:** solicitá amablemente los datos faltantes e indicá que son requeridos para poder asesorarlo. Informá que, una vez que tengamos todos los datos, un asesor comercial se contactará con una propuesta personalizada.
    - **Si están todos los datos:** informá que un asesor comercial se contactará en breve con la propuesta. Si detectás que en el hilo se los habías pedido antes, agradecé que los haya enviado.
  - Incluí el nombre del solicitante si figura en el correo.
- `comentario_reenvio`:
  - **Si faltan datos:** 🚌 FYI - Oportunidad de servicio GRUPAL B2C entrante. Se le pidieron datos faltantes - 👀 Controlar.
  - **Si están completos:** 🚌 FYA - Oportunidad de servicio GRUPAL B2C. 🙋‍♂️ Contactar al cliente.
- `borrador`:
  - **Si faltan datos:** false
  - **Si están completos:** true

### 📢 Regla - Consulta de servicio de remís **B2B**

#### Condiciones
El correo pregunta por precios, cotizaciones o presupuestos de un traslado de remís, y encaja en el perfil B2B. También aplica si el asunto contiene "Source: WebTrasladaPresupuesto" y el lead es de una empresa (perfil B2B) para un servicio de remís.

#### Campos de decisión
- `accion`: responder_y_reenviar
- `reenviar_a`: mbfernandez@traslada.com.ar;rodrigosalinas@traslada.com.ar
- `categorias`: ["Comercial", "B2B", "Remis", "Lead"]
- `instruccion_respuesta`:
  - Agradecé el interés (si no lo hiciste en un mensaje anterior del hilo).
  - **Según si están los datos mínimos requeridos** (ver la base de conocimiento del buzón):
    - **Si faltan datos:** solicitá amablemente los datos faltantes e indicá que son requeridos para poder asesorarlo. Informá que, una vez que tengamos todos los datos, un asesor comercial se contactará con una propuesta personalizada.
    - **Si están todos los datos:** informá que un asesor comercial se contactará en breve con la propuesta. Si detectás que en el hilo se los habías pedido antes, agradecé que los haya enviado.
  - Incluí el nombre de la persona y de la empresa si figuran en el correo.
- `comentario_reenvio`:
  - **Si faltan datos:** 💼 FYI - Oportunidad de servicio REMIS B2B. Se le pidieron datos faltantes - 👀 Controlar.
  - **Si están completos:** 💼 FYA - Oportunidad de servicio REMIS B2B. 🙋‍♂️ Contactar al cliente.
- `borrador`:
  - **Si faltan datos:** false
  - **Si están completos:** true

### 📢 Regla - Consulta de servicio Grupal Eventual **B2B**

#### Condiciones
El correo pregunta por precios, cotizaciones o presupuestos de un traslado grupal para una fecha o evento específico (Eventual), y encaja en el perfil B2B. También aplica si el asunto contiene "Source: WebTrasladaPresupuesto" y el lead es de una empresa (perfil B2B) para un traslado grupal puntual/eventual.

#### Campos de decisión
- `accion`: responder_y_reenviar
- `reenviar_a`: vstaque@traslada.com.ar;jgomezmoreno@traslada.com.ar;rodrigosalinas@traslada.com.ar
- `categorias`: ["Comercial", "B2B", "Grupal", "Lead"]
- `instruccion_respuesta`:
  - Agradecé el interés (si no lo hiciste en un mensaje anterior del hilo).
  - **Según si están los datos mínimos requeridos** (ver la base de conocimiento del buzón):
    - **Si faltan datos:** informá que, una vez que tengamos todos los datos, un asesor comercial se contactará con una propuesta personalizada. Pedí amablemente los datos que faltan.
    - **Si están todos los datos:** informá que un asesor comercial se contactará en breve con la propuesta. Si detectás que en el hilo se los habías pedido antes, agradecé que los haya enviado.
  - Incluí el nombre del solicitante y de la empresa si figuran en el correo.
- `comentario_reenvio`:
  - **Si faltan datos:** 🚌 FYI - Oportunidad de servicio GRUPAL Eventual B2B entrante. Se le pidieron datos faltantes - 👀 Controlar.
  - **Si están completos:** 🚌 FYA - Oportunidad de servicio GRUPAL Eventual B2B. 🙋‍♂️ Contactar al cliente.
- `carpeta_archivo`:
  - **Si faltan datos:** "Comercial/Analizado"
  - **Si están completos:** null
- `borrador`:
  - **Si faltan datos:** false
  - **Si están completos:** true

### 📢 Regla - Consulta de servicio Recurrente **B2B**

#### Condiciones
El correo pregunta por precios, cotizaciones, presupuestos o contratación periódica de un traslado, y encaja en el perfil B2B. También aplica si el asunto contiene "Source: WebTrasladaCharters" (lead del formulario web de charters, que corresponde a traslado de personal grupal recurrente B2B).

#### Campos de decisión
- `accion`: responder_y_reenviar
- `reenviar_a`: vstaque@traslada.com.ar;jgomezmoreno@traslada.com.ar;rodrigosalinas@traslada.com.ar
- `categorias`: ["Comercial", "B2B", "Charter", "Lead", "⭐ Prioritario"]
- `instruccion_respuesta`:
  - Agradecé el interés (si no lo hiciste en un mensaje anterior del hilo).
  - **Según si están los datos mínimos requeridos** (ver la base de conocimiento del buzón):
    - **Si faltan datos:** informá que, una vez que tengamos todos los datos, un asesor comercial se contactará con una propuesta personalizada. Pedí amablemente los datos que faltan.
    - **Si están todos los datos:** informá que un asesor comercial se contactará en breve con la propuesta. Si detectás que en el hilo se los habías pedido antes, agradecé que los haya enviado.
  - Incluí el nombre del solicitante y de la empresa si figuran en el correo.
- `comentario_reenvio`:
  - **Si faltan datos:** 📅 FYI - Oportunidad de contrato B2B entrante. Se le pidieron datos faltantes - 👀 Controlar.
  - **Si están completos:** 📅 FYA - Oportunidad de contrato B2B. 🙋‍♂️ Contactar al cliente.
- `carpeta_archivo`:
  - **Si faltan datos:** "Comercial/Analizado"
  - **Si están completos:** null
- `borrador`:
  - **Si faltan datos:** false
  - **Si están completos:** true

### 📢 Regla - Licitación o concurso de precios

#### Condiciones
Correo con pliego, concurso, licitación, RFQ/RFP, proceso de selección de proveedores, o documentación licitatoria adjunta.

#### Campos de decisión
- `accion`: responder_y_reenviar
- `reenviar_a`: vstaque@traslada.com.ar;jgomezmoreno@traslada.com.ar;rodrigosalinas@traslada.com.ar
- `instruccion_respuesta`: Tono formal. Confirmar recepción de documentación. Indicar que equipo comercial fue notificado y trabajará en la propuesta. Si hay fecha límite, reconocerla. No comprometer condiciones.
- `comentario_reenvio`: 🧾 FYA - Licitación. 🙋‍♂️ Analizar.
- `categorias`: ["Comercial", "Licitación", "⭐ Prioritario"]
- `borrador`: true

### 📢🔀 Regla - Derivación a otra área

#### Condiciones
El correo no corresponde a una gestión comercial sino a otra área: reclamos, atención al cliente, soporte técnico, facturación, operaciones, gestión de choferes/prestadores.

#### Ejemplos que aplican
- "el chofer no llegó", "quiero cancelar mi reserva de mañana", "necesito cambiar el horario de un viaje ya agendado".
- "necesito la factura del viaje del martes", "tengo un problema con un pago".
- "soy chofer y no puedo acceder a la app".

#### Ejemplos que NO aplican
- Consultas de precio o presupuesto de un traslado nuevo (eso es Consulta comercial).

#### Campos de decisión
- `accion`: reenviar
- `reenviar_a`: según el área que corresponda, elegí UN destino de esta tabla:
  - Soporte técnico / incidentes de sistema → reservas@traslada.com.ar
  - Facturación, pagos, comprobantes → administracion@traslada.com.ar
  - Operaciones / consultas post-reserva (estado, cambios, cancelaciones) → reservas@traslada.com.ar
  - Gestión de choferes → flota@traslada.com.ar
  - Atención al cliente / reclamos / objetos perdidos → sac@traslada.com.ar
- `comentario_reenvio`: 🔀 Correo recibido en Ventas que corresponde a esta área. Derivado para su gestión.
- `categorias`: ["Derivado"]
- `carpeta_archivo`: "Redirigidos"

### 📢 Regla - Lead de formulario de Contacto

#### Condiciones
El asunto contiene "Source: WebTrasladaContacto". Es un lead del formulario de contacto general de la web, donde el cliente escribió un mensaje libre en el campo "Notas". El cliente real es el email del campo "E-mail:" del cuerpo.

#### Campos de decisión
- `accion`: responder_y_reenviar
- `reenviar_a`: vstaque@traslada.com.ar;jgomezmoreno@traslada.com.ar
- `categorias`: ["Comercial", "Lead", "Web"]
- `borrador`: true
- `instruccion_respuesta`:
  - Leé el contenido del campo "Notas" del lead y respondé según lo que pida:
    - **Si es una consulta por un traslado/viaje** (precios, presupuesto, disponibilidad): tratala como una consulta comercial. Si faltan datos mínimos requeridos (ver base de conocimiento del buzón), pedilos amablemente e informá que un asesor lo contactará. Si están todos los datos, informá que un asesor lo contactará en breve con una propuesta.
    - **Si es una consulta general que podés responder con la base de conocimiento del buzón** (ej. zonas donde operamos, tipos de servicio): respondela directamente, de forma clara y cordial.
    - **Si es cualquier otra cosa** o no podés resolverla: saludá, confirmá la recepción del mensaje e informá que nos pondremos en contacto a la brevedad. No inventes información.
  - Tratá al cliente por su nombre (campo "Nombre" del lead) si está disponible.

### 📢 Regla - Lead de registro en la app (informativo)

#### Condiciones
El asunto contiene "Source: WebClientesTraslada". Es una notificación informativa de que un cliente se registró en la app. No requiere ninguna acción ni respuesta.

#### Campos de decisión
- `accion`: ignorar
- `categorias`: ["Web", "Registro"]

### 📢📁 Regla - Archivo de conversaciones finalizadas

Cuando determinés que la conversación está completamente resuelta (el cliente agradeció, confirmó conformidad, o el tema claramente no requiere seguimiento), asigná `carpeta_archivo` con la carpeta correspondiente:

- El cliente aceptó un presupuesto o contrató el servicio → `"Comercial/Cerrado"`
- La solicitud fue rechazada (fuera de servicio, sin disponibilidad, no aplica) → `"Comercial/NoAtendible"`

Si la conversación sigue abierta, el cliente no respondió, o hay dudas → dejá `carpeta_archivo` en null.

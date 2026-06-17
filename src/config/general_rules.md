## Red Flags

### Amenaza legal
**condiciones:** El correo menciona abogados, demandas, juicio, "voy a denunciar", acciones legales, mediación, o cualquier lenguaje que implique una acción legal contra la empresa.

- `escalar_a`: estebansomma@traslada.com.ar
- `categorias`: ["🚨 Red Flag", "Legal"]

### Mención de prensa o redes sociales
**condiciones:** El cliente amenaza con publicar su experiencia en redes sociales, contactar medios de comunicación, hacer pública su queja, o menciona periodistas.

- `escalar_a`: estebansomma@traslada.com.ar
- `categorias`: ["🚨 Red Flag", "Reputacional"]

## Reglas

### 📢 Regla - Publicidad y correos no solicitados

#### Condiciones
El correo es claramente promocional, publicitario, o una oferta no solicitada de productos o servicios dirigida a la empresa (no una consulta de un cliente).

#### Ejemplos que aplican
- newsletters comerciales, ofertas de proveedores, propuestas de agencias de marketing, correos masivos con diseño de campaña.

#### Ejemplos que NO aplican
- El correo es una consulta genuina de un cliente sobre nuestros servicios.
- La oferta es de un proveedor con quien ya tenemos relación.
- Hay dudas sobre si es publicidad o una consulta real → usá la regla que mejor aplique.

#### Campos de decisión
- `accion`: ignorar
- `carpeta_archivo`: "Publicidad"
- `categorias`: ["Publicidad"]
- `comentario_reenvio`: null


### 📢 Regla - Respuesta automática general

#### Condiciones
Cualquier correo que no encaje en las reglas anteriores y sea de un remitente externo.

No aplica a correos internos del dominio traslada.com.ar, dottransfers.com y vak.com.ar, **excepto los leads de formularios web (asunto "Nuevo lead - Source:"), que aunque vengan de un remitente interno deben procesarse con su regla correspondiente.**

#### Campos de decisión
- `accion`: responder
- `instruccion_respuesta`: Agradecé el contacto. Indicá que revisaremos su mensaje y responderán a la brevedad. No detalles más información.
- `categorias`: ["Ignorar"]

## Leads de formularios web
Los correos con asunto que empieza con "Nuevo lead - Source:" son leads generados por los formularios de nuestras webs. Aunque el remitente sea un correo interno (@traslada.com.ar), NO son correos internos a ignorar: representan a un CLIENTE EXTERNO que completó un formulario. El cliente real es el email del campo "E-mail:" del cuerpo. 
Estos correos SÍ deben procesarse según la regla de lead que corresponda a su Source.
# Oppu — Plan del demo para la Solution Interview

> **Estado:** v1.0 (stack en Python; revisado en 5 rondas con Codex / GPT-6-Astra). Se ajusta después de las Solution Interviews.
> **Base:** `Oppu_Problem_Interview_Consolidado.md` (11 Problem Interviews, Lean Canvas v2).
> **Propuesta de valor a probar:** *"Te avisamos a tiempo, y solo de lo que va con tu carrera y ciclo."*

Cada decisión del plan apunta a la evidencia que la justifica (por ejemplo, `§19.6` es la sección 19.6 del documento consolidado). Si una entrevista contradice esa evidencia, la decisión se revisa.

---

## 1. Qué debe lograr el demo

El demo no es el producto final. Es un instrumento para la Solution Interview. Tiene que dejar que un estudiante **viva la experiencia con su propio perfil** y nos dé evidencia sobre:

1. si el filtro por carrera, ciclo e intereses produce oportunidades que le sirven;
2. si entiende y usa la fecha de cierre y el recordatorio (intención; la conducta real se mide en el mini-piloto, §2.2);
3. si el formato de cada aviso es suficiente para decidir si postular;
4. qué canal y qué frecuencia de alertas declara preferir.

Por eso el demo tiene que ser **funcional con datos reales**. Un prototipo en Figma no puede personalizar la lista según la carrera y el ciclo de cada entrevistado, y eso es justo lo que queremos validar.

**Alcance de la evidencia:** con unas 10 entrevistas, los resultados son **exploratorios**: sirven para decidir qué construir y qué descartar, no para afirmar efectos generalizables. Los umbrales se expresan en proporción (por ejemplo, "6 de 10" equivale a 60 % si participan 12 personas).

---

## 2. Hipótesis de solución

### 2.1. En la entrevista

| # | Hipótesis | Criterio de éxito | Cómo se mide |
|---|---|---|---|
| **S1 — Relevancia** | Con el servicio **curación + filtro**, el estudiante considera relevante la mayoría de lo que ve. | **Mediana por participante** ≥ 70 % de "Me sirve" sobre sus tarjetas expuestas (fórmula en §8.1). Se reporta también el agregado y la distribución. | Exposición real de cada tarjeta y voto 👍/👎. Mide el servicio completo, no el filtro aislado (§7). |
| **S2 — Anticipación (intención)** | Al ver la fecha de cierre, el estudiante quiere asegurarse de no olvidarla. | ≥ 60 % de participantes usan "Recuérdame" en al menos una oportunidad que marcaron como relevante, **durante las fases sin indicación** (pasos 3 y 4 del guion). | Evento `recordatorio_creado` con su fase. Solo mide intención y descubribilidad. |
| **S3 — Accionabilidad** | Con la tarjeta y el detalle, el estudiante puede decidir si postularía sin buscar información fuera. | ≥ 70 % completan la tarea de decisión (sí **o** no) en ≤ 60 s y declaran tener la información necesaria. | Tarea con una **tarjeta reservada** que no apareció en el feed, cronometrada por el observador (§9). El clic en "Postular" se registra aparte y no cuenta para S3. |
| **S4 — Canal** | Descriptiva: no asumimos un canal ganador (`§18.3`). | Sin umbral. Se reporta la distribución de primera opción (push, WhatsApp, correo, "ninguno") y los motivos. | Pregunta en el onboarding + seguimiento verbal. |
| **S5a — Volumen** | El estudiante tolera pocas alertas. | ≥ 70 % eligen un máximo de 3 alertas por semana o menos. | Selector de máximo semanal. |
| **S5b — Formato** | Se prefiere un resumen semanal + alertas urgentes antes que alertas sueltas. | Descriptiva: se reporta la distribución. | Selector de formato. |
| **S6 — Compatibilidad** | Exploratoria: ¿el indicador Alta/Media ayuda a priorizar o genera desconfianza? (`§19.6`) | Sin umbral causal. Se reportan los argumentos a favor y en contra. Se retira si ≥ 40 % expresa desconfianza. | Preguntas después de las tareas. |
| **S7 — Interés con compromiso** | Quien vive el demo quiere recibir alertas reales. | ≥ 50 % se inscriben en el mini-piloto con consentimiento explícito. Mide interés comprometido, no uso sostenido. | Pantalla final de inscripción. |

### 2.2. Mini-piloto concierge (conducta real)

La entrevista no puede mostrar si una alerta llega a tiempo y cambia lo que hace el estudiante. Para eso, los inscritos en S7 entran en un **piloto concierge de 2 semanas** que empieza en el siguiente sprint, **solo después** de que las herramientas del piloto pasen su verificación (hito "Piloto aprobado", §10).

**Canales operativos:** solo **WhatsApp** y **correo**, enviados a mano. Push no se ofrece en el piloto porque no está implementado. En la inscripción se registran por separado el **canal preferido** (S4, puede ser push o "ninguno") y el **canal operativo consentido**. Se cuenta cuántos no se inscriben porque su canal preferido no está disponible, para interpretar S7.

**Mensajes y accesos:** cada mensaje enviado es un registro `Mensaje` (destinatario, canal, tipo `alerta` o `resumen`, token único, hora real de envío) con una o varias oportunidades asociadas (`MensajeOportunidad`, cada una con su hito). Un resumen semanal es **un** mensaje aunque incluya varias oportunidades. El link del mensaje es `/a/<token>` y abre una **página del piloto** (`/p/<token>`) con solo las oportunidades de ese mensaje, independiente de la sesión de la entrevista (que ya está finalizada). Desde ahí, "Postular" pasa por `/ir/<id>?m=<token>`.

**La hora de envío es la real y confirmada:** la pantalla de `envios_del_dia` tiene, por mensaje, un botón **"Preparar"** que abre WhatsApp (`wa.me` con el texto ya escrito) o el correo y registra `preparado_at`, y un botón **"Confirmar enviado"** que la persona pulsa cuando el mensaje efectivamente salió y que registra `enviado_at`. Solo los mensajes confirmados cuentan para P1 y para el tope. Un mensaje preparado y no confirmado en 30 minutos pasa a **"por verificar"**, nunca a pendiente automáticamente: la persona revisa el historial de WhatsApp o del correo y lo confirma con la hora observada, o lo devuelve explícitamente a pendiente. Así no se reenvía algo que sí salió.

**Calendario del piloto:**

| Momento | Qué pasa |
|---|---|
| Día 1–14 del piloto | Envíos según la política (§6.4). El último envío es el día 14. |
| Cierre de observación | **72 h después del último `enviado_at` confirmado** (alrededor del día 17). Es el **corte analítico**: los accesos y bajas posteriores no cuentan para P1 y P3. Las bajas posteriores **sí** detienen la encuesta y sus recordatorios y activan la eliminación del contacto. |
| Cierre de observación | Se envía la **encuesta final**, que cubre todo lo ocurrido hasta ese momento. Así la ventana de P2 es la misma para todos. |
| +2 días | Recordatorio de la encuesta a quien no respondió. |
| +4 días | Cierre de la encuesta y análisis. |
| Día 21 a más tardar | Eliminación de contactos (§11). Si la encuesta se atrasa, la eliminación no se atrasa: lo no respondido queda como "desconocido". |

**Encuesta final:** por cada alerta recibida, ¿ya la conocías?, ¿iniciaste la postulación (creaste cuenta, abriste o enviaste el formulario) y en qué fecha?; y en general, ¿el volumen te pareció bien, mucho o poco?

| # | Hipótesis del piloto | Criterio | Denominador y reglas |
|---|---|---|---|
| **P1** | Los participantes acceden a las alertas. | ≥ 50 % de los mensajes tienen al menos un acceso al enlace en 72 h. | Denominador: mensajes enviados (un resumen cuenta como uno). Accesos con agente de usuario de previsualización conocido (WhatsApp, Facebook, Google) se excluyen; accesos en los primeros 5 s tras el envío se marcan como **ambiguos** y se reporta P1 **con y sin** ellos. Si las dos cifras quedan a distintos lados del 50 %, P1 es inconclusa. Mide acceso al enlace, no lectura. |
| **P2** | Tras una alerta, el participante inicia postulaciones. | ≥ 30 % de los participantes declaran haber iniciado, **después** de la alerta, al menos una postulación que no conocían antes. | Participantes con ≥ 1 envío que respondieron la encuesta. Se reporta como acción autodeclarada, sin atribuir causalidad. No respondieron: se reportan aparte. |
| **P3** | El volumen es aceptable. | ≤ 20 % en **rechazo** (pidieron bajar la frecuencia, salieron o respondieron "mucho"). | Participantes con ≥ 1 envío, clasificados en **aceptación** (respondió "bien" o "poco"), **rechazo** y **desconocido** (sin respuesta ni baja). Solo se concluye si al menos el 70 % tiene resultado conocido **y** el peor caso (desconocidos contados como rechazo) no cambia el veredicto; si no, P3 es **inconclusa**. |

---

## 3. Alcance del demo (MoSCoW)

### Must (sin esto no hay entrevista)

- **Onboarding de menos de 60 s:** carrera, ciclo, tipos de oportunidad, hasta 3 intereses (consultoría, finanzas, investigación…), situación (busco prácticas ahora / pronto / no por ahora), canal preferido, máximo semanal y formato.
- **Feed "Para ti"** con 5 a 7 tarjetas, no un feed infinito (`§18.4`).
- **Tarjeta:** tipo, organización, **"Cierra en N días"**, resumen de 3 puntos, compatibilidad, 👍/👎 y botón **"Postular"**.
- **Detalle:** requisitos, fechas, fuente oficial, "verificado hace N días" (`§19.8`). Si la convocatoria ya cerró, se muestra como **cerrada**, sin botón para postular.
- **"Recuérdame":** guarda la intención y ofrece **descargar el .ics** (con alarmas 7 días y 1 día antes del cierre) o **abrir Google Calendar** (que usa los avisos predeterminados del participante; la pantalla lo indica). En el demo, el recordatorio efectivo es ese evento de calendario. La app **no promete** enviar un aviso que no va a enviar. Pulsar el botón, exportar y guardar el evento son cosas distintas y se reportan por separado.
- **Feedback por tarjeta:** 👍/👎 con motivo opcional ("no es mi carrera", "no es mi ciclo", "no me interesa", "ya lo sabía"). Se puede cambiar el voto; cuenta el último.
- **Alerta simulada** dentro de la app, disparada desde el panel del entrevistador (§4).
- **Panel del entrevistador** (protegido con PIN): crear entrevista, reiniciar, disparar alerta, finalizar.
- **Datos reales:** convocatorias vigentes que cubran a todos los perfiles reclutados (§7).
- **Registro de eventos** (§8) y exportación a CSV.
- **Admin de Django** para cargar, etiquetar y verificar convocatorias.
- **Inscripción al mini-piloto** con consentimiento específico (§11).

### Should (solo después de congelar y ensayar el Must)

- **Compartir por WhatsApp** desde la tarjeta (`§19.4`, `§19.5`).
- **Badge "Poco frecuente"** para intercambio y doble grado (`§19.3`).
- **Guardadas** (lista simple).

### Could (fuera del compromiso del sprint)

- PWA instalable y Web Push real (`pywebpush`).
- Envío automático de recordatorios y resumen semanal por correo.
- Comparación contrabalanceada de tarjeta con y sin compatibilidad (S6 confirmatoria).
- Extracción asistida por IA del texto de una convocatoria.

### Won't (fuera del demo, a propósito)

- Agregador automático o scraping. La curación es manual (concierge).
- Integración real con UP Experience o con el correo institucional. Se pregunta en la entrevista, no se construye.
- Bot real de WhatsApp: en el piloto los mensajes se envían a mano.
- Monetización, cuentas de empresas, publicación por terceros, feed social o anuncios (`§19.8`).

---

## 4. Flujo del demo en la entrevista

```
Entrevistador: panel (PIN) ──► "Nueva entrevista" (código E01) ──► entrega el celular / link
             │
             ▼
Estudiante:  Onboarding ──► Feed "Para ti" (5–7 tarjetas) ──► 👍/👎
             │
             ├──► Detalle ──► Postular (/ir/<id>) / Recuérdame (.ics / Google Calendar)
             │
             ▼
Entrevistador dispara la alerta simulada ──► el estudiante la abre (o no)
             │
             ▼
Cierre: inscripción opcional al mini-piloto ──► Entrevistador: "Finalizar entrevista"
```

**Vinculación entre el panel y el celular del participante:**

- El entrevistador crea la entrevista en su panel (en su propio celular o laptop). El panel muestra un **QR / link con un token aleatorio** de un solo uso (`/e/<token>`).
- El celular del participante abre ese link: el servidor vincula **esa** sesión a la entrevista y marca el token como usado. Sin token válido no se puede entrar al demo.
- La **alerta simulada** llega al celular del participante por **consulta periódica con HTMX** (cada 3 s pregunta al servidor si hay una alerta pendiente). Sin WebSockets.
- **Finalizar** invalida la entrevista en el servidor: cualquier petición posterior de esa sesión **a las rutas del demo** muestra "Entrevista finalizada". Las rutas del piloto (`/a/`, `/p/`, `/ir/?m=`) no dependen de esa sesión. Así no depende de cerrar el navegador del participante.
- Se prueba con dos entrevistas simultáneas (§10).

**Aislamiento entre entrevistas:**

- Cada entrevista es un registro `Entrevista` (código `E01`, `E02`…). El perfil, los votos y los eventos cuelgan de ella.
- **Reiniciar** es una acción explícita del panel del entrevistador: finaliza la entrevista actual y genera un token nuevo. **Nunca borra** datos anteriores. Recargar la página no reinicia nada.
- Los datos de pruebas internas y ensayos se marcan como `es_prueba` y se excluyen del análisis.

**Perfil de respaldo:** si el demo falla con el perfil real, se usa un perfil precargado solo para mostrar la interfaz. Con perfil de respaldo, esa entrevista se **excluye de S1, S2 y S3** (no es su perfil); S4, S5, S6, S7 y las respuestas cualitativas siguen siendo válidas.

---

## 5. Arquitectura y tecnologías

### 5.1. Decisión principal: web app en Python

El equipo domina Python, así que el demo se construye con **Django**: un solo lenguaje para servidor, páginas, administración y análisis. Es una web responsiva que se abre con un link en cualquier celular, sin instalar nada.

| Opción | A favor | En contra | Decisión |
|---|---|---|---|
| **Django + HTMX** | Todo en Python. El admin de Django da el panel de contenido sin programarlo. HTMX permite interacciones fluidas (👍/👎, "Recuérdame") sin un frontend en JavaScript. | Requiere un JavaScript mínimo para medir exposición (§8). | **Elegida.** |
| FastAPI + React/Next.js | API limpia y frontend moderno. | Dos lenguajes y admin hecho a mano. | Descartada para el demo. |
| Streamlit / Reflex | Muy rápido en Python puro. | Aspecto de "dashboard", poco control de la interfaz, que es justo lo que se evalúa. | Descartada. |
| App nativa (Expo) | Push nativo confiable. | Instalación en cada entrevista; no es Python. | Reconsiderar para el piloto si push domina en S4. |
| Figma clicable | Lo más rápido. | No personaliza por perfil: no valida S1. | Solo para bocetar el día 1. |

### 5.2. Stack

| Capa | Tecnología | Por qué |
|---|---|---|
| Lenguaje y framework | **Python 3.12 + Django 5.2 LTS** | Lo que el equipo domina, con soporte extendido. Incluye ORM, migraciones, sesiones, formularios y admin. |
| Dependencias | **uv** con `uv.lock` versionado; **ruff** para lint y formato | Mismas versiones para los 4 integrantes y en producción. |
| Interfaz | **Plantillas de Django + HTMX + Tailwind CSS** (CLI standalone, sin Node) | Interfaz rápida, visual y limpia (`§20.3`). daisyUI es opcional; si su configuración standalone complica el día 2, se usa Tailwind solo. |
| JavaScript propio | Un archivo pequeño: medición de exposición de tarjetas (IntersectionObserver) y tiempos de tarea | Es lo único que no resuelve el servidor. |
| Base de datos | **PostgreSQL** en producción (Neon o Supabase, plan gratuito). Desarrollo y pruebas pueden usar SQLite porque el modelo solo usa campos portables. | Carreras e intereses son relaciones muchos-a-muchos, no `ArrayField`. |
| Identidad | **Sin login** para estudiantes: la sesión de Django apunta a la `Entrevista`. Admin y panel del entrevistador con usuario/PIN. | Cualquier login es fricción en una entrevista de 25 minutos. |
| Contenido | **Django admin** con filtros por tipo, carrera, estado y fecha de cierre, y acción "marcar como verificada" | Panel listo desde el día 2. |
| Importación | `manage.py importar_convocatorias`: lee el CSV exportado de Google Sheets con el módulo `csv`, usa un **identificador estable** (`codigo`) para actualizar sin duplicar y reporta errores por fila | Reimportar es seguro. |
| Calendario | **icalendar** para el .ics + link de Google Calendar | Hace real el recordatorio sin enviar notificaciones. |
| Analítica | **Tabla propia de eventos** + `manage.py exportar_eventos` a CSV; análisis con **pandas** en un notebook | Los datos quedan en nuestra base y se analizan en Python. Sin PostHog. |
| Servidor y estáticos | **gunicorn** + **WhiteNoise** | Configuración estándar de Django en producción. |
| Hosting | **Railway** o **Render** desde GitHub; durante la semana de entrevistas, un plan que **no se duerma** (unos 5–7 USD) | El plan gratuito de Render tarda unos 50 s en despertar: inaceptable delante de un entrevistado. |
| Calidad | **pytest + pytest-django**; **Playwright para Python** para el flujo principal | Casos obligatorios en §10. |

### 5.3. Estructura del proyecto

```
oppu/
  config/          settings (base / producción), urls
  catalogo/        Carrera, Interes, Oportunidad; admin; importación
  perfiles/        Entrevista, Perfil, onboarding
  feed/            matching.py, feed, detalle, voto, recordatorio, .ics, /ir/<id>
  entrevistas/     panel del entrevistador, alerta simulada, inscripción al piloto
  eventos/         Evento, registro, exportación
  templates/  static/
  tests/
analisis/          notebook de la matriz de evidencia
```

### 5.4. Despliegue (checklist)

- Variables de entorno: `SECRET_KEY`, `DATABASE_URL`, `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`, PIN del entrevistador. Nada de secretos en el repositorio.
- `DEBUG=False`, HTTPS, cookies seguras.
- Migraciones y `collectstatic` en cada despliegue.
- Admin en una ruta no obvia, con contraseñas fuertes y solo para el equipo. La exportación de eventos y del piloto solo es accesible para el staff.
- Copia de seguridad de la base antes y después de la semana de entrevistas.

---

## 6. Lógica central

### 6.1. Filtros duros (si no cumple, no se muestra)

- `estado = publicada`;
- la carrera del perfil está en las carreras de la oportunidad, o la oportunidad es "todas las carreras";
- el ciclo del perfil está entre `ciclo_min` y `ciclo_max` (inclusive);
- `fecha_apertura` es nula o ya pasó;
- `fecha_cierre` es **hoy o posterior** (zona horaria `America/Lima`; una convocatoria que cierra hoy se muestra hasta las 23:59 salvo que tenga hora de cierre explícita);
- verificada hace **7 días o menos**. Si se pasa de ese plazo, se reverifica antes de la entrevista.

Las convocatorias sin fecha de cierre (postulación continua) no entran en el demo: el valor que se prueba es el aviso antes del cierre.

### 6.2. Compatibilidad (afinidad, sin urgencia)

| Factor | Puntos |
|---|---|
| El tipo coincide con los tipos elegidos | 50 |
| Al menos un interés en común | 30 |
| Situación "busco prácticas ahora" y la oportunidad es de prácticas | 20 |

- **Alta:** 70 o más. **Media:** 40–69. Por debajo de 40 no se muestra.
- La urgencia **no** suma a la compatibilidad: una oportunidad no se vuelve más "compatible" porque cierre pronto.

### 6.3. Orden del feed (prioridad)

1. Compatibilidad (Alta antes que Media).
2. Dentro de cada grupo: primero las que cierran en 14 días o menos, luego las poco frecuentes (intercambio, doble grado).
3. Desempate: fecha de cierre más cercana y luego `codigo`.

Máximo 7 tarjetas. Si quedan menos de 5, el feed muestra lo que hay y un mensaje honesto ("Por ahora estas son las que van con tu perfil"). Nunca se rellena con oportunidades que no pasan el filtro.

**Los pesos se congelan** desde el ensayo del día 6 hasta el final de las entrevistas, para que todos los participantes vean el mismo algoritmo.

Implementación: `feed/matching.py`, funciones puras (perfil + oportunidades + fecha actual → lista ordenada con compatibilidad), cubiertas con pytest.

### 6.4. Política de notificaciones (para el mini-piloto)

Responde a los riesgos de retención de `§19.8`. La aplica el equipo a mano durante el piloto:

- **Hitos posibles por oportunidad:** `nueva`, `recordatorio_14d` (solo poco frecuentes: intercambio, doble grado), `recordatorio_7d`, `recordatorio_2d`. Los recordatorios solo aplican a oportunidades marcadas como relevantes o con "Recuérdame".
- **Tipos de mensaje:** `alerta` (una oportunidad, un hito) o `resumen` (varias oportunidades con sus hitos).
- **Sin duplicados:** como máximo una vez por participante + oportunidad + hito, sea en alerta o en resumen.
- **Tope semanal:** el máximo que eligió cada participante, contado en **mensajes**, nunca más de 3. Si el formato es "resumen semanal + urgentes", el resumen cuenta como 1 mensaje y los urgentes son solo los `recordatorio_2d`.
- **Prioridad cuando se llega al tope:** primero `recordatorio_2d`, luego poco frecuentes, luego `recordatorio_7d`, por último `nueva`. Lo que no entra se agrupa en el siguiente resumen o se descarta.
- **Horario:** nada entre 22:00 y 08:00; lo que caería ahí se envía a las 08:00, **salvo** que la oportunidad ya haya cerrado para entonces, en cuyo caso se descarta.
- **Antes de cada envío** se verifica que la oportunidad siga abierta y vigente.
- Cada mensaje dice cómo bajar la frecuencia o salir.
- **Baja:** al registrarla (`baja_at`) se detienen los envíos de inmediato y se cancelan los mensajes pendientes o preparados sin confirmar. En ≤ 48 h se borra el **contacto**, pero se conservan, sin datos de contacto, la inscripción anonimizada, sus mensajes, accesos y la baja misma, porque P3 necesita contar ese rechazo.

Para no depender de la memoria del equipo, un comando `manage.py envios_del_dia` lista qué enviar hoy a quién aplicando estas reglas; el equipo envía a mano y marca cada envío como hecho en el admin.

### 6.5. Modelo de datos

```
Carrera             id, nombre
Interes             id, nombre

Oportunidad         id, codigo (único, estable), titulo, organizacion, tipo,
                    carreras (M2M Carrera), todas_carreras (bool),
                    intereses (M2M Interes), ciclo_min, ciclo_max,
                    fecha_apertura (nula), fecha_cierre, hora_cierre (nula),
                    resumen_1, resumen_2, resumen_3, requisitos,
                    link_postulacion, fuente_url,
                    frecuencia ('unica'|'anual'|'recurrente'),
                    verificado_at, estado ('borrador'|'publicada'|'cerrada')

Entrevista          id, codigo (único, E01…), token (aleatorio, un solo uso),
                    token_usado_at, entrevistador, observador, inicio, fin
                    (si tiene fin, la sesión queda invalidada), es_prueba,
                    usa_perfil_respaldo, oportunidad_tarea (reservada para S3),
                    alerta_pendiente, notas

Perfil              id, entrevista (1:1), carrera, ciclo, tipos,
                    intereses (M2M, hasta 3), situacion, canal_preferido,
                    max_semanal, formato_alertas

Interaccion         perfil, oportunidad  (único por par)
                    expuesta_at, voto ('sirve'|'no_sirve'|nulo), motivo,
                    recordatorio_at, postular_click_at

Evento              id, entrevista, oportunidad (nula), nombre, origen
                    ('feed'|'detalle'|'alerta'|'tarea'), fase (paso del
                    guion), variante, creado_at, datos (JSON pequeño)

InscripcionPiloto   id, entrevista, contacto, canal_preferido,
                    canal_operativo ('whatsapp'|'correo'),
                    consentimiento_texto_version, consentimiento_at,
                    baja_at (nula)

Mensaje             id, inscripcion, canal, tipo ('alerta'|'resumen'),
                    programado_para, preparado_at, enviado_at (confirmado),
                    estado ('pendiente'|'preparado'|'por_verificar'|'enviado'|'cancelado'),
                    enviado_por, token (único)

MensajeOportunidad  mensaje, oportunidad, hito   (único: inscripcion +
                    oportunidad + hito, validado al crear)

AccesoMensaje       id, mensaje, accedido_at, user_agent,
                    clasificacion ('humano'|'bot'|'ambiguo')

RespuestaPiloto     id, inscripcion, oportunidad (nula), ya_la_conocia,
                    inicio_postulacion (bool), fecha_inicio, volumen
                    ('bien'|'mucho'|'poco'), respondido_at
```

---

## 7. Contenido: la parte más crítica

La calidad del filtro depende de la calidad de los datos (`§24.12`). Si el feed se ve vacío o irrelevante, S1 fallaría por un problema de contenido, no del concepto.

1. **Reclutar primero, curar después:** desde el día 1 se reclutan los entrevistados con un formulario corto: carrera, ciclo y **tipos de oportunidad que buscan**. La curación apunta a esos perfiles.
2. **Matriz de cobertura antes de entrevistar:** `manage.py cobertura` ejecuta el **matching completo** (`matching.py`) para cada perfil reclutado, más **una tarjeta reservada** para la tarea S3. Como coincidir en tipo ya da 50 puntos (Media), el resultado sin intereses es un mínimo garantizado. **Meta: al menos 6 por perfil (5 para el feed + 1 reservada).** Un perfil que no llega se cubre con más convocatorias reales; si tras la búsqueda sigue sin cobertura, se registra como **perfil no cubierto** (es un hallazgo, no un descarte silencioso) y se entrevista igual para las demás hipótesis, excluyéndolo de S1 y S3.
   - **Esfuerzo de búsqueda fijo:** las fuentes del punto 4, con un máximo de 1 hora por perfil no cubierto. Se registran las fuentes revisadas.
3. **Volumen orientativo:** 40 a 60 convocatorias reales y vigentes, priorizando becas y prácticas (`§19.2`).
4. **Fuentes:** las que citaron los entrevistados: correo institucional, bolsa de trabajo, LinkedIn, Instagram de la universidad, RedAlumni y páginas de becas.
5. **Control de sesgo:** se publican **todas** las convocatorias reales encontradas que cumplen los criterios de calidad, no solo las "buenas" para cada perfil, y el etiquetado se hace con reglas escritas (qué carreras, qué ciclos) revisadas por una segunda persona. Aun así, la curación dirigida selecciona catálogo y muestra: **S1 se reporta como relevancia del servicio curación + filtro**, que es justamente lo que ofrecería un Oppu concierge en sus inicios.
6. **Reverificación:** la noche anterior a cada día de entrevistas se revisan fechas y links.

---

## 8. Métricas e instrumentación

### 8.1. Definiciones

- **Tarjeta expuesta:** al menos el 50 % de la tarjeta visible en pantalla durante **1 segundo continuo**, con la pestaña visible. Se registra una sola vez por par perfil–oportunidad, también tras recargas o cuando HTMX reemplaza partes de la página.
- **Fórmula de S1 por participante:** votos "Me sirve" ÷ tarjetas expuestas **en el feed durante el paso 3** (origen `feed`). No cuentan las exposiciones de la tarjeta reservada (origen `tarea`) ni de la alerta. Las expuestas sin voto quedan en el denominador (cuentan en contra) y además se reporta su número aparte. Un participante con 0 tarjetas expuestas no tiene S1 (se reporta como incidencia).
- **Fases:** cada evento lleva el paso del guion en que ocurrió (lo marca el panel del entrevistador). S2 solo cuenta recordatorios de los pasos 3 y 4.
- **Voto:** cuenta el último. Recargas y dobles clics no crean votos nuevos (`Interaccion` es única por par).
- **Clics de salida:** "Postular" pasa por `/ir/<id>`, que registra el clic en el servidor y luego redirige.

### 8.2. Eventos

| Evento | Qué demuestra (y qué no) | Hipótesis |
|---|---|---|
| `onboarding_completado` (duración) | Fricción del onboarding. | — |
| `tarjeta_expuesta` | El participante tuvo la tarjeta en pantalla. | S1 |
| `voto_registrado` (valor, motivo) | Juicio de relevancia. | S1 |
| `recordatorio_creado` | Usó "Recuérdame". | S2 |
| `ics_descargado`, `gcal_abierto` | Abrió la opción de calendario. **No** confirma que guardó el evento. | S2 |
| `postular_click` (origen) | Hizo clic hacia la postulación. **No** confirma que postuló. | Contexto |
| `alerta_mostrada`, `alerta_abierta` | Reacción a la alerta simulada. | Contexto |
| `piloto_inscrito` (canal preferido y operativo) | Compromiso con consentimiento. | S7 |
| `piloto_rechazo` (motivo, incluido "mi canal no está disponible") | Por qué no se inscribió. | S7 |
| `AccesoMensaje` (fuera de la tabla de eventos) | Acceso al enlace de un mensaje del piloto. **No** confirma lectura. | P1 |

Todos llevan entrevista, oportunidad (si aplica), origen, variante y fecha. El análisis se hace **por participante y en agregado**, en el notebook de `analisis/`, que también genera la **matriz de evidencia por hipótesis** (`§22.1`).

---

## 9. Guion de la Solution Interview

Aplica la retrospectiva: ficha de perfil completa, sin "respuesta esperada", sin preguntas sobre terceros y con un guion corto (`§22`). Roles: un entrevistador y un observador que cronometra y toma notas en la ficha.

1. **Ficha de perfil (2 min):** carrera, ciclo, asociación o comité, si practica o trabaja, si está buscando algo ahora. (Ya se conocen carrera y ciclo por el reclutamiento.)
2. **Recordar el problema (3 min):** "La última vez que te enteraste tarde de algo, ¿qué pasó?" Confirma que es del segmento, sin vender.
3. **Onboarding y feed sin ayuda (4 min):** el estudiante completa el onboarding y recorre el feed. Instrucción única: "Marca las que te sirven y las que no." (S1)
4. **Tarea de decisión (S3, cronometrada):**
   - se usa la **tarjeta reservada** de esa entrevista: una oportunidad que pasa el filtro de su perfil pero **no apareció en el feed** (el sistema la aparta al armar el feed);
   - el entrevistador la envía desde su panel ("Mostrar tarea"); el tiempo empieza **cuando la tarjeta aparece en el celular** (el celular registra `tarea_mostrada` con su hora y el observador arranca el cronómetro al verla), con la frase: "Con lo que ves aquí, ¿postularías a esta? Sí o no, y por qué.";
   - si no hay tarjeta reservada disponible, S3 no se mide para ese participante y se anota como incidencia;
   - termina cuando da una decisión (sí **o** no);
   - luego: "¿Te faltó algún dato para decidir?". El observador anota tiempo, decisión, si salió de la app y qué faltó.
5. **Observar la anticipación (S2):** no se pide usar "Recuérdame". Se observa si lo usa por su cuenta durante los pasos 3 y 4. Al final del paso, se puede preguntar: "Si esta te interesa, ¿cómo harías para no olvidarla?"
6. **Alerta simulada (2 min):** el entrevistador la dispara desde su panel: "¿Qué harías al ver esto?"
7. **Preguntas de seguimiento (5 min):** canal preferido y por qué (incluye "ninguno"), máximo de alertas por semana, formato, compatibilidad ("¿la usarías? ¿confías en ella?"), qué falta, qué sobra y qué haría que la dejes de usar.
8. **Cierre con compromiso (2 min):** "Vamos a hacer un piloto de 2 semanas con alertas reales. ¿Quieres participar?" Si acepta: consentimiento y contacto. (S7)

Duración total: unos 25 minutos, más 10 minutos entre entrevistas para reiniciar y completar notas.

---

## 10. Criterios de aceptación y pruebas

El demo se considera listo para entrevistas cuando pasa todo esto.

**Pruebas automáticas (pytest):**

- filtros: límites de ciclo (`ciclo_min` y `ciclo_max` inclusive), "todas las carreras", estado distinto de publicada, apertura futura, cierre hoy (antes y después de la hora de cierre), cierre ayer, verificación vencida;
- compatibilidad y orden: casos de Alta, Media y excluida; desempates deterministas; máximo 7;
- feed con menos de 5 resultados: mensaje de feed corto, sin relleno;
- `Interaccion` única por par: doble clic y recarga no duplican votos; cambiar el voto conserva el último;
- `/ir/<id>` registra el evento y redirige; con una oportunidad cerrada no redirige a la postulación;
- reiniciar entrevista crea una nueva y conserva intactos los datos anteriores;
- .ics válido (fecha, zona horaria, título, link) y con **alarmas** a 7 días y 1 día antes del instante de cierre, **omitiendo las que ya pasaron**, comparando instantes completos en `America/Lima` (casos: cierre en 3 días → solo la de 1 día; hoy 10:00 y cierre mañana 18:00 → la de 1 día sí se incluye; hoy 20:00 y cierre mañana 18:00 → sin alarmas y aviso en pantalla);
- S1 excluye exposiciones de la tarjeta reservada y de la alerta;
- vinculación: un token solo se puede usar una vez; sin token no se entra; tras "Finalizar" la sesión del participante muestra "Entrevista finalizada"; **dos entrevistas simultáneas** no mezclan perfiles, votos ni alertas;
- la alerta simulada llega solo al participante de esa entrevista;
- el feed nunca incluye la tarjeta reservada para S3;
- exposición: no se registra con menos de 1 s continuo ni con la pestaña oculta; no se duplica tras recarga o reemplazo HTMX (prueba con Playwright);
- fases: un recordatorio creado en el paso 5 no cuenta para S2;
- importación: reimportar el mismo CSV no duplica; filas con errores se reportan por número de fila;
- exportación de eventos: columnas esperadas, excluye `es_prueba`;
- panel del entrevistador y exportaciones inaccesibles sin autenticación.

**Prueba de punta a punta (Playwright):** onboarding → feed → voto → detalle → recordatorio → alerta simulada → inscripción al piloto.

**Prueba manual en el entorno desplegado:** en al menos un Android y un iPhone reales, con datos móviles, incluida una pérdida breve de conexión durante el feed. Importar el .ics en Google Calendar (Android) y Calendario (iOS) y comprobar que la alarma aparece; si un calendario la ignora, la pantalla lo advierte.

**Ensayo:** dos entrevistas completas con personas fuera del equipo, usando el guion y la ficha.

**Hito "Demo aprobado"** (fin del día 6): todo lo anterior en verde. Sin esto no empiezan las entrevistas.

**Hito "Piloto aprobado"** (antes del primer envío del piloto), con pruebas propias:

- `envios_del_dia`: respeta tope en mensajes, prioridad, horario, unicidad por participante + oportunidad + hito, resumen como un solo mensaje, y descarta oportunidades cerradas o que cerrarían antes de las 08:00;
- "Preparar" registra `preparado_at` y **no** cuenta como envío; "Confirmar enviado" registra `enviado_at`; doble clic no duplica; un preparado sin confirmar pasa a "por verificar" (no a pendiente) y solo vuelve a pendiente por acción explícita; confirmar con hora observada funciona; cancelar y reintentar funciona;
- baja: detiene envíos y cancela pendientes de inmediato, también si ocurre entre la encuesta y su recordatorio (no se envía el recordatorio); el borrado elimina el contacto pero conserva los datos anonimizados que usa P3;
- `/a/<token>` y `/p/<token>`: registran el acceso, clasifican humano / bot / ambiguo con un conjunto de datos de prueba conocido, y funcionan **desde un navegador nuevo y desde la sesión de una entrevista ya finalizada**, incluido `/ir/<id>?m=<token>`;
- el cálculo de P2 con ejemplos: postulación iniciada **antes** del primer mensaje sobre esa oportunidad (no cuenta), **después** del cierre de observación (no cuenta) y sin fecha suficiente para ordenarla (se reporta como **indeterminada**);
- el cálculo de P1 (con y sin ambiguos) y de P3 (aceptación / rechazo / desconocido, cobertura mínima, peor caso) con datos de ejemplo;
- un envío real de prueba a WhatsApp y a correo de miembros del equipo.

---

## 11. Datos personales

Conforme a la Ley N.º 29733 de Protección de Datos Personales del Perú:

- en la entrevista no se pide nombre ni contacto; el perfil es anónimo y queda ligado al código de entrevista;
- la inscripción al piloto tiene un **consentimiento específico** (texto versionado) que explica qué mensajes se enviarán, por qué canal, durante cuánto tiempo y cómo salir. Elegir "WhatsApp" en el onboarding **no** autoriza mensajes;
- los contactos solo los ven los miembros del equipo que operan el piloto;
- en el día 21 del piloto a más tardar (después del cierre de observación del día 17) se borran los contactos de la base **y** de cualquier CSV o notebook derivado; el análisis usa solo códigos de entrevista;
- quien pida la baja deja de recibir mensajes de inmediato y su contacto se elimina en un máximo de 48 horas; solo se conservan datos sin contacto para el análisis (§6.4).

---

## 12. Plan de trabajo (sprint de 9 días)

| Día | Desarrollo (2 personas) | Contenido (1 persona) | Entrevistas (1 persona) |
|---|---|---|---|
| 1 | Hipótesis cerradas, bocetos de 5 pantallas, modelo de datos. | Plantilla de carga y reglas de etiquetado. | **Inicio del reclutamiento**, con cuotas por tramo de ciclo. |
| 2 | Proyecto Django, modelos, admin, importación, despliegue vacío. | Curación (primeras 20). | Reclutamiento; ficha de perfil. |
| 3 | Onboarding, `matching.py` con pruebas, **registro de eventos y exportación**. | Curación para los perfiles reclutados. | Guion y ficha del observador. |
| 4 | Feed, tarjeta, detalle, voto, `/ir/<id>`, recordatorio + .ics. | Matriz de cobertura (`manage.py cobertura`). | Agenda de entrevistas cerrada. |
| 5 | Panel del entrevistador, **vinculación por token**, alerta simulada (HTMX), tarjeta reservada, inscripción al piloto, notebook de análisis. | Completar cobertura a ≥ 6 por perfil (5 + reservada). | Texto de consentimiento. |
| 6 | **Solo ensayo y correcciones:** 2 entrevistas de prueba, pruebas en celulares. **Hito "Demo aprobado"; congelar demo y pesos.** | Reverificación. | Ajustes al guion tras el ensayo. |
| 7 | **Un binomio** entrevistador–observador por turno (5–6 entrevistas, unos 35 min cada una con el cambio). Una persona de desarrollo de **guardia técnica**, que entre entrevistas construye las herramientas del piloto (`Mensaje`, `/a/` y `/p/`, `envios_del_dia`). La cuarta persona hace la reverificación y descansa para el turno siguiente. | Reverificación nocturna. | Coordinación de agenda. |
| 8 | Igual que el día 7, rotando roles para que todos entrevisten. | Reverificación nocturna. | Coordinación de agenda. |
| 9 | Análisis con el notebook, Lean Canvas v3, decisión, Sprint Review. Pruebas del **hito "Piloto aprobado"**. | Selección de oportunidades para los inscritos. | |

El mini-piloto empieza el primer día del siguiente sprint, solo si el hito "Piloto aprobado" está en verde. Si no, se retrasa; nunca se envía con herramientas sin probar.

Los Should solo se trabajan si el Must está completo y probado al final del día 5. Si algo del Must se atrasa, lo primero que se recorta es la parte visual, nunca el registro de eventos, la vinculación ni el aislamiento entre entrevistas.

### 12.1. Operación del mini-piloto (2 semanas, durante el siguiente sprint)

| Rol | Responsable | Dedicación estimada |
|---|---|---|
| Curación y reverificación de oportunidades para los inscritos | 1 persona (la de contenido) | ~3 h por semana |
| Envíos diarios con `envios_del_dia` (WhatsApp Business y correo), bajas en ≤ 48 h | 1 persona | ~20 min por día |
| Encuesta final, recordatorio y cierre | 1 persona | ~2 h en total, hasta el cierre de la encuesta |
| Mantenimiento técnico (hosting, `/a/` y `/p/`) | 1 persona de desarrollo | Guardia, ~1 h por semana, hasta el día 21 |
| Eliminación de contactos y verificación | 1 persona + revisión de otra | ~1 h, día 21 a más tardar |

- El hosting sin suspensión y la base de datos se mantienen **hasta el día 21** del piloto (enlaces operativos hasta el cierre de observación y acceso a datos hasta la eliminación de contactos; otros ~5–7 USD).
- El canal operativo (WhatsApp Business de un número del equipo y un correo del proyecto) se configura **antes** del día 7, para no captar inscripciones a un canal que no existe.

---

## 13. Riesgos del demo y mitigación

| Riesgo | Mitigación |
|---|---|
| Datos escasos o desactualizados que invalidan S1 por un problema de contenido. | Reclutar primero, matriz de cobertura, control de sesgo y reverificación nocturna (§7). |
| El demo falla en plena entrevista. | Congelar el día 6, pruebas de §10, guardia técnica y perfil de respaldo que no cuenta para S1. |
| El hosting tarda en despertar. | Plan sin suspensión durante la semana de entrevistas. |
| La entrevista se convierte en *sales pitch*. | Tareas antes que preguntas; el entrevistador no explica funciones. |
| Resultados inflados por la curación a mano. | Publicar todo lo que cumple criterios y etiquetado con reglas revisadas (§7.5). |
| Sesgo de muestra (otra vez ciclos intermedios y avanzados). | Cuotas por tramo de ciclo y al menos 3 personas fuera de comités o asociaciones (`§18.1`). |
| Conclusiones más fuertes que la evidencia. | Resultados exploratorios, reportados por participante; la conducta real se mide en el piloto. |

---

## 14. Cómo se ajusta este plan después de las entrevistas

| Si encontramos… | Entonces… |
|---|---|
| S1 bajo y el motivo dominante es "no es mi ciclo/carrera" | Afinar las reglas de etiquetado y los filtros duros antes de construir más. |
| S1 bajo y el motivo dominante es "no me interesa" | Más intereses específicos en el onboarding o aprender de los 👎. |
| S3 bajo y faltan siempre los mismos datos | Añadir esos campos a la tarjeta o al detalle. |
| Push domina en S4 | Evaluar PWA con Web Push o app nativa para el piloto. |
| WhatsApp domina en S4 | Priorizar la WhatsApp Cloud API; la app queda como detalle y preferencias. |
| Muchos piden "que esté en UP Experience" | Explorar alianza o integración con la universidad (`§20.7`). |
| S7 por debajo del 50 % | No construir más funciones; revisar la propuesta de valor antes del piloto. |
| S6 genera desconfianza | Quitar el indicador y explicar "por qué te lo mostramos". |
| P1–P3 del piloto fallan | Revisar canal, momento y volumen de las alertas antes de automatizar. |

---

## 15. Supuestos de este plan (confirmar con el equipo)

- El piloto es en una sola universidad (el documento sugiere la Universidad del Pacífico, por UP Experience y RedAlumni).
- El sprint dura 9 días, como el anterior; el mini-piloto continúa en el siguiente.
- Al menos 2 integrantes programan en Python; nadie necesita más JavaScript que el archivo de medición de exposición.
- Presupuesto: cero, salvo el hosting sin suspensión durante las entrevistas y el piloto (unos 10–15 USD en total).
- El equipo puede dedicar las horas del mini-piloto (§12.1) durante el siguiente sprint.

# Oppu — Plan del demo para la Solution Interview

> **Estado:** borrador v0.1, para ajustar después de las Solution Interviews.
> **Base:** `Oppu_Problem_Interview_Consolidado.md` (11 Problem Interviews, Lean Canvas v2).
> **Propuesta de valor a probar:** *"Te avisamos a tiempo, y solo de lo que va con tu carrera y ciclo."*

Cada decisión del plan apunta a la evidencia que la justifica (por ejemplo, `§19.6` es la sección 19.6 del documento consolidado). Si una entrevista contradice esa evidencia, la decisión se revisa.

---

## 1. Qué debe lograr el demo

El demo no es el producto final. Es un instrumento para la Solution Interview. Tiene que dejar que un estudiante **viva la experiencia con su propio perfil** y nos dé evidencia sobre:

1. si el filtro por carrera y ciclo produce oportunidades que de verdad le sirven;
2. si la anticipación y los recordatorios cambian su comportamiento;
3. si el formato de cada aviso es suficiente para decidir y postular;
4. por qué canal y con qué frecuencia quiere recibir las alertas.

Por eso el demo tiene que ser **funcional con datos reales**, no solo pantallas estáticas. Un prototipo en Figma no puede personalizar la lista según la carrera y el ciclo de cada entrevistado, y eso es justo lo que queremos validar.

---

## 2. Hipótesis de solución

Mismo formato del sprint anterior: falsables y con criterio de éxito. Meta: 10 entrevistas o más.

| # | Hipótesis | Criterio de éxito | Cómo la mide el demo |
|---|---|---|---|
| **S1 — Relevancia** | Si le mostramos a un estudiante las oportunidades filtradas por carrera, ciclo e intereses, marcará la mayoría como relevantes. | ≥ 70 % de las tarjetas vistas marcadas como "Me sirve" (hoy perciben 10–30 %, `§17`). | Botones 👍/👎 en cada tarjeta, con evento registrado. |
| **S2 — Anticipación** | Si el estudiante ve la fecha de cierre y puede activar un recordatorio, lo hará para las oportunidades que le interesan. | ≥ 6 de 10 activan al menos un recordatorio durante la sesión. | Botón "Recuérdame", con evento registrado. |
| **S3 — Accionabilidad** | Con un resumen de 3 puntos y un link directo, el estudiante puede decidir si postula sin buscar más información. | ≥ 7 de 10 completan la tarea "decide si postularías a X" en menos de 60 s y sin salir de la app. | Tarea cronometrada en la entrevista y evento "Ir a postular". |
| **S4 — Canal** | No hay un canal único. Push, WhatsApp y correo-resumen tienen cada uno su segmento. | Registrar la distribución. Se valida si ningún canal supera el 60 % (`§18.3`). | Selector de canal en el onboarding y preguntas de seguimiento. |
| **S5 — Frecuencia** | Aceptan como máximo unas pocas alertas por semana y prefieren un resumen semanal más alertas urgentes. | ≥ 7 de 10 eligen "resumen + urgentes" o un límite de 3 o menos por semana. | Selector de frecuencia en el onboarding. |
| **S6 — Compatibilidad** | Mostrar un indicador de compatibilidad (Alta/Media) aumenta la confianza en la recomendación (`§19.6`, sugerencia de Joaquin). | ≥ 6 de 10 dicen que lo usarían para priorizar. Se descarta si genera desconfianza. | Pregunta tras ver las tarjetas; variante con y sin indicador. |
| **S7 — Compromiso** | Quien vive el demo quiere seguir usándolo. | ≥ 5 de 10 dejan su correo o WhatsApp para un piloto real. Es el criterio más fuerte: compromiso, no opinión. | Pantalla final "¿Quieres recibir alertas reales?". |

---

## 3. Alcance del demo (MoSCoW)

### Must (sin esto no hay entrevista)

- **Onboarding de menos de 60 s:** carrera, ciclo, tipos de oportunidad, situación (busco prácticas ahora / pronto / no por ahora), canal y frecuencia preferidos.
- **Feed "Para ti"** con **pocas** tarjetas (5 a 7), no un feed infinito (`§18.4`). Ordenadas por urgencia y compatibilidad.
- **Tarjeta de oportunidad:** tipo, organización, **"Cierra en N días"**, resumen de 3 puntos, compatibilidad, botón **"Postular"** con link directo (`§19.6`).
- **Detalle:** requisitos, fechas, fuente oficial, "verificado hace N días" para combatir la información desactualizada (`§19.8`).
- **Recordatorio:** "Recuérdame" con calendario predefinido (ver §6) y opción **"Agregar a Google Calendar / .ics"**.
- **Feedback por tarjeta:** "¿Te sirve?" 👍/👎, con motivo opcional ("no es mi carrera", "no es mi ciclo", "no me interesa", "ya lo sabía").
- **Simulación de alerta:** una notificación que aparece dentro de la app durante la entrevista (ver §5.3), para observar la reacción sin depender del teléfono del entrevistado.
- **Datos reales:** 30 a 50 convocatorias reales y vigentes, de las categorías prioritarias (`§19.2`).
- **Registro de eventos** para medir S1–S3 y S7.

### Should (si hay tiempo dentro del sprint)

- **Compartir por WhatsApp** desde la tarjeta. Ataca el boca a boca poco confiable y la asimetría de acceso (`§19.4`, `§19.5`).
- **Guardadas / Mis postulaciones** con un estado simple: guardada → postulé.
- **Badge "Poco frecuente"** para intercambio y doble grado, cuyo dolor es mayor (`§19.3`).
- **Pantalla de preferencias:** canales, frecuencia, horario silencioso.
- **Panel admin mínimo** para cargar y etiquetar convocatorias sin tocar la base de datos.

### Could (solo si sobra tiempo; no son necesarios para validar)

- Push real (Web Push) para entrevistados que instalen la PWA.
- Resumen semanal por correo.
- Variante A/B de la tarjeta (con y sin compatibilidad) para S6.
- Extracción asistida por IA: pegar el texto de una convocatoria y obtener título, fecha, requisitos y resumen.

### Won't (fuera del demo, a propósito)

- Agregador automático o scraping de fuentes. La curación es manual (concierge): primero validamos que el valor existe y después automatizamos.
- Integración real con UP Experience o con el correo institucional. Se mencionan en la entrevista como pregunta, no se construyen.
- Bot real de WhatsApp (ver §5.3: se simula).
- Monetización, cuentas de empresas, publicación de convocatorias por terceros.
- Feed social, comentarios o anuncios. Los anuncios son una causa explícita de abandono (`§19.8`).

---

## 4. Flujo del demo en la entrevista

```
Inicio ──► Onboarding (carrera, ciclo, intereses, situación, canal, frecuencia)
             │
             ▼
         Feed "Para ti" (5–7 tarjetas) ──► 👍/👎 por tarjeta
             │
             ├──► Detalle ──► Postular (link) / Recuérdame / Calendario / Compartir
             │
             ▼
         Alerta simulada ("Cierra en 2 días: Beca X") ──► abre el detalle
             │
             ▼
         Cierre: "¿Quieres recibir alertas reales?" ──► deja correo/WhatsApp (S7)
```

**Modo entrevista:** una URL con parámetro (`?modo=entrevista`) que:

- reinicia el estado al empezar, para que cada entrevistado parta de cero;
- etiqueta los eventos con un código de entrevista (`E01`, `E02`…) para cruzarlos con las notas;
- tiene un botón oculto para que el entrevistador dispare la alerta simulada en el momento adecuado.

**Contraste "antes / después" (opcional, 1 minuto):** mostrar una captura de una bandeja de correo masivo real anonimizada y luego el feed filtrado. Ayuda a anclar la comparación sin hacer un pitch.

---

## 5. Arquitectura y tecnologías

### 5.1. Decisión principal: PWA (web app móvil) y no app nativa

| Opción | A favor | En contra | Decisión |
|---|---|---|---|
| **PWA (Next.js)** | Se abre con un link en cualquier celular, sin instalar nada. Un solo código para móvil y escritorio. Despliegue en minutos. Gratis. | El push en iOS solo funciona si se agrega a la pantalla de inicio (iOS 16.4 o superior). | **Elegida para el demo.** |
| App nativa (Expo / React Native) | Push nativo confiable y sensación de app real. | Hay que instalarla (Expo Go o TestFlight): fricción en cada entrevista. Más lenta de iterar. | Reconsiderar para el piloto si push gana en S4. |
| Figma clicable | Lo más rápido de hacer. | No personaliza por perfil, así que no puede validar S1. | Útil solo para bocetar antes de programar. |

### 5.2. Stack

| Capa | Tecnología | Por qué |
|---|---|---|
| Frontend | **Next.js** (App Router) + **TypeScript** | Estándar, con mucha documentación. Mismo proyecto para app y admin. |
| UI | **Tailwind CSS** + **shadcn/ui** | Interfaz rápida, visual y limpia, como pidieron (`§20.3`) sin diseñar todo desde cero. |
| PWA | Manifest + service worker (**Serwist**) | Instalable y lista para Web Push. |
| Base de datos y auth | **Supabase** (Postgres, Auth por enlace mágico o código, Row Level Security) | Plan gratuito suficiente. Tablas editables desde su panel, que sirve de admin inicial. |
| Programación de recordatorios | **Supabase Cron** (pg_cron) + Edge Function | Revisa cada hora qué recordatorios vencen y los envía. |
| Push (Could) | **Web Push** con claves VAPID (librería `web-push`) | Sin costo y sin depender de terceros. |
| Correo (Could) | **Resend** | Plan gratuito y API simple para el resumen semanal. |
| WhatsApp | **Mago de Oz** en el demo: mensajes manuales desde WhatsApp Business con plantilla fija. En el piloto: WhatsApp Cloud API (Meta) o Twilio. | La API oficial exige verificar el negocio y aprobar plantillas: semanas de trámite para algo que primero hay que validar. |
| Calendario | Archivo **.ics** generado en el servidor + link a Google Calendar | Barato de hacer y ataca directamente el "me olvidé de la fecha". |
| Analítica | **PostHog** (plan gratuito) | Eventos para S1–S7 y grabación de sesiones para revisar después de cada entrevista. |
| Hosting | **Vercel** | Despliegue automático en cada push a GitHub y URL pública para las entrevistas. |
| Calidad | **Vitest** para la lógica de matching, **Playwright** para el flujo principal | Que el demo no falle en plena entrevista (`§19.8`: "si falla, la dejo"). |

**Costo estimado del demo:** S/ 0, con todo en planes gratuitos. Un dominio propio es opcional.

### 5.3. Alertas durante la entrevista

Depender del celular del entrevistado (permisos, iOS, modo no molestar) es arriesgado. En el demo:

1. **Alerta dentro de la app:** un toast o banner con el formato exacto de la notificación, disparado por el entrevistador. Siempre funciona.
2. **Push real**, solo si el entrevistado ya instaló la PWA y aceptó notificaciones. Es un extra.
3. **WhatsApp:** si el entrevistado elige WhatsApp, el equipo le manda manualmente un mensaje con la plantilla después de la entrevista, y se registra si lo abrió o respondió.

---

## 6. Lógica central

### 6.1. Matching (filtro y compatibilidad)

**Filtros duros** (si no cumple, no se muestra):

- la carrera del estudiante está en `carreras` de la convocatoria, o la convocatoria es "todas las carreras";
- el ciclo está entre `ciclo_min` y `ciclo_max`;
- `fecha_cierre` es posterior a hoy y la convocatoria está verificada.

**Puntaje** entre las que pasan el filtro (pesos iniciales, a ajustar con S1):

| Factor | Peso | Nota |
|---|---|---|
| El tipo coincide con lo que eligió (beca, prácticas…) | 40 | |
| Situación "busco prácticas ahora" y la oportunidad es de prácticas | 20 | La búsqueda depende del momento (`§18.2`). |
| Urgencia: cierra en 14 días o menos | 20 | |
| Poco frecuente: intercambio o doble grado | 10 | `§19.3` |
| Coincide con intereses específicos (consultoría, finanzas…) | 10 | |

- **Compatibilidad mostrada:** Alta (70 o más) / Media (40–69). Por debajo de 40 no se muestra. Se usan etiquetas y no porcentajes para no aparentar una precisión falsa. Validarlo en S6.
- **Feed:** máximo 7 tarjetas, ordenadas por puntaje.
- **Implementación:** una función pura en TypeScript, cubierta con pruebas.

### 6.2. Política de notificaciones (anti-spam)

Responde a los riesgos de retención de `§19.8`:

- **Tope:** como máximo 3 alertas por semana por usuario, además del resumen semanal si lo eligió.
- **Recordatorios automáticos** solo para oportunidades guardadas o de compatibilidad Alta: **7 días y 2 días antes del cierre**.
- **Poco frecuentes** (intercambio, doble grado): aviso al abrir la convocatoria y además 14 días antes.
- **Horario silencioso:** de 22:00 a 08:00.
- Cada alerta lleva un botón para silenciar el tipo o bajar la frecuencia.

### 6.3. Modelo de datos

```
profiles            id, carrera, ciclo, tipos[], intereses[], situacion,
                    canal_preferido, frecuencia, horario_silencio,
                    consentimiento_at, codigo_entrevista

opportunities       id, titulo, organizacion, tipo, carreras[] | 'todas',
                    ciclo_min, ciclo_max, fecha_apertura, fecha_cierre,
                    resumen[3], requisitos, link_postulacion, fuente_url,
                    frecuencia ('unica'|'anual'|'recurrente'),
                    verificado_at, estado ('borrador'|'publicada'|'cerrada')

user_opportunity    user_id, opportunity_id, guardada, recordatorio,
                    estado ('vista'|'guardada'|'postule'),
                    feedback ('sirve'|'no_sirve'), motivo

notifications       id, user_id, opportunity_id, canal, tipo
                    ('nueva'|'recordatorio'|'resumen'), programada_para,
                    enviada_at, abierta_at

waitlist            id, contacto, canal, perfil_resumen, created_at   -- S7
```

---

## 7. Contenido: la parte más crítica

La calidad del filtro depende de la calidad de los datos (`§24.12`). Sin datos buenos, el demo valida el problema equivocado.

- **Volumen:** 30 a 50 convocatorias **reales y vigentes**. Aproximadamente 40 % becas, 35 % prácticas o empleo, 25 % intercambio, doble grado, concursos y talleres (`§19.2`).
- **Fuentes:** las mismas que citaron los entrevistados: correo institucional, bolsa de trabajo, LinkedIn, Instagram de la universidad, RedAlumni y páginas de becas.
- **Variedad de perfiles:** cubrir al menos 5 carreras y 3 tramos de ciclo (1–4, 5–7, 8–10), para que cualquier entrevistado vea un feed creíble.
- **Etiquetado:** cada convocatoria con carreras, rango de ciclos, tipo, fecha de cierre, resumen de 3 puntos y link. Un responsable revisa el etiquetado.
- **Plantilla de carga:** Google Sheet → importación CSV a Supabase, o el panel admin si se llega al Should.

---

## 8. Métricas e instrumentación

| Evento | Para qué |
|---|---|
| `onboarding_completado` (con duración) | Fricción del onboarding (meta: menos de 60 s). |
| `tarjeta_vista`, `feedback_dado` (sirve / no sirve + motivo) | **S1:** % de relevancia. Es la métrica principal del Canvas v2 (`§20.4`). |
| `recordatorio_activado`, `calendario_agregado` | **S2** |
| `detalle_abierto`, `postular_click` (con tiempo desde la vista) | **S3:** "postulaciones iniciadas desde una alerta". |
| `canal_elegido`, `frecuencia_elegida` | **S4, S5** |
| `alerta_mostrada`, `alerta_abierta` | Reacción a la alerta. |
| `waitlist_registro` | **S7** |

Todos los eventos llevan `codigo_entrevista` para armar la **matriz de evidencia por hipótesis** mientras se entrevista, una mejora pedida en la retrospectiva (`§22.1`).

---

## 9. Guion de la Solution Interview (esqueleto)

Aplica la retrospectiva: perfil completo, sin "respuesta esperada", sin preguntas sobre terceros y con un guion más corto (`§22`).

1. **Ficha de perfil (2 min):** carrera, ciclo, asociación o comité, si practica o trabaja, si está buscando algo ahora.
2. **Recordar el problema (3 min):** "La última vez que te enteraste tarde de algo, ¿qué pasó?" Sirve para confirmar que es del segmento, sin vender.
3. **Uso libre del demo (5 min):** onboarding y feed sin ayuda. Observar y no explicar.
4. **Tareas (8 min):**
   - "Marca las que te sirven y las que no." (S1)
   - "Elige una a la que postularías y dime si tienes lo necesario para decidir." (S3, cronometrada)
   - "Si no quieres que se te pase, ¿qué harías?" (S2)
   - El entrevistador dispara la alerta simulada: "¿Qué harías al ver esto?"
5. **Preguntas de seguimiento (5 min):** canal y por qué, cuántas alertas por semana como máximo, compatibilidad (¿confías?, ¿la usarías?), qué falta y qué sobra, y qué haría que la dejes de usar.
6. **Cierre con compromiso (2 min):** "Vamos a hacer un piloto con alertas reales. ¿Te anoto?" (S7)

Duración total: unos 25 minutos.

---

## 10. Plan de trabajo (sprint de 9 días)

| Día | Entregable |
|---|---|
| 1 | Hipótesis S1–S7 cerradas por el equipo, bocetos de las 5 pantallas, plantilla de datos. |
| 2 | Proyecto creado (Next.js + Supabase + Vercel), esquema de base de datos, despliegue vacío. **En paralelo:** inicio de la curación de convocatorias. |
| 3 | Onboarding y perfil. Función de matching con pruebas. |
| 4 | Feed, tarjeta y detalle. Postular, recordatorio y .ics. |
| 5 | Feedback 👍/👎, alerta simulada, modo entrevista, eventos en PostHog. **Datos:** 30 o más convocatorias cargadas. |
| 6 | Should: compartir por WhatsApp, guardadas, preferencias. Prueba piloto interna con 2 personas fuera del equipo. |
| 7 | Correcciones del piloto. **Congelar el demo.** Inicio de entrevistas. |
| 8 | Entrevistas, con la matriz de evidencia llenándose en vivo. |
| 9 | Análisis S1–S7, Lean Canvas v3, decisión y Sprint Review. |

**Reparto sugerido (4 personas):** 2 en desarrollo (frontend y backend/datos), 1 en curación y etiquetado de contenido, 1 en guion, reclutamiento y logística de entrevistas. Desde el día 7, todos entrevistan.

---

## 11. Riesgos del demo y mitigación

| Riesgo | Mitigación |
|---|---|
| Datos escasos o desactualizados: el feed se ve vacío o irrelevante y se invalida S1 por un problema de contenido, no del concepto. | La curación empieza el día 2, cubre varios perfiles y lleva fecha de verificación. Se revisa la noche anterior a cada entrevista. |
| El demo falla en plena entrevista. | Congelarlo el día 7, pruebas del flujo principal y una versión de respaldo con un perfil precargado. |
| La entrevista se convierte en *sales pitch* (impedimento del sprint anterior). | Primero uso libre y tareas, y al final las preguntas. El entrevistador no explica funciones. |
| Problemas con el push en iOS o Android. | Alerta dentro de la app como camino principal (§5.3). |
| Datos personales. | Datos mínimos (sin nombre obligatorio), consentimiento explícito en el onboarding conforme a la Ley N.º 29733 de Protección de Datos Personales del Perú, y borrado tras el análisis si no se sumaron al piloto. |
| Sesgo de muestra: otra vez solo ciclos intermedios o avanzados. | Cuotas de reclutamiento por tramo de ciclo y al menos 3 personas fuera de comités o asociaciones (`§18.1`). |

---

## 12. Cómo se ajusta este plan después de las entrevistas

| Si encontramos… | Entonces… |
|---|---|
| S1 por debajo del 70 % y el motivo dominante es "no es mi ciclo" o "no es mi carrera" | Afinar el etiquetado y los filtros duros antes de construir más. |
| S1 por debajo del 70 % y el motivo dominante es "no me interesa" | Pedir más intereses específicos en el onboarding o aprender de los 👎. |
| Push gana claramente en S4 | Evaluar una app nativa (Expo) para el piloto. |
| WhatsApp gana en S4 | Priorizar la WhatsApp Cloud API y que la app sea solo el lugar de detalle y preferencias. |
| Muchos piden "que esté en UP Experience" | Explorar una alianza o integración con la universidad, la ventaja competitiva hipotética (`§20.7`). |
| S7 por debajo del 50 % | No construir más funciones. Revisar la propuesta de valor antes del piloto. |
| S6 genera desconfianza | Quitar el indicador de compatibilidad y explicar "por qué te lo mostramos". |

---

## 13. Supuestos de este plan (confirmar con el equipo)

- El piloto es en una sola universidad (el documento sugiere la Universidad del Pacífico, por UP Experience y RedAlumni).
- El sprint dura 9 días, como el anterior.
- Al menos 2 integrantes pueden programar en JavaScript o TypeScript. Si no, plan B: Figma clicable y feeds precalculados por perfil, aceptando una validación más débil de S1.
- Presupuesto cero.

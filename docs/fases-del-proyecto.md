# Oppu — Fases del proyecto

> Divide el plan (`plan-demo-solution-interview.md`, v1.0) en fases pequeñas. Cada fase termina en una **puerta de validación**: no se empieza la siguiente hasta que la anterior la pasa.
> Las referencias `§N` apuntan a secciones del plan.

---

## 1. Cómo se trabaja cada fase

Cada fase sigue el mismo ciclo. Los roles están fijos para que no haya dos autores sobre el mismo código.

| Paso | Qué se hace | Quién |
|---|---|---|
| 1. Especificar | Mini-especificación de la fase: qué se construye, qué no, criterios de aceptación y pruebas. Se guarda en `docs/fases/F<N>.md`. | **Claude** |
| 2. Revisar la especificación | Revisión de solo lectura con la skill `codex-review`. **Máximo 2 rondas.** | **Codex** (`gpt-6-astra`) |
| 3. Aprobar la especificación | El equipo lee la especificación revisada y la aprueba o la ajusta. | **Equipo** |
| 4. Implementar | Código y pruebas en la rama de trabajo, con commits pequeños. Lint, formato y pruebas en verde antes de cada push. | **Claude** |
| 5. Revisar el código | `codex review --base <commit de inicio de la fase>`, de solo lectura. Claude verifica cada hallazgo contra el código, corrige lo que es real y explica lo que rechaza. **Máximo 2 rondas.** | **Codex** (`gpt-6.1-sol`) + **Claude** |
| 6. Validar | Puerta de la fase: pruebas automáticas + verificación humana de la tabla de cada fase. | **Equipo** |
| 7. Cerrar | Se registra el resultado en `docs/fases/F<N>.md` (qué pasó, qué se aprendió, qué cambia) y se etiqueta el commit (`fase-N`). | **Claude** |

**Reglas:**

- Una fase por vez. Si la puerta falla, se itera dentro de la misma fase.
- Si una fase revela que el plan está mal, se actualiza el plan antes de seguir.
- Codex nunca escribe en el repositorio. Sus hallazgos son consejos que Claude verifica, no órdenes.
- El login de Codex se pierde al cerrar la sesión: en cada sesión nueva hay que repetir `codex login --device-auth`.

---

## 2. Mapa de fases

```
F0 Fundaciones ─► F1 Catálogo ─► F2 Matching ─► F3 Experiencia ─► F4 Medición ─► F5 Modo entrevista
                                                                                        │
                                                       ◄── puerta "Demo aprobado" ──────┘
                                                                                        ▼
                                                     F6 Solution Interviews (sin código)
                                                                                        │
                                       F7 Herramientas del piloto ◄── decisión ─────────┘
                                                │
                                ◄── puerta "Piloto aprobado"
                                                ▼
                                    F8 Mini-piloto y análisis
```

| Fase | Días del sprint (§12) | Depende de |
|---|---|---|
| F0 Fundaciones | 1–2 | — |
| F1 Catálogo y contenido | 2 | F0 |
| F2 Matching | 3 | F1 |
| F3 Experiencia del estudiante | 3–4 | F2 |
| F4 Medición | 4–5 | F3 |
| F5 Modo entrevista | 5–6 | F4 |
| F6 Solution Interviews | 7–9 | F5 aprobada |
| F7 Herramientas del piloto | 7–9 (guardia) y siguiente sprint | F6 con decisión de seguir |
| F8 Mini-piloto y análisis | Siguiente sprint (~3 semanas) | F7 aprobada |

En paralelo a F0–F5, desde el día 1, el equipo recluta entrevistados y cura convocatorias (§7). Eso no es código, pero F2 y F5 lo necesitan.

---

## 3. Fases

### F0 — Fundaciones

**Objetivo:** un proyecto Django vacío pero real, desplegado y con calidad automática desde el primer día.

**Incluye:**
- proyecto `oppu/` con Django 5.2, `uv` y `uv.lock`, `ruff`, `pytest` + `pytest-django`;
- settings separados (base / producción), variables de entorno, `DEBUG=False` en producción, gunicorn + WhiteNoise (§5.4);
- integración continua en GitHub Actions: lint, formato y pruebas en cada push;
- página de inicio mínima con Tailwind y la estructura de apps vacías (§5.3);
- despliegue en Railway o Render con PostgreSQL;
- `docs/DESARROLLO.md`: cómo levantar el proyecto en local.

**Puerta de validación:**

| Verificación | Cómo |
|---|---|
| CI en verde | GitHub Actions. |
| Un integrante que no lo construyó levanta el proyecto en su máquina siguiendo `DESARROLLO.md` en menos de 15 minutos. | Prueba con una persona del equipo. |
| La URL pública responde con HTTPS y el admin pide login. | Navegador. |
| No hay secretos en el repositorio. | Revisión del diff. |

---

### F1 — Catálogo y contenido

**Objetivo:** el equipo de contenido puede cargar y mantener convocatorias reales sin ayuda técnica.

**Incluye:**
- modelos `Carrera`, `Interes`, `Oportunidad` con relaciones M2M (§6.5);
- admin con filtros por tipo, carrera, estado y fecha de cierre, y acción "marcar como verificada";
- plantilla de Google Sheets y `manage.py importar_convocatorias` (identificador estable, reimportación sin duplicar, errores por fila);
- reglas de etiquetado escritas (§7.5).

**Puerta de validación:**

| Verificación | Cómo |
|---|---|
| Pruebas de importación en verde (§10). | CI. |
| La persona de contenido carga **20 convocatorias reales** con la plantilla y corrige una en el admin, sin ayuda. | Prueba con esa persona. |
| Reimportar el mismo CSV no crea duplicados. | Manual, en el entorno desplegado. |
| Una segunda persona revisa el etiquetado de 5 convocatorias al azar contra las reglas escritas. | Revisión cruzada. |

---

### F2 — Matching

**Objetivo:** dado un perfil, el sistema devuelve las oportunidades correctas y en el orden correcto.

**Incluye:**
- `feed/matching.py`: filtros duros, compatibilidad, orden, máximo 7 y tarjeta reservada (§6.1–6.3);
- `manage.py cobertura` (§7.2) sobre los perfiles reclutados;
- pruebas de todos los casos de filtros, compatibilidad y orden de §10.

**Puerta de validación:**

| Verificación | Cómo |
|---|---|
| Pruebas de matching en verde. | CI. |
| Para 3 perfiles reales del reclutamiento, el equipo revisa el feed generado: ¿alguna oportunidad está claramente fuera de lugar? ¿falta alguna obvia? | Revisión del equipo con la salida del comando. |
| Matriz de cobertura generada; se lista qué perfiles no llegan a 6. | `manage.py cobertura`. |

**Iteración típica:** si el equipo encuentra oportunidades fuera de lugar, se corrige primero el etiquetado (F1) y después los pesos, en ese orden.

---

### F3 — Experiencia del estudiante

**Objetivo:** un estudiante recorre el demo en su celular sin ayuda.

**Incluye:**
- onboarding (§3 Must), feed "Para ti", tarjeta, detalle, oportunidad cerrada;
- voto 👍/👎 con motivo y cambio de voto (HTMX);
- `/ir/<id>`;
- "Recuérdame" con .ics (alarmas correctas, §10) y link de Google Calendar;
- prueba de punta a punta con Playwright.

**Puerta de validación:**

| Verificación | Cómo |
|---|---|
| Pruebas y Playwright en verde. | CI. |
| Funciona en un Android y un iPhone reales con datos móviles. | Prueba manual. |
| **Prueba de pasillo:** 2 personas fuera del equipo completan el onboarding en menos de 60 s y votan sin preguntar nada. | Observación, sin explicar. |
| El .ics importado muestra la alarma en Google Calendar y en Calendario de iOS. | Prueba manual. |

**Iteración típica:** si en la prueba de pasillo alguien se traba, se corrige la pantalla y se repite con otra persona.

---

### F4 — Medición

**Objetivo:** los datos que salen del demo responden S1–S7 sin interpretación manual.

**Incluye:**
- modelo `Evento` e `Interaccion` (§6.5), con fase y origen;
- archivo JavaScript de exposición (§8.1);
- `manage.py exportar_eventos` y notebook `analisis/` que calcula S1–S3 por participante y la matriz de evidencia;
- pruebas de exposición, fases y exportación (§10).

**Puerta de validación:**

| Verificación | Cómo |
|---|---|
| Pruebas en verde, incluidas las de exposición con Playwright. | CI. |
| **Sesión con resultado conocido:** un integrante hace una sesión siguiendo un guion escrito (por ejemplo, "vota 4 sí, 2 no, deja 1 sin votar, crea 1 recordatorio en el paso 5"). El notebook debe dar exactamente los valores esperados. | Comparación de resultados. |

---

### F5 — Modo entrevista

**Objetivo:** el demo está listo para una entrevista real, operado por el equipo.

**Incluye:**
- `Entrevista`, panel del entrevistador con PIN, token con QR de un solo uso, finalizar y reiniciar (§4);
- alerta simulada por HTMX polling y tarjeta reservada para la tarea S3 (`tarea_mostrada`);
- perfil de respaldo;
- inscripción al piloto con consentimiento versionado (§11) y registro de rechazos;
- checklist de despliegue completo (§5.4).

**Puerta de validación = hito "Demo aprobado" (§10):**

| Verificación | Cómo |
|---|---|
| Todas las pruebas de §10 de la parte demo en verde. | CI. |
| Dos entrevistas simultáneas no mezclan datos. | Prueba manual con 4 dispositivos. |
| **Ensayo:** 2 entrevistas completas con personas fuera del equipo, con guion, ficha y observador. | Ensayo. |
| Después del ensayo, el notebook produce la matriz de evidencia de esas 2 entrevistas (marcadas `es_prueba`). | Notebook. |
| Demo y pesos congelados (etiqueta `demo-v1`). | Git. |

---

### F6 — Solution Interviews (sin código)

**Objetivo:** obtener la evidencia.

**Incluye:** 10 o más entrevistas con el guion de §9, reverificación nocturna del contenido y guardia técnica.

**Puerta de validación:**

| Verificación | Cómo |
|---|---|
| ≥ 10 entrevistas válidas (sin perfil de respaldo) y cuotas por tramo de ciclo cumplidas. | Ficha. |
| Matriz de evidencia S1–S7 completa. | Notebook. |
| Decisión del equipo con la tabla de §14: perseverar, ajustar o pivotar. Lean Canvas v3. | Sprint Review. |

**Durante F6 no se cambia el código del demo**, salvo un error que impida la entrevista. Si eso pasa, se anota y las entrevistas previas se comparan con cuidado.

---

### F7 — Herramientas del piloto

**Objetivo:** el equipo puede operar el piloto concierge sin errores de envío ni de privacidad.

**Solo se hace si F6 decide seguir.** Las conclusiones de F6 pueden cambiar esta fase (por ejemplo, si WhatsApp domina en S4).

**Incluye:** `Mensaje`, `MensajeOportunidad`, `AccesoMensaje`, `RespuestaPiloto`; rutas `/a/`, `/p/`, `/ir/?m=`; `envios_del_dia` con Preparar / Confirmar / Por verificar; bajas; cálculos de P1–P3 en el notebook (§2.2, §6.4).

**Puerta de validación = hito "Piloto aprobado" (§10):**

| Verificación | Cómo |
|---|---|
| Pruebas de la parte piloto de §10 en verde. | CI. |
| Envío real de prueba por WhatsApp y correo a miembros del equipo, con acceso, baja y verificación de borrado. | Prueba manual. |
| P1–P3 calculados correctamente sobre datos de ejemplo conocidos. | Notebook. |

---

### F8 — Mini-piloto y análisis

**Objetivo:** medir conducta real (P1–P3).

**Incluye:** operación de 2 semanas según §12.1, encuesta final, análisis y eliminación de contactos.

**Puerta de validación:**

| Verificación | Cómo |
|---|---|
| P1–P3 calculados, con inconclusos reportados como tales. | Notebook. |
| Contactos eliminados de la base y de los archivos derivados antes del día 21. | Verificación por una segunda persona. |
| Decisión sobre el siguiente paso del producto (automatizar, cambiar de canal, pivotar). | Sprint Review. |

---

## 4. Costo y ritmo esperados

- **F0–F5:** unas 6 especificaciones y 6 revisiones de código con Codex; entre 12 y 24 llamadas a Codex en total.
- Las fases F0 y F1 son las más mecánicas: si la revisión de la especificación no encuentra nada importante en la primera ronda, no hace falta una segunda.
- Las fases con más riesgo y donde Codex rinde más son **F2** (lógica del matching), **F4** (medición) y **F7** (envíos y datos personales).

# Reglas de etiquetado de convocatorias

Estas reglas existen para que dos personas etiqueten igual la misma convocatoria. Si una convocatoria no encaja en ninguna regla, anótala y decidan juntos; después se agrega aquí.

## Código

Formato `TIPO-AAAA-NNN`, donde `TIPO` es `BEC`, `PRA`, `INT`, `DOB`, `CON`, `TAL` o `VOL`; `AAAA` el año de cierre y `NNN` un correlativo. Ejemplo: `BEC-2026-014`. **Nunca cambies el código de una convocatoria ya cargada**: es la llave de la sincronización (si lo cambias, se crea otra).

## Tipo

| Tipo | Úsalo cuando… |
|---|---|
| `beca` | La convocatoria da dinero o exoneración para estudiar (pregrado, cursos, posgrado, idiomas). |
| `practicas` | Prácticas pre profesionales, profesionales o empleos (incluye trainee y part-time). |
| `intercambio` | Un ciclo o más en otra universidad, sin título adicional. |
| `doble_grado` | Programa que otorga un segundo título. |
| `concurso` | Retos, case competitions, hackatones, premios. |
| `taller` | Cursos cortos, talleres, charlas formativas, ferias con inscripción. |
| `voluntariado` | Actividades sin pago con fin social. |

Si una convocatoria tiene dos naturalezas (p. ej. un concurso cuyo premio son prácticas), usa la que el estudiante **hace** para postular (concurso).

## Carreras

- Si la convocatoria no restringe carreras, o dice "todas las carreras", escribe `todas`.
- Si menciona carreras, escribe **solo** esas, separadas por `;`, con los nombres exactos del admin (Carreras). Ejemplo: `Economía;Finanzas`.
- "Carreras de negocios" en la UP = `Administración;Contabilidad;Finanzas;Marketing;Negocios Internacionales;Ingeniería Empresarial`. "Carreras afines a X": incluye solo las claramente afines y anótalo para revisarlo.

## Ciclos (1 a 12)

| La convocatoria dice… | `ciclo_min` | `ciclo_max` |
|---|---|---|
| Nada sobre ciclo | 1 | 12 |
| "Desde 5.º ciclo" | 5 | 12 |
| "Hasta 6.º ciclo" | 1 | 6 |
| "Últimos ciclos" / "por egresar" | 8 | 12 |
| "Tercio superior" u otro requisito académico | (no es ciclo) va en `requisitos` | |
| "Egresados" únicamente | No cargarla: el demo es para estudiantes. | |

## Intereses (opcional, hasta 3)

Elige los que un estudiante interesado en ese tema reconocería de inmediato. Si dudas, déjalo vacío: es mejor que un interés incorrecto.

## Resumen: 3 puntos de máximo 120 caracteres

Lo que el estudiante necesita para decidir en segundos si le sirve:
1. **El beneficio** (qué gana): "Cubre el 100 % de la matrícula de un semestre".
2. **El requisito clave** (quién puede): "Desde 5.º ciclo, promedio mínimo de 14".
3. **El esfuerzo o plazo** (qué implica postular): "Ensayo + entrevista; resultados en junio".

Sin adjetivos de marketing ("increíble oportunidad"), sin repetir el título.

## Fechas

- `fecha_cierre`: la última fecha para postular según la **fuente oficial**. Si no hay fecha de cierre, la convocatoria no entra al demo.
- `hora_cierre`: solo si la fuente la indica; si no, déjala vacía (se toma 23:59).
- `frecuencia`: `unica` si es una edición especial, `anual` si se repite cada año, `recurrente` si se abre varias veces al año.

## Fuentes y verificación

- `fuente_url`: la página oficial donde se publica la convocatoria (no una captura ni un post reenviado, salvo que sea la única fuente; en ese caso, anótalo).
- **Verificar** (en el admin, acción "Marcar como verificada ahora") significa: abriste **ambos** links, funcionan, y la fecha de cierre coincide con la fuente oficial. Se repite si pasan más de 7 días.

## Qué no va en la hoja

Datos personales, notas internas o comentarios: la pestaña de convocatorias está **publicada** y cualquiera con el link puede leerla. Usa otra pestaña, no publicada, para notas.

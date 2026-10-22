# Ficha de Sistematización — Espiral 2
## ERP Django · Espiral E2: Modelado de Datos y ORM
## UTEC Celaya · Técnico en Programación (SEP 3061300006-23)

| Campo | Contenido |
|---|---|
| **Número de espiral** | 2 |
| **Nombre del ciclo** | Modelado de Datos y ORM |
| **Semanas** | W04 – W06 |
| **Fecha de inicio** | 13/10/2026 |
| **Fecha de cierre** | 21/10/2026 |
| **Responsable** | Odalis Denisse Mendez Obregon |
| **Asesor** | MC. Román Fernando López González |

---

## 1. Objetivo del ciclo

Diseñar, implementar y validar el esquema de base de datos completo del
ERP en Django, garantizando integridad referencial, normalización 3FN y
cobertura de pruebas ≥ 15 tests de modelo.

---

## 2. Tareas realizadas

| # | Tarea | Estado | Tiempo invertido |
|---|---|---|---|
| 1 | Diseño diagrama ER (8 entidades) | ✅ W04 | 2h |
| 2 | Normalización 3FN y decisiones de diseño | ✅ W04 | 1h |
| 3 | Aprobación del asesor | ✅ W04 | 15m |
| 4 | Implementar models.py × 6 apps | ✅ W05 | 3h |
| 5 | Ejecutar makemigrations + migrate | ✅ W05 | 1h |
| 6 | Registrar en admin.py | ✅ W05 | 1h |
| 7 | Agregar validators y clean() | ✅ W06 | 1h |
| 8 | Suite de tests de modelo (>15) | ✅ W06 | 2h |
| 9 | Instalar django-jazzmin | ✅ W06 | 1h |

---

## 3. Evidencias generadas

- [x] Diagrama ER: `docs/diagramas/diagrama_er.md`
- [x] Decisiones de diseño: `docs/decisiones_diseno.md`
- [x] Tabla de entidades: `docs/entidades_atributos.md`
- [x] Migraciones: `*/migrations/0001_initial.py` × 6 apps
- [x] Migración de validadores: `ventas/migrations/0002_validators_pedido.py`
- [x] Tests: `tests/test_w06_validadores.py` — resultado: 17/17 OK
- [x] Commit de cierre: `Sprint 1 CIERRE [M2]: Jazzmin + clean() + 66 tests OK...`

---

## 4. Criterios de aceptación

| Criterio | Estado | Evidencia |
|---|---|---|
| Diagrama ER aprobado por el asesor | ✅ | Firma en ficha |
| `showmigrations` → `[X] 0001_initial` en 6 apps | ✅ | Terminal |
| `/admin/` muestra las 8 entidades | ✅ | Captura de Jazzmin |
| ≥ 15 tests de modelo PASSED | ✅ | 66 tests acumulados |
| Precio negativo → ValidationError | ✅ | Test específico |
| Correo duplicado → IntegrityError | ✅ | Test específico |

---

## 5. Problemas encontrados y soluciones

| Problema | Causa | Solución aplicada |
|---|---|---|
| Error `NameError: name 'Categoria' is not defined` | La clase Producto estaba antes que Categoria en models.py | Se ordenaron las clases correctamente. |
| Fallo de instalación de Pillow en VS Code | El entorno virtual no registraba el paquete | Se forzó la instalación con `python -m pip install Pillow`. |

---

## 6. Lecciones aprendidas

1. Es vital diseñar el diagrama ER antes de escribir código para evitar errores de llaves foráneas.
2. El método `full_clean()` es indispensable para que se ejecuten los validadores; `save()` directo no los llama.
3. Jazzmin mejora radicalmente la experiencia de usuario del panel de administración con poco esfuerzo.

---

## 7. Tiempo total invertido

| Categoría | Horas |
|---|---|
| Diseño / planeación | 3 |
| Implementación | 6 |
| Pruebas | 3 |
| Documentación | 2 |
| **Total Espiral 2** | **14** |

---

## 8. Aprobación formal del diagrama ER

| Rol | Nombre | Fecha | Observaciones |
|---|---|---|---|
| Desarrollador | Odalis Denisse Mendez Obregon | 21/10/2026 | |
| **Asesor (PO)** | **MC. Román Fernando López González** | 21/10/2026 | Aprobado ✅ |
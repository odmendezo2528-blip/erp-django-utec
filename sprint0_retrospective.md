# Sprint 0 Retrospective — ERP Django
## Semanas W01–W03 · Espiral 1

**Fecha:** 16/10/2026
**Facilitador/Scrum Master:** Odalis Denisse Mendez Obregon

## ¿Qué funcionó bien? (Keep)

1. El entorno portable en USB permitió trabajar sin depender de las PCs del laboratorio.
2. La separación de `settings.py` y `settings_prod.py` facilitó el despliegue sin tocar el desarrollo local.
3. El sistema de templates Fable 5 AzulERP con modo claro/oscuro se ve profesional y funcional.

## ¿Qué mejorar? (Improve)

1. Documentar mejor los comandos de activación del entorno virtual.
2. Verificar el encoding de los archivos generados por PowerShell antes de subirlos al repositorio.

## ¿Qué eliminar? (Drop)

1. Los archivos temporales (logs, requirements_new.txt) que generaron ruido en el repo.

## Acción de mejora (Kaizen) para Sprint 1

> "En el Sprint 1, voy a crear un script `iniciar_sesion.bat` mejorado que restaure el entorno y la configuración de Git automáticamente, para mejorar el arranque de cada sesión de trabajo."

## Velocidad del Sprint 0

| HU | Planificado (pts) | Entregado (pts) |
|---|---|---|
| HU-E1-01 Entorno portable | 3 | 3 |
| HU-E1-02 Scripts sincronización | 2 | 2 |
| HU-E1-03 Repositorio GitHub | 2 | 2 |
| HU-E1-04 Despliegue Render.com | 3 | 3 |
| **Total** | **10** | **10** |

**Velocidad real del equipo:** 10 puntos / sprint

---

## Sprint Goal verificado

> "Al finalizar el Sprint 0, existe un proyecto Django 4.2 desplegado
> en Render.com con URL pública funcional y repositorio en GitHub con
> historial de commits."

**Estado:** ✅ **COMPLETADO**

### Evidencias del Sprint Goal

| Criterio | Estado | Evidencia |
|---|---|---|
| Proyecto Django 4.2 funcional | ✅ | `manage.py check` sin errores |
| URL pública en Render.com | ✅ | https://erp-utec-django-1.onrender.com |
| Repositorio GitHub con ≥ 6 commits | ✅ | 7 commits en rama `main` |
| 35 tests pasando (W01 + W02 + W03) | ✅ | `Ran 35 tests ... OK` |
| `manage.py check` sin errores | ✅ | `System check identified no issues` |
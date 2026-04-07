# Modelo 303 IVA - Automatización serverless para Vercel

Proyecto base real para automatizar la preparación y validación del modelo 303 a partir de:
- un Excel de trabajo procedente de Zifra
- uno o varios PDFs del modelo 303

Incluye:
- arquitectura serverless compatible con Vercel
- endpoints `/api/upload`, `/api/process`, `/api/result`, `/api/download`
- lectura de Excel con trazabilidad hoja/celda
- lectura de PDF del modelo 303 con extracción de metadatos y casillas
- motor de mapeo configurable por JSON/YAML
- comparación Excel vs PDF
- exportación de resultados a JSON y Excel

## Estructura

```text
api/
frontend/
src/
examples/
docs/
```

## Ejecución local

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn api.upload:app --reload --port 8000
```

Para probar el flujo completo localmente se recomienda lanzar con `vercel dev`.

## Flujo recomendado

1. `POST /api/upload` con `excel_file` y `pdf_files`
2. `POST /api/process` con `process_id`
3. `GET /api/result?process_id=...`
4. `GET /api/download?process_id=...&kind=excel`

## Modo serverless

- En producción se recomienda `STORAGE_BACKEND=s3`
- El sistema no depende de estado en memoria entre invocaciones
- Cada endpoint es independiente

## Limitaciones del proyecto base

- Los PDFs escaneados requieren OCR externo si no contienen texto embebido
- El mapeo 303 debe ajustarse a la estructura real del Excel Zifra del cliente
- La lógica de rectificativas está preparada pero puede necesitar reglas específicas de negocio

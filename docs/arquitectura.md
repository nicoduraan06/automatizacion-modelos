# Arquitectura funcional y técnica

## Principios

1. Stateless por diseño.
2. Persistencia fuera de la función serverless.
3. Procesamiento idempotente por `process_id`.
4. Separación clara entre parsers, reglas, servicios y endpoints.
5. Trazabilidad completa desde casilla 303 hasta origen Excel/PDF.

## Componentes

- `api/`: endpoints serverless de Vercel.
- `src/parsers`: lectura de Excel y PDF.
- `src/mappings`: reglas del modelo 303.
- `src/services`: orquestación del proceso.
- `src/storage`: almacenamiento local temporal o S3.
- `src/models`: contratos de datos con Pydantic.
- `src/utils`: helpers comunes.
- `frontend`: formulario HTML y tabla de resultados.

## Estrategia de rendimiento

- Subida y persistencia primero.
- Procesamiento después bajo demanda.
- Exportación separada para no recalcular.
- Posibilidad futura de externalizar el paso pesado a cola.

## Trazabilidad mínima por casilla

Cada casilla calculada devuelve:
- código de casilla
- valor calculado
- valor PDF si existe
- diferencia
- regla aplicada
- evidencias de origen
  - hoja
  - celda
  - valor
  - fórmula si existe

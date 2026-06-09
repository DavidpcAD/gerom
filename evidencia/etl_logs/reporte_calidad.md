# Reporte de calidad de datos (pre-ETL)

Fuente: base operacional `op` de Las Salsas de Lucho.

| Dimensión de calidad | Hallazgo | Registros |
|---|---|---:|
| Completitud | Clientes con fecha_registro nula/vacia | 10 |
| Completitud | Ventas con canal_texto nulo/vacio | 38 |
| Completitud | Lineas con costo_unitario nulo | 319 |
| Validez | Lineas con cantidad <= 0 | 18 |
| Validez | Lineas con cantidad atipica (>500) | 25 |
| Unicidad | Lineas duplicadas exactas (clave natural id_venta+producto+cant) | 37 |
| Integridad | Ventas con id_cliente inexistente (FK rota) | 15 |
| Consistencia | Variantes de texto distintas en provincia (cliente) | 21 |
| Consistencia | Variantes de texto distintas en canal_texto | 19 |

> Estos hallazgos son tratados por las reglas R1–R10 del ETL (ver etl/etl_pipeline.py y la documentación).
# Chat Conversacional + Bigquery + IA

Este proyecto implementa un chat conversacional inteligente que permite realizar análisis de datos de natalidad en Estados Unidos utilizando consultas en lenguaje natural. El sistema combina BigQuery para el acceso a datos, Gemini AI para la generación automática de consultas SQL, y Streamlit para una interfaz interactiva y visualizaciones.

![Dashboard Principal](/docs/Screenshot%202025-06-06%20014200.png)

### Componentes Principales

- **🤖 Motor de IA Conversacional**: Transforma preguntas en lenguaje natural a consultas SQL optimizadas usando Gemini AI
- **📊 Conexión BigQuery**: Acceso directo a la base de datos pública de natalidad de Google Cloud Platform
- **📈 Visualización Automática**: Generación inteligente de gráficos basados en los resultados de las consultas
- **💬 Interfaz Chat**: Sistema de chat intuitivo que mantiene el historial de conversaciones

## 📦 Fuente de Datos

Los datos provienen del dataset público **`bigquery-public-data.samples.natality`** que contiene registros históricos de nacimientos en Estados Unidos desde **1969 hasta 2008**. Esta base de datos incluye información detallada sobre:

| Campo | Descripción |
|-------|-------------|
| year | Año de nacimiento (1969-2008) |
| state | Estado donde ocurrió el nacimiento |
| weight_pounds | Peso del bebé al nacer en libras |
| mother_age | Edad de la madre |
| gestation_weeks | Semanas de gestación |
| plurality | Número de bebés (1=simple, 2=gemelos, etc.) |
| is_male | Género del bebé (booleano) |
| mother_race | Raza de la madre (códigos numéricos) |
| father_age | Edad del padre |
| mother_married | Estado civil de la madre |
| cigarette_use | Uso de cigarrillos durante el embarazo |
| alcohol_use | Consumo de alcohol durante el embarazo |
| apgar_1min / apgar_5min | Puntuaciones Apgar del recién nacido |

**Volumen de datos**: Millones de registros de nacimientos procesados eficientemente a través de BigQuery.

## 🧠 Motor de IA Conversacional

El sistema utiliza **gemini-2.0-flash-thinking-exp-1219** para interpretar preguntas en lenguaje natural y generar consultas SQL precisas. El proceso incluye:

### Procesamiento de Consultas Naturales
- **Análisis contextual** de la pregunta del usuario
- **Mapeo inteligente** de conceptos a campos de la base de datos
- **Validación automática** de rangos temporales (evita consultas fuera del período 1969-2008)
- **Optimización de sintaxis** específica para BigQuery

### Generación SQL Inteligente
```sql
-- Ejemplo de consulta generada automáticamente
SELECT 
  state,
  AVG(weight_pounds) as peso_promedio,
  COUNT(*) as total_nacimientos
FROM `bigquery-public-data.samples.natality`
WHERE year = 2005 AND weight_pounds IS NOT NULL
GROUP BY state
ORDER BY peso_promedio DESC
LIMIT 10
```

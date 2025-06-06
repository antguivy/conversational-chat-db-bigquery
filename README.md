# 👶 Dashboard de Análisis de Natalidad

Este proyecto implementa un chat conversacional inteligente que permite realizar análisis avanzados de datos de natalidad en Estados Unidos utilizando consultas en lenguaje natural. El sistema combina BigQuery para el acceso a datos, Gemini AI para la generación automática de consultas SQL, y Streamlit para una interfaz interactiva y visualizaciones en tiempo real.

![Dashboard Principal](https://via.placeholder.com/800x400/2980b9/ffffff?text=Dashboard+de+Natalidad)

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

El sistema utiliza **Gemini 1.5 Flash** para interpretar preguntas en lenguaje natural y generar consultas SQL precisas. El proceso incluye:

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

### Manejo de Casos Especiales
- **Consultas vacías**: Análisis inteligente del por qué no hay resultados
- **Sugerencias automáticas**: Reformulación de preguntas para obtener mejores resultados
- **Validación temporal**: Alertas cuando se consultan años fuera del rango disponible

## 📊 Sistema de Visualización

### Generación Automática de Gráficos
El sistema analiza automáticamente los resultados y determina el tipo de visualización más apropiado:

- **Gráficos de barras** para comparaciones entre estados o años
- **Detección automática** de variables categóricas vs numéricas
- **Límite inteligente** de 20 elementos para mantener legibilidad
- **Priorización** de campos clave como 'year' y 'state' para ejes X

### Características de Visualización
- **Colores consistentes** con el tema del dashboard
- **Títulos dinámicos** basados en los datos mostrados
- **Fondo transparente** para integración perfecta
- **Responsivo** para diferentes tamaños de pantalla

## 🎯 Motor de Análisis y Explicaciones

### Análisis Adaptativo
El sistema ajusta automáticamente la profundidad del análisis según el tipo de pregunta:

#### Preguntas Directas
- Respuestas **concisas y directas**
- Enfoque en el resultado numérico clave
- Ejemplo: *"El peso promedio al nacer en 2005 fue de 7.3 libras"*

#### Preguntas Analíticas
- **Análisis detallado** con insights
- **Identificación de patrones** y tendencias
- **Conclusiones** basadas en los datos
- Ejemplo: *"Análisis de tendencia muestra aumento gradual en la edad promedio de las madres de 24.1 años en 2000 a 25.8 años en 2008"*

### Manejo Inteligente de Errores
- **Diagnóstico automático** de consultas sin resultados
- **Explicaciones contextuales** del por qué no hay datos
- **Sugerencias de reformulación** para obtener mejores resultados

## 🛠️ Arquitectura Técnica

### Stack Tecnológico
- **[Streamlit](https://streamlit.io/)**: Framework para la interfaz web interactiva
- **[Google BigQuery](https://cloud.google.com/bigquery)**: Base de datos en la nube para consultas SQL a gran escala
- **[Gemini AI](https://ai.google.dev/)**: Modelo de lenguaje para generación de SQL y análisis
- **[Plotly](https://plotly.com/)**: Visualizaciones interactivas y responsivas
- **[Pandas](https://pandas.pydata.org/)**: Manipulación y análisis de datos estructurados

### Optimizaciones de Rendimiento
- **Cache inteligente** (TTL 3600s) para metadatos de tablas
- **Conexión persistente** a BigQuery mediante decoradores
- **Lazy loading** de visualizaciones solo cuando son necesarias
- **Validación previa** de consultas para evitar errores costosos

## 💡 Ejemplos de Uso

### Consultas Básicas
```
"¿Cuál es el peso promedio al nacer en el año 2005?"
"Muestra los 20 pesos más elevados de los recién nacidos en 2005"
```

### Análisis Comparativos
```
"Compara las semanas de gestación promedio para madres menores de 20 años vs. madres mayores de 35 en el año 2005"
"Calcula el peso promedio en libras para los 10 estados con más nacimientos en 2007"
```

### Análisis de Tendencias
```
"Analiza la tendencia de la edad promedio de la madre entre 2000 y 2008"
"Muestra la tendencia del número de nacimientos por año desde 2000 a 2008"
```

### Consultas Específicas
```
"¿Cuál es la cantidad de nacimientos de gemelos (plurality=2) por año desde 1990 hasta 1995?"
```

## 🔍 Características Avanzadas

### Interfaz de Usuario
- **Chat persistente** que mantiene historial de consultas
- **Expansor SQL** para ver las consultas generadas
- **Tablas interactivas** con todos los resultados
- **Sidebar informativo** con estado de conexiones y ejemplos

### Validación de Datos
- **Verificación automática** de rangos temporales válidos
- **Manejo robusto** de valores nulos y datos faltantes
- **Sanitización** de consultas SQL para prevenir inyecciones

### Experiencia de Usuario
- **Mensajes de estado** claros durante el procesamiento
- **Iconos y emojis** para mejorar la legibilidad
- **Diseño responsive** que funciona en móviles y desktop
- **Tooltips informativos** para guiar al usuario

## 🎯 Objetivo del Proyecto

Este dashboard demuestra la **democratización del análisis de datos** mediante interfaces conversacionales. Permite que usuarios sin conocimientos técnicos profundos puedan:

- **Explorar** grandes volúmenes de datos de salud pública
- **Generar insights** mediante preguntas naturales
- **Visualizar tendencias** automáticamente
- **Comprender patrones** en datos de natalidad históricos

## 🚀 Características Destacadas

- **🤖 IA Conversacional**: Transforma lenguaje natural en consultas SQL precisas
- **📊 Visualización Automática**: Gráficos generados inteligentemente según los datos
- **🔍 Análisis Contextual**: Explicaciones adaptadas al tipo de pregunta
- **⚡ Alto Rendimiento**: Optimizado para consultas rápidas en BigQuery
- **🎨 UX Intuitiva**: Interfaz de chat familiar y fácil de usar
- **📈 Insights Automáticos**: Identificación de patrones y tendencias relevantes

---

*Dashboard desarrollado para facilitar el análisis de datos de salud pública mediante inteligencia artificial conversacional*
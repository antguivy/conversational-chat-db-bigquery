"""app Streamlit"""

import json
import os
import streamlit as st
import pandas as pd
from google.cloud import bigquery
from google.oauth2 import service_account
from google.api_core.exceptions import GoogleAPIError
import plotly.express as px
from google import genai
from dotenv import load_dotenv

load_dotenv()
# Configuración de la página
st.set_page_config(
    page_title="Dashboard de Análisis de Natalidad",
    page_icon="👶",
    layout="wide",
)
# CSS personalizado para el diseño moderno (sin cambios)
st.markdown(
    """
<style>
    .main-header {
        background: linear-gradient(135deg, #1f4e79 0%, #2980b9 50%, #3498db 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(31, 78, 121, 0.3);
    }
    
    .main-header h1 {
        color: white;
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
    }
    
    .main-header p {
        color: rgba(255,255,255,0.9);
        font-size: 1.2rem;
        margin: 0.5rem 0 0 0;
    }
    
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        border: 1px solid #f0f0f0;
        margin: 0.5rem 0;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
    }
    
    .info-section {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 4px solid #1f4e79;
        margin: 1rem 0;
    }
    
    .quick-action-btn {
        background: linear-gradient(135deg, #1f4e79 0%, #2980b9 100%);
        color: white;
        border: none;
        padding: 0.75rem 1.5rem;
        border-radius: 8px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(31, 78, 121, 0.3);
        width: 100%;
        margin: 0.25rem 0;
    }
    
    .quick-action-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(31, 78, 121, 0.4);
    }
    
    .api-key-container {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #dee2e6;
    }
    
    .status-indicator {
        display: inline-block;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        margin-right: 8px;
    }
    
    .status-connected {
        background-color: #28a745;
        box-shadow: 0 0 8px rgba(40, 167, 69, 0.4);
    }
    
    .sidebar-section {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    
    .chat-container {
        background: white;
        border-radius: 12px;
        padding: 2rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        margin-top: 1rem;
        min-height: 70vh;
    }

    .stChatInput > div > div > textarea {
        border-radius: 20px;
        border: 2px solid #e0e0e0;
        padding: 15px 20px;
    }

    .stChatInput > div > div > textarea:focus {
        border-color: #1f4e79;
        box-shadow: 0 0 10px rgba(31, 78, 121, 0.2);
    }
</style>
""",
    unsafe_allow_html=True,
)

# --- CONFIGURACIÓN BIGQUERY ---
SERVICE_ACCOUNT_FILE = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
PROJECT_ID = "ai-agent-452404"
DATASET_ID = "bigquery-public-data"
DATASET_NAME = "samples"


# Función actualizada para información de la tabla de natalidad
@st.cache_data(ttl=3600)
def get_natality_table_info():
    """
    Información estructurada de la tabla de natalidad.
    """
    natality_table = {
        "natality": {
            "descripcion": "Contiene datos sobre nacimientos en los Estados Unidos, cubriendo los años 1969 a 2008.",
            "campos": [
                "source_year (INTEGER) - Año de la fuente de datos. Ejemplo: 1975",
                "year (INTEGER) - Año de nacimiento de cuatro dígitos. Ejemplo: 1975",
                "month (INTEGER) - Mes de nacimiento, donde 1 = Enero.",
                "day (INTEGER) - Día del nacimiento, empezando desde 1.",
                "wday (INTEGER) - Día de la semana, donde 1 = Domingo y 7 = Sábado.",
                "state (STRING) - Abreviatura postal del estado. No disponible después de 2004.",
                "is_male (BOOLEAN) - Verdadero si el bebé es varón, falso si es mujer.",
                "child_race (INTEGER) - Raza del bebé (1-Blanco, 2-Negro, 3-Indio Americano, 4-Chino, etc.).",
                "weight_pounds (FLOAT) - Peso del bebé al nacer, en libras.",
                "plurality (INTEGER) - Número de bebés de este embarazo (2=gemelos, 3=trillizos, etc.).",
                "apgar_1min (INTEGER) - Puntaje Apgar a 1 minuto (0-10), años 1978-2002.",
                "apgar_5min (INTEGER) - Puntaje Apgar a 5 minutos (0-10), años 1978-2002.",
                "mother_residence_state (STRING) - Estado de residencia de la madre.",
                "mother_race (INTEGER) - Raza de la madre (mismos códigos que child_race).",
                "mother_age (INTEGER) - Edad de la madre.",
                "gestation_weeks (INTEGER) - Semanas de gestación.",
                "lmp (STRING) - Fecha del último período menstrual (MMDDYYYY). '99' o '9999' indican desconocido.",
                "mother_married (BOOLEAN) - Verdadero si la madre estaba casada.",
                "mother_birth_state (STRING) - Estado de nacimiento de la madre.",
                "cigarette_use (BOOLEAN) - Verdadero si la madre fumó (desde 2003).",
                "cigarettes_per_day (INTEGER) - Número de cigarrillos por día (desde 2003).",
                "alcohol_use (BOOLEAN) - Verdadero si la madre consumió alcohol (desde 1989).",
                "drinks_per_week (INTEGER) - Bebidas alcohólicas por semana (desde 1989).",
                "weight_gain_pounds (INTEGER) - Aumento de peso de la madre en libras.",
                "born_alive_alive (INTEGER) - Hijos previos nacidos vivos que siguen vivos.",
                "born_alive_dead (INTEGER) - Hijos previos nacidos vivos que han fallecido.",
                "born_dead (INTEGER) - Hijos nacidos muertos.",
                "ever_born (INTEGER) - Total de hijos nacidos de la madre.",
                "father_race (INTEGER) - Raza del padre (mismos códigos que child_race).",
                "father_age (INTEGER) - Edad del padre.",
                "record_weight (INTEGER) - Peso del registro para muestreo estadístico.",
            ],
        }
    }
    return natality_table


@st.cache_resource
def initialize_bigquery():
    try:
        credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE
        )
        client = bigquery.Client(credentials=credentials, project=PROJECT_ID)
        dataset_ref = f"{DATASET_ID}.{DATASET_NAME}"
        dataset = client.get_dataset(dataset_ref)
        tables = client.list_tables(dataset)
        tables_info = [
            f"{DATASET_ID}.{DATASET_NAME}.{table.table_id}" for table in tables
        ]
        return client, tables_info
    except GoogleAPIError as e:
        st.error(f"❌ Error de conexión a BigQuery:\n\n{e}")
        return None, []
    except Exception as e:
        st.error(f"❌ Error inesperado:\n\n{e}")
        return None, []


@st.cache_data(ttl=3600)
def build_tables_context(tables_info):
    tables_context = []
    # Renombrado de variable para reflejar el nuevo contexto
    natality_table_info = get_natality_table_info() 

    for table_ref in tables_info:
        table_name = table_ref.split(".")[-1].replace("`", "")

        # Comparación con la nueva variable
        if table_name in natality_table_info:
            table_info = natality_table_info[table_name]

            table_context = f"Tabla: {table_name}\n"
            table_context += f"Descripción: {table_info['descripcion']}\n"
            table_context += "Campos:\n"

            for field in table_info["campos"]:
                table_context += f"  - {field}\n"

            tables_context.append(table_context)

    return tables_context


def initialize_gemini(gemini_api_key):
    if not gemini_api_key:
        st.warning(
            "🔑 Por favor, introduce tu Gemini API key para utilizar el chatbot."
        )
        return None

    try:
        # La inicialización del cliente se mantiene igual, es genérica.
        client = genai.Client(api_key=gemini_api_key)
        generation_config = {
            "temperature": 0,
            "top_p": 0.95,
            "top_k": 64,
            "max_output_tokens": 8192,
        }

        model_config = {
            "model": "gemini-2.0-flash-thinking-exp-1219", # Actualizado a un modelo recomendado
            "generation_config": generation_config,
        }

        return client, model_config
    except Exception as e:
        st.error(f"❌ Error al inicializar Gemini: {e}")
        return None, None


def generate_sql_query(client, model_config, question, tables_info, tables_context):
    # --- PROMPT COMPLETAMENTE REESCRITO PARA NATALIDAD ---
    sql_prompt = f"""
        Eres un experto en análisis de datos de salud pública, especializado en estadísticas de natalidad en EE.UU.
        Tu tarea es convertir preguntas sobre datos de nacimientos en consultas SQL para BigQuery.

        TABLA DISPONIBLE (Base de datos de natalidad):
        {chr(10).join(tables_info)}

        ESTRUCTURA DETALLADA DE LA TABLA:
        {chr(10).join(tables_context)}

        REGLAS IMPORTANTES:
        - ¡AVISO CRÍTICO SOBRE LOS DATOS! La tabla `natality` contiene datos HISTÓRICOS, principalmente del periodo 1969 a 2008.
          Si la pregunta del usuario es sobre un año fuera de este rango (ej. 2020, 2024), la consulta NO devolverá resultados.
          Evita generar filtros para años posteriores a 2008. Si el usuario no especifica un año, asume que está interesado en el rango histórico o en un año representativo como 2005.
        - Usa siempre la sintaxis de BigQuery SQL.
        - Siempre usa backticks (`) alrededor del nombre completo de la tabla, por ejemplo: `bigquery-public-data.samples.natality`.
        - Las columnas clave para análisis son `weight_pounds`, `mother_age`, `gestation_weeks`, `state`, `year`.
        - NUNCA uses la columna `_DATA_DATE` si está presente.

        PREGUNTA DEL USUARIO: {question}

        Responde ÚNICAMENTE con el código SQL, sin explicaciones adicionales.
    """

    try:
        response = client.models.generate_content(
            model=model_config["model"],
            contents=sql_prompt,
            config=model_config["generation_config"],
        )
        sql_query = response.text.strip()

        sql_query = sql_query.strip()
        if sql_query.startswith("```sql"):
            sql_query = sql_query[6:]
        if sql_query.endswith("```"):
            sql_query = sql_query[:-3]
        return sql_query.strip()
    except Exception as e:
        st.error(f"❌ Error al generar la consulta SQL: {e}")
        return None


def execute_sql_query(client, sql_query):
    try:
        query_job = client.query(sql_query)
        df = query_job.to_dataframe()

        is_empty = df is None or df.empty
        return df, False, is_empty  # Return df, error_occurred, is_empty
    except Exception as e:
        st.error(f"❌ Error al ejecutar la consulta SQL: {e}")
        return None, True, False  # Return None, True, False (error occurred, not empty)


def generate_explanation(client, model_config, question, sql_query, df_result):
    """
    Genera una explicación de los resultados, adaptando automáticamente su profundidad
    a la complejidad de la pregunta del usuario.
    """
    try:
        # --- PROMPT PARA RESULTADOS VACÍOS ACTUALIZADO ---
        if df_result is None or df_result.empty:
            explanation_prompt = f"""
            La consulta SQL sobre estadísticas de natalidad se ejecutó correctamente pero no devolvió resultados. 
            Esto es común en este dataset, probablemente por una de estas razones:
            1. La pregunta se refiere a un año reciente (posterior a 2008), y el dataset es histórico.
            2. Los filtros aplicados son demasiado específicos (ej. una combinación de estado, edad y raza muy particular).
            
            Pregunta del usuario: "{question}"
            Consulta SQL ejecutada: 
            ```sql
            {sql_query}
            ```
            
            Tu tarea es explicar amablemente al usuario por qué no se encontraron datos. 
            - Revisa la consulta y la pregunta.
            - Si la consulta filtra por un año > 2008, menciona que esa es la causa más probable debido a que los datos son históricos (1969-2008).
            - Sugiere reformular la pregunta, por ejemplo, probando un rango de años diferente (como 2000-2008) o usando filtros menos restrictivos.
            - Sé conciso y servicial. No digas que la consulta es errónea, porque no lo es.
            """
        else:
            # --- PROMPT PARA ANÁLISIS DE RESULTADOS ACTUALIZADO ---
            df_text = df_result.to_string()
            explanation_prompt = f"""
            Eres un experto en análisis de datos de salud pública y tu objetivo es explicar los resultados de una consulta sobre natalidad de una manera clara y útil para el usuario.

            PREGUNTA ORIGINAL DEL USUARIO:
            "{question}"

            RESULTADOS OBTENIDOS:
            ```
            {df_text}
            ```

            TAREA:
            Analiza los resultados y responde directamente a la pregunta del usuario. Adapta la profundidad de tu respuesta a la naturaleza de la pregunta original:
            - Para preguntas directas y factuales (ej: "¿Cuál fue el peso promedio al nacer?", "¿Cuántos nacimientos hubo?"), da una respuesta concisa y directa, mencionando el resultado clave de los datos.
            - Para preguntas que piden análisis, comparaciones o tendencias (ej: "Compara el peso al nacer en dos estados", "Analiza la tendencia de la edad de la madre"), proporciona un análisis más detallado. Destaca 1 o 2 insights importantes, menciona cualquier patrón o dato interesante y, si es posible, ofrece una breve conclusión.

            Utiliza un lenguaje claro y accesible. Si ayuda a la claridad, usa listas o texto en negrita para resaltar la información clave.
            """

        response = client.models.generate_content(
            model=model_config["model"],
            contents=explanation_prompt,
            config=model_config["generation_config"],
        )
        return response.text
    except Exception as e:
        st.error(f"❌ Error al generar el análisis: {e}")
        return "Error al generar el análisis de los resultados."


def create_visualization(df_result):
    """Crear visualización si es apropiado"""
    fig = None

    if df_result is not None and len(df_result) > 0 and len(df_result.columns) >= 2:
        numeric_cols = df_result.select_dtypes(include=["number"]).columns.tolist()
        categorical_cols = df_result.select_dtypes(exclude=["number"]).columns.tolist()

        if len(numeric_cols) >= 1 and len(df_result) <= 20: # Límite de barras para legibilidad
            if len(categorical_cols) >= 1:
                # Lógica para elegir ejes (prioriza 'year' o 'state' si existen)
                x_axis = categorical_cols[0]
                if 'year' in df_result.columns:
                    x_axis = 'year'
                elif 'state' in df_result.columns:
                    x_axis = 'state'
                
                fig = px.bar(
                    df_result,
                    x=x_axis,
                    y=numeric_cols[0],
                    title=f"📈 {numeric_cols[0].replace('_', ' ').title()} por {x_axis.replace('_', ' ').title()}",
                    color_discrete_sequence=["#2980b9"], # Un color del gradiente
                )
                fig.update_layout(
                    plot_bgcolor="rgba(0,0,0,0)",
                    paper_bgcolor="rgba(0,0,0,0)",
                )

    return fig


def process_query(prompt, gemini_api_key, client, tables_info, tables_context):
    """Función consolidada para procesar consultas y evitar duplicación"""
    if not gemini_api_key:
        error_msg = "🔑 Por favor, proporciona tu API key de Gemini en el sidebar."
        return {
            "role": "assistant", "content": error_msg,
            "data": None, "fig": None, "sql_query": None,
        }

    model_result = initialize_gemini(gemini_api_key)
    if not model_result or not model_result[0]: # Se comprueba que el resultado y el cliente no sean nulos
        error_msg = "❌ Error al inicializar Gemini. Verifica tu API key."
        return {
            "role": "assistant", "content": error_msg,
            "data": None, "fig": None, "sql_query": None,
        }

    client_ai, model_config = model_result
    sql_query = generate_sql_query(
        client_ai, model_config, prompt, tables_info, tables_context
    )

    if not sql_query:
        error_msg = "❌ No se pudo generar la consulta SQL. Por favor, reformula tu pregunta."
        return {
            "role": "assistant", "content": error_msg,
            "data": None, "fig": None, "sql_query": None,
        }

    df_result, error_occurred, is_empty = execute_sql_query(client, sql_query)

    if error_occurred:
        error_msg = "❌ Error en la consulta. Por favor, verifica la sintaxis o reformula tu pregunta."
        return {
            "role": "assistant", "content": error_msg,
            "data": None, "fig": None, "sql_query": sql_query,
        }
    elif is_empty:
        explanation = generate_explanation(
            client_ai, model_config, prompt, sql_query, None,
        )
        empty_msg = f"""
        ### 📊 Consulta Ejecutada Correctamente
        
        La consulta SQL es válida y se ejecutó sin errores, pero **no se encontraron datos** que coincidan con tu pregunta.

        ### 🤔 Análisis del Asistente de IA:
        {explanation}
        """
        return {
            "role": "assistant", "content": empty_msg,
            "data": None, "fig": None, "sql_query": sql_query,
        }
    else:
        fig = create_visualization(df_result)
        explanation = generate_explanation(
            client_ai, model_config, prompt, sql_query, df_result
        )
        full_response = explanation
        return {
            "role": "assistant", "content": full_response,
            "data": df_result, "fig": fig, "sql_query": sql_query,
        }


# Inicializar BigQuery
client, tables_info = initialize_bigquery()

if not client:
    st.stop()

tables_context = build_tables_context(tables_info=tables_info)

# --- SIDEBAR - ACTUALIZADA PARA NATALIDAD ---
with st.sidebar:
    st.markdown(
        """
    <div class="sidebar-section">
        <h2 style="color: #1f4e79; margin-top: 0;">👶 Análisis de Natalidad</h2>
        <p style="color: #666; margin: 0;">Dashboard de análisis de salud pública</p>
    </div>
    """,
        unsafe_allow_html=True,
    )
    st.markdown("### 🔑 Configuración")
    gemini_api_key = st.text_input(
        "Gemini API Key",
        type="password",
        placeholder="Introduce tu API key...",
        help="Necesario para el análisis con IA",
    )
    if gemini_api_key:
        st.success("✅ API Key configurada")
    else:
        st.warning("⚠️ API Key requerida")

    st.markdown("### 📊 Base de Datos")
    st.success("✅ BigQuery Conectado")
    st.info("Datos de natalidad de EE.UU. (1969-2008)")

    st.markdown("### 📋 Fuente de Datos")
    # Expander actualizado para la tabla de natalidad
    with st.expander("Tabla `natality`", expanded=False):
        st.write("Datos de nacimientos en EE.UU.")
        st.write("• Peso, gestación, pluralidad")
        st.write("• Datos demográficos de los padres")
        st.write("• Información por estado y año")

# --- MAIN CONTENT - ACTUALIZADO PARA NATALIDAD ---
st.markdown(
    """
<div class="main-header">
    <h1>👶 Dashboard de Análisis de Natalidad</h1>
    <p>🤖 Analiza estadísticas de nacimientos en EE.UU. con IA • Obtén insights sobre peso, gestación y tendencias demográficas.</p>
</div>
""",
    unsafe_allow_html=True,
)

st.markdown("### 💡 ¿Qué puedes preguntar?")
col1, col2 = st.columns(2)
# Columnas de ejemplos actualizadas
with col1:
    st.markdown(
        """
        **📊 Estadísticas Generales**
        - ¿Cuál es el peso promedio al nacer en el año 2005?
        - Muestra los 20 pesos más elevados de los recien nacidos en el año 2005
        """
    )
with col2:
    st.markdown(
        """
        **🔬 Análisis y Comparaciones**
        - Analiza la tendencia de la edad promedio de la madre entre 2000 y 2008.
        - ¿Cuál es la cantidad de nacimientos de gemelos (plurality=2) por año desde 1990 hasta 1995?
        """
    )

st.markdown("### 🎯 Ejemplos específicos para copiar y pegar:")
# Ejemplos de "copia y pega" actualizados
st.markdown(
    """
- *"Calcula el peso promedio en libras (`weight_pounds`) para los 10 estados con más nacimientos en 2007"*
- *"Muestra la tendencia del número de nacimientos por año desde 2000 a 2008"*
- *"Compara las semanas de gestación promedio para madres menores de 20 años vs. madres mayores de 35 en el año 2005"*
"""
)

st.markdown("---")
# --- CHAT INTERFACE (sin cambios en la lógica) ---
if "messages" not in st.session_state:
    st.session_state.messages = []

message_container = st.container()
with message_container:
    for i, message in enumerate(st.session_state.messages):
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message["role"] == "assistant" and message.get("sql_query"):
                with st.expander("📝 Ver Consulta SQL Generada", expanded=False):
                    st.code(message["sql_query"], language="sql")
            if message.get("data") is not None:
                st.markdown("### 📊 Resultados:")
                st.dataframe(message["data"], use_container_width=True)
            if message.get("fig") is not None:
                st.plotly_chart(message["fig"], use_container_width=True)

# Placeholder del input actualizado
if prompt := st.chat_input(
    "💬 Pregunta sobre peso al nacer, edad de la madre, etc..."
):
    st.session_state.messages.append(
        {
            "role": "user", "content": prompt,
            "data": None, "fig": None, "sql_query": None, "processed": False,
        }
    )
    st.rerun()

if (
    st.session_state.messages
    and st.session_state.messages[-1]["role"] == "user"
    and not st.session_state.messages[-1].get("processed")
):
    last_message = st.session_state.messages[-1]
    prompt = last_message["content"]

    # Spinner actualizado
    with st.spinner("👶 Analizando datos de natalidad..."):
        response_data = process_query(
            prompt, gemini_api_key, client, tables_info, tables_context
        )
    
    last_message["processed"] = True
    st.session_state.messages.append(response_data)
    st.rerun()

# --- Footer actualizado ---
st.markdown("---")
st.markdown(
    """
<div style="text-align: center; padding: 1rem; color: #666;">
    <p>👶 Dashboard de Análisis de Natalidad • Potenciado por BigQuery y Gemini AI</p>
</div>
""",
    unsafe_allow_html=True,
)
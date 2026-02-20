import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from datetime import datetime

# ============================================
# CONFIGURACIÓN DE LA PÁGINA
# ============================================
st.set_page_config(
    page_title="Analizador de Plátano y Camote",
    page_icon="🍌",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.title("🍌 Analizador de Plátano y Camote")
st.markdown("""
Herramienta especializada para productores de **plátano** y **camote** en Costa Rica.
Basada en datos históricos del CENADA y FAOSTAT.
""")

# ============================================
# CARGA DE DATOS (con caché)
# ============================================
@st.cache_data
def cargar_datos():
    """Carga todos los archivos CSV necesarios."""
    archivos = {
        'frutas': 'frutas_estacionales.csv',
        'hortalizas': 'hortalizas_estacionales.csv',
        'precios_mensuales': 'precios_mensuales_producto.csv',
        'camote_precios': 'camote_precios.csv',
        'camote_oferta': 'camote_oferta.csv',
        'faostat': 'FAOSTAT_data_en_2-19-2026.csv',
        'precio_general': 'precio_general_producto.csv' # <- Nuevo archivo útil
    }

    datos = {}
    for key, filename in archivos.items():
        if os.path.exists(filename):
            try:
                # Leer archivos, manejando posibles errores de codificación o formato
                if filename.endswith('.csv'):
                    # Intentar con codificación utf-8, si falla, probar con latin1
                    try:
                        datos[key] = pd.read_csv(filename, encoding='utf-8')
                    except UnicodeDecodeError:
                        datos[key] = pd.read_csv(filename, encoding='latin1')
                else:
                    datos[key] = pd.read_csv(filename)
            except Exception as e:
                st.sidebar.error(f"Error cargando {filename}: {e}")
                datos[key] = None
        else:
            datos[key] = None
            st.sidebar.warning(f"Archivo no encontrado: {filename}")

    return datos

datos = cargar_datos()

# Extraer datos específicos
indices_frutas = datos.get('frutas')
indices_hortalizas = datos.get('hortalizas')
precios_mensuales = datos.get('precios_mensuales')
camote_precios = datos.get('camote_precios')
camote_oferta = datos.get('camote_oferta')
faostat = datos.get('faostat')
precio_general = datos.get('precio_general')

# ============================================
# PROCESAR DATOS DE PLÁTANO
# ============================================
def procesar_platano():
    """Extrae datos de plátano de los índices y precios."""
    platano_data = {}

    # Buscar en índices de frutas (Plátano Maduro y Verde)
    if indices_frutas is not None:
        # Asegurarse de que la columna 'Cultivo' existe
        if 'Cultivo' in indices_frutas.columns:
            maduro = indices_frutas[indices_frutas['Cultivo'] == 'Plátano Maduro']
            verde = indices_frutas[indices_frutas['Cultivo'] == 'Plátano Verde']

            if not maduro.empty:
                platano_data['indice_maduro'] = maduro.iloc[0]
            if not verde.empty:
                platano_data['indice_verde'] = verde.iloc[0]
        else:
            st.sidebar.warning("El archivo 'frutas_estacionales.csv' no tiene la columna 'Cultivo'.")

    # Buscar precios reales en 'precios_mensuales'
    if precios_mensuales is not None:
        if 'producto' in precios_mensuales.columns:
            # Filtrar por productos que contengan 'Plátano' (maduro, verde, primera, segunda)
            precios_platano = precios_mensuales[
                precios_mensuales['producto'].str.contains('Plátano', na=False, case=False)
            ].copy()
            if not precios_platano.empty:
                platano_data['precios'] = precios_platano
        else:
            st.sidebar.warning("El archivo 'precios_mensuales_producto.csv' no tiene la columna 'producto'.")

    # También podrías buscar en 'precio_general' si existe
    if precio_general is not None:
        if 'producto' in precio_general.columns:
            precios_gral_platano = precio_general[
                precio_general['producto'].str.contains('Plátano', na=False, case=False)
            ]
            if not precios_gral_platano.empty:
                platano_data['precio_general'] = precios_gral_platano

    return platano_data

# ============================================
# PROCESAR DATOS DE CAMOTE
# ============================================
def procesar_camote():
    """Extrae todos los datos de camote disponibles."""
    camote_data = {}

    # Índice estacional de hortalizas
    if indices_hortalizas is not None:
        if 'Cultivo' in indices_hortalizas.columns:
            idx = indices_hortalizas[indices_hortalizas['Cultivo'] == 'Camote']
            if not idx.empty:
                camote_data['indice'] = idx.iloc[0]
        else:
            st.sidebar.warning("El archivo 'hortalizas_estacionales.csv' no tiene la columna 'Cultivo'.")

    # Precios mensuales generales
    if precios_mensuales is not None:
        if 'producto' in precios_mensuales.columns:
            precios_camote = precios_mensuales[
                precios_mensuales['producto'].str.contains('Camote', na=False, case=False) &
                ~precios_mensuales['producto'].str.contains('Zanahoria', na=False, case=False) # Excluir Camote Zanahoria si es necesario
            ].copy()
            if not precios_camote.empty:
                camote_data['precios_mensuales'] = precios_camote
        else:
            st.sidebar.warning("El archivo 'precios_mensuales_producto.csv' no tiene la columna 'producto'.")

    # Datos históricos específicos de camote (precios y oferta)
    if camote_precios is not None:
        # Limpiar datos de precios históricos (hay valores 1.0 que son errores y valores atípicos altos como 980.95)
        # También hay valores como 66.67 en el índice. Vamos a filtrar con más cuidado.
        try:
            # Convertir a numérico para asegurar
            camote_precios['Precio_ColonesKg'] = pd.to_numeric(camote_precios['Precio_ColonesKg'], errors='coerce')
            # Filtrar precios que probablemente sean erróneos (menores a 10 o mayores a 2000, por ejemplo)
            camote_precios_clean = camote_precios[
                (camote_precios['Precio_ColonesKg'] > 10) &
                (camote_precios['Precio_ColonesKg'] < 2000)
            ].copy()
            if not camote_precios_clean.empty:
                camote_data['precios_historicos'] = camote_precios_clean
        except Exception as e:
            st.sidebar.error(f"Error limpiando camote_precios: {e}")

    if camote_oferta is not None:
        camote_data['oferta'] = camote_oferta

    # FAOSTAT para precios al productor (Sweet potatoes)
    if faostat is not None:
        if 'Item' in faostat.columns:
            fao_camote = faostat[faostat['Item'].str.contains('Sweet potatoes', na=False, case=False)].copy()
            if not fao_camote.empty:
                camote_data['faostat'] = fao_camote
        else:
            st.sidebar.warning("El archivo 'FAOSTAT...csv' no tiene la columna 'Item'.")

    # Precio general
    if precio_general is not None:
        if 'producto' in precio_general.columns:
            precio_gral_camote = precio_general[
                (precio_general['producto'].str.contains('Camote', na=False, case=False)) &
                (~precio_general['producto'].str.contains('Zanahoria', na=False, case=False))
            ]
            if not precio_gral_camote.empty:
                camote_data['precio_general'] = precio_gral_camote

    return camote_data

platano_data = procesar_platano()
camote_data = procesar_camote()

# ============================================
# MAPA DE MESES
# ============================================
meses_nombre = {
    1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril',
    5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto',
    9: 'Setiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
}
meses_abrev = ['Ene','Feb','Mar','Abr','May','Jun','Jul','Ago','Set','Oct','Nov','Dic']

# ============================================
# INTERFAZ DE USUARIO
# ============================================
st.sidebar.header("⚙️ Configuración")

# Selector principal con énfasis en los dos cultivos
opcion = st.sidebar.radio(
    "Seleccionar análisis:",
    ["🍌 Plátano", "🥔 Camote", "📊 Comparar ambos"]
)

# Parámetros comunes
ciclo_platano = st.sidebar.number_input(
    "Ciclo del plátano (meses)",
    min_value=6, max_value=12, value=12, step=1,
    help="El plátano tarda típicamente 9-12 meses en producir"
)

ciclo_camote = st.sidebar.number_input(
    "Ciclo del camote (meses)",
    min_value=3, max_value=6, value=4, step=1,
    help="El camote tarda típicamente 4-5 meses"
)

# ============================================
# FUNCIÓN PARA CALCULAR ESTACIONALIDAD
# ============================================
def calcular_estacionalidad(serie_indice, titulo):
    """Calcula y devuelve un DataFrame con los índices mensuales."""
    if serie_indice is None:
        st.warning(f"No hay datos de estacionalidad para {titulo}")
        return None

    # Extraer índices mensuales, asumiendo que las columnas son las abreviaturas de los meses
    valores = []
    for mes in meses_abrev:
        if mes in serie_indice.index:
            val = pd.to_numeric(serie_indice[mes], errors='coerce')
            if pd.isna(val):
                val = 1.0  # Asignar 1.0 si el valor no es numérico
        else:
            val = 1.0  # Asignar 1.0 si la columna del mes no existe
        valores.append(val)

    df_indices = pd.DataFrame({
        'mes_num': list(range(1,13)),
        'mes': meses_abrev,
        'indice': valores
    })

    return df_indices

def mostrar_resultados(df_indices, ciclo, titulo):
    """Muestra los resultados para un cultivo."""
    if df_indices is None:
        return None, None, None

    # Calcular para cada mes de siembra
    resultados = []
    for mes_siembra in range(1, 13):
        mes_cosecha = mes_siembra + ciclo
        if mes_cosecha > 12:
            mes_cosecha -= 12
        # Buscar el índice de cosecha
        indice_row = df_indices[df_indices['mes_num'] == mes_cosecha]
        if not indice_row.empty:
            indice_cosecha = indice_row['indice'].values[0]
        else:
            indice_cosecha = 1.0  # Fallback
        beneficio = (indice_cosecha - 1) * 100
        resultados.append({
            'Mes siembra': mes_siembra,
            'Nombre mes': meses_nombre[mes_siembra],
            'Mes cosecha': mes_cosecha,
            'Índice cosecha': indice_cosecha,
            'Beneficio %': beneficio
        })

    df_resultados = pd.DataFrame(resultados)

    # Encontrar la mejor siembra (mayor índice de cosecha)
    mejor_fila = df_resultados.loc[df_resultados['Índice cosecha'].idxmax()]
    mejor_siembra = {
        'mes': mejor_fila['Nombre mes'],
        'cosecha': meses_nombre[mejor_fila['Mes cosecha']],
        'beneficio': mejor_fila['Beneficio %']
    }

    # Encontrar el mejor mes de venta en general
    mejor_venta_fila = df_indices.loc[df_indices['indice'].idxmax()]
    mejor_venta = {
        'mes': mejor_venta_fila['mes'],
        'indice': mejor_venta_fila['indice']
    }

    # Mostrar resultados
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(
            f"🌱 Mejor siembra {titulo}",
            f"{mejor_siembra['mes']}",
            f"Cosecha en {mejor_siembra['cosecha']}"
        )
    with col2:
        st.metric(
            "💰 Mejor venta",
            f"{mejor_venta['mes']}",
            f"Índice {mejor_venta['indice']:.3f}"
        )
    with col3:
        st.metric(
            "📈 Beneficio (teórico)",
            f"{mejor_siembra['beneficio']:.1f}%"
        )

    # Gráfico
    fig, ax = plt.subplots(figsize=(8, 3))
    colores = ['green' if x < 1 else 'orange' if x < 1.1 else 'red' for x in df_indices['indice']]
    bars = ax.bar(df_indices['mes'], df_indices['indice'], color=colores, alpha=0.7)
    ax.axhline(y=1, color='black', linestyle='--', linewidth=0.8)
    ax.set_ylabel('Índice de Estacionalidad')
    ax.set_title(f'Estacionalidad - {titulo}')
    ax.set_ylim(0, max(df_indices['indice']) * 1.1)

    # Resaltar mejor venta
    mejor_idx = df_indices['indice'].idxmax()
    if mejor_idx is not None:
        bars[mejor_idx].set_color('blue')
        bars[mejor_idx].set_alpha(0.9)

    st.pyplot(fig)

    return df_resultados, mejor_siembra, mejor_venta

# ============================================
# SECCIÓN DE PLÁTANO
# ============================================
if opcion == "🍌 Plátano" or opcion == "📊 Comparar ambos":
    st.header("🍌 Análisis de Plátano")

    with st.expander("Ver detalles del plátano", expanded=(opcion=="🍌 Plátano")):
        # Mostrar ambos tipos (maduro y verde)
        col_p1, col_p2 = st.columns(2)

        with col_p1:
            if 'indice_maduro' in platano_data:
                st.subheader("Plátano Maduro")
                df_maduro = calcular_estacionalidad(platano_data['indice_maduro'], "Plátano Maduro")
                if df_maduro is not None:
                    mostrar_resultados(df_maduro, ciclo_platano, "Plátano Maduro")
            else:
                st.info("No hay datos de índice para plátano maduro en 'frutas_estacionales.csv'.")

        with col_p2:
            if 'indice_verde' in platano_data:
                st.subheader("Plátano Verde")
                df_verde = calcular_estacionalidad(platano_data['indice_verde'], "Plátano Verde")
                if df_verde is not None:
                    mostrar_resultados(df_verde, ciclo_platano, "Plátano Verde")
            else:
                st.info("No hay datos de índice para plátano verde en 'frutas_estacionales.csv'.")

        # Precios reales
        if 'precios' in platano_data:
            st.subheader("📊 Precios reales recientes (por calidad/tipo)")
            # Mostrar los últimos precios de cada tipo de plátano
            df_precios = platano_data['precios'].sort_values(['año', 'mes'], ascending=False).head(15)
            df_precios['fecha'] = df_precios['año'].astype(str) + '-' + df_precios['mes'].astype(str).str.zfill(2)
            st.dataframe(df_precios[['fecha', 'producto', 'precio_promedio', 'num_registros']], hide_index=True)
        elif 'precio_general' in platano_data:
            st.subheader("💰 Precio general promedio")
            st.dataframe(platano_data['precio_general'])

# ============================================
# SECCIÓN DE CAMOTE
# ============================================
if opcion == "🥔 Camote" or opcion == "📊 Comparar ambos":
    st.header("🥔 Análisis de Camote")

    with st.expander("Ver detalles del camote", expanded=(opcion=="🥔 Camote")):
        # Estacionalidad principal
        if 'indice' in camote_data:
            st.subheader("Estacionalidad (índice CENADA)")
            df_camote_indice = calcular_estacionalidad(camote_data['indice'], "Camote")
            if df_camote_indice is not None:
                mostrar_resultados(df_camote_indice, ciclo_camote, "Camote")
        else:
            st.warning("No hay índice estacional para camote en 'hortalizas_estacionales.csv'.")

        # Precios mensuales recientes
        if 'precios_mensuales' in camote_data:
            st.subheader("📈 Precios mensuales recientes (CENADA)")
            ultimos = camote_data['precios_mensuales'].sort_values(['año', 'mes'], ascending=False).head(12)
            ultimos['fecha'] = ultimos['año'].astype(str) + '-' + ultimos['mes'].astype(str).str.zfill(2)
            st.dataframe(ultimos[['fecha', 'precio_promedio', 'num_registros', 'producto']], hide_index=True)

            # Estadísticas
            promedio = camote_data['precios_mensuales']['precio_promedio'].mean()
            maximo = camote_data['precios_mensuales']['precio_promedio'].max()
            minimo = camote_data['precios_mensuales']['precio_promedio'].min()

            col_e1, col_e2, col_e3 = st.columns(3)
            col_e1.metric("Precio promedio (general)", f"₡{promedio:.0f}")
            col_e2.metric("Máximo histórico", f"₡{maximo:.0f}")
            col_e3.metric("Mínimo histórico", f"₡{minimo:.0f}")

        # Datos históricos detallados (2017-2024)
        if 'precios_historicos' in camote_data:
            st.subheader("📊 Histórico de precios (2017-2024)")

            # Calcular promedio por mes histórico
            hist_mensual = camote_data['precios_historicos'].groupby('Mes')['Precio_ColonesKg'].mean().reset_index()
            hist_mensual.columns = ['Mes', 'precio_promedio']

            # Gráfico comparativo
            fig_hist, ax_hist = plt.subplots(figsize=(10, 4))
            meses_orden = ['Enero','Febrero','Marzo','Abril','Mayo','Junio',
                          'Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre']
            hist_mensual['mes_num'] = hist_mensual['Mes'].apply(lambda x: meses_orden.index(x) + 1 if x in meses_orden else 0)
            hist_mensual = hist_mensual.sort_values('mes_num')

            ax_hist.plot(hist_mensual['Mes'], hist_mensual['precio_promedio'],
                        marker='o', linewidth=2, color='green')
            ax_hist.set_ylabel('Precio (₡/kg)')
            ax_hist.set_xlabel('Mes')
            ax_hist.set_title('Precio histórico promedio por mes (2017-2024)')
            ax_hist.grid(True, alpha=0.3)
            plt.xticks(rotation=45)
            st.pyplot(fig_hist)

            # Tabla
            st.dataframe(hist_mensual[['Mes', 'precio_promedio']].style.format({
                'precio_promedio': '₡{:.0f}'
            }), hide_index=True)

        # Oferta histórica
        if 'oferta' in camote_data:
            st.subheader("📦 Oferta histórica (toneladas)")
            oferta_mensual = camote_data['oferta'].groupby('Mes')['Oferta_Toneladas'].mean().reset_index()
            oferta_mensual.columns = ['Mes', 'oferta_promedio']

            fig_of, ax_of = plt.subplots(figsize=(10, 3))
            meses_orden = ['Enero','Febrero','Marzo','Abril','Mayo','Junio',
                          'Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre']
            oferta_mensual['mes_num'] = oferta_mensual['Mes'].apply(lambda x: meses_orden.index(x) + 1 if x in meses_orden else 0)
            oferta_mensual = oferta_mensual.sort_values('mes_num')

            ax_of.bar(oferta_mensual['Mes'], oferta_mensual['oferta_promedio'], color='orange', alpha=0.7)
            ax_of.set_ylabel('Toneladas')
            ax_of.set_xlabel('Mes')
            ax_of.set_title('Oferta promedio por mes (2017-2024)')
            plt.xticks(rotation=45)
            st.pyplot(fig_of)

        # FAOSTAT (precios al productor)
        if 'faostat' in camote_data:
            st.subheader("🌎 Precios internacionales (FAOSTAT)")
            fao = camote_data['faostat'].sort_values('Year', ascending=False).head(10)
            # Conversión aproximada USD a CRC (usando un tipo de cambio estimado, podrías hacerlo configurable)
            # Por simplicidad, usaremos un valor fijo o lo dejamos en USD.
            tipo_cambio = st.sidebar.number_input("Tipo de cambio USD a CRC", value=500.0, key="tc_fao")
            fao['Valor_CRC'] = fao['Value'] * tipo_cambio
            st.dataframe(fao[['Year', 'Value', 'Valor_CRC']].rename(columns={
                'Year': 'Año',
                'Value': 'USD/tonelada',
                'Valor_CRC': '₡/kg (aprox)'
            }), hide_index=True)

        # Precio general
        if 'precio_general' in camote_data:
            st.subheader("💰 Precio general promedio")
            st.dataframe(camote_data['precio_general'])

# ============================================
# COMPARACIÓN
# ============================================
if opcion == "📊 Comparar ambos":
    st.header("📊 Comparación Plátano vs Camote")

    col_comp1, col_comp2 = st.columns(2)

    with col_comp1:
        st.subheader("🍌 Plátano")
        if 'indice_maduro' in platano_data:
            df_p = calcular_estacionalidad(platano_data['indice_maduro'], "Plátano Maduro")
            if df_p is not None:
                mejor_p = df_p.loc[df_p['indice'].idxmax()]
                st.metric("Mejor mes venta (maduro)", f"{mejor_p['mes']}", f"Índice {mejor_p['indice']:.3f}")

        if 'precios' in platano_data:
            precio_p = platano_data['precios']['precio_promedio'].mean()
            st.metric("Precio promedio (todos)", f"₡{precio_p:.0f}")

    with col_comp2:
        st.subheader("🥔 Camote")
        if 'indice' in camote_data:
            df_c = calcular_estacionalidad(camote_data['indice'], "Camote")
            if df_c is not None:
                mejor_c = df_c.loc[df_c['indice'].idxmax()]
                st.metric("Mejor mes venta", f"{mejor_c['mes']}", f"Índice {mejor_c['indice']:.3f}")

        if 'precios_mensuales' in camote_data:
            precio_c = camote_data['precios_mensuales']['precio_promedio'].mean()
            st.metric("Precio promedio", f"₡{precio_c:.0f}")

    # Gráfico comparativo
    st.subheader("Comparación de estacionalidad")

    fig_comp, ax_comp = plt.subplots(figsize=(10, 4))

    if 'indice_maduro' in platano_data:
        df_p = calcular_estacionalidad(platano_data['indice_maduro'], "")
        if df_p is not None:
            ax_comp.plot(df_p['mes'], df_p['indice'], marker='o', label='Plátano (Maduro)', linewidth=2)

    if 'indice' in camote_data:
        df_c = calcular_estacionalidad(camote_data['indice'], "")
        if df_c is not None:
            ax_comp.plot(df_c['mes'], df_c['indice'], marker='s', label='Camote', linewidth=2)

    ax_comp.axhline(y=1, color='gray', linestyle='--', alpha=0.5)
    ax_comp.set_ylabel('Índice (1 = promedio)')
    ax_comp.set_xlabel('Mes')
    ax_comp.set_title('Comparación de estacionalidad')
    ax_comp.legend()
    ax_comp.grid(True, alpha=0.3)

    st.pyplot(fig_comp)

# ============================================
# PIE DE PÁGINA
# ============================================
st.markdown("---")
st.markdown(
    f"""
    <div style='text-align: center; color: gray;'>
        <p style='font-family: sans-serif; margin-bottom: 10px;'>
            Última actualización: {datetime.now().strftime("%d/%m/%Y %H:%M")}<br>
            Datos: PIMA/CENADA, FAOSTAT
        </p>
        <div style='font-family: monospace; color: #00ff00; font-size: 10px; line-height: 1.2; text-align: center; white-space: pre; background-color: transparent; margin: 15px 0;'>
██████╗ █████╗ ██████╗ ██████╗  ██████╗ ███╗   ██╗ █████╗ ████████╗ ██████╗ 
██╔════╝██╔══██╗██╔══██╗██╔══██╗██╔═══██╗████╗  ██║██╔══██╗╚══██╔══╝██╔═══██╗
██║     ███████║██████╔╝██████╔╝██║   ██║██╔██╗ ██║███████║   ██║   ██║   ██║
██║     ██╔══██║██╔══██╗██╔══██╗██║   ██║██║╚██╗██║██╔══██║   ██║   ██║   ██║
╚██████╗██║  ██║██║  ██║██████╔╝╚██████╔╝██║ ╚████║██║  ██║   ██║   ╚██████╔╝
 ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝  ╚═════╝ ╚═╝  ╚═══╝╚═╝  ╚═╝   ╚═╝    ╚═════╝ 
        </div>
        <div style='font-family: monospace; margin-top: 10px;'>
            <p style='color: #0ff; margin: 2px;'>> USER: cArbonAto</p>
            <p style='color: #ff0; margin: 2px;'>> MODE: ACTIVIST_HACKER</p>
            <p style='color: #0f0; margin: 2px;'>> STATUS: CONNECTED</p>
            <p style='color: #f0f; margin: 2px;'>> ANONYMOUS</p>
        </div>
        <p style='color: #888; font-size: 10px; margin-top: 15px; font-style: italic;'>
            ⚠️ ESTA NO ES UNA HERRAMIENTA OFICIAL DEL GOBIERNO ⚠️
        </p>
    </div>
    """,
    unsafe_allow_html=True
)
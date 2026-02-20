import pandas as pd
import numpy as np
import os

# ============================================
# CONFIGURACIÓN
# ============================================
# Rutas de archivos (ajusta según tu carpeta)
RUTA_FRUTAS = 'frutas_estacionales.csv'
RUTA_HORTALIZAS = 'hortalizas_estacionales.csv'
RUTA_PRECIOS_MENSUALES = 'precios_mensuales_producto.csv'
RUTA_CAMOTE_PRECIOS = 'camote_precios.csv'
RUTA_FAOSTAT = 'FAOSTAT_data_en_2-19-2026.csv'
RUTA_CICLOS = 'ciclos_cultivo.csv'  # Lo crearemos

# ============================================
# 1. CARGAR ÍNDICES ESTACIONALES
# ============================================
def cargar_indices():
    """Carga los índices estacionales de frutas y hortalizas y los unifica."""
    indices_list = []
    
    # Frutas
    if os.path.exists(RUTA_FRUTAS):
        df_frutas = pd.read_csv(RUTA_FRUTAS)
        df_frutas['tipo'] = 'fruta'
        indices_list.append(df_frutas)
    
    # Hortalizas
    if os.path.exists(RUTA_HORTALIZAS):
        df_hortalizas = pd.read_csv(RUTA_HORTALIZAS)
        df_hortalizas['tipo'] = 'hortaliza'
        indices_list.append(df_hortalizas)
    
    if not indices_list:
        print("No se encontraron archivos de índices estacionales.")
        return pd.DataFrame()
    
    df_indices = pd.concat(indices_list, ignore_index=True)
    
    # Convertir a formato largo (producto, mes, indice)
    meses = ['Ene','Feb','Mar','Abr','May','Jun','Jul','Ago','Set','Oct','Nov','Dic']
    meses_num = {m:i+1 for i,m in enumerate(meses)}
    
    df_largo = pd.melt(df_indices, id_vars=['Cultivo', 'tipo'], value_vars=meses,
                        var_name='mes_str', value_name='indice')
    df_largo['mes'] = df_largo['mes_str'].map(meses_num)
    df_largo.rename(columns={'Cultivo': 'producto'}, inplace=True)
    df_largo = df_largo[['producto', 'mes', 'indice', 'tipo']].dropna()
    
    return df_largo

# ============================================
# 2. CARGAR PRECIOS MENSUALES DEL JSON (CENADA)
# ============================================
def cargar_precios_mensuales():
    """Carga precios mensuales procesados del JSON."""
    if not os.path.exists(RUTA_PRECIOS_MENSUALES):
        print(f"No se encontró {RUTA_PRECIOS_MENSUALES}")
        return pd.DataFrame()
    df = pd.read_csv(RUTA_PRECIOS_MENSUALES)
    # Asegurar tipos
    df['año'] = df['año'].astype(int)
    df['mes'] = df['mes'].astype(int)
    return df

# ============================================
# 3. CARGAR DATOS DE CAMOTE (PDF)
# ============================================
def cargar_camote():
    if not os.path.exists(RUTA_CAMOTE_PRECIOS):
        return pd.DataFrame()
    df = pd.read_csv(RUTA_CAMOTE_PRECIOS)
    # Convertir nombres de mes a número
    meses_map = {'Enero':1,'Febrero':2,'Marzo':3,'Abril':4,'Mayo':5,'Junio':6,
                 'Julio':7,'Agosto':8,'Septiembre':9,'Octubre':10,'Noviembre':11,'Diciembre':12}
    df['mes'] = df['Mes'].map(meses_map)
    df['año'] = df['Año'].astype(int)
    df.rename(columns={'Precio_ColonesKg': 'precio'}, inplace=True)
    return df[['año', 'mes', 'precio']]

# ============================================
# 4. CARGAR CICLOS DE CULTIVO
# ============================================
def cargar_ciclos():
    """Carga ciclos de cultivo desde CSV o usa valores por defecto."""
    if os.path.exists(RUTA_CICLOS):
        df = pd.read_csv(RUTA_CICLOS)
        # Asegurar columnas: producto, ciclo_meses
        if 'producto' in df.columns and 'ciclo_meses' in df.columns:
            return df
    # Si no existe, crear un diccionario por defecto (esto deberías completarlo)
    ciclos_default = {
        'Camote': 5,
        'Apio Verde': 3,
        'Ayote Sazón': 4,
        'Ayote Tierno': 4,
        'Brócoli': 3,
        'Cebolla Seca Amarilla Burra': 4,
        'Cebolla Seca Amarilla Suelta': 4,
        'Cebolla Seca Amarilla Trenza': 4,
        'Cebolla Seca Morada': 4,
        'Cebollino': 3,
        'Chayote Tierno Criollo': 4,
        'Chayote Tierno Quelite': 4,
        'Chile Dulce': 3,
        'Coliflor': 3,
        'Culantro Castilla': 2,
        'Elote': 3,
        'Espinaca': 2,
        'Fresa': 4,
        'Jengibre Sazón': 8,
        'Lechuga Americana': 2,
        'Limón Mandarina': 12,
        'Limón Mesino': 12,
        'Mamón Chino Injertado': 12,
        'Mandarina Primera': 12,
        'Mandarina Segunda': 12,
        'Manga Grande Cavallini': 12,
        'Manga Grande Keitt': 12,
        'Manga Grande Tommy': 12,
        'Maracuyá': 9,
        'Melón Cantaloupe': 3,
        'Mora Congelada': 12,
        'Mora Fresca': 12,
        'Naranja Dulce': 12,
        'Naranjilla': 9,
        'Ñampí': 8,
        'Papa Amarilla': 4,
        'Papa Blanca': 4,
        'Papaya Híbrida': 9,
        'Pejibaye': 36,
        'Pepino': 3,
        'Piña': 18,
        'Pipa Pelada': 12,
        'Plátano Maduro': 12,
        'Plátano Verde': 12,
        'Remolacha': 3,
        'Repollo Morado': 3,
        'Repollo Verde': 3,
        'Sandía Grande de Campo': 3,
        'Sandía Mediana de Campo': 3,
        'Tamarindo': 36,
        'Tiquisque': 8,
        'Tomate': 4,
        'Vainica': 3,
        'Yuca Parafinada': 8,
        'Zanahoria': 3,
        'Zuquini': 3,
        'Aguacate Hass Costa Rica': 12,
    }
    df = pd.DataFrame(list(ciclos_default.items()), columns=['producto', 'ciclo_meses'])
    return df

# ============================================
# 5. INTEGRAR TODO EN UNA BASE DE CONOCIMIENTO
# ============================================
def crear_base_conocimiento():
    """Combina índices, precios y ciclos en una estructura unificada."""
    indices = cargar_indices()
    precios_mensuales = cargar_precios_mensuales()
    camote = cargar_camote()
    ciclos = cargar_ciclos()
    
    # Crear un DataFrame base con todos los productos únicos de índices y precios
    productos_indices = set(indices['producto'].unique()) if not indices.empty else set()
    productos_precios = set(precios_mensuales['producto'].unique()) if not precios_mensuales.empty else set()
    productos_camote = set(['Camote']) if not camote.empty else set()
    todos_productos = productos_indices.union(productos_precios).union(productos_camote)
    
    # Para cada producto, necesitamos:
    # - índice mensual (prioridad: de PDFs, si no, calcular de precios reales)
    # - ciclo (de ciclos, si no, None)
    
    # Construir un DataFrame de índices consolidado
    if not indices.empty:
        indice_df = indices[['producto', 'mes', 'indice']].copy()
    else:
        indice_df = pd.DataFrame(columns=['producto', 'mes', 'indice'])
    
    # Si tenemos precios mensuales, podemos calcular índices reales para productos sin índice PDF
    if not precios_mensuales.empty:
        # Calcular precio promedio anual por producto para 2025 (o todos los años)
        # Usamos solo 2025 para tener un año completo (si hay datos)
        precios_2025 = precios_mensuales[precios_mensuales['año'] == 2025]
        if not precios_2025.empty:
            precio_anual = precios_2025.groupby('producto')['precio_promedio'].mean().reset_index()
            precio_anual.columns = ['producto', 'precio_anual']
            precios_con_anual = pd.merge(precios_2025, precio_anual, on='producto')
            precios_con_anual['indice_real'] = precios_con_anual['precio_promedio'] / precios_con_anual['precio_anual']
            # Unir con índices existentes para priorizar PDF
            # Para productos sin índice PDF, agregamos estos índices reales
            productos_sin_indice = set(precios_con_anual['producto'].unique()) - set(indice_df['producto'].unique())
            if productos_sin_indice:
                indices_reales = precios_con_anual[precios_con_anual['producto'].isin(productos_sin_indice)]
                indices_reales = indices_reales[['producto', 'mes', 'indice_real']].rename(columns={'indice_real':'indice'})
                indice_df = pd.concat([indice_df, indices_reales], ignore_index=True)
    
    # Agregar datos de camote (si ya está en índices, no duplicar)
    if not camote.empty and 'Camote' not in indice_df['producto'].unique():
        # Calcular índice real de camote a partir de sus precios históricos
        camote_anual = camote.groupby('año')['precio'].mean().reset_index()
        camote_anual.columns = ['año', 'precio_anual']
        camote_con_anual = pd.merge(camote, camote_anual, on='año')
        camote_con_anual['indice_real'] = camote_con_anual['precio'] / camote_con_anual['precio_anual']
        # Promediar índices por mes a través de los años
        camote_indice_mensual = camote_con_anual.groupby('mes')['indice_real'].mean().reset_index()
        camote_indice_mensual['producto'] = 'Camote'
        camote_indice_mensual.rename(columns={'indice_real': 'indice'}, inplace=True)
        indice_df = pd.concat([indice_df, camote_indice_mensual[['producto', 'mes', 'indice']]], ignore_index=True)
    
    # Unir con ciclos
    base = pd.merge(indice_df, ciclos, on='producto', how='left')
    
    return base, ciclos

# ============================================
# 6. FUNCIÓN DE RECOMENDACIÓN
# ============================================
def recomendar_para_producto(base, producto, ciclo_usuario=None):
    """
    Para un producto dado, encuentra mejor mes de siembra y venta.
    Retorna un diccionario con resultados.
    """
    # Filtrar datos del producto
    prod_data = base[base['producto'] == producto].copy()
    if prod_data.empty:
        return None
    
    # Obtener ciclo (si el usuario lo especifica, lo usamos)
    if ciclo_usuario is not None:
        ciclo = ciclo_usuario
    else:
        # Tomar el ciclo de la base (si existe)
        ciclo = prod_data['ciclo_meses'].iloc[0] if pd.notna(prod_data['ciclo_meses'].iloc[0]) else None
    
    if ciclo is None:
        return {"error": "No se tiene ciclo para este producto."}
    
    # Asegurar que tenemos datos para todos los meses (puede faltar alguno)
    meses_completos = pd.DataFrame({'mes': range(1,13)})
    prod_data = pd.merge(meses_completos, prod_data, on='mes', how='left')
    # Rellenar índices faltantes con 1 (promedio) o interpolar? Por simplicidad, asumimos 1 si no hay dato.
    prod_data['indice'].fillna(1.0, inplace=True)
    
    # Mejor mes para vender: el de mayor índice
    mejor_venta = prod_data.loc[prod_data['indice'].idxmax()]
    mejor_mes_venta = int(mejor_venta['mes'])
    max_indice = mejor_venta['indice']
    
    # Para siembra: evaluar cada mes de siembra
    resultados_siembra = []
    for mes_siembra in range(1,13):
        mes_cosecha = mes_siembra + ciclo - 1
        if mes_cosecha > 12:
            mes_cosecha -= 12
        # Buscar índice en mes_cosecha
        indice_cosecha = prod_data[prod_data['mes'] == mes_cosecha]['indice'].values
        if len(indice_cosecha) > 0:
            indice = indice_cosecha[0]
        else:
            indice = 1.0
        resultados_siembra.append({
            'mes_siembra': mes_siembra,
            'mes_cosecha': mes_cosecha,
            'indice_cosecha': indice
        })
    
    # Mejor siembra: el que maximiza indice_cosecha
    mejor_siembra = max(resultados_siembra, key=lambda x: x['indice_cosecha'])
    
    # Diferencia porcentual entre mejor mes de venta y el promedio (1.0)
    diff_venta = (max_indice - 1.0) * 100
    
    # Diferencia entre el mejor mes de cosecha (de la mejor siembra) y el promedio
    diff_siembra = (mejor_siembra['indice_cosecha'] - 1.0) * 100
    
    # También podríamos mostrar el peor mes para referencia
    peor_venta = prod_data.loc[prod_data['indice'].idxmin()]
    min_indice = peor_venta['indice']
    diff_venta_peor = (max_indice - min_indice) * 100
    
    return {
        'producto': producto,
        'ciclo_meses': ciclo,
        'mejor_mes_siembra': mejor_siembra['mes_siembra'],
        'mes_cosecha_mejor_siembra': mejor_siembra['mes_cosecha'],
        'indice_cosecha_mejor_siembra': mejor_siembra['indice_cosecha'],
        'beneficio_siembra_%': diff_siembra,
        'mejor_mes_venta': mejor_mes_venta,
        'indice_mejor_venta': max_indice,
        'beneficio_venta_%': diff_venta,
        'peor_mes_venta': peor_venta['mes'],
        'indice_peor_venta': min_indice,
        'rango_venta_%': diff_venta_peor
    }

# ============================================
# 7. INTERFAZ SIMPLE (LÍNEA DE COMANDOS)
# ============================================
def main():
    print("Cargando base de conocimiento...")
    base, ciclos = crear_base_conocimiento()
    if base.empty:
        print("No se pudo crear la base de datos.")
        return
    
    print(f"Base cargada con {base['producto'].nunique()} productos.")
    
    while True:
        print("\n--- RECOMENDADOR DE SIEMBRA Y VENTA ---")
        print("Productos disponibles (primeros 20):")
        productos_lista = sorted(base['producto'].unique())
        for i, p in enumerate(productos_lista[:20]):
            print(f"  {i+1}. {p}")
        if len(productos_lista) > 20:
            print("  ... (hay más)")
        
        prod_input = input("\nIngrese el nombre exacto del producto (o 'salir'): ").strip()
        if prod_input.lower() == 'salir':
            break
        
        if prod_input not in productos_lista:
            print("Producto no encontrado. Intente de nuevo.")
            continue
        
        # Preguntar si desea usar ciclo por defecto o ingresar uno
        ciclo_op = input("¿Usar ciclo por defecto? (s/n): ").strip().lower()
        if ciclo_op == 'n':
            try:
                ciclo_user = int(input("Ingrese ciclo en meses: "))
            except:
                print("Ciclo inválido, usando por defecto.")
                ciclo_user = None
        else:
            ciclo_user = None
        
        resultado = recomendar_para_producto(base, prod_input, ciclo_user)
        if resultado is None:
            print("No hay suficientes datos para este producto.")
            continue
        
        print("\n" + "="*50)
        print(f"RESULTADOS PARA: {resultado['producto']}")
        print(f"Ciclo de cultivo: {resultado['ciclo_meses']} meses")
        print("-" * 30)
        print(f"🌱 MEJOR MES PARA SEMBRAR: {resultado['mejor_mes_siembra']} (cosecha en mes {resultado['mes_cosecha_mejor_siembra']})")
        print(f"   Índice de precio esperado en cosecha: {resultado['indice_cosecha_mejor_siembra']:.3f}")
        print(f"   Beneficio vs promedio: {resultado['beneficio_siembra_%']:+.1f}%")
        print("-" * 30)
        print(f"💰 MEJOR MES PARA VENDER: {resultado['mejor_mes_venta']}")
        print(f"   Índice máximo: {resultado['indice_mejor_venta']:.3f}")
        print(f"   Beneficio vs promedio: {resultado['beneficio_venta_%']:+.1f}%")
        print(f"   Rango entre mejor y peor mes: {resultado['rango_venta_%']:.1f}%")
        print("="*50)

if __name__ == "__main__":
    main()
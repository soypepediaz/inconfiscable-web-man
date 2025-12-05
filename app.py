import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import yfinance as yf
from typing import Tuple, List
import math

# Configuración de la página
st.set_page_config(
    page_title="Inconfiscable - El Camino Hacia La Libertad Financiera",
    page_icon="🔒",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS personalizado para ocultar la barra lateral
hide_sidebar = """
    <style>
        [data-testid="collapsedControl"] {
            display: none
        }
        [data-testid="stSidebarNav"] {
            display: none
        }
    </style>
"""
st.markdown(hide_sidebar, unsafe_allow_html=True)

# Estilos personalizados
st.markdown("""
    <style>
        :root {
            --color-trap: #E63946;
            --color-illusion: #F77F00;
            --color-break: #06A77D;
            --color-unconfiscable: #2D6A4F;
            --color-dark: #0B0E11;
            --color-text: #FFFFFF;
        }
        
        body {
            background-color: var(--color-dark);
            color: var(--color-text);
        }
        
        .hero-section {
            background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
            padding: 60px 20px;
            text-align: center;
            border-bottom: 3px solid #E63946;
        }
        
        .hero-title {
            font-size: 3em;
            font-weight: bold;
            margin-bottom: 20px;
            background: linear-gradient(90deg, #E63946, #F77F00, #06A77D, #2D6A4F);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .pillar-section {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 40px 0;
        }
        
        .pillar-card {
            padding: 30px;
            border-radius: 10px;
            border-left: 5px solid;
            color: white;
        }
        
        .pillar-trap {
            background-color: rgba(230, 57, 70, 0.1);
            border-left-color: #E63946;
        }
        
        .pillar-illusion {
            background-color: rgba(247, 127, 0, 0.1);
            border-left-color: #F77F00;
        }
        
        .pillar-break {
            background-color: rgba(6, 168, 125, 0.1);
            border-left-color: #06A77D;
        }
        
        .pillar-unconfiscable {
            background-color: rgba(45, 106, 79, 0.1);
            border-left-color: #2D6A4F;
        }
        
        .calculator-section {
            background-color: rgba(30, 30, 30, 0.8);
            padding: 40px;
            border-radius: 10px;
            margin: 40px 0;
            border: 2px solid #06A77D;
        }
        
        .results-section {
            margin: 40px 0;
        }
        
        .scenario-card {
            padding: 30px;
            border-radius: 10px;
            margin: 20px 0;
        }
        
        .scenario-a {
            background-color: rgba(230, 57, 70, 0.15);
            border: 2px solid #E63946;
        }
        
        .scenario-b {
            background-color: rgba(45, 106, 79, 0.15);
            border: 2px solid #2D6A4F;
        }
        
        .metric {
            display: flex;
            justify-content: space-between;
            padding: 10px 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .metric-label {
            font-weight: bold;
        }
        
        .metric-value {
            color: #06A77D;
            font-weight: bold;
        }
        
        .cta-button {
            background-color: #2D6A4F;
            color: white;
            padding: 15px 30px;
            border: none;
            border-radius: 5px;
            font-size: 16px;
            cursor: pointer;
            margin: 20px 0;
            width: 100%;
        }
        
        .cta-button:hover {
            background-color: #06A77D;
        }
        
        .footer {
            text-align: center;
            padding: 40px 20px;
            border-top: 1px solid rgba(255, 255, 255, 0.1);
            margin-top: 60px;
            color: rgba(255, 255, 255, 0.7);
        }
    </style>
""", unsafe_allow_html=True)

# Funciones de utilidad
@st.cache_data
def get_bitcoin_prices(start_date: datetime, end_date: datetime) -> dict:
    """
    Obtiene histórico de precios de Bitcoin usando yfinance.
    Maneja automáticamente diferentes formatos de datos que yfinance puede devolver.
    """
    try:
        # Descargar datos de Bitcoin usando yfinance
        btc_data = yf.download('BTC-USD', start=start_date, end=end_date, progress=False)
        
        if btc_data.empty:
            st.error("❌ No se encontraron datos de Bitcoin para el período seleccionado. Intenta con un período más reciente.")
            return {}
        
        # Convertir a diccionario {fecha: precio_cierre}
        prices = {}
        
        try:
            # Método 1: Acceso directo a columna 'Close' (formato simple)
            if 'Close' in btc_data.columns:
                for index, row in btc_data.iterrows():
                    try:
                        date = index.date()
                        close_price = float(row['Close'])
                        # Validar que el precio es válido
                        if close_price > 0:
                            prices[date] = close_price
                    except (ValueError, TypeError):
                        continue
            else:
                # Método 2: MultiIndex (formato reciente de yfinance)
                for index in btc_data.index:
                    try:
                        date = index.date()
                        close_value = None
                        
                        # Busca la columna Close en MultiIndex
                        if isinstance(btc_data.columns, pd.MultiIndex):
                            # Busca cualquier columna que contenga 'Close'
                            for col in btc_data.columns:
                                if isinstance(col, tuple) and 'Close' in col:
                                    try:
                                        val = btc_data.loc[index, col]
                                        if pd.notna(val):
                                            close_value = float(val)
                                            break
                                    except:
                                        continue
                        
                        # Si no encontró, busca en columnas simples
                        if close_value is None:
                            for col in btc_data.columns:
                                if 'Close' in str(col):
                                    try:
                                        val = btc_data.loc[index, col]
                                        if pd.notna(val):
                                            close_value = float(val)
                                            break
                                    except:
                                        continue
                        
                        # Guardar si es válido
                        if close_value is not None and close_value > 0:
                            prices[date] = close_value
                    except Exception:
                        continue
        
        except Exception as e:
            st.error(f"❌ Error al procesar datos de Bitcoin: {str(e)}")
            return {}
        
        if not prices:
            st.error("❌ No se pudieron extraer precios válidos de los datos descargados.")
            return {}
        
        return prices
        
    except Exception as e:
        st.error(f"❌ Error al obtener precios de Bitcoin: {str(e)}")
        return {}

def get_purchase_dates(start_date: datetime, end_date: datetime, frequency: str, 
                       day_of_week: int = None, day_of_month: int = None) -> List[datetime]:
    """Genera lista de fechas de compra según la frecuencia especificada"""
    dates = []
    current_date = start_date
    
    if frequency == "Diaria":
        while current_date <= end_date:
            dates.append(current_date)
            current_date += timedelta(days=1)
    
    elif frequency == "Semanal":
        while current_date <= end_date:
            if current_date.weekday() == day_of_week:
                dates.append(current_date)
            current_date += timedelta(days=1)
    
    elif frequency == "Mensual":
        month_date = current_date
        while month_date <= end_date:
            # Manejo de meses con menos días
            if day_of_month == 31:
                # Último día del mes
                next_month = (month_date.replace(day=1) + timedelta(days=32)).replace(day=1)
                last_day = (next_month - timedelta(days=1)).day
                target_day = min(day_of_month, last_day)
            else:
                target_day = day_of_month
            
            try:
                purchase_date = month_date.replace(day=target_day)
                if current_date <= purchase_date <= end_date:
                    dates.append(purchase_date)
                # Avanzar al siguiente mes
                if month_date.month == 12:
                    month_date = month_date.replace(year=month_date.year + 1, month=1)
                else:
                    month_date = month_date.replace(month=month_date.month + 1)
            except ValueError:
                # Día inválido para este mes, avanzar
                if month_date.month == 12:
                    month_date = month_date.replace(year=month_date.year + 1, month=1)
                else:
                    month_date = month_date.replace(month=month_date.month + 1)
    
    return sorted(list(set(dates)))

def calculate_dca(start_date: datetime, end_date: datetime, amount_usd: float, 
                  frequency: str, day_of_week: int = None, day_of_month: int = None,
                  bitcoin_prices: dict = None) -> Tuple[float, float, list]:
    """Calcula DCA y retorna (BTC acumulado, inversión total, lista de compras)"""
    
    if not bitcoin_prices:
        return 0, 0, []
    
    purchase_dates = get_purchase_dates(start_date, end_date, frequency, day_of_week, day_of_month)
    
    if not purchase_dates:
        return 0, 0, []
    
    total_btc = 0
    total_invested = 0
    purchases = []
    
    # Obtener fechas disponibles en orden
    bitcoin_dates = sorted(bitcoin_prices.keys())
    
    for target_date in purchase_dates:
        # Buscar precio en la fecha exacta o más cercana anterior
        price = None
        
        if target_date in bitcoin_prices:
            price = bitcoin_prices[target_date]
        else:
            # Buscar el precio más cercano anterior
            for btc_date in reversed(bitcoin_dates):
                if btc_date <= target_date:
                    price = bitcoin_prices[btc_date]
                    break
        
        # Si no hay precio anterior, usar el primero disponible
        if price is None and bitcoin_dates:
            price = bitcoin_prices[bitcoin_dates[0]]
        
        # Si encontramos un precio, registrar la compra
        if price is not None and price > 0:
            btc_bought = amount_usd / price
            total_btc += btc_bought
            total_invested += amount_usd
            purchases.append({
                'date': target_date,
                'price': price,
                'amount_usd': amount_usd,
                'btc_bought': btc_bought
            })
    
    return total_btc, total_invested, purchases

def calculate_cagr(initial_value: float, final_value: float, years: float) -> float:
    """Calcula CAGR (Compound Annual Growth Rate)"""
    if initial_value <= 0 or years <= 0:
        return 0
    return (pow(final_value / initial_value, 1 / years) - 1) * 100

# ============ INTERFAZ PRINCIPAL ============

# Hero Section
st.markdown("""
    <div class="hero-section">
        <h1 class="hero-title">El Camino Hacia Lo Inconfiscable</h1>
        <p style="font-size: 1.2em; color: rgba(255, 255, 255, 0.8);">
            Descubre cómo escapar del control del sistema financiero tradicional
        </p>
    </div>
""", unsafe_allow_html=True)

# Los 4 Pilares
st.markdown("## Los Cuatro Pilares del Viaje")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
        <div class="pillar-card pillar-trap">
            <h3>🔴 La Trampa</h3>
            <p>Fondos en exchanges centralizados son confiscables. 
            Trazabilidad 100%. El Estado sabe cuándo, cómo y cuánto compraste.</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
        <div class="pillar-card pillar-break">
            <h3>🔵 La Ruptura</h3>
            <p>Compra Token DM2. Intercambia USDC por DM2. 
            Rompe la trazabilidad onchain anonimizando tus fondos.</p>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
        <div class="pillar-card pillar-illusion">
            <h3>🟠 La Ilusión</h3>
            <p>Autocustodia previene confiscación inmediata, PERO 
            la trazabilidad permanece. Las autoridades saben que lo tienes.</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
        <div class="pillar-card pillar-unconfiscable">
            <h3>🟢 Lo Inconfiscable</h3>
            <p>Rompe la trazabilidad. Obtén verdadera privacidad y control total. 
            Tus activos descentralizados. Solo tú los controlas.</p>
        </div>
    """, unsafe_allow_html=True)

# Sección de Calculadora
st.markdown("## Simula Tu Futuro Inconfiscable")

st.markdown("""
    <div class="calculator-section">
        <p style="font-size: 1.1em; color: rgba(255, 255, 255, 0.9);">
            Descubre la diferencia entre comprar Bitcoin de forma tradicional (atrapado en el sistema) 
            versus de forma anónima y descentralizada (verdaderamente inconfiscable).
        </p>
    </div>
""", unsafe_allow_html=True)

# Inputs de la calculadora
col1, col2 = st.columns(2)

with col1:
    start_date = st.date_input(
        "📅 Fecha de inicio de tu inversión",
        value=datetime(2020, 1, 1),
        min_value=datetime(2010, 1, 1),
        max_value=datetime.now()
    )
    
    amount_usd = st.number_input(
        "💵 Cantidad a comprar periódicamente (USD)",
        min_value=10.0,
        value=500.0,
        step=10.0
    )

with col2:
    frequency = st.selectbox(
        "📊 Frecuencia de recompras",
        ["Diaria", "Semanal", "Mensual"]
    )
    
    if frequency == "Semanal":
        day_of_week = st.selectbox(
            "Día de la semana",
            ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"],
            index=0
        )
        day_of_week_num = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"].index(day_of_week)
        day_of_month = None
    elif frequency == "Mensual":
        day_of_month = st.selectbox(
            "Día del mes",
            list(range(1, 32)),
            index=0
        )
        day_of_week_num = None
    else:
        day_of_week_num = None
        day_of_month = None

col1, col2 = st.columns(2)

with col1:
    future_price = st.number_input(
        "🎯 Precio futuro de Bitcoin (USD)",
        min_value=1000.0,
        value=100000.0,
        step=1000.0
    )

with col2:
    future_date = st.date_input(
        "📅 Fecha en que alcanzará ese precio",
        value=datetime(2030, 1, 1),
        min_value=datetime.now(),
        max_value=datetime(2050, 12, 31)
    )

# Botón de cálculo
calculate_button = st.button("🚀 Simular Mi Futuro Inconfiscable", use_container_width=True)

if calculate_button:
    # Validar fechas
    if start_date >= future_date:
        st.error("❌ La fecha de inicio debe ser anterior a la fecha futura.")
    else:
        with st.spinner("⏳ Obteniendo datos históricos de Bitcoin desde Yahoo Finance..."):
            # Obtener precios históricos usando yfinance
            bitcoin_prices = get_bitcoin_prices(start_date, future_date)
            
            if bitcoin_prices:
                # Calcular DCA para ambos escenarios
                btc_accumulated, total_invested, purchases = calculate_dca(
                    start_date,
                    future_date,
                    amount_usd,
                    frequency,
                    day_of_week_num if frequency == "Semanal" else None,
                    day_of_month if frequency == "Mensual" else None,
                    bitcoin_prices
                )
                
                if btc_accumulated > 0.0001 and total_invested > 0 and len(purchases) > 0:
                    # Cálculos para Escenario A (La Trampa)
                    gross_value_a = btc_accumulated * future_price
                    taxes = gross_value_a * 0.25  # 25% de impuestos
                    net_value_a = gross_value_a - taxes
                    roi_a = ((net_value_a - total_invested) / total_invested * 100) if total_invested > 0 else 0
                    years = (future_date - start_date).days / 365.25
                    cagr_a = calculate_cagr(total_invested, net_value_a, years)
                    
                    # Cálculos para Escenario B (Lo Inconfiscable)
                    gross_value_b = btc_accumulated * future_price
                    net_value_b = gross_value_b  # Sin impuestos
                    roi_b = ((net_value_b - total_invested) / total_invested * 100) if total_invested > 0 else 0
                    cagr_b = calculate_cagr(total_invested, net_value_b, years)
                    
                    # Mostrar resultados
                    st.markdown("## 📊 Resultados Comparativos")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("""
                            <div class="scenario-card scenario-a">
                                <h3>🔴 Escenario A: La Trampa</h3>
                                <p style="color: rgba(255, 255, 255, 0.8); font-size: 0.9em;">
                                    Compra tradicional a través de exchange centralizado. 
                                    El Estado controla tu información. Atrapado en el sistema.
                                </p>
                            </div>
                        """, unsafe_allow_html=True)
                        
                        st.metric("Inversión Total", f"${total_invested:,.2f}")
                        st.metric("Bitcoin Acumulado", f"{btc_accumulated:.4f} BTC")
                        st.metric("Valor Bruto (al precio futuro)", f"${gross_value_a:,.2f}")
                        st.metric("Impuestos (25%)", f"-${taxes:,.2f}", delta=None)
                        st.metric("Valor Neto", f"${net_value_a:,.2f}")
                        st.metric("Rentabilidad", f"{roi_a:.2f}%")
                        st.metric("CAGR", f"{cagr_a:.2f}%")
                    
                    with col2:
                        st.markdown("""
                            <div class="scenario-card scenario-b">
                                <h3>🟢 Escenario B: Lo Inconfiscable</h3>
                                <p style="color: rgba(255, 255, 255, 0.8); font-size: 0.9em;">
                                    Compra anónima, descentralizada y autocustodiada. 
                                    Nadie sabe cuánto tienes. Verdadera libertad financiera.
                                </p>
                            </div>
                        """, unsafe_allow_html=True)
                        
                        st.metric("Inversión Total", f"${total_invested:,.2f}")
                        st.metric("Bitcoin Acumulado", f"{btc_accumulated:.4f} BTC")
                        st.metric("Valor Bruto (al precio futuro)", f"${gross_value_b:,.2f}")
                        st.metric("Impuestos", "$0 (Sin impacto fiscal)")
                        st.metric("Valor Neto", f"${net_value_b:,.2f}")
                        st.metric("Rentabilidad", f"{roi_b:.2f}%")
                        st.metric("CAGR", f"{cagr_b:.2f}%")
                    
                    # Diferencia
                    st.markdown("---")
                    difference = net_value_b - net_value_a
                    st.markdown(f"""
                        <div style="background-color: rgba(45, 106, 79, 0.2); padding: 20px; border-radius: 10px; border-left: 5px solid #2D6A4F;">
                            <h3>💰 Tu Ventaja Por Ser Inconfiscable</h3>
                            <p style="font-size: 1.2em; color: #06A77D; font-weight: bold;">
                                ${difference:,.2f} más en tu bolsillo
                            </p>
                            <p style="color: rgba(255, 255, 255, 0.8);">
                                Esto es lo que ahorras en impuestos y lo que ganas por no estar atrapado en el sistema.
                            </p>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    # Tabla detallada de compras
                    with st.expander("📋 Ver detalle de todas las compras"):
                        df_purchases = pd.DataFrame(purchases)
                        df_purchases['date'] = df_purchases['date'].astype(str)
                        df_purchases.columns = ['Fecha', 'Precio BTC (USD)', 'Inversión (USD)', 'BTC Comprado']
                        st.dataframe(df_purchases, use_container_width=True)
                    
                    # Informe comparativo
                    st.markdown("## 🎯 Opciones Como Ser Inconfiscable")
                    
                    st.markdown("""
                        ### Vivir de tus Bitcoin sin venderlos
                        
                        Una vez que eres inconfiscable, tienes opciones que los atrapados en el sistema no tienen:
                        
                        **Préstamo Pignorado**: Puedes usar tus Bitcoin como colateral para obtener un préstamo en USD o stablecoins, 
                        sin necesidad de venderlos. Esto significa:
                        
                        - **Mantener tu exposición a Bitcoin**: Tus BTC siguen creciendo mientras usas el dinero del préstamo
                        - **Vivir del préstamo**: Usa los fondos para tus gastos diarios
                        - **Pagar intereses bajos**: Plataformas DeFi ofrecen tasas mucho menores que bancos tradicionales
                        - **Sin confiscación**: Nadie puede quitarte tus Bitcoin porque están en tu autocustodia
                        - **Privacidad total**: Tus transacciones no están vinculadas a tu identidad
                        
                        ### Comparación con el Escenario A (La Trampa)
                        
                        Si estuvieras atrapado en el sistema tradicional:
                        
                        - **Tendrías que vender** para acceder a tu dinero (pagando impuestos sobre ganancias)
                        - **El Estado sabría** exactamente cuándo y cuánto vendiste
                        - **Estarías vigilado** en cada transacción
                        - **No tendrías privacidad** financiera real
                        - **Tus fondos estarían en riesgo** de confiscación
                        
                        ### La Libertad Financiera Real
                        
                        Ser inconfiscable significa:
                        
                        - **Control total** sobre tus activos
                        - **Privacidad financiera** completa
                        - **Libertad** para hacer lo que quieras con tu dinero
                        - **Protección** contra la confiscación y el control estatal
                        - **Oportunidades** que el sistema tradicional nunca te dará
                    """)
                    
                    # Formulario de registro
                    st.markdown("---")
                    st.markdown("""
                        <div style="background: linear-gradient(135deg, rgba(45, 106, 79, 0.2), rgba(6, 168, 125, 0.2)); padding: 40px; border-radius: 10px; border: 2px solid #06A77D;">
                            <h2 style="color: #06A77D; text-align: center;">🔐 Comienza Tu Viaje Hacia Lo Inconfiscable</h2>
                            <p style="text-align: center; color: rgba(255, 255, 255, 0.9); font-size: 1.1em;">
                                Recibe una secuencia de correos explicándote los 4 pasos para hacerte verdaderamente inconfiscable.
                            </p>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        email = st.text_input(
                            "📧 Tu email",
                            placeholder="tu@email.com"
                        )
                    
                    with col2:
                        name = st.text_input(
                            "👤 Tu nombre (opcional)",
                            placeholder="Tu nombre"
                        )
                    
                    if st.button("📬 Recibir la Secuencia de Correos", use_container_width=True):
                        if email and "@" in email:
                            st.success("✅ ¡Gracias! Revisa tu email para confirmar tu suscripción.")
                            st.info("""
                                Recibirás una secuencia de correos que te explicará:
                                
                                **Paso 1**: Configurar tu propio banco autocustodia
                                **Paso 2**: Hacer tu primera compra de dinero onchain
                                **Paso 3**: Romper la trazabilidad onchain, anonimizando tus fondos
                                **Paso 4**: Comprar Bitcoin de manera recurrente sin KYC, de forma descentralizada
                                
                                Estos correos contienen el QUÉ, pero no el CÓMO. 
                                Si quieres aprender el CÓMO en detalle, accede a la formación Inconfiscable.
                            """)
                        else:
                            st.error("❌ Por favor, ingresa un email válido")
                else:
                    st.error(f"❌ No se encontraron suficientes datos de compra. Se encontraron {len(purchases)} compras. Intenta con un período más reciente o una cantidad diferente.")
            else:
                st.error("❌ No se pudieron obtener los datos históricos de Bitcoin. Por favor, intenta más tarde o con un período diferente.")

# Footer
st.markdown("""
    <div class="footer">
        <p>© 2024 Inconfiscable - El Camino Hacia La Libertad Financiera</p>
        <p style="font-size: 0.9em; color: rgba(255, 255, 255, 0.5);">
            Disclaimer: Esta herramienta es solo educativa. No es asesoramiento financiero. 
            Consulta con profesionales antes de tomar decisiones de inversión.
        </p>
    </div>
""", unsafe_allow_html=True)

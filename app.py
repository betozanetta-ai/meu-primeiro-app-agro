import streamlit as st
import yfinance as yf
from geopy.geocoders import Nominatim
from geopy.distance import geodesic

st.set_page_config(page_title="AgroDecisão: Inteligência de Mercado", layout="wide")

def fmt_br(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

st.title("🌾 AgroDecisão: Inteligência de Margem")
st.markdown("---")

# --- 1. DADOS DE MERCADO ---
@st.cache_data(ttl=3600)
def buscar_dados():
    ticker = yf.Ticker("ZS=F")
    hist = ticker.history(period="2d") # Pegamos 2 dias para ver a variação
    
    soja_hoje = hist['Close'].iloc[-1] * 2.20462
    soja_ontem = hist['Close'].iloc[-2] * 2.20462
    var_chicago = ((soja_hoje - soja_ontem) / soja_ontem) * 100
    
    dolar = yf.Ticker("USDBRL=X").history(period="1d")['Close'].iloc[-1]
    return dolar, soja_hoje, var_chicago

dolar, soja_usd, var_chicago = buscar_dados()
preco_bruto = soja_usd * dolar

# --- 2. INPUTS DE ROTA ---
col1, col2 = st.columns(2)
with col1:
    origem = st.text_input("Sua Localização:", "São José do Rio Preto - SP")
    destino = st.text_input("Destino do Grão:", "Bebedouro - SP")
with col2:
    # Simulando um "histórico" de frete para o insight funcionar
    frete_atual_km = st.number_input("Preço do Frete hoje (R$ por KM/Saca):", value=0.15)
    frete_anterior = 0.14 # Valor base para comparação de variação
    var_frete = ((frete_atual_km - frete_anterior) / frete_anterior) * 100

# --- 3. CÁLCULO E INSIGHT ---
if st.button("ANALISAR GANHO REAL"):
    geolocator = Nominatim(user_agent="agro_insight")
    loc1, loc2 = geolocator.geocode(origem), geolocator.geocode(destino)
    
    if loc1 and loc2:
        distancia = geodesic((loc1.latitude, loc1.longitude), (loc2.latitude, loc2.longitude)).km
        custo_frete = distancia * frete_atual_km
        ganho_liquido = preco_bruto - custo_frete

        # --- O INSIGHT (A sua ideia central) ---
        st.markdown("### 💡 Insight do Especialista")
        
        if var_chicago > 0 and var_frete > var_chicago:
            st.error(f"🚨 **CUIDADO:** O preço em Chicago subiu {var_chicago:.1f}%, mas o frete para sua região subiu {var_frete:.1f}%. Seu ganho real caiu!")
        elif var_chicago > 0 and var_frete <= var_chicago:
            st.success(f"🚀 **OPORTUNIDADE:** Chicago subiu {var_chicago:.1f}% e superou a alta do frete. Momento favorável!")
        else:
            st.warning("📉 Chicago em queda. Avalie segurar o estoque se o frete não baixar.")

        st.markdown("---")
        # --- OUTPUTS FINAIS ---
        c1, c2, c3 = st.columns(3)
        c1.metric("Preço de Mercado", fmt_br(preco_bruto))
        c2.metric("Custo do Frete", fmt_br(custo_frete), f"{distancia:.1f} km")
        c3.metric("LUCRO LÍQUIDO", fmt_br(ganho_liquido))
    else:
        st.error("Verifique os nomes das cidades.")

st.sidebar.markdown(f"**Variação Chicago:** {var_chicago:+.2f}%")

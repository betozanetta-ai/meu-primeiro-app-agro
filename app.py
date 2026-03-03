import streamlit as st
import yfinance as yf
from geopy.geocoders import Nominatim
from geopy.distance import geodesic

# Configuração de Localização (Português/Brasil)
import locale
try:
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
except:
    locale.setlocale(locale.LC_ALL, '')

st.set_page_config(page_title="AgroDecisão: Frete Real", page_icon="🚛", layout="wide")

# Função para formatar moeda brasileira
def formato_real(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

st.title("🚛 Simulador de Frete e Margem Real")
st.markdown("---")

# --- MERCADO EM TEMPO REAL ---
@st.cache_data(ttl=3600)
def buscar_dados():
    dolar = yf.Ticker("USDBRL=X").history(period="1d")['Close'].iloc[-1]
    soja_chicago = yf.Ticker("ZS=F").history(period="1d")['Close'].iloc[-1] * 2.204
    return dolar, soja_chicago

dolar, soja_usd = buscar_dados()
preco_ref_br = soja_usd * dolar

# --- LAYOUT EM COLUNAS ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("📍 Configuração da Rota")
    origem = st.text_input("Cidade de Origem (Ex: São José do Rio Preto - SP)", "São José do Rio Preto - SP")
    destino = st.text_input("Cidade de Destino (Ex: Bebedouro - SP)", "Bebedouro - SP")
    
    st.info("💡 O app calcula a distância real via satélite.")

with col2:
    st.subheader("💰 Custos Logísticos")
    # Valor base sugerido (ajustável pelo produtor para ser o valor REAL do dia)
    custo_km = st.number_input("Custo por KM/Saca (R$):", value=0.15, step=0.01, format="%.2f")
    custo_producao = st.number_input("Seu Custo de Produção (R$/Saca):", value=100.0, step=1.0, format="%.2f")

# --- CÁLCULO DE ROTA ---
if st.button("CALCULAR MARGEM LÍQUIDA"):
    geolocator = Nominatim(user_agent="agro_app_rio_preto")
    loc1 = geolocator.geocode(origem)
    loc2 = geolocator.geocode(destino)

    if loc1 and loc2:
        distancia = geodesic((loc1.latitude, loc1.longitude), (loc2.latitude, loc2.longitude)).km
        frete_total = distancia * custo_km
        preco_liquido = preco_ref_br - frete_total
        lucro = preco_liquido - custo_producao
        
        st.markdown("---")
        st.subheader("📊 Resultado da Operação")
        
        res_col1, res_col2, res_col3 = st.columns(3)
        res_col1.metric("Distância Total", f"{distancia:.1f} KM")
        res_col2.metric("Frete por Saca", formato_real(frete_total))
        res_col3.metric("Preço Líquido (Origem)", formato_real(preco_liquido))
        
        st.markdown(f"### Lucro Estimado: **{formato_real(lucro)}** por saca")
    else:
        st.error("Erro: Não encontrei as cidades. Verifique se digitou 'Cidade - UF' corretamente.")

# Rodapé com indicadores
st.sidebar.markdown("### 📈 Mercado Hoje")
st.sidebar.write(f"**Dólar:** {formato_real(dolar)}")
st.sidebar.write(f"**Chicago:** US$ {soja_usd:.2f}")

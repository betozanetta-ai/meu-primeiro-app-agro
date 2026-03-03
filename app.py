import streamlit as st
import yfinance as yf
import pandas as pd

# Configuração da página
st.set_page_config(page_title="AgroDecisão Ceagesp", page_icon="🌾")

st.title("🌾 AgroDecisão: Momento de Venda")
st.markdown("---")

# --- BUSCA DE DADOS ---
@st.cache_data(ttl=3600) # Faz o app não baixar tudo de novo toda vez que você clica
def carregar_dados_mercado():
    dolar = yf.Ticker("USDBRL=X").history(period="1d")['Close'].iloc[-1]
    soja_chicago = yf.Ticker("ZS=F").history(period="1d")['Close'].iloc[-1]
    return dolar, soja_chicago

dolar, chicago = carregar_dados_mercado()

# --- INPUTS DO USUÁRIO ---
col1, col2 = st.columns(2)
with col1:
    custo_producao = st.number_input("Seu Custo (R$/Saca)", value=110.0)
with col2:
    frete_regiao = st.number_input("Frete até Comprador (R$)", value=12.0)

# --- LÓGICA DE NEGÓCIO ---
# Aqui simulamos o preço que buscamos do CEPEA ou Notícias Agrícolas
preco_referencia = 138.50 # Você pode conectar a função do CEPEA aqui
preco_liquido = preco_referencia - frete_regiao
margem = ((preco_liquido - custo_producao) / custo_producao) * 100

# --- EXIBIÇÃO ---
st.metric(label="Preço Líquido na Fazenda", value=f"R$ {preco_liquido:.2f}", 
          delta=f"{(preco_liquido - custo_producao):.2f} de lucro por saca")

if margem > 15:
    st.success(f"ÓTIMA OPORTUNIDADE: Margem de {margem:.1f}%")
    st.write("💡 Sugestão: Trave pelo menos 20% da safra hoje.")
elif margem > 0:
    st.warning(f"MARGEM APERTADA: {margem:.1f}%")
    st.write("💡 Sugestão: Aguarde melhora no dólar ou frete.")
else:
    st.error(f"PREJUÍZO DETECTADO: {margem:.1f}%")

st.markdown("---")
st.write(f"**Indicadores Globais:** Dólar R$ {dolar:.2f} | Chicago US$ {chicago:.2f}")

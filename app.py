import streamlit as st
import yfinance as yf
import pandas as pd

# Configuração da página para parecer um App profissional
st.set_page_config(page_title="AgroDecisão Ceagesp", page_icon="🌾", layout="centered")

st.title("🌾 AgroDecisão: Lucro Real")
st.markdown("---")

# --- BUSCA DE DADOS (CHICAGO E DÓLAR) ---
@st.cache_data(ttl=3600)
def carregar_dados_mercado():
    dolar = yf.Ticker("USDBRL=X").history(period="1d")['Close'].iloc[-1]
    # Soja Chicago (ZS=F) - valor em bushels
    soja_chicago_bushel = yf.Ticker("ZS=F").history(period="1d")['Close'].iloc[-1]
    # Conversão simples: Bushel para Saca (60kg) -> fator aprox. 2.204
    preco_saca_chicago_usd = soja_chicago_bushel * 2.204
    return dolar, preco_saca_chicago_usd

dolar, soja_usd = carregar_dados_mercado()
preco_referencia_reais = soja_usd * dolar

# --- LOGÍSTICA E FRETE (O pulo do gato) ---
st.subheader("📍 Simulação por Região")

# Tabela de fretes médios (R$ por saca) - Você pode ajustar esses valores depois
tabela_fretes = {
    "Sorriso (MT)": 25.00,
    "Rio Verde (GO)": 18.50,
    "Cascavel (PR)": 12.00,
    "Passo Fundo (RS)": 11.00,
    "Londrina (PR)": 10.00,
    "Outra / Manual": 0.00
}

escolha = st.selectbox("Selecione a origem da soja:", list(tabela_fretes.keys()))

if escolha == "Outra / Manual":
    frete_final = st.number_input("Informe o valor do frete (R$):", value=15.0)
else:
    frete_final = tabela_fretes[escolha]
    st.info(f"🚚 Frete estimado para {escolha}: **R$ {frete_final:.2f}/saca**")

# --- INPUT DE CUSTO ---
custo_producao = st.number_input("Seu Custo de Produção (R$/Saca):", value=100.0)

# --- CÁLCULO FINAL ---
preco_liquido = preco_referencia_reais - frete_final
lucro_por_saca = preco_liquido - custo_producao
margem = (lucro_por_saca / custo_producao) * 100

# --- EXIBIÇÃO DO RESULTADO ---
st.markdown("---")
col1, col2 = st.columns(2)

with col1:
    st.metric(label="Preço Líquido (Fazenda)", value=f"R$ {preco_liquido:.2f}")
with col2:
    color = "normal" if lucro_por_saca > 0 else "inverse"
    st.metric(label="Lucro por Saca", value=f"R$ {lucro_por_saca:.2f}", delta=f"{margem:.1f}%", delta_color=color)

if margem > 20:
    st.success("✅ EXCELENTE MARGEM: Hora de avaliar venda ou trava!")
elif margem > 5:
    st.warning("⚠️ MARGEM APERTADA: Cuidado com as oscilações do dólar.")
else:
    st.error("🚨 RISCO DE PREJUÍZO: Reveja a estratégia logística ou aguarde Chicago.")

st.sidebar.markdown("### Indicadores de Mercado")
st.sidebar.write(f"💵 Dólar: R$ {dolar:.2f}")
st.sidebar.write(f"📈 Chicago (Saca): US$ {soja_usd:.2f}")

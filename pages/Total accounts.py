# FASE 1 - Total Accounts Ultra-Simples
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Total Accounts - FASE 1", page_icon="💰")

st.title("💰 Total Accounts - FASE 1")
st.success("✅ Página funcionando!")

# Detectar ambiente
is_cloud = False
try:
    import os
    if 'STREAMLIT_SHARING_MODE' in os.environ:
        is_cloud = True
except:
    pass

if is_cloud:
    st.success("☁️ Funcionando no Streamlit Cloud")
else:
    st.info("💻 Executando localmente")

st.subheader("📊 Resumo de Contas")

# Dados de exemplo
data = {
    'Conta': ['Receitas', 'Despesas', 'Investimentos', 'Lucro'],
    'Valor': [5000000, -3000000, -1000000, 1000000],
    'Tipo': ['Entrada', 'Saída', 'Saída', 'Resultado']
}

df = pd.DataFrame(data)
df['Valor_Formatado'] = df['Valor'].apply(lambda x: f"R$ {x:,.0f}")
st.dataframe(df[['Conta', 'Valor_Formatado', 'Tipo']], use_container_width=True)

st.subheader("📈 Distribuição")
st.bar_chart(df.set_index('Conta')['Valor'])

st.info("💡 FASE 1: Análises detalhadas serão implementadas nas próximas fases")
st.caption("Total Accounts - FASE 1")
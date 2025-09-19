# FASE 1 - Waterfall Analysis Ultra-Simples
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Waterfall - FASE 1", page_icon="🌊")

st.title("🌊 Waterfall Analysis - FASE 1")
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

st.subheader("🌊 Análise Cascata")

# Dados de exemplo para waterfall
data = {
    'Categoria': ['Inicial', 'Entrada A', 'Entrada B', 'Saída C', 'Final'],
    'Valor': [1000, 500, 300, -200, 1600],
    'Tipo': ['Base', 'Positivo', 'Positivo', 'Negativo', 'Total']
}

df = pd.DataFrame(data)
st.dataframe(df, use_container_width=True)

st.subheader("📊 Fluxo Simplificado")
st.bar_chart(df.set_index('Categoria')['Valor'])

st.info("💡 FASE 1: Gráfico waterfall interativo será implementado nas próximas fases")
st.caption("Waterfall Analysis - FASE 1")
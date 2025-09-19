# FASE 1 - IA Unificada Ultra-Simples
import streamlit as st
import pandas as pd

st.set_page_config(page_title="IA Unificada - FASE 1", page_icon="🤖")

st.title("🤖 IA Unificada - FASE 1")
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

# Dados de exemplo
st.subheader("📊 Análise Simplificada")
data = {
    'Análise': ['Tendência', 'Padrão', 'Anomalia', 'Previsão'],
    'Resultado': ['Crescimento 5%', 'Sazonal', 'Detectada', 'Estável'],
    'Confiança': [0.85, 0.92, 0.78, 0.88]
}

df = pd.DataFrame(data)
st.dataframe(df, use_container_width=True)

st.subheader("📈 Confiança das Análises")
st.bar_chart(df.set_index('Análise')['Confiança'])

st.info("💡 FASE 1: Funcionalidades completas serão adicionadas gradualmente")
st.caption("IA Unificada - FASE 1")

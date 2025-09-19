import streamlit as st
import pandas as pd
import os

# Configuração básica
st.set_page_config(page_title="Dashboard KE5Z", page_icon="📊")

# Título imediato para health check
st.title("📊 Dashboard KE5Z")
st.write("✅ Aplicação funcionando!")

# Detectar ambiente
is_cloud = True
try:
    base_url = st.get_option('server.baseUrlPath') or ''
    is_cloud = 'share.streamlit.io' in base_url
except:
    pass

# Informação do ambiente
if is_cloud:
    st.success("☁️ Executando no Streamlit Cloud")
else:
    st.info("💻 Executando localmente")

# Tentar carregar dados
try:
    arquivo = os.path.join("KE5Z", "KE5Z.parquet")
    if os.path.exists(arquivo):
        df = pd.read_parquet(arquivo)
        st.success(f"✅ Dados carregados: {len(df):,} registros")
        
        # Mostrar amostra
        st.dataframe(df.head(10))
    else:
        st.warning("⚠️ Arquivo de dados não encontrado")
        st.info("📄 Criando dados de exemplo...")
        
        # Dados de exemplo
        df = pd.DataFrame({
            'USI': ['Veículos', 'Motores'] * 5,
            'Período': ['2024-01', '2024-02'] * 5,
            'Valor': [1000, 2000] * 5
        })
        st.dataframe(df)
        
except Exception as e:
    st.error(f"Erro: {e}")
    st.info("Usando dados básicos...")
    
    # Dados mínimos
    df = pd.DataFrame({'Status': ['OK'], 'Teste': [1]})
    st.dataframe(df)

st.markdown("---")
st.info("💡 Dashboard KE5Z - Versão minimalista para teste")

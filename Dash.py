# FASE 1 - Dashboard KE5Z Ultra-Básico para Teste Streamlit Cloud
import streamlit as st
import pandas as pd

# Configuração básica da página
st.set_page_config(
    page_title="Dashboard KE5Z - FASE 1",
    page_icon="📊",
    layout="wide"
)

# Health check imediato
st.title("📊 Dashboard KE5Z - FASE 1")
st.success("✅ Sistema funcionando!")

# Detectar ambiente
is_cloud = False
try:
    # Tentar detectar se está no Streamlit Cloud
    import os
    if 'STREAMLIT_SHARING_MODE' in os.environ or 'share.streamlit.io' in str(st.get_option('server.baseUrlPath') or ''):
        is_cloud = True
except:
    pass

# Informação do ambiente
if is_cloud:
    st.success("☁️ SUCESSO! Funcionando no Streamlit Cloud")
    st.balloons()
else:
    st.info("💻 Executando localmente")

# Dados de exemplo ultra-simples (sem arquivos externos)
st.subheader("📊 Dados de Teste")

# Criar dados de exemplo pequenos
data = {
    'USI': ['Veículos', 'Motores', 'Peças', 'Outros', 'Veículos', 'Motores'],
    'Período': ['2024-01', '2024-02', '2024-03', '2024-01', '2024-02', '2024-03'],
    'Type 05': ['A', 'B', 'A', 'C', 'A', 'B'],
    'Type 06': ['X', 'Y', 'Z', 'X', 'Y', 'Z'],
    'Valor': [1000000, 2000000, 1500000, 500000, 800000, 1200000]
}

df = pd.DataFrame(data)

# Mostrar dados
st.dataframe(df, use_container_width=True)

# Sidebar com filtros básicos
st.sidebar.title("🔍 Filtros")
st.sidebar.markdown("---")

# Filtros simples
usi_selected = st.sidebar.multiselect(
    "Selecionar USI:",
    options=df['USI'].unique(),
    default=df['USI'].unique()
)

periodo_selected = st.sidebar.multiselect(
    "Selecionar Período:",
    options=sorted(df['Período'].unique()),
    default=sorted(df['Período'].unique())
)

# Aplicar filtros
df_filtered = df.copy()
if usi_selected:
    df_filtered = df_filtered[df_filtered['USI'].isin(usi_selected)]
if periodo_selected:
    df_filtered = df_filtered[df_filtered['Período'].isin(periodo_selected)]

# Informações da sidebar
st.sidebar.markdown("---")
st.sidebar.metric("Registros", len(df_filtered))
st.sidebar.metric("Total (R$)", f"{df_filtered['Valor'].sum():,.0f}")

# Área principal com dados filtrados
if len(df_filtered) > 0:
    st.subheader("📈 Dados Filtrados")
    st.dataframe(df_filtered, use_container_width=True)
    
    # Gráfico básico usando st.bar_chart (nativo do Streamlit)
    st.subheader("📊 Gráfico por Período")
    chart_data = df_filtered.groupby('Período')['Valor'].sum()
    st.bar_chart(chart_data)
    
    # Resumo por USI
    st.subheader("📋 Resumo por USI")
    summary = df_filtered.groupby('USI')['Valor'].sum().reset_index()
    summary.columns = ['USI', 'Total (R$)']
    summary['Total (R$)'] = summary['Total (R$)'].apply(lambda x: f"R$ {x:,.0f}")
    st.dataframe(summary, use_container_width=True)
    
else:
    st.warning("⚠️ Nenhum dado encontrado com os filtros selecionados")

# Status da aplicação
st.markdown("---")
st.subheader("🔧 Status do Sistema")

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.success("✅ Streamlit: OK")
with col2:
    st.success("✅ Pandas: OK")
with col3:
    st.success("✅ Dados: OK")
with col4:
    st.success("✅ Filtros: OK")

# Informações da FASE 1
st.info("""
💡 **FASE 1 - Teste Básico**
- ✅ Sem autenticação
- ✅ Dados hardcoded (pequenos)
- ✅ Interface simples
- ✅ Filtros básicos
- ✅ Gráfico nativo

**Se esta versão funcionar no Streamlit Cloud, podemos adicionar funcionalidades gradualmente!**
""")

st.markdown("---")
st.caption("Dashboard KE5Z - FASE 1 | Teste Streamlit Cloud")
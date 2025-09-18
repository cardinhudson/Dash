#!/usr/bin/env python3
"""
Versão do dashboard otimizada para Streamlit Cloud
Sem sistema de autenticação para evitar erros
"""
import streamlit as st
import pandas as pd
import os
import altair as alt

# Configuração da página
st.set_page_config(
    page_title="Dashboard KE5Z",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Detectar ambiente
try:
    base_url = st.get_option('server.baseUrlPath') or ''
    is_cloud = 'share.streamlit.io' in base_url
except Exception:
    is_cloud = False

# Header
st.title("📊 Dashboard - Visualização de Dados TC - KE5Z")
st.subheader("Somente os dados com as contas do Perímetro TC")

# Informar sobre ambiente
if is_cloud:
    st.sidebar.info("☁️ **Modo Cloud**\nVersão simplificada para máxima compatibilidade")
else:
    st.sidebar.success("💻 **Modo Local**")

st.markdown("---")

# Carregar dados com tratamento robusto
@st.cache_data(show_spinner=True)
def load_data():
    """Carrega os dados do arquivo parquet"""
    try:
        arquivo_parquet = os.path.join("KE5Z", "KE5Z.parquet")
        
        if not os.path.exists(arquivo_parquet):
            st.error(f"❌ Arquivo não encontrado: {arquivo_parquet}")
            return pd.DataFrame()
        
        # Carregar dados
        df = pd.read_parquet(arquivo_parquet)
        
        # Validar dados
        if df.empty:
            st.error("❌ Arquivo parquet está vazio")
            return pd.DataFrame()
            
        # Filtrar dados válidos
        df = df[df['USI'].notna()]
        
        # Limitar dados no cloud
        if is_cloud and len(df) > 50000:
            st.warning("☁️ Limitando dados para melhor performance no cloud")
            df = df.sample(n=50000, random_state=42)
        
        return df
        
    except Exception as e:
        st.error(f"❌ Erro ao carregar dados: {str(e)}")
        return pd.DataFrame()

# Carregar dados
with st.spinner("🔄 Carregando dados..."):
    df_total = load_data()

if df_total.empty:
    st.error("❌ Não foi possível carregar os dados.")
    st.info("💡 **Possíveis soluções:**")
    st.info("1. Verifique se o arquivo KE5Z.parquet existe na pasta KE5Z/")
    st.info("2. Certifique-se que o arquivo foi enviado para o repositório")
    st.stop()

st.success(f"✅ Dados carregados: {len(df_total):,} registros")

# Filtros
st.sidebar.title("Filtros")

# Filtro USI
try:
    if 'USI' in df_total.columns:
        usina_opcoes = ["Todos"] + sorted(df_total['USI'].dropna().astype(str).unique().tolist())
        default_usina = ["Veículos"] if "Veículos" in usina_opcoes else ["Todos"]
        usina_selecionada = st.sidebar.multiselect("Selecione a USINA:", usina_opcoes, default=default_usina)
        
        if "Todos" in usina_selecionada or not usina_selecionada:
            df_filtrado = df_total.copy()
        else:
            df_filtrado = df_total[df_total['USI'].astype(str).isin(usina_selecionada)]
    else:
        df_filtrado = df_total.copy()
        usina_selecionada = ["Todos"]
except Exception as e:
    st.sidebar.error(f"Erro no filtro USI: {str(e)}")
    df_filtrado = df_total.copy()

# Filtro Período
try:
    if 'Período' in df_filtrado.columns:
        periodo_opcoes = ["Todos"] + sorted(df_filtrado['Período'].dropna().astype(str).unique().tolist())
        periodo_selecionado = st.sidebar.selectbox("Selecione o Período:", periodo_opcoes)
        if periodo_selecionado != "Todos":
            df_filtrado = df_filtrado[df_filtrado['Período'].astype(str) == str(periodo_selecionado)]
except Exception as e:
    st.sidebar.error(f"Erro no filtro Período: {str(e)}")
    periodo_selecionado = "Todos"

# Informações dos filtros
st.sidebar.markdown("---")
st.sidebar.subheader("📊 Resumo")
try:
    st.sidebar.write(f"**Linhas:** {df_filtrado.shape[0]:,}")
    st.sidebar.write(f"**Colunas:** {df_filtrado.shape[1]}")
    if 'Valor' in df_filtrado.columns:
        total_valor = df_filtrado['Valor'].sum()
        st.sidebar.write(f"**Total:** R$ {total_valor:,.2f}")
except Exception as e:
    st.sidebar.error(f"Erro no resumo: {str(e)}")

# Gráfico principal
if 'Período' in df_filtrado.columns and 'Valor' in df_filtrado.columns:
    st.subheader("📊 Soma do Valor por Período")
    
    try:
        # Criar gráfico de barras
        chart = alt.Chart(df_filtrado).mark_bar().encode(
            x=alt.X('Período:N', title='Período'),
            y=alt.Y('sum(Valor):Q', title='Soma do Valor'),
            color=alt.Color('sum(Valor):Q', scale=alt.Scale(scheme='viridis')),
            tooltip=['Período:N', 'sum(Valor):Q']
        ).properties(
            title='Soma do Valor por Período',
            height=400
        )
        
        # Adicionar rótulos
        labels = chart.mark_text(
            align='center',
            baseline='bottom',
            dy=-5,
            fontSize=12
        ).encode(
            text=alt.Text('sum(Valor):Q', format=',.2f')
        )
        
        st.altair_chart(chart + labels, use_container_width=True)
        
    except Exception as e:
        st.error(f"Erro ao criar gráfico: {str(e)}")

# Tabela pivô
if 'USI' in df_filtrado.columns and 'Período' in df_filtrado.columns and 'Valor' in df_filtrado.columns:
    st.subheader("📋 Tabela Dinâmica - Soma do Valor por USI e Período")
    
    try:
        df_pivot = df_filtrado.pivot_table(
            index='USI', 
            columns='Período', 
            values='Valor', 
            aggfunc='sum', 
            margins=True, 
            margins_name='Total', 
            fill_value=0
        )
        
        # Formatar e exibir
        styled_df = df_pivot.style.format('R$ {:,.2f}')
        st.dataframe(styled_df, use_container_width=True)
        
    except Exception as e:
        st.error(f"Erro ao criar tabela pivô: {str(e)}")

# Tabela de dados
st.subheader("📋 Dados Filtrados")
try:
    # Limitar exibição para performance
    display_limit = 1000 if is_cloud else 5000
    df_display = df_filtrado.head(display_limit)
    
    st.dataframe(df_display, use_container_width=True)
    
    if len(df_filtrado) > display_limit:
        st.info(f"Mostrando primeiros {display_limit:,} registros de {len(df_filtrado):,} total")
        
except Exception as e:
    st.error(f"Erro ao exibir dados: {str(e)}")

# Footer
st.markdown("---")
st.info("💡 Esta é uma versão otimizada para Streamlit Cloud. "
        "Para funcionalidades completas, execute localmente.")

if is_cloud:
    st.success("☁️ Executando no Streamlit Cloud - Deploy realizado com sucesso!")

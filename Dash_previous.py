#!/usr/bin/env python3
"""
Dashboard KE5Z - Versão ultra-segura para Streamlit Cloud
Com tratamento robusto de erros e fallbacks
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

# Sistema de autenticação com fallback
try:
    from auth_simple import (verificar_autenticacao, exibir_header_usuario,
                             eh_administrador, verificar_status_aprovado)
    
    # Tentar autenticação
    verificar_autenticacao()
    
    # Verificar se o usuário está aprovado
    if 'usuario_nome' in st.session_state and not verificar_status_aprovado(st.session_state.usuario_nome):
        st.warning("⏳ Sua conta ainda está pendente de aprovação.")
        st.stop()
        
    auth_working = True
    
except Exception as e:
    # Fallback: sem autenticação se houver erro
    auth_working = False
    st.warning(f"⚠️ Sistema de autenticação indisponível: {str(e)}")
    st.info("🔓 Executando em modo aberto (sem autenticação)")
    
    # Funções dummy para compatibilidade
    def exibir_header_usuario():
        st.sidebar.info("🔓 Modo sem autenticação")
    
    def eh_administrador():
        return True  # Todos são admin no modo fallback

# Header
st.title("📊 Dashboard - Visualização de Dados TC - KE5Z")
st.subheader("Somente os dados com as contas do Perímetro TC")

# Exibir header do usuário
try:
    exibir_header_usuario()
except:
    pass

# Informar sobre ambiente
if is_cloud:
    if auth_working:
        st.sidebar.info("☁️ **Streamlit Cloud** - Autenticação ativa")
    else:
        st.sidebar.warning("☁️ **Streamlit Cloud** - Modo aberto")
else:
    st.sidebar.success("💻 **Modo Local**")

st.markdown("---")

# Carregar dados com tratamento ultra-robusto
@st.cache_data(show_spinner=True)
def load_data():
    """Carrega os dados do arquivo parquet com máximo tratamento de erro"""
    try:
        arquivo_parquet = os.path.join("KE5Z", "KE5Z.parquet")
        
        if not os.path.exists(arquivo_parquet):
            st.error(f"❌ Arquivo não encontrado: {arquivo_parquet}")
            return pd.DataFrame()
        
        # Carregar dados
        df = pd.read_parquet(arquivo_parquet)
        
        # Validações
        if df.empty:
            st.error("❌ Arquivo parquet está vazio")
            return pd.DataFrame()
        
        # Verificar colunas essenciais
        required_cols = ['USI', 'Valor']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            st.warning(f"⚠️ Colunas ausentes: {missing_cols}")
        
        # Filtrar dados válidos
        if 'USI' in df.columns:
            df = df[df['USI'].notna()]
        
        # Limitar dados no cloud para performance
        if is_cloud and len(df) > 100000:
            st.warning("☁️ Limitando dados para melhor performance no cloud")
            df = df.sample(n=100000, random_state=42)
        
        return df
        
    except Exception as e:
        st.error(f"❌ Erro ao carregar dados: {str(e)}")
        st.info("💡 **Possíveis soluções:**")
        st.info("1. Verifique se o arquivo KE5Z.parquet existe")
        st.info("2. Certifique-se que foi enviado para o repositório")
        return pd.DataFrame()

# Carregar dados
with st.spinner("🔄 Carregando dados..."):
    df_total = load_data()

if df_total.empty:
    st.error("❌ Não foi possível carregar os dados.")
    st.stop()

st.success(f"✅ Dados carregados: {len(df_total):,} registros")

# Filtros com tratamento de erro
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
    else:
        periodo_selecionado = "Todos"
except Exception as e:
    st.sidebar.error(f"Erro no filtro Período: {str(e)}")
    periodo_selecionado = "Todos"

# Filtros adicionais com tratamento de erro
for col_name, label in [("Centro cst", "Centro cst"), ("Nº conta", "Conta contábil")]:
    try:
        if col_name in df_filtrado.columns:
            opcoes = ["Todos"] + sorted(df_filtrado[col_name].dropna().astype(str).unique().tolist())
            
            # Limitar opções no cloud
            if is_cloud and len(opcoes) > 50:
                opcoes = opcoes[:50]
                st.sidebar.info(f"☁️ {label}: Limitando opções")
            
            if col_name == "Nº conta":
                selecionadas = st.sidebar.multiselect(f"Selecione {label}:", opcoes)
                if selecionadas:
                    df_filtrado = df_filtrado[df_filtrado[col_name].astype(str).isin(selecionadas)]
            else:
                selecionado = st.sidebar.selectbox(f"Selecione {label}:", opcoes)
                if selecionado != "Todos":
                    df_filtrado = df_filtrado[df_filtrado[col_name].astype(str) == str(selecionado)]
    except Exception as e:
        st.sidebar.error(f"Erro no filtro {label}: {str(e)}")

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
        
        st.altair_chart(chart, use_container_width=True)
        
    except Exception as e:
        st.error(f"Erro ao criar gráfico: {str(e)}")

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

# Área administrativa simplificada
try:
    if eh_administrador():
        st.sidebar.markdown("---")
        st.sidebar.subheader("👑 Área Administrativa")
        st.sidebar.info("Sistema administrativo ativo")
except:
    pass

# Footer
st.markdown("---")
if auth_working:
    st.success("✅ Dashboard KE5Z funcionando com autenticação")
else:
    st.info("ℹ️ Dashboard KE5Z funcionando em modo aberto")

if is_cloud:
    st.info("☁️ Executando no Streamlit Cloud")
else:
    st.info("💻 Executando localmente")

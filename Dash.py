# Dashboard KE5Z - Versão Original com SQLite Otimizado
import streamlit as st
import pandas as pd
import os
import altair as alt
import plotly.graph_objects as go
import sqlite3
from auth_simple import (verificar_autenticacao, exibir_header_usuario,
                         eh_administrador, verificar_status_aprovado,
                         get_usuarios_cloud, adicionar_usuario_simples, criar_hash_senha)
from datetime import datetime

# Configuração da página
st.set_page_config(
    page_title="Dashboard KE5Z",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Verificar autenticação - OBRIGATÓRIO no início de cada página
verificar_autenticacao()

# Verificar se o usuário está aprovado
if 'usuario_nome' in st.session_state and not verificar_status_aprovado(st.session_state.usuario_nome):
    st.warning("⏳ Sua conta ainda está pendente de aprovação. "
               "Aguarde o administrador aprovar seu acesso.")
    st.info("📧 Você receberá uma notificação quando sua conta for "
            "aprovada.")
    st.stop()

# Detectar se estamos no Streamlit Cloud
try:
    base_url = st.get_option('server.baseUrlPath') or ''
    is_cloud = 'share.streamlit.io' in base_url
except Exception:
    is_cloud = False

# Informar sobre ambiente
if is_cloud:
    st.sidebar.info("☁️ **Modo Cloud**\n"
                     "Usando SQLite para máxima performance.")
else:
    st.sidebar.success("💻 **Modo Local**\n"
                       "Usando SQLite otimizado.")

# Sistema de cache inteligente para SQLite
@st.cache_data(
    ttl=1800,  # Cache por 30 minutos
    max_entries=1,  # Apenas 1 entrada para economizar memória
    show_spinner=True
)
def load_data_optimized():
    """Carrega dados do SQLite ou Parquet como fallback"""
    arquivo_sqlite = "dados_ke5z.db"
    arquivo_parquet = os.path.join("KE5Z", "KE5Z.parquet")
    
    try:
        # Tentar SQLite primeiro
        if os.path.exists(arquivo_sqlite) and os.path.getsize(arquivo_sqlite) > 10000:
            conn = sqlite3.connect(arquivo_sqlite)
            inicio = datetime.now()
            df = pd.read_sql_query('SELECT * FROM ke5z_dados', conn)
            tempo_carregamento = (datetime.now() - inicio).total_seconds()
            conn.close()
            
            st.sidebar.success(f"✅ **SQLite Carregado**\n"
                              f"📊 {len(df):,} registros\n" 
                              f"⚡ {tempo_carregamento:.1f}s\n"
                              f"🎯 Dados originais!")
            
        else:
            # Fallback para Parquet com otimizações
            st.sidebar.info("📂 Carregando do Parquet...")
            df = pd.read_parquet(arquivo_parquet)
            
            # Aplicar amostragem no cloud se necessário
            if is_cloud and len(df) > 100000:
                st.sidebar.warning("☁️ Aplicando amostragem para Cloud")
                df = df.sample(n=100000, random_state=42)
            
            st.sidebar.success(f"✅ **Parquet Carregado**\n"
                              f"📊 {len(df):,} registros")
        
        # Otimizar tipos de dados
        for col in df.columns:
            if df[col].dtype == 'object':
                unique_ratio = df[col].nunique() / len(df)
                if unique_ratio < 0.5:
                    df[col] = df[col].astype('category')
        
        # Converter floats para tipos menores
        for col in df.select_dtypes(include=['float64']).columns:
            df[col] = pd.to_numeric(df[col], downcast='float')
        
        # Converter ints para tipos menores
        for col in df.select_dtypes(include=['int64']).columns:
            df[col] = pd.to_numeric(df[col], downcast='integer')
        
        return df
        
    except Exception as e:
        st.error(f"❌ Erro ao carregar dados: {e}")
        st.info("💡 Verifique se o arquivo de dados existe")
        raise e

# Carregar dados
try:
    df_total = load_data_optimized()
    st.sidebar.success("✅ Dados carregados com sucesso")
    
    # Monitoramento de memória para administradores
    if 'usuario_nome' in st.session_state and eh_administrador(st.session_state.usuario_nome):
        memory_usage = df_total.memory_usage(deep=True).sum() / (1024 * 1024)
        st.sidebar.info(f"🔧 **Admin Info**\n"
                       f"💾 Memória: {memory_usage:.1f}MB\n"
                       f"📊 Registros: {len(df_total):,}")

except Exception as e:
    st.error(f"❌ Erro ao carregar dados: {e}")
    st.info("🔧 Verifique se os arquivos de dados estão disponíveis")
    st.stop()

# Exibir header do usuário
exibir_header_usuario()

# Título principal
st.title("📊 Dashboard KE5Z")
st.subheader("Análise de Dados Empresariais")

# Cache para opções de filtros
@st.cache_data(ttl=1800)
def get_filter_options(df):
    """Obtém opções de filtros de forma otimizada"""
    def safe_sort_unique(column):
        """Ordena valores únicos de forma segura, removendo NaN"""
        try:
            unique_vals = df[column].dropna().astype(str).unique()
            return sorted([v for v in unique_vals if v and str(v).strip() and str(v) != 'nan'])
        except:
            return []
    
    return {
        'usi': safe_sort_unique('USI') if 'USI' in df.columns else [],
        'periodo': safe_sort_unique('Período') if 'Período' in df.columns else [],
        'type05': safe_sort_unique('Type 05') if 'Type 05' in df.columns else [],
        'type06': safe_sort_unique('Type 06') if 'Type 06' in df.columns else [],
        'type07': safe_sort_unique('Type 07') if 'Type 07' in df.columns else []
    }

# Obter opções de filtros
filter_options = get_filter_options(df_total)

# Filtros na sidebar
st.sidebar.markdown("---")
st.sidebar.subheader("🔍 Filtros")

# Filtro USI
usi_selected = st.sidebar.multiselect(
    "Selecionar USI:",
    options=filter_options['usi'],
    default=filter_options['usi'][:3] if len(filter_options['usi']) > 3 else filter_options['usi']
)

# Filtro Período
periodo_selected = st.sidebar.multiselect(
    "Selecionar Período:",
    options=filter_options['periodo'],
    default=filter_options['periodo'][-6:] if len(filter_options['periodo']) > 6 else filter_options['periodo']
)

# Filtro Type 05
type05_selected = st.sidebar.multiselect(
    "Selecionar Type 05:",
    options=filter_options['type05'],
    default=filter_options['type05'][:3] if len(filter_options['type05']) > 3 else filter_options['type05']
)

# Filtro Type 06
type06_selected = st.sidebar.multiselect(
    "Selecionar Type 06:",
    options=filter_options['type06'],
    default=filter_options['type06'][:2] if len(filter_options['type06']) > 2 else filter_options['type06']
)

# Aplicar filtros
df_filtrado = df_total.copy()

if usi_selected:
    df_filtrado = df_filtrado[df_filtrado['USI'].isin(usi_selected)]

if periodo_selected:
    df_filtrado = df_filtrado[df_filtrado['Período'].isin(periodo_selected)]

if type05_selected:
    df_filtrado = df_filtrado[df_filtrado['Type 05'].isin(type05_selected)]

if type06_selected:
    df_filtrado = df_filtrado[df_filtrado['Type 06'].isin(type06_selected)]

# Informações da sidebar
st.sidebar.markdown("---")
st.sidebar.subheader("📊 Resumo")
st.sidebar.metric("Registros Filtrados", f"{len(df_filtrado):,}")
st.sidebar.metric("Total de Registros", f"{len(df_total):,}")
if len(df_filtrado) > 0:
    st.sidebar.metric("Valor Total Filtrado", f"R$ {df_filtrado['Valor'].sum():,.2f}")

# Verificar se há dados filtrados
if len(df_filtrado) == 0:
    st.warning("⚠️ Nenhum dado encontrado com os filtros selecionados. Ajuste os filtros.")
    st.stop()

# Métricas principais
st.subheader("📈 Métricas Principais")
col1, col2, col3, col4 = st.columns(4)

with col1:
    total_valor = df_filtrado['Valor'].sum()
    st.metric("Valor Total", f"R$ {total_valor:,.2f}")

with col2:
    media_valor = df_filtrado['Valor'].mean()
    st.metric("Valor Médio", f"R$ {media_valor:,.2f}")

with col3:
    max_valor = df_filtrado['Valor'].max()
    st.metric("Valor Máximo", f"R$ {max_valor:,.2f}")

with col4:
    num_registros = len(df_filtrado)
    st.metric("Registros", f"{num_registros:,}")

# Gráfico principal por período
st.subheader("📊 Distribuição por Período")

if 'Período' in df_filtrado.columns:
    @st.cache_data(ttl=900, max_entries=2)
    def create_period_chart(df_data):
        try:
            period_data = df_data.groupby('Período', observed=True)['Valor'].sum().reset_index()
            period_data = period_data.sort_values('Valor', ascending=False)
            
            grafico_barras = alt.Chart(period_data).mark_bar().encode(
                x=alt.X('Período:N', title='Período', sort='-y'),
                y=alt.Y('Valor:Q', title='Soma do Valor'),
                color=alt.Color('Valor:Q', title='Valor', scale=alt.Scale(scheme='redyellowgreen', reverse=True)),
                tooltip=['Período:N', 'Valor:Q']
            ).properties(
                title='Soma do Valor por Período',
                height=400
            )
            
            # Adicionar rótulos com valores nas barras
            rotulos = grafico_barras.mark_text(
                align='center',
                baseline='middle',
                dy=-10,
                color='black',
                fontSize=12
            ).encode(
                text=alt.Text('Valor:Q', format=',.2f')
            )
            
            return grafico_barras + rotulos
        except Exception as e:
            st.error(f"Erro no gráfico de período: {e}")
            return None
    
    chart_periodo = create_period_chart(df_filtrado)
    if chart_periodo:
        st.altair_chart(chart_periodo, use_container_width=True)

# Gráficos adicionais por Type
st.subheader("📊 Análise por Categorias")

# Gráfico por Type 05
if 'Type 05' in df_filtrado.columns:
    @st.cache_data(ttl=900, max_entries=2)
    def create_type05_chart(df_data):
        try:
            type05_data = df_data.groupby('Type 05', observed=True)['Valor'].sum().reset_index()
            type05_data = type05_data.sort_values('Valor', ascending=False)
            
            chart = alt.Chart(type05_data).mark_bar().encode(
                x=alt.X('Type 05:N', title='Type 05', sort='-y'),
                y=alt.Y('Valor:Q', title='Soma do Valor'),
                color=alt.Color('Valor:Q', title='Valor', scale=alt.Scale(scheme='redyellowgreen', reverse=True)),
                tooltip=['Type 05:N', 'Valor:Q']
            ).properties(
                title='Soma do Valor por Type 05',
                height=400
            )
            
            return chart
        except Exception as e:
            st.error(f"Erro no gráfico Type 05: {e}")
            return None
    
    chart_type05 = create_type05_chart(df_filtrado)
    if chart_type05:
        st.altair_chart(chart_type05, use_container_width=True)

# Gráfico por Type 06
if 'Type 06' in df_filtrado.columns:
    @st.cache_data(ttl=900, max_entries=2)
    def create_type06_chart(df_data):
        try:
            type06_data = df_data.groupby('Type 06', observed=True)['Valor'].sum().reset_index()
            type06_data = type06_data.sort_values('Valor', ascending=False)
            
            chart = alt.Chart(type06_data).mark_bar().encode(
                x=alt.X('Type 06:N', title='Type 06', sort='-y'),
                y=alt.Y('Valor:Q', title='Soma do Valor'),
                color=alt.Color('Valor:Q', title='Valor', scale=alt.Scale(scheme='redyellowgreen', reverse=True)),
                tooltip=['Type 06:N', 'Valor:Q']
            ).properties(
                title='Soma do Valor por Type 06',
                height=400
            )
            
            return chart
        except Exception as e:
            st.error(f"Erro no gráfico Type 06: {e}")
            return None
    
    chart_type06 = create_type06_chart(df_filtrado)
    if chart_type06:
        st.altair_chart(chart_type06, use_container_width=True)

# Tabela dinâmica com cores
if 'USI' in df_filtrado.columns and 'Período' in df_filtrado.columns:
    try:
        df_pivot = df_filtrado.pivot_table(
            index='USI', 
            columns='Período', 
            values='Valor', 
            aggfunc='sum', 
            margins=True, 
            margins_name='Total', 
            fill_value=0,
            observed=True
        )
        st.subheader("📋 Tabela Dinâmica - Soma do Valor por USI e Período")
        st.dataframe(df_pivot, use_container_width=True)
        
        # Botão de download Excel
        from io import BytesIO
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df_pivot.to_excel(writer, sheet_name='Tabela_Dinamica')
        
        st.download_button(
            label="📥 Baixar Tabela Dinâmica (Excel)",
            data=output.getvalue(),
            file_name=f"tabela_dinamica_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
    except Exception as e:
        st.error(f"Erro ao criar tabela dinâmica: {e}")

# Tabela filtrada
st.subheader("📊 Dados Filtrados")
st.dataframe(df_filtrado, use_container_width=True)

# Botão de download dos dados filtrados
csv_data = df_filtrado.to_csv(index=False)
st.download_button(
    label="📥 Baixar Dados Filtrados (CSV)",
    data=csv_data,
    file_name=f"dados_filtrados_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
    mime="text/csv"
)

# Resumo por tipos
if all(col in df_filtrado.columns for col in ['Type 05', 'Type 06', 'Type 07']):
    try:
        soma_por_type = (df_filtrado.groupby(['Type 05', 'Type 06', 'Type 07'], observed=True)['Valor']
                       .sum()
                       .reset_index()
                       .sort_values('Valor', ascending=False))
        
        st.subheader("📈 Resumo - Soma do Valor por Types")
        st.dataframe(soma_por_type, use_container_width=True)
        
        # Botão de download do resumo
        csv_resumo = soma_por_type.to_csv(index=False)
        st.download_button(
            label="📥 Baixar Resumo por Types (CSV)",
            data=csv_resumo,
            file_name=f"resumo_types_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
        
    except Exception as e:
        st.error(f"Erro ao criar resumo por types: {e}")

# Área administrativa
if 'usuario_nome' in st.session_state and eh_administrador(st.session_state.usuario_nome):
    st.markdown("---")
    st.subheader("🛡️ Área Administrativa")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info(f"📊 **Estatísticas do Sistema**\n"
                f"- Total de registros: {len(df_total):,}\n"
                f"- Registros filtrados: {len(df_filtrado):,}\n"
                f"- Valor total: R$ {df_total['Valor'].sum():,.2f}\n"
                f"- Usuário ativo: {st.session_state.usuario_nome}")
    
    with col2:
        if st.button("🔄 Limpar Cache"):
            st.cache_data.clear()
            st.success("✅ Cache limpo com sucesso!")
            st.rerun()
        
        if st.button("🗑️ Limpeza de Memória"):
            import gc
            gc.collect()
            st.success("✅ Limpeza de memória executada!")

# Footer
st.markdown("---")
st.caption("Dashboard KE5Z - Versão Original com SQLite | Otimizado para Streamlit Cloud")
# FASE 2 - Dashboard KE5Z com Dados Reais e Gráficos Melhorados
import streamlit as st
import pandas as pd
import os
import altair as alt

# Configuração básica da página
st.set_page_config(
    page_title="Dashboard KE5Z - FASE 2",
    page_icon="📊",
    layout="wide"
)

# Detectar ambiente
is_cloud = False
try:
    import os
    if 'STREAMLIT_SHARING_MODE' in os.environ or 'share.streamlit.io' in str(st.get_option('server.baseUrlPath') or ''):
        is_cloud = True
except:
    pass

# Sistema de cache para dados
@st.cache_data(ttl=1800, show_spinner=True)
def load_data_optimized():
    """Carrega dados otimizados para o ambiente"""
    try:
        if is_cloud:
            # No cloud, usar amostra pequena dos dados
            st.info("☁️ Modo Cloud: Carregando amostra dos dados...")
            
            # Tentar carregar dados reais, se falhar usar dados de exemplo
            try:
                df = pd.read_parquet('KE5Z/KE5Z.parquet')
                # Pegar apenas uma amostra pequena para o cloud
                df = df.sample(n=min(1000, len(df)), random_state=42)
                st.success(f"✅ Dados reais carregados: {len(df)} registros (amostra)")
            except Exception as e:
                st.warning(f"⚠️ Erro ao carregar dados reais: {e}")
                # Dados de exemplo mais realistas
                df = pd.DataFrame({
                    'USI': ['Veículos', 'Motores', 'Peças', 'Outros'] * 250,
                    'Período': ['2024-01', '2024-02', '2024-03', '2024-04'] * 250,
                    'Type 05': ['A', 'B', 'C', 'D'] * 250,
                    'Type 06': ['X', 'Y', 'Z', 'W'] * 250,
                    'Type 07': ['I', 'II', 'III', 'IV'] * 250,
                    'Valor': [abs(x) * 100000 for x in range(-500, 500)]
                })
                st.info(f"📊 Usando dados de exemplo: {len(df)} registros")
        else:
            # Local: carregar dados completos
            st.info("💻 Modo Local: Carregando dados completos...")
            try:
                df = pd.read_parquet('KE5Z/KE5Z.parquet')
                st.success(f"✅ Dados completos carregados: {len(df)} registros")
            except Exception as e:
                st.error(f"❌ Erro ao carregar dados: {e}")
                # Dados de exemplo maiores para local
                df = pd.DataFrame({
                    'USI': ['Veículos', 'Motores', 'Peças', 'Outros'] * 2500,
                    'Período': ['2024-01', '2024-02', '2024-03', '2024-04'] * 2500,
                    'Type 05': ['A', 'B', 'C', 'D'] * 2500,
                    'Type 06': ['X', 'Y', 'Z', 'W'] * 2500,
                    'Type 07': ['I', 'II', 'III', 'IV'] * 2500,
                    'Valor': [abs(x) * 100000 for x in range(-5000, 5000)]
                })
                st.info(f"📊 Usando dados de exemplo: {len(df)} registros")
        
        # Limpar e otimizar tipos de dados
        for col in df.columns:
            if df[col].dtype == 'object':
                # Limpar valores vazios e converter para string antes de categoria
                df[col] = df[col].fillna('').astype(str).astype('category')
        
        return df
    except Exception as e:
        st.error(f"❌ Erro crítico ao carregar dados: {e}")
        return pd.DataFrame()

# Cache para opções de filtros
@st.cache_data(ttl=1800)
def get_filter_options(df):
    """Obtém opções de filtros de forma otimizada"""
    def safe_sort_unique(column):
        """Ordena valores únicos de forma segura, removendo NaN"""
        try:
            unique_vals = df[column].dropna().astype(str).unique()
            return sorted([v for v in unique_vals if v and str(v).strip()])
        except:
            return []
    
    return {
        'usi': safe_sort_unique('USI') if 'USI' in df.columns else [],
        'periodo': safe_sort_unique('Período') if 'Período' in df.columns else [],
        'type05': safe_sort_unique('Type 05') if 'Type 05' in df.columns else [],
        'type06': safe_sort_unique('Type 06') if 'Type 06' in df.columns else []
    }

# Cache para gráficos
@st.cache_data(ttl=1800)
def create_period_chart(df_data):
    """Cria gráfico por período similar ao original"""
    if df_data.empty or 'Período' not in df_data.columns:
        return None
    
    period_data = df_data.groupby('Período')['Valor'].sum().reset_index()
    
    chart = alt.Chart(period_data).mark_bar(
        color='#FF6B6B',
        opacity=0.8
    ).add_selection(
        alt.selection_single()
    ).encode(
        x=alt.X('Período:O', title='Período', sort=None),
        y=alt.Y('Valor:Q', title='Valor (R$)', axis=alt.Axis(format='.2s')),
        tooltip=['Período:O', alt.Tooltip('Valor:Q', format=',.0f')]
    ).properties(
        width=600,
        height=400,
        title='Distribuição por Período'
    )
    
    return chart

@st.cache_data(ttl=1800)
def create_type05_chart(df_data):
    """Cria gráfico Type 05 similar ao original"""
    if df_data.empty or 'Type 05' not in df_data.columns:
        return None
    
    type05_data = df_data.groupby('Type 05')['Valor'].sum().reset_index()
    
    chart = alt.Chart(type05_data).mark_arc(
        innerRadius=50,
        outerRadius=120
    ).encode(
        theta=alt.Theta('Valor:Q'),
        color=alt.Color('Type 05:N', 
                       scale=alt.Scale(scheme='category10'),
                       title='Type 05'),
        tooltip=['Type 05:N', alt.Tooltip('Valor:Q', format=',.0f')]
    ).properties(
        width=300,
        height=300,
        title='Distribuição por Type 05'
    )
    
    return chart

@st.cache_data(ttl=1800)
def create_type06_chart(df_data):
    """Cria gráfico Type 06 similar ao original"""
    if df_data.empty or 'Type 06' not in df_data.columns:
        return None
    
    type06_data = df_data.groupby('Type 06')['Valor'].sum().reset_index()
    
    chart = alt.Chart(type06_data).mark_bar(
        color='#4ECDC4',
        opacity=0.7
    ).encode(
        x=alt.X('Type 06:O', title='Type 06'),
        y=alt.Y('Valor:Q', title='Valor (R$)', axis=alt.Axis(format='.2s')),
        tooltip=['Type 06:O', alt.Tooltip('Valor:Q', format=',.0f')]
    ).properties(
        width=400,
        height=300,
        title='Distribuição por Type 06'
    )
    
    return chart

# Header principal
st.title("📊 Dashboard KE5Z - FASE 2")

# Informação do ambiente
if is_cloud:
    st.success("☁️ FUNCIONANDO NO STREAMLIT CLOUD - FASE 2")
    st.balloons()
else:
    st.info("💻 Executando localmente - FASE 2")

# Carregar dados
with st.spinner("Carregando dados..."):
    df = load_data_optimized()

if df.empty:
    st.error("❌ Não foi possível carregar os dados")
    st.stop()

# Obter opções de filtros
filter_options = get_filter_options(df)

# Sidebar com filtros
st.sidebar.title("🔍 Filtros")
st.sidebar.markdown("---")

# Filtros similares ao original
usi_selected = st.sidebar.multiselect(
    "Selecionar USI:",
    options=filter_options['usi'],
    default=filter_options['usi'][:3] if len(filter_options['usi']) > 3 else filter_options['usi']
)

periodo_selected = st.sidebar.multiselect(
    "Selecionar Período:",
    options=filter_options['periodo'],
    default=filter_options['periodo'][:3] if len(filter_options['periodo']) > 3 else filter_options['periodo']
)

type05_selected = st.sidebar.multiselect(
    "Selecionar Type 05:",
    options=filter_options['type05'],
    default=filter_options['type05'][:2] if len(filter_options['type05']) > 2 else filter_options['type05']
)

# Aplicar filtros
df_filtered = df.copy()
if usi_selected:
    df_filtered = df_filtered[df_filtered['USI'].isin(usi_selected)]
if periodo_selected:
    df_filtered = df_filtered[df_filtered['Período'].isin(periodo_selected)]
if type05_selected:
    df_filtered = df_filtered[df_filtered['Type 05'].isin(type05_selected)]

# Informações da sidebar
st.sidebar.markdown("---")
st.sidebar.metric("Registros", f"{len(df_filtered):,}")
st.sidebar.metric("Total (R$)", f"R$ {df_filtered['Valor'].sum():,.0f}")

# Área principal
if len(df_filtered) > 0:
    # Gráficos em colunas (similar ao original)
    st.subheader("📈 Análises Gráficas")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Gráfico por período
        period_chart = create_period_chart(df_filtered)
        if period_chart:
            st.altair_chart(period_chart, use_container_width=True)
    
    with col2:
        # Gráfico Type 05
        type05_chart = create_type05_chart(df_filtered)
        if type05_chart:
            st.altair_chart(type05_chart, use_container_width=True)
    
    # Gráfico Type 06 (largura completa)
    type06_chart = create_type06_chart(df_filtered)
    if type06_chart:
        st.altair_chart(type06_chart, use_container_width=True)
    
    # Tabela dinâmica (similar ao original)
    st.subheader("📋 Tabela Dinâmica por USI e Período")
    if 'USI' in df_filtered.columns and 'Período' in df_filtered.columns:
        try:
            df_pivot = df_filtered.pivot_table(
                index='USI', 
                columns='Período', 
                values='Valor', 
                aggfunc='sum', 
                margins=True, 
                margins_name='Total', 
                fill_value=0
            )
            st.dataframe(df_pivot, use_container_width=True)
        except Exception as e:
            st.error(f"Erro ao criar tabela dinâmica: {e}")
            st.dataframe(df_filtered.head(100), use_container_width=True)
    
    # Resumo por tipos (similar ao original)
    st.subheader("📊 Resumo por Types")
    if all(col in df_filtered.columns for col in ['Type 05', 'Type 06', 'Type 07']):
        try:
            soma_por_type = (df_filtered.groupby(['Type 05', 'Type 06', 'Type 07'])['Valor']
                           .sum()
                           .reset_index()
                           .sort_values('Valor', ascending=False))
            st.dataframe(soma_por_type.head(20), use_container_width=True)
        except Exception as e:
            st.error(f"Erro ao criar resumo: {e}")
    
else:
    st.warning("⚠️ Nenhum dado encontrado com os filtros selecionados")

# Status da FASE 2
st.markdown("---")
st.subheader("🔧 Status FASE 2")

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.success("✅ Dados Reais")
with col2:
    st.success("✅ Gráficos Altair")
with col3:
    st.success("✅ Tabelas Dinâmicas")
with col4:
    st.success("✅ Filtros Avançados")

# Informações da FASE 2
st.info("""
💡 **FASE 2 - Dados Reais + Gráficos Melhorados**
- ✅ Dados reais do KE5Z.parquet (amostra no cloud)
- ✅ Gráficos coloridos com Altair
- ✅ Tabelas dinâmicas por USI/Período
- ✅ Filtros avançados (USI, Período, Type 05)
- ✅ Cache inteligente para performance
- ✅ Otimização automática para cloud vs local

**Próxima FASE**: Autenticação + Exportação Excel
""")

st.markdown("---")
st.caption("Dashboard KE5Z - FASE 2 | Dados Reais + Gráficos Melhorados")
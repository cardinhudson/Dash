import streamlit as st
import pandas as pd
import os
import altair as alt
import plotly.graph_objects as go
from datetime import datetime
import re

# Importar sistema de autenticação
try:
    from auth_simple import (verificar_autenticacao, exibir_header_usuario,
                             eh_administrador, verificar_status_aprovado)
    auth_available = True
except ImportError:
    auth_available = False

# Configuração da página
st.set_page_config(
    page_title="IA Unificada - KE5Z",
    page_icon="🤖",
    layout="wide"
)

# Verificar autenticação se disponível
if auth_available:
    verificar_autenticacao()
    
    # Verificar se o usuário está aprovado
    if 'usuario_nome' in st.session_state and not verificar_status_aprovado(st.session_state.usuario_nome):
        st.warning("⏳ Sua conta ainda está pendente de aprovação.")
        st.stop()
    
    # Exibir header do usuário
    exibir_header_usuario()

# Detectar ambiente
try:
    base_url = st.get_option('server.baseUrlPath') or ''
    is_cloud = 'share.streamlit.io' in base_url
except Exception:
    is_cloud = False

st.title("🤖 IA Unificada - Análise Avançada")
st.subheader("Assistente Inteligente e Análise Waterfall")

# Carregar dados (mesmo sistema do dashboard principal)
@st.cache_data(ttl=1800, show_spinner=True)
def load_data():
    """Carrega dados para análise IA"""
    arquivo_sqlite = "dados_ke5z.db"
    arquivo_parquet = os.path.join("KE5Z", "KE5Z.parquet")
    
    try:
        # Tentar SQLite primeiro
        if os.path.exists(arquivo_sqlite) and os.path.getsize(arquivo_sqlite) > 10000:
            import sqlite3
            conn = sqlite3.connect(arquivo_sqlite)
            df = pd.read_sql_query('SELECT * FROM ke5z_dados', conn)
            conn.close()
            st.sidebar.success("✅ Dados SQLite carregados")
        else:
            # Fallback para Parquet
            df = pd.read_parquet(arquivo_parquet)
            
            # Amostragem no cloud
            if is_cloud and len(df) > 50000:
                df = df.sample(n=50000, random_state=42)
                st.sidebar.info("☁️ Amostra carregada para cloud")
            else:
                st.sidebar.success("✅ Dados Parquet carregados")
        
        return df
        
    except Exception as e:
        st.error(f"❌ Erro ao carregar dados: {e}")
        return pd.DataFrame()

# Carregar dados
df = load_data()

if df.empty:
    st.error("❌ Não foi possível carregar os dados")
    st.stop()

# Filtros básicos
st.sidebar.subheader("🔍 Filtros IA")

# Filtro por período (últimos meses)
periodos_disponiveis = sorted([x for x in df['Período'].unique() if pd.notna(x)])
periodo_selected = st.sidebar.multiselect(
    "Períodos para análise:",
    options=periodos_disponiveis,
    default=periodos_disponiveis[-6:] if len(periodos_disponiveis) > 6 else periodos_disponiveis
)

# Filtro USI
usi_disponiveis = sorted([x for x in df['USI'].unique() if pd.notna(x) and str(x).strip()])
usi_selected = st.sidebar.multiselect(
    "USIs para análise:",
    options=usi_disponiveis,
    default=usi_disponiveis[:3] if len(usi_disponiveis) > 3 else usi_disponiveis
)

# Aplicar filtros
df_filtered = df.copy()
if periodo_selected:
    df_filtered = df_filtered[df_filtered['Período'].isin(periodo_selected)]
if usi_selected:
    df_filtered = df_filtered[df_filtered['USI'].isin(usi_selected)]

# Informações dos dados filtrados
st.sidebar.metric("Registros", f"{len(df_filtered):,}")
st.sidebar.metric("Valor Total", f"R$ {df_filtered['Valor'].sum():,.2f}")

# Seção 1: Assistente IA (Simulado)
st.subheader("🧠 Assistente Inteligente")

# Análises automáticas
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 📊 Insights Automáticos")
    
    if len(df_filtered) > 0:
        # Análise de tendência
        if len(periodo_selected) > 1:
            tendencia_data = df_filtered.groupby('Período')['Valor'].sum().sort_index()
            if len(tendencia_data) > 1:
                variacao = ((tendencia_data.iloc[-1] - tendencia_data.iloc[0]) / tendencia_data.iloc[0]) * 100
                if variacao > 5:
                    st.success(f"📈 **Tendência Positiva**: Crescimento de {variacao:.1f}%")
                elif variacao < -5:
                    st.warning(f"📉 **Tendência Negativa**: Queda de {abs(variacao):.1f}%")
                else:
                    st.info(f"📊 **Tendência Estável**: Variação de {variacao:.1f}%")
        
        # Análise de USI dominante
        usi_valores = df_filtered.groupby('USI')['Valor'].sum().sort_values(ascending=False)
        if len(usi_valores) > 0:
            usi_dominante = usi_valores.index[0]
            participacao = (usi_valores.iloc[0] / usi_valores.sum()) * 100
            st.info(f"🏆 **USI Dominante**: {usi_dominante} ({participacao:.1f}%)")
        
        # Análise de sazonalidade
        if 'Período' in df_filtered.columns:
            try:
                df_temp = df_filtered.copy()
                df_temp['Mes'] = df_temp['Período'].str[-2:]
                sazonalidade = df_temp.groupby('Mes')['Valor'].mean().sort_values(ascending=False)
                mes_forte = sazonalidade.index[0]
                st.info(f"📅 **Sazonalidade**: Mês {mes_forte} é o mais forte")
            except:
                pass

with col2:
    st.markdown("### 🎯 Recomendações")
    
    recomendacoes = [
        "💡 Analisar fatores que influenciam a USI dominante",
        "📈 Investigar oportunidades de crescimento nas USIs menores", 
        "🔍 Monitorar tendências mensais para planejamento",
        "⚡ Otimizar processos nos períodos de maior volume",
        "📊 Implementar alertas para variações significativas"
    ]
    
    for rec in recomendacoes:
        st.write(rec)

# Seção 2: Análise Waterfall
st.subheader("🌊 Análise Waterfall")

if len(df_filtered) > 0 and len(periodo_selected) > 1:
    # Preparar dados para waterfall
    waterfall_data = df_filtered.groupby('Período')['Valor'].sum().sort_index()
    
    if len(waterfall_data) > 1:
        # Criar dados do waterfall
        periodos = list(waterfall_data.index)
        valores = list(waterfall_data.values)
        
        # Calcular variações
        inicial = valores[0]
        variacoes = [valores[i] - valores[i-1] for i in range(1, len(valores))]
        final = valores[-1]
        
        # Criar gráfico waterfall com Plotly
        fig = go.Figure()
        
        # Valor inicial
        fig.add_trace(go.Waterfall(
            name="Waterfall",
            orientation="v",
            measure=["absolute"] + ["relative"] * len(variacoes) + ["total"],
            x=[periodos[0]] + periodos[1:] + ["Total"],
            y=[inicial] + variacoes + [final],
            text=[f"R$ {inicial:,.0f}"] + [f"R$ {v:+,.0f}" for v in variacoes] + [f"R$ {final:,.0f}"],
            textposition="outside",
            connector={"line": {"color": "rgb(63, 63, 63)"}},
            increasing={"marker": {"color": "green"}},
            decreasing={"marker": {"color": "red"}},
            totals={"marker": {"color": "blue"}}
        ))
        
        fig.update_layout(
            title="Análise Waterfall - Evolução por Período",
            showlegend=False,
            height=500,
            xaxis_title="Período",
            yaxis_title="Valor (R$)"
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Análise da waterfall
        st.markdown("### 📈 Análise da Evolução")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Valor Inicial", f"R$ {inicial:,.2f}")
        with col2:
            variacao_total = final - inicial
            st.metric("Variação Total", f"R$ {variacao_total:+,.2f}")
        with col3:
            st.metric("Valor Final", f"R$ {final:,.2f}")

# Seção 3: Análise Detalhada por Categorias
st.subheader("📊 Análise por Categorias")

if 'Type 05' in df_filtered.columns:
    col1, col2 = st.columns(2)
    
    with col1:
        # Gráfico Type 05
        type05_data = df_filtered.groupby('Type 05')['Valor'].sum().sort_values(ascending=False).head(10)
        
        if len(type05_data) > 0:
            chart = alt.Chart(pd.DataFrame({
                'Type 05': type05_data.index,
                'Valor': type05_data.values
            })).mark_bar(color='steelblue').encode(
                x=alt.X('Valor:Q', title='Valor (R$)'),
                y=alt.Y('Type 05:N', title='Type 05', sort='-x'),
                tooltip=['Type 05:N', 'Valor:Q']
            ).properties(
                title='Top 10 - Type 05',
                height=300
            )
            
            st.altair_chart(chart, use_container_width=True)
    
    with col2:
        # Tabela com percentuais
        if len(type05_data) > 0:
            type05_df = pd.DataFrame({
                'Type 05': type05_data.index,
                'Valor': type05_data.values,
                'Percentual': (type05_data.values / type05_data.sum() * 100)
            })
            
            type05_df['Valor'] = type05_df['Valor'].apply(lambda x: f"R$ {x:,.2f}")
            type05_df['Percentual'] = type05_df['Percentual'].apply(lambda x: f"{x:.1f}%")
            
            st.dataframe(type05_df, use_container_width=True)

# Exportação de dados
st.subheader("📥 Exportação")

col1, col2 = st.columns(2)

with col1:
    # Download dados filtrados
    csv_data = df_filtered.to_csv(index=False)
    st.download_button(
        label="📥 Baixar Dados Filtrados (CSV)",
        data=csv_data,
        file_name=f"ia_analise_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )

with col2:
    # Download análise waterfall
    if len(df_filtered) > 0 and len(periodo_selected) > 1:
        waterfall_summary = pd.DataFrame({
            'Período': periodos,
            'Valor': valores,
            'Variação': [0] + variacoes
        })
        
        csv_waterfall = waterfall_summary.to_csv(index=False)
        st.download_button(
            label="📥 Baixar Análise Waterfall (CSV)",
            data=csv_waterfall,
            file_name=f"waterfall_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )

# Footer
st.markdown("---")
st.caption("IA Unificada - Análise Inteligente de Dados KE5Z")
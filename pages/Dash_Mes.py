# %%
import streamlit as st
import pandas as pd
import os
import altair as alt
import plotly.graph_objects as go
import sys
from datetime import datetime

# Adicionar diretório pai ao path para importar auth_simple
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from auth_simple import (verificar_autenticacao, exibir_header_usuario,
                         eh_administrador, verificar_status_aprovado, is_modo_cloud, get_modo_operacao)

# Configuração otimizada da página para melhor performance
st.set_page_config(
    page_title="Dashboard KE5Z - Mês",
    page_icon="📅",
    layout="wide",
    initial_sidebar_state="auto"
)

# Configurações para otimizar conexão e performance
if 'connection_optimized' not in st.session_state:
    # Configurar pandas para usar menos memória
    pd.set_option('display.max_columns', 50)
    pd.set_option('display.max_rows', 1000)
    
    # Marcar como otimizado
    st.session_state.connection_optimized = True

# Verificar autenticação - OBRIGATÓRIO no início de cada página
verificar_autenticacao()

# Verificar se o usuário está aprovado
if 'usuario_nome' in st.session_state and not verificar_status_aprovado(st.session_state.usuario_nome):
    st.warning("⏳ Sua conta ainda está pendente de aprovação. "
               "Aguarde o administrador aprovar seu acesso.")
    st.info("📧 Você receberá uma notificação quando sua conta for "
            "aprovada.")
    st.stop()

# Usar modo selecionado no login (substitui detecção automática)
is_cloud = is_modo_cloud()

# Informar sobre modo selecionado (COMPACTO)
modo_atual = get_modo_operacao()
if modo_atual == 'cloud':
    st.sidebar.success("☁️ **Modo Cloud** (Mensal)")
else:
    st.sidebar.success("💻 **Modo Completo** (Mensal)")


# Sistema de cache inteligente para otimização de memória e conexão
@st.cache_data(
    ttl=3600,
    max_entries=3,  # Cache para os 3 tipos de arquivo
    show_spinner=True,
    persist="disk"
)
def load_data_optimized(arquivo_tipo="completo"):
    """Carrega dados com otimização inteligente de memória
    
    Args:
        arquivo_tipo: "completo", "main" (sem Others), "others", ou "main_filtered"
    """
    
    # Definir qual arquivo carregar
    arquivos_disponiveis = {
        "completo": "KE5Z.parquet",
        "main": "KE5Z_main.parquet", 
        "others": "KE5Z_others.parquet",
        "main_filtered": "KE5Z.parquet"  # Usa arquivo completo mas filtra Others
    }
    
    nome_arquivo = arquivos_disponiveis.get(arquivo_tipo, "KE5Z.parquet")
    arquivo_parquet = os.path.join("KE5Z", nome_arquivo)
    
    try:
        if not os.path.exists(arquivo_parquet):
            # Se arquivo específico não existe, tentar arquivo completo
            if arquivo_tipo != "completo":
                st.warning(f"⚠️ Arquivo {nome_arquivo} não encontrado, carregando dados completos...")
                return load_data_optimized("completo")
            raise FileNotFoundError(f"Arquivo não encontrado: {arquivo_parquet}")
        
        # Verificar tamanho do arquivo
        file_size_mb = os.path.getsize(arquivo_parquet) / (1024 * 1024)
        
        # Carregar dados
        df = pd.read_parquet(arquivo_parquet)
        
        # Aplicar filtro especial para main_filtered (cloud mode)
        if arquivo_tipo == "main_filtered" and 'USI' in df.columns:
            # Filtrar para remover Others, simulando arquivo main
            df = df[df['USI'] != 'Others'].copy()
            st.sidebar.info(f"🔄 Filtro aplicado: {len(df):,} registros (Others removidos)")
        
        # Otimizar tipos de dados para economizar memória (sem alterar conteúdo)
        original_memory = df.memory_usage(deep=True).sum() / (1024 * 1024)
        
        for col in df.columns:
            if df[col].dtype == 'object':
                unique_ratio = df[col].nunique() / len(df)
                if unique_ratio < 0.5:  # Menos de 50% valores únicos
                    df[col] = df[col].astype('category')
        
        # Converter floats para tipos menores
        for col in df.select_dtypes(include=['float64']).columns:
            df[col] = pd.to_numeric(df[col], downcast='float')

        
        # Converter ints para tipos menores
        for col in df.select_dtypes(include=['int64']).columns:
            df[col] = pd.to_numeric(df[col], downcast='integer')
        
        # Calcular economia de memória
        optimized_memory = df.memory_usage(deep=True).sum() / (1024 * 1024)
        saved_memory = original_memory - optimized_memory
        
        if saved_memory > 1:  # Economia significativa
            st.sidebar.success(f"💾 Memória economizada: {saved_memory:.1f}MB")
        
        return df
        
    except Exception as e:
        raise e

# Interface para seleção de dados (COMPACTO)
st.sidebar.markdown("---")
st.sidebar.markdown("**🗂️ Dados**")

# Verificar quais arquivos estão disponíveis
arquivos_status = {}
for tipo, nome in [("completo", "KE5Z.parquet"), ("main", "KE5Z_main.parquet"), ("others", "KE5Z_others.parquet")]:
    caminho = os.path.join("KE5Z", nome)
    arquivos_status[tipo] = os.path.exists(caminho)

# Opções disponíveis baseadas nos arquivos existentes
opcoes_dados = []

# Priorizar arquivos otimizados sempre
if arquivos_status.get("main", False):
    opcoes_dados.append(("📊 Dados Principais (sem Others)", "main"))
if arquivos_status.get("others", False):
    opcoes_dados.append(("📋 Apenas Others", "others"))

# Dados completos: APENAS no modo local E quando não há arquivos otimizados
if not is_cloud and arquivos_status.get("completo", False):
    # Se há arquivos otimizados, mostrar completo como opção adicional
    # Se não há arquivos otimizados, será a única opção
    opcoes_dados.append(("📁 Dados Completos", "completo"))

# Tratamento especial para Streamlit Cloud
if is_cloud:
    if not opcoes_dados:  # Não há arquivos otimizados no cloud
        if arquivos_status.get("completo", False):
            # No cloud, usar arquivo completo como "dados principais" temporariamente
            # mas filtrar internamente para remover Others
            opcoes_dados = [("📊 Dados Otimizados (filtrados)", "main_filtered")]
            st.sidebar.warning("⚠️ **Modo Cloud Temporário**\nUsando arquivo completo com filtro interno.\nPara melhor performance, gere arquivos separados localmente.")
        else:
            st.error("❌ **Erro no Streamlit Cloud**: Nenhum arquivo de dados encontrado!")
            st.error("Faça upload dos arquivos parquet para o repositório.")
            st.stop()

# Fallback para modo local sem arquivos otimizados
if not opcoes_dados and not is_cloud:
    if arquivos_status.get("completo", False):
        opcoes_dados = [("📁 Dados Completos", "completo")]
    else:
        st.error("❌ **Erro**: Nenhum arquivo de dados encontrado!")
        st.error("Execute a extração de dados para gerar os arquivos necessários.")
        st.stop()

# Widget de seleção com prioridade para dados principais
def get_default_index():
    """Retorna o índice padrão priorizando dados principais"""
    opcoes_values = [op[1] for op in opcoes_dados]
    
    # Prioridade: main > main_filtered > others > completo
    if "main" in opcoes_values:
        return opcoes_values.index("main")
    elif "main_filtered" in opcoes_values:
        return opcoes_values.index("main_filtered")
    elif "others" in opcoes_values:
        return opcoes_values.index("others")
    else:
        return 0  # Primeiro disponível

opcao_selecionada = st.sidebar.selectbox(
    "Escolha o conjunto de dados:",
    options=[op[1] for op in opcoes_dados],
    format_func=lambda x: next(op[0] for op in opcoes_dados if op[1] == x),
    index=get_default_index()  # Priorizar dados principais
)

# Mostrar informações sobre a seleção
if opcao_selecionada == "main":
    info_msg = "🎯 **Dados Otimizados**\nCarregando apenas dados principais (USI ≠ 'Others')\nMelhor performance para análises gerais."
    if is_cloud:
        info_msg += "\n\n☁️ **Modo Cloud**: Arquivo otimizado para melhor performance."
    st.sidebar.info(info_msg)
elif opcao_selecionada == "main_filtered":
    st.sidebar.info("🎯 **Dados Otimizados (Filtrados)**\n"
                   "Carregando dados principais com filtro interno\n"
                   "☁️ **Modo Cloud**: Otimização automática aplicada")
elif opcao_selecionada == "others":
    info_msg = "🔍 **Dados Others**\nCarregando apenas registros USI = 'Others'\nPara análise específica de Others."
    if is_cloud:
        info_msg += "\n\n☁️ **Modo Cloud**: Arquivo otimizado para melhor performance."
    st.sidebar.info(info_msg)
else:
    st.sidebar.info("📊 **Dados Completos**\n"
                   "Todos os registros incluindo Others\n"
                   "💻 **Disponível apenas no modo local**")

# Mostrar aviso sobre otimização no cloud
if is_cloud:
    st.sidebar.success("⚡ **Otimização Ativa**\n"
                      "Dashboard otimizado para um mês por vez!")

# Carregar dados
try:
    df_total = load_data_optimized(opcao_selecionada)
    st.sidebar.success("✅ Dados carregados com sucesso")
    
    # Log informativo
    if not is_cloud:
        st.sidebar.info(f"📊 {len(df_total)} registros carregados")
        
except FileNotFoundError:
    st.error("❌ Arquivo de dados não encontrado!")
    st.error(f"🔍 Procurando por arquivos na pasta `KE5Z/`")
    st.info("💡 **Soluções:**")
    st.info("1. Verifique se os arquivos parquet estão na pasta `KE5Z/`")
    st.info("2. Execute a extração de dados localmente")
    st.info("3. Faça commit dos arquivos no repositório")
    
    if is_cloud:
        st.warning("☁️ **No Streamlit Cloud:** Certifique-se que os arquivos "
                  "foram enviados para o repositório")
    
    st.stop()
    
except Exception as e:
    st.error(f"❌ Erro ao carregar dados: {str(e)}")
    st.info("🔧 **Possíveis causas:**")
    st.info("• Arquivo corrompido ou formato inválido")
    st.info("• Problema de permissões")
    st.info("• Arquivo muito grande")
    
    if is_cloud:
        st.info("☁️ **No Cloud:** Verifique se o arquivo tem menos de 100MB")
    
    st.stop()

# Filtrar o df_total com a coluna 'USI' que não seja nula (incluindo 'Others')
df_total = df_total[df_total['USI'].notna()]

# Header com informações do usuário e botão de logout
col1, col2, col3 = st.columns([2, 1, 1])
with col1:
    st.title("📅 Dashboard KE5Z - Análise Mensal")
    st.caption("Dashboard otimizado para análise de um mês por vez")
    
with col2:
    if st.button("🔄 Recarregar Dados"):
        st.cache_data.clear()
        st.rerun()

with col3:
    exibir_header_usuario()

st.markdown("---")

# ============= FILTRO PRINCIPAL: SELEÇÃO DE MÊS =============
st.sidebar.markdown("---")
st.sidebar.subheader("📅 Filtro Principal - Mês")

# Mapear números para nomes dos meses (GLOBAL)
meses_nomes = {
    1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril',
    5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
    9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
}

# Função auxiliar para obter nome do mês de forma segura
def get_nome_mes_seguro(mes_selecionado):
    """Retorna o nome do mês de forma segura, lidando com 'Todos' e valores inválidos"""
    try:
        if isinstance(mes_selecionado, str) and mes_selecionado == "Todos":
            return "Todos os Meses"
        mes_num = int(mes_selecionado)
        return meses_nomes.get(mes_num, f'Mês {mes_selecionado}')
    except (ValueError, TypeError):
        return f'Período {mes_selecionado}'

# Verificar se existe coluna 'Mes' ou 'Período' para filtro mensal
coluna_mes = None
if 'Mes' in df_total.columns:
    coluna_mes = 'Mes'
elif 'Período' in df_total.columns:
    coluna_mes = 'Período'

if coluna_mes:
    meses_disponiveis = sorted(df_total[coluna_mes].dropna().unique())
    
    # Seleção de mês único
    mes_selecionado = st.sidebar.selectbox(
        "🎯 Selecione UM mês para análise:",
        options=meses_disponiveis,
        format_func=lambda x: f"{get_nome_mes_seguro(x)} ({x})",
        index=len(meses_disponiveis)-1 if meses_disponiveis else 0  # Último mês disponível
    )
    
    # Aplicar filtro de mês
    df_mes = df_total[df_total[coluna_mes] == mes_selecionado].copy()
    
    st.sidebar.success(f"📊 **{get_nome_mes_seguro(mes_selecionado)}**")
    st.sidebar.info(f"📈 {len(df_mes):,} registros neste mês")
    
    # Mostrar economia de dados
    reducao_percentual = (1 - len(df_mes) / len(df_total)) * 100
    st.sidebar.success(f"⚡ Redução: {reducao_percentual:.1f}% dos dados")
    
else:
    st.sidebar.error("❌ Coluna 'Mes' ou 'Período' não encontrada nos dados!")
    df_mes = df_total.copy()
    mes_selecionado = "Todos"

# Filtros (COMPACTO)
st.sidebar.markdown("---")
st.sidebar.markdown("**🔍 Filtros**")

# Filtro USI
if 'USI' in df_mes.columns:
    usi_opcoes = ["Todos"] + sorted(df_mes['USI'].dropna().unique().tolist())
    usi_selecionada = st.sidebar.multiselect(
        "Selecione USI:",
        usi_opcoes,
        default=["Todos"]
    )
    
    if "Todos" not in usi_selecionada and usi_selecionada:
        df_mes = df_mes[df_mes['USI'].isin(usi_selecionada)]

# Cache para opções de filtros (otimização de performance)
@st.cache_data(ttl=1800, max_entries=3)
def get_filter_options(df, column_name):
    """Obtém opções de filtro com cache para melhor performance"""
    if column_name in df.columns:
        return ["Todos"] + sorted(df[column_name].dropna().astype(str).unique().tolist())
    return ["Todos"]

# Filtro 3: Centro cst (com cache otimizado)
if 'Centro cst' in df_mes.columns:
    centro_cst_opcoes = get_filter_options(df_mes, 'Centro cst')
    centro_cst_selecionado = st.sidebar.selectbox("Selecione o Centro cst:", centro_cst_opcoes)
    if centro_cst_selecionado != "Todos":
        df_mes = df_mes[df_mes['Centro cst'].astype(str) == str(centro_cst_selecionado)]

# Filtro 4: Conta contábil (com cache otimizado)
if 'Nº conta' in df_mes.columns:
    conta_contabil_opcoes = get_filter_options(df_mes, 'Nº conta')[1:]  # Remove "Todos" para multiselect
    conta_contabil_selecionadas = st.sidebar.multiselect("Selecione a Conta contábil:", conta_contabil_opcoes)
    if conta_contabil_selecionadas:
        df_mes = df_mes[df_mes['Nº conta'].astype(str).isin(conta_contabil_selecionadas)]

# Filtros principais (com cache otimizado)
filtros_principais = [
    ("Type 05", "Type 05", "multiselect"),
    ("Type 06", "Type 06", "multiselect"), 
    ("Type 07", "Type 07", "multiselect"),
    ("Fornecedor", "Fornecedor", "multiselect"),
    ("Fornec.", "Fornec.", "multiselect"),
    ("Tipo", "Tipo", "multiselect")
]

for col_name, label, widget_type in filtros_principais:
    if col_name in df_mes.columns:
        opcoes = get_filter_options(df_mes, col_name)
        if widget_type == "multiselect":
            selecionadas = st.sidebar.multiselect(f"Selecione o {label}:", opcoes, default=["Todos"])
            if selecionadas and "Todos" not in selecionadas:
                df_mes = df_mes[df_mes[col_name].astype(str).isin(selecionadas)]

# Filtros avançados (expansível)
with st.sidebar.expander("🔍 Filtros Avançados"):
    filtros_avancados = [
        ("Oficina", "Oficina", "multiselect"),
        ("Usuário", "Usuário", "multiselect"),
        ("Denominação", "Denominação", "multiselect"),
        ("Dt.lçto.", "Data Lançamento", "multiselect")
    ]
    
    for col_name, label, widget_type in filtros_avancados:
        if col_name in df_mes.columns:
            opcoes = get_filter_options(df_mes, col_name)
            # Limitar opções para melhor performance
            if len(opcoes) > 101:  # 100 + "Todos"
                opcoes = opcoes[:101]
                st.caption(f"⚠️ {label}: Limitado a 100 opções para performance")
            
            if widget_type == "multiselect":
                selecionadas = st.multiselect(f"Selecione o {label}:", opcoes, default=["Todos"])
                if selecionadas and "Todos" not in selecionadas:
                    df_mes = df_mes[df_mes[col_name].astype(str).isin(selecionadas)]

# Resumo (COMPACTO)
st.sidebar.markdown("---")
st.sidebar.markdown("**📊 Resumo**")
st.sidebar.write(f"**Linhas:** {df_mes.shape[0]:,}")
if 'Valor' in df_mes.columns:
    st.sidebar.write(f"**Total:** R$ {df_mes['Valor'].sum():,.2f}")

# ============= DASHBOARD PRINCIPAL =============
if not df_mes.empty:
    # Métricas principais
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_valor = df_mes['Valor'].sum()
        st.metric(
            "💰 Valor Total", 
            f"R$ {total_valor:,.2f}",
            help=f"Soma total dos valores para {get_nome_mes_seguro(mes_selecionado)}"
        )
    
    with col2:
        total_registros = len(df_mes)
        st.metric(
            "📊 Registros", 
            f"{total_registros:,}",
            help="Número total de registros no período selecionado"
        )
    
    with col3:
        if 'USI' in df_mes.columns:
            usi_count = df_mes['USI'].nunique()
            st.metric(
                "🏭 USIs Ativas", 
                f"{usi_count}",
                help="Número de USIs diferentes no período"
            )
    
    with col4:
        if 'Fornecedor' in df_mes.columns:
            fornecedor_count = df_mes['Fornecedor'].nunique()
            st.metric(
                "🏢 Fornecedores", 
                f"{fornecedor_count}",
                help="Número de fornecedores únicos"
            )
    
    st.markdown("---")
    
    # Layout em abas para organizar visualizações
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Gráficos Principais", "📈 Análise USI", "🔍 Detalhes", "📋 Tabela"])
    
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            # Gráfico por Type 05
            if 'Type 05' in df_mes.columns and 'Valor' in df_mes.columns:
                st.subheader("📊 Análise por Type 05")
                type05_data = df_mes.groupby('Type 05')['Valor'].sum().sort_values(ascending=False)
                
                fig_type05 = go.Figure(data=[
                    go.Bar(
                        x=type05_data.index,
                        y=type05_data.values,
                        marker_color='lightblue'
                    )
                ])
                fig_type05.update_layout(
                    title=f"Valores por Type 05 - {get_nome_mes_seguro(mes_selecionado)}",
                    xaxis_title="Type 05",
                    yaxis_title="Valor (R$)",
                    height=400
                )
                st.plotly_chart(fig_type05, use_container_width=True)
        
        with col2:
            # Gráfico por Type 06
            if 'Type 06' in df_mes.columns and 'Valor' in df_mes.columns:
                st.subheader("📈 Análise por Type 06")
                type06_data = df_mes.groupby('Type 06')['Valor'].sum().sort_values(ascending=False)
                
                fig_type06 = go.Figure(data=[
                    go.Bar(
                        x=type06_data.index,
                        y=type06_data.values,
                        marker_color='lightcoral'
                    )
                ])
                fig_type06.update_layout(
                    title=f"Valores por Type 06 - {get_nome_mes_seguro(mes_selecionado)}",
                    xaxis_title="Type 06",
                    yaxis_title="Valor (R$)",
                    height=400
                )
                st.plotly_chart(fig_type06, use_container_width=True)
    
    with tab2:
        # Análise detalhada por USI
        if 'USI' in df_mes.columns and 'Valor' in df_mes.columns:
            st.subheader("🏭 Análise Detalhada por USI")
            
            usi_data = df_mes.groupby('USI')['Valor'].agg(['sum', 'count', 'mean']).round(2)
            usi_data.columns = ['Valor Total', 'Quantidade', 'Valor Médio']
            usi_data = usi_data.sort_values('Valor Total', ascending=False)
            
            # Gráfico de pizza para USI
            fig_usi = go.Figure(data=[
                go.Pie(
                    labels=usi_data.index,
                    values=usi_data['Valor Total'],
                    hole=0.4
                )
            ])
            fig_usi.update_layout(
                title=f"Distribuição por USI - {get_nome_mes_seguro(mes_selecionado)}",
                height=500
            )
            st.plotly_chart(fig_usi, use_container_width=True)
            
            # Tabela detalhada
            st.subheader("📊 Resumo por USI")
            st.dataframe(usi_data, use_container_width=True)
    
    with tab3:
        # Análises adicionais
        st.subheader("🔍 Análises Detalhadas")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Top 10 Fornecedores
            if 'Fornecedor' in df_mes.columns:
                st.subheader("🏢 Top 10 Fornecedores")
                top_fornecedores = (df_mes.groupby('Fornecedor')['Valor']
                                  .sum()
                                  .sort_values(ascending=False)
                                  .head(10))
                
                fig_fornecedores = go.Figure(data=[
                    go.Bar(
                        y=top_fornecedores.index,
                        x=top_fornecedores.values,
                        orientation='h',
                        marker_color='lightgreen'
                    )
                ])
                fig_fornecedores.update_layout(
                    title="Top 10 Fornecedores por Valor",
                    height=400
                )
                st.plotly_chart(fig_fornecedores, use_container_width=True)
        
        with col2:
            # Estatísticas gerais
            st.subheader("📈 Estatísticas do Mês")
            
            if 'Valor' in df_mes.columns:
                stats = df_mes['Valor'].describe()
                
                stats_df = pd.DataFrame({
                    'Estatística': ['Média', 'Mediana', 'Desvio Padrão', 'Mínimo', 'Máximo'],
                    'Valor': [
                        f"R$ {stats['mean']:,.2f}",
                        f"R$ {stats['50%']:,.2f}",
                        f"R$ {stats['std']:,.2f}",
                        f"R$ {stats['min']:,.2f}",
                        f"R$ {stats['max']:,.2f}"
                    ]
                })
                
                st.dataframe(stats_df, use_container_width=True, hide_index=True)
    
    with tab4:
        # Tabela completa filtrada
        st.subheader(f"📋 Dados Completos - {get_nome_mes_seguro(mes_selecionado)}")
        
        # Opção para limitar número de linhas mostradas
        max_rows = st.selectbox("Máximo de linhas para exibir:", [100, 500, 1000, 5000], index=1)
        
        if len(df_mes) > max_rows:
            st.info(f"📊 Mostrando primeiras {max_rows:,} linhas de {len(df_mes):,} registros totais")
            st.dataframe(df_mes.head(max_rows), use_container_width=True)
        else:
            st.dataframe(df_mes, use_container_width=True)
        
        # Botão para download
        if st.button("📥 Preparar Download Excel"):
            with st.spinner("Preparando arquivo..."):
                # Criar arquivo Excel otimizado
                output_filename = f"KE5Z_{get_nome_mes_seguro(mes_selecionado).replace(' ', '_')}.xlsx"
                
                # Salvar temporariamente
                df_mes.to_excel(output_filename, index=False)
                
                # Ler como bytes para download
                with open(output_filename, 'rb') as f:
                    bytes_data = f.read()
                
                st.download_button(
                    label="📥 Download Excel",
                    data=bytes_data,
                    file_name=output_filename,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
                
                # Remover arquivo temporário
                os.remove(output_filename)

else:
    st.warning("⚠️ Nenhum dado encontrado para os filtros selecionados.")
    st.info("💡 Tente ajustar os filtros ou verificar se os dados estão disponíveis.")

# Rodapé com informações
st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    if coluna_mes:
        st.info(f"📅 **Mês Selecionado**: {get_nome_mes_seguro(mes_selecionado)}")

with col2:
    st.info(f"📊 **Registros Filtrados**: {len(df_mes):,}")

with col3:
    if 'Valor' in df_mes.columns:
        st.info(f"💰 **Valor Total**: R$ {df_mes['Valor'].sum():,.2f}")

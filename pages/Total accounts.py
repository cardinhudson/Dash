import streamlit as st
import pandas as pd
import os
import sys

# Adicionar diretório pai ao path para importar auth_simple
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from auth_simple import (verificar_autenticacao, exibir_header_usuario,
                  verificar_status_aprovado, is_modo_cloud, get_modo_operacao)

# Configuração da página
st.set_page_config(
    page_title="Total Accounts - Dashboard KE5Z",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="auto"
)

# Verificar autenticação - OBRIGATÓRIO no início de cada página
verificar_autenticacao()

# Verificar se o usuário está aprovado
if ('usuario_nome' in st.session_state and 
    not verificar_status_aprovado(st.session_state.usuario_nome)):
    st.warning("⏳ Sua conta ainda está pendente de aprovação. "
               "Aguarde o administrador aprovar seu acesso.")
    st.info("📧 Você receberá uma notificação quando sua conta for "
            "aprovada.")
    st.stop()

# Header com informações do usuário
col1, col2, col3 = st.columns([2, 1, 1])
with col1:
    st.title("📊 Total Accounts - Centro de Lucro 02S")
    st.subheader("Somatório de todas as contas do centro de lucro 02S, "
                 "exceto as contas D_B")

# Exibir header do usuário
exibir_header_usuario()

st.markdown("---")

# Conteúdo da nova página
st.write("Esta página contém o somatório de todas as contas do centro de "
         "lucro 02S, exceto as contas D_B!")

# Usar modo selecionado no login (substitui detecção automática)
is_cloud = is_modo_cloud()

# Informar sobre modo selecionado
modo_atual = get_modo_operacao()
if modo_atual == 'cloud':
    st.sidebar.info("☁️ **Modo Cloud (Otimizado)**\n"
                     "Dados otimizados para melhor performance.")
else:
    st.sidebar.success("💻 **Modo Completo**\n"
                       "Acesso a todos os conjuntos de dados.")

# Interface para seleção de dados
st.sidebar.markdown("---")
st.sidebar.subheader("🗂️ Seleção de Dados")

# Verificar quais arquivos estão disponíveis
arquivos_status = {}
for tipo, nome in [("completo", "KE5Z.parquet"), ("main", "KE5Z_main.parquet"), ("others", "KE5Z_others.parquet")]:
    caminho = os.path.join("KE5Z", nome)
    arquivos_status[tipo] = os.path.exists(caminho)

# Opções disponíveis baseadas nos arquivos existentes
opcoes_dados = []
if arquivos_status.get("main", False):
    opcoes_dados.append(("📊 Dados Principais (sem Others)", "main"))
if arquivos_status.get("others", False):
    opcoes_dados.append(("📋 Apenas Others", "others"))

# No Streamlit Cloud, NÃO mostrar dados completos para evitar sobrecarga
if not is_cloud and arquivos_status.get("completo", False):
    opcoes_dados.append(("📁 Dados Completos", "completo"))

# Se não há arquivos separados, usar apenas completo (modo local)
if not opcoes_dados:
    if is_cloud:
        st.error("❌ **Erro no Streamlit Cloud**: Arquivos otimizados não encontrados!")
        st.error("Execute a extração localmente para gerar `KE5Z_main.parquet` e `KE5Z_others.parquet`")
        st.stop()
    else:
        opcoes_dados = [("📁 Dados Completos", "completo")]

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
                      "Usando arquivos separados para melhor performance no Cloud!")

@st.cache_data(ttl=3600, max_entries=3, persist="disk", show_spinner=True)
def load_data_optimized(arquivo_tipo="completo"):
    """Carrega dados com otimização inteligente de memória - WATERFALL OTIMIZADO"""
    
    # PRIORIDADE 1: Tentar arquivo waterfall otimizado (68% menor + Nº conta!)
    arquivo_waterfall = os.path.join("KE5Z", "KE5Z_waterfall.parquet")
    if os.path.exists(arquivo_waterfall):
        try:
            df = pd.read_parquet(arquivo_waterfall)
            # Aplicar filtro se necessário baseado no tipo solicitado
            if arquivo_tipo == "main" and 'USI' in df.columns:
                df = df[df['USI'] != 'Others'].copy()
            elif arquivo_tipo == "others" and 'USI' in df.columns:
                df = df[df['USI'] == 'Others'].copy()
            # arquivo_tipo "completo" usa todos os dados do waterfall
            
            st.sidebar.success("⚡ **WATERFALL OTIMIZADO**\nUsando arquivo 68% menor + Nº conta!")
            return df
        except Exception as e:
            st.sidebar.warning(f"⚠️ Erro no arquivo waterfall: {str(e)}")
    
    # FALLBACK: Usar arquivos originais se waterfall não estiver disponível
    arquivos_disponiveis = {
        "completo": "KE5Z.parquet",
        "main": "KE5Z_main.parquet", 
        "others": "KE5Z_others.parquet"
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
        
        df = pd.read_parquet(arquivo_parquet)
        
        # Otimização de memória (sem alterar valores)
        try:
            for col in df.columns:
                if df[col].dtype == 'object':
                    # Converter para category quando adequado
                    unique_ratio = (df[col].nunique(dropna=True) / max(1, len(df)))
                    if unique_ratio < 0.5:
                        df[col] = df[col].astype('category')
            for col in df.select_dtypes(include=['float64']).columns:
                df[col] = pd.to_numeric(df[col], downcast='float')
            for col in df.select_dtypes(include=['int64']).columns:
                df[col] = pd.to_numeric(df[col], downcast='integer')
        except Exception:
            pass
        return df
        
    except Exception as e:
        st.error(f"❌ Erro ao carregar dados: {str(e)}")
        st.stop()

# Ler o arquivo parquet com otimização
try:
    df_principal = load_data_optimized(opcao_selecionada)
    st.sidebar.success("✅ Dados carregados com sucesso")
    if not is_cloud:
        st.sidebar.info(f"📊 {len(df_principal)} registros carregados")
except Exception as e:
    st.error(f"❌ Erro ao carregar dados: {str(e)}")
    st.stop()

# Filtros para o DataFrame (padronizados com página principal)
st.sidebar.title("Filtros")

# Filtro 1: USINA
usina_opcoes = ["Todos"] + sorted(df_principal['USI'].dropna().astype(str).unique().tolist()) if 'USI' in df_principal.columns else ["Todos"]
default_usina = ["Veículos"] if "Veículos" in usina_opcoes else ["Todos"]
usina_selecionada = st.sidebar.multiselect("Selecione a USINA:", usina_opcoes, default=default_usina)

# Filtrar o DataFrame com base na USI
if "Todos" in usina_selecionada or not usina_selecionada:
    df_filtrado = df_principal.copy()
else:
    df_filtrado = df_principal[df_principal['USI'].astype(str).isin(usina_selecionada)]

# Filtro 2: Período
periodo_opcoes = ["Todos"] + sorted(df_filtrado['Período'].dropna().astype(str).unique().tolist()) if 'Período' in df_filtrado.columns else ["Todos"]
periodo_selecionado = st.sidebar.selectbox("Selecione o Período:", periodo_opcoes)
if periodo_selecionado != "Todos":
    df_filtrado = df_filtrado[df_filtrado['Período'].astype(str) == str(periodo_selecionado)]

# Filtro 3: Centro cst
if 'Centro cst' in df_filtrado.columns:
    centro_cst_opcoes = ["Todos"] + sorted(df_filtrado['Centro cst'].dropna().astype(str).unique().tolist())
    centro_cst_selecionado = st.sidebar.selectbox("Selecione o Centro cst:", centro_cst_opcoes)
    if centro_cst_selecionado != "Todos":
        df_filtrado = df_filtrado[df_filtrado['Centro cst'].astype(str) == str(centro_cst_selecionado)]

# Filtro 4: Conta contábil
if 'Nº conta' in df_filtrado.columns:
    conta_contabil_opcoes = sorted(df_filtrado['Nº conta'].dropna().astype(str).unique().tolist())
    conta_contabil_selecionadas = st.sidebar.multiselect("Selecione a Conta contábil:", conta_contabil_opcoes)
    if conta_contabil_selecionadas:
        df_filtrado = df_filtrado[df_filtrado['Nº conta'].astype(str).isin(conta_contabil_selecionadas)]

# Cache para opções de filtros (otimização de performance)
@st.cache_data(ttl=1800, max_entries=3)
def get_filter_options(df, column_name):
    """Obtém opções de filtro com cache para melhor performance"""
    if column_name in df.columns:
        return ["Todos"] + sorted(df[column_name].dropna().astype(str).unique().tolist())
    return ["Todos"]

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
    if col_name in df_filtrado.columns:
        opcoes = get_filter_options(df_filtrado, col_name)
        if widget_type == "multiselect":
            selecionadas = st.sidebar.multiselect(f"Selecione o {label}:", opcoes, default=["Todos"])
            if selecionadas and "Todos" not in selecionadas:
                df_filtrado = df_filtrado[df_filtrado[col_name].astype(str).isin(selecionadas)]

# Filtros avançados (expansível)
with st.sidebar.expander("🔍 Filtros Avançados"):
    filtros_avancados = [
        ("Nº conta", "Conta Contábil", "multiselect"),
        ("Centro cst", "Centro de Custo", "multiselect"),
        ("Oficina", "Oficina", "multiselect"),
        ("Usuário", "Usuário", "multiselect"),
        ("Denominação", "Denominação", "multiselect"),
        ("Dt.lçto.", "Data Lançamento", "multiselect")
    ]
    
    for col_name, label, widget_type in filtros_avancados:
        if col_name in df_filtrado.columns:
            opcoes = get_filter_options(df_filtrado, col_name)
            # Limitar opções para melhor performance
            if len(opcoes) > 101:  # 100 + "Todos"
                opcoes = opcoes[:101]
                st.caption(f"⚠️ {label}: Limitado a 100 opções para performance")
            
            if widget_type == "multiselect":
                selecionadas = st.multiselect(f"Selecione o {label}:", opcoes, default=["Todos"])
                if selecionadas and "Todos" not in selecionadas:
                    df_filtrado = df_filtrado[df_filtrado[col_name].astype(str).isin(selecionadas)]

##################################################################################################

# Título da nova página
st.title("Total SAP KE5Z - Todas as USINAS")

# Verificar se a coluna USI existe
if 'USI' not in df_filtrado.columns:
    st.error("❌ **Coluna 'USI' não encontrada nos dados!**")
    st.warning("⚠️ **Possíveis causas:**")
    st.write("1. Os dados não foram extraídos corretamente")
    st.write("2. O merge com dados SAPIENS não foi realizado")
    st.write("3. O arquivo KE5Z.parquet precisa ser regenerado")
    
    st.info("💡 **Soluções:**")
    st.write("- Execute a **Extração de Dados** na página correspondente")
    st.write("- Certifique-se de que o arquivo 'Dados SAPIENS.xlsx' existe")
    st.write("- Verifique se os merges estão funcionando corretamente")
    
    st.subheader("📋 Colunas disponíveis nos dados:")
    colunas_disponiveis = sorted(df_filtrado.columns.tolist())
    for i, col in enumerate(colunas_disponiveis, 1):
        st.write(f"{i}. {col}")
    
    st.stop()

# Criar uma tabela dinâmica (pivot table) para somar os valores por 'USI', incluindo campos desta coluna vazio ou NAN, a coluna por 'Período' e uma linha total
tabela_somada = df_filtrado.pivot_table(index='USI', columns='Período', values='Valor', aggfunc='sum', fill_value=0, margins=True, margins_name='Total')
# Exibir a tabela somada na página com os numeros formatados como moeda brasileira
tabela_somada = tabela_somada.style.format("R$ {:,.2f}", decimal=",",thousands=".")
st.dataframe(tabela_somada)


##################################################################################################
# Título da nova página
st.title("Total SAP KE5Z - Todas as contas")
# Criar uma tabela dinâmica (pivot table) para somar os valores por 'Nº conta' incluindo a coluna por 'Período'
tabela_somada = df_filtrado.pivot_table(index='Nº conta', columns='Período', values='Valor', aggfunc='sum', fill_value=0, margins=True, margins_name='Total')

# Exibir a tabela somada na página com os numeros formatados como moeda brasileira
tabela_somada = tabela_somada.style.format("R$ {:,.2f}", decimal=",",thousands=".")
st.dataframe(tabela_somada)

# ============= GRÁFICOS MÊS A MÊS (MESMO PADRÃO DO DASH PRINCIPAL) =============
st.markdown("---")
st.subheader("📊 Análise Gráfica Mês a Mês")

# Gráfico principal por Período (mesmo padrão do Dash.py)
@st.cache_data(ttl=900, max_entries=2)
def create_period_chart_total_accounts(df_data):
    """Cria gráfico de período otimizado - MESMO PADRÃO DO DASH PRINCIPAL"""
    try:
        chart_data = df_data.groupby('Período')['Valor'].sum().reset_index()
        
        import altair as alt
        grafico_barras = alt.Chart(chart_data).mark_bar().encode(
            x=alt.X('Período:N', title='Período'),
            y=alt.Y('Valor:Q', title='Soma do Valor'),
            color=alt.Color('Valor:Q', title='Valor', scale=alt.Scale(scheme='redyellowgreen', reverse=True)),
            tooltip=['Período:N', 'Valor:Q']
        ).properties(
            title='Total Accounts - Soma do Valor por Período',
            height=400
        )
        
        return grafico_barras
    except Exception as e:
        st.error(f"Erro ao criar gráfico de período: {e}")
        return None

# Gráfico por Type 05 (mesmo padrão do Dash.py)
@st.cache_data(ttl=900, max_entries=2)
def create_type05_chart_total_accounts(df_data):
    """Cria gráfico Type 05 otimizado - MESMO PADRÃO DO DASH PRINCIPAL"""
    try:
        type05_data = df_data.groupby('Type 05')['Valor'].sum().reset_index()
        type05_data = type05_data.sort_values('Valor', ascending=False)
        
        import altair as alt
        chart = alt.Chart(type05_data).mark_bar().encode(
            x=alt.X('Type 05:N', title='Type 05', sort='-y'),
            y=alt.Y('Valor:Q', title='Soma do Valor'),
            color=alt.Color('Valor:Q', title='Valor', scale=alt.Scale(scheme='redyellowgreen', reverse=True)),
            tooltip=['Type 05:N', 'Valor:Q']
        ).properties(
            title='Total Accounts - Soma do Valor por Type 05',
            height=400
        )
        
        return chart
    except Exception as e:
        st.error(f"Erro no gráfico Type 05: {e}")
        return None

# Gráfico por Type 06 (mesmo padrão do Dash.py)
@st.cache_data(ttl=900, max_entries=2)
def create_type06_chart_total_accounts(df_data):
    """Cria gráfico Type 06 otimizado - MESMO PADRÃO DO DASH PRINCIPAL"""
    try:
        type06_data = df_data.groupby('Type 06')['Valor'].sum().reset_index()
        type06_data = type06_data.sort_values('Valor', ascending=False)
        
        import altair as alt
        chart = alt.Chart(type06_data).mark_bar().encode(
            x=alt.X('Type 06:N', title='Type 06', sort='-y'),
            y=alt.Y('Valor:Q', title='Soma do Valor'),
            color=alt.Color('Valor:Q', title='Valor', scale=alt.Scale(scheme='redyellowgreen', reverse=True)),
            tooltip=['Type 06:N', 'Valor:Q']
        ).properties(
            title='Total Accounts - Soma do Valor por Type 06',
            height=400
        )
        
        return chart
    except Exception as e:
        st.error(f"Erro no gráfico Type 06: {e}")
        return None

# Exibir gráficos em colunas
col1, col2 = st.columns(2)

with col1:
    # Gráfico principal por período
    grafico_periodo = create_period_chart_total_accounts(df_filtrado)
    if grafico_periodo:
        # Adicionar rótulos com valores nas barras
        import altair as alt
        rotulos = grafico_periodo.mark_text(
            align='center',
            baseline='middle',
            dy=-10,
            color='black',
            fontSize=12
        ).encode(
            text=alt.Text('Valor:Q', format=',.2f')
        )
        
        grafico_completo = grafico_periodo + rotulos
        st.altair_chart(grafico_completo, use_container_width=True)

with col2:
    # Gráfico por Type 05
    if 'Type 05' in df_filtrado.columns:
        chart_type05 = create_type05_chart_total_accounts(df_filtrado)
        if chart_type05:
            st.altair_chart(chart_type05, use_container_width=True)

# Segunda linha de gráficos
col3, col4 = st.columns(2)

with col3:
    # Gráfico por Type 06
    if 'Type 06' in df_filtrado.columns:
        chart_type06 = create_type06_chart_total_accounts(df_filtrado)
        if chart_type06:
            st.altair_chart(chart_type06, use_container_width=True)

with col4:
    # Gráfico por USI (adicional)
    if 'USI' in df_filtrado.columns:
        @st.cache_data(ttl=900, max_entries=2)
        def create_usi_chart_total_accounts(df_data):
            """Cria gráfico USI otimizado"""
            try:
                usi_data = df_data.groupby('USI')['Valor'].sum().reset_index()
                usi_data = usi_data.sort_values('Valor', ascending=False)
                
                import altair as alt
                chart = alt.Chart(usi_data).mark_bar().encode(
                    x=alt.X('USI:N', title='USI', sort='-y'),
                    y=alt.Y('Valor:Q', title='Soma do Valor'),
                    color=alt.Color('Valor:Q', title='Valor', scale=alt.Scale(scheme='redyellowgreen', reverse=True)),
                    tooltip=['USI:N', 'Valor:Q']
                ).properties(
                    title='Total Accounts - Soma do Valor por USI',
                    height=400
                )
                
                return chart
            except Exception as e:
                st.error(f"Erro no gráfico USI: {e}")
                return None
        
        chart_usi = create_usi_chart_total_accounts(df_filtrado)
        if chart_usi:
            st.altair_chart(chart_usi, use_container_width=True)

st.markdown("---")

# Função para exportar uma única tabela para Excel
def exportar_excel(df, nome_arquivo):
    """Exporta DataFrame para Excel e retorna bytes para download"""
    from io import BytesIO
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=True, sheet_name='Dados')
    output.seek(0)
    return output.getvalue()

# Botão para download da tabela "Total SAP KE5Z - Todas as contas"
if st.button("📥 Baixar Total SAP KE5Z - Todas as contas (Excel)", use_container_width=True):
    with st.spinner("Gerando arquivo..."):
        # Criar a tabela pivot novamente para exportação (sem formatação de estilo)
        tabela_para_exportar = df_filtrado.pivot_table(index='Nº conta', columns='Período', values='Valor', aggfunc='sum', fill_value=0, margins=True, margins_name='Total')
        excel_data = exportar_excel(tabela_para_exportar, 'KE5Z_total_contas.xlsx')
        
        # Forçar download usando JavaScript
        import base64
        b64 = base64.b64encode(excel_data).decode()
        href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="KE5Z_total_contas.xlsx">💾 Clique aqui para baixar</a>'
        st.markdown(href, unsafe_allow_html=True)
        st.success("✅ Arquivo gerado! Clique no link acima para baixar.")

# Exibir o número de linhas e colunas do DataFrame filtrado e a soma do valor total
st.sidebar.write(f"Número de linhas: {df_filtrado.shape[0]}")
st.sidebar.write(f"Número de colunas: {df_filtrado.shape[1]}")
st.sidebar.write(f"Soma do Valor total: R$ {df_filtrado['Valor'].sum():,.2f}")



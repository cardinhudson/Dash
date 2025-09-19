import streamlit as st
import pandas as pd
import os
from auth import (verificar_autenticacao, exibir_header_usuario,
                  verificar_status_aprovado)

# Configuração da página
st.set_page_config(
    page_title="Total Accounts - Dashboard KE5Z",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
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

# Caminho do arquivo parquet
arquivo_parquet = os.path.join("KE5Z", "KE5Z.parquet")

# Sistema de cache otimizado para Total accounts
@st.cache_data(
    show_spinner=True,
    max_entries=1,
    ttl=1800,  # Cache por 30 minutos
    persist="disk"  # Salvar em disco para liberar RAM
)
def load_total_accounts_data():
    """Carrega dados com otimização de performance para Total accounts"""
    arquivo_parquet = os.path.join("KE5Z", "KE5Z.parquet")
    
    if not os.path.exists(arquivo_parquet):
        st.error(f"❌ Arquivo não encontrado: {arquivo_parquet}")
        st.info("💡 Execute a extração de dados na página principal para "
                "gerar o arquivo necessário.")
        st.stop()
    
    # Carregar dados
    df = pd.read_parquet(arquivo_parquet)
    
    # Otimizar tipos de dados
    for col in df.columns:
        if df[col].dtype == 'object':
            unique_ratio = df[col].nunique() / len(df)
            if unique_ratio < 0.5:
                df[col] = df[col].astype('category')
    
    return df

# Carregar dados otimizados
df_principal = load_total_accounts_data()

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

# Filtros adicionais (padronizados com outras páginas)
for col_name, label in [("Fornecedor", "Fornecedor"), ("Fornec.", "Fornec."), ("Tipo", "Tipo"), ("Type 05", "Type 05"), ("Type 06", "Type 06"), ("Type 07", "Type 07")]:
    if col_name in df_filtrado.columns:
        opcoes = ["Todos"] + sorted(df_filtrado[col_name].dropna().astype(str).unique().tolist())
        selecionadas = st.sidebar.multiselect(f"Selecione o {label}:", opcoes, default=["Todos"])
        if selecionadas and "Todos" not in selecionadas:
            df_filtrado = df_filtrado[df_filtrado[col_name].astype(str).isin(selecionadas)]

##################################################################################################

# Título da nova página
st.title("Total SAP KE5Z - Todas as USINAS")
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



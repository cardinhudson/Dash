# %%
import streamlit as st
import pandas as pd
import os
import altair as alt
import plotly.graph_objects as go
from auth_simple import (verificar_autenticacao, exibir_header_usuario,
                         eh_administrador, verificar_status_aprovado,
                         get_usuarios_cloud, adicionar_usuario_simples, criar_hash_senha)
from datetime import datetime

# Configuração otimizada da página para melhor performance
st.set_page_config(
    page_title="Dashboard KE5Z",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
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

# Detectar se estamos no Streamlit Cloud
try:
    base_url = st.get_option('server.baseUrlPath') or ''
    is_cloud = 'share.streamlit.io' in base_url
except Exception:
    is_cloud = False

# Informar sobre ambiente
if is_cloud:
    st.sidebar.info("☁️ **Modo Cloud**\n"
                     "Algumas funcionalidades são limitadas no Streamlit Cloud.")
else:
    st.sidebar.success("💻 **Modo Local**\n"
                       "Todas as funcionalidades disponíveis.")

# Sistema de cache inteligente para otimização de memória e conexão
@st.cache_data(
    ttl=3600,
    max_entries=1,
    show_spinner=True,
    persist="disk"
)
def load_data_optimized():
    """Carrega dados com otimização inteligente de memória"""
    arquivo_parquet = os.path.join("KE5Z", "KE5Z.parquet")
    
    try:
        if not os.path.exists(arquivo_parquet):
            raise FileNotFoundError(f"Arquivo não encontrado: {arquivo_parquet}")
        
        # Verificar tamanho do arquivo
        file_size_mb = os.path.getsize(arquivo_parquet) / (1024 * 1024)
        
        # Carregar dados
        df = pd.read_parquet(arquivo_parquet)
        
        # Remover amostragem para não afetar gráficos; apenas compactar tipos
        
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

# Carregar dados
try:
    df_total = load_data_optimized()
    st.sidebar.success("✅ Dados carregados com sucesso")
    
    # Log informativo
    if not is_cloud:
        st.sidebar.info(f"📊 {len(df_total)} registros carregados")
        
except FileNotFoundError:
    st.error("❌ Arquivo de dados não encontrado!")
    st.error(f"🔍 Procurando por: `KE5Z/KE5Z.parquet`")
    st.info("💡 **Soluções:**")
    st.info("1. Verifique se o arquivo `KE5Z.parquet` está na pasta `KE5Z/`")
    st.info("2. Execute a extração de dados localmente")
    st.info("3. Faça commit do arquivo no repositório")
    
    if is_cloud:
        st.warning("☁️ **No Streamlit Cloud:** Certifique-se que o arquivo "
                  "foi enviado para o repositório")
    
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
    st.title("📊 Dashboard - Visualização de Dados TC - KE5Z")
st.subheader("Somente os dados com as contas do Perímetro TC")

# Exibir header do usuário
exibir_header_usuario()

st.markdown("---")

# Filtros para o DataFrame
st.sidebar.title("Filtros")

# Cache para opções de filtros (otimização de performance)
@st.cache_data(ttl=1800, max_entries=3)
def get_filter_options(df, column_name):
    """Obtém opções de filtro com cache para melhor performance"""
    if column_name in df.columns:
        return ["Todos"] + sorted(df[column_name].dropna().astype(str).unique().tolist())
    return ["Todos"]

# Filtro 1: USINA (com cache otimizado)
usina_opcoes = get_filter_options(df_total, 'USI')
default_usina = ["Veículos"] if "Veículos" in usina_opcoes else ["Todos"]
usina_selecionada = st.sidebar.multiselect("Selecione a USINA:", usina_opcoes, default=default_usina)

# Filtrar o DataFrame com base na USI
if "Todos" in usina_selecionada or not usina_selecionada:
    df_filtrado = df_total.copy()
else:
    df_filtrado = df_total[df_total['USI'].astype(str).isin(usina_selecionada)]

# Filtro 2: Período (com cache otimizado)
periodo_opcoes = get_filter_options(df_filtrado, 'Período')
periodo_selecionado = st.sidebar.selectbox("Selecione o Período:", periodo_opcoes)
if periodo_selecionado != "Todos":
    df_filtrado = df_filtrado[df_filtrado['Período'].astype(str) == str(periodo_selecionado)]

# Filtro 3: Centro cst (com cache otimizado)
if 'Centro cst' in df_filtrado.columns:
    centro_cst_opcoes = get_filter_options(df_filtrado, 'Centro cst')
    centro_cst_selecionado = st.sidebar.selectbox("Selecione o Centro cst:", centro_cst_opcoes)
    if centro_cst_selecionado != "Todos":
        df_filtrado = df_filtrado[df_filtrado['Centro cst'].astype(str) == str(centro_cst_selecionado)]

# Filtro 4: Conta contábil (com cache otimizado)
if 'Nº conta' in df_filtrado.columns:
    conta_contabil_opcoes = get_filter_options(df_filtrado, 'Nº conta')[1:]  # Remove "Todos" para multiselect
    conta_contabil_selecionadas = st.sidebar.multiselect("Selecione a Conta contábil:", conta_contabil_opcoes)
    if conta_contabil_selecionadas:
        df_filtrado = df_filtrado[df_filtrado['Nº conta'].astype(str).isin(conta_contabil_selecionadas)]

# Filtros adicionais (com cache otimizado)
for col_name, label in [("Fornecedor", "Fornecedor"), ("Fornec.", "Fornec."), ("Tipo", "Tipo"), ("Type 05", "Type 05"), ("Type 06", "Type 06"), ("Type 07", "Type 07")]:
    if col_name in df_filtrado.columns:
        opcoes = get_filter_options(df_filtrado, col_name)
        selecionadas = st.sidebar.multiselect(f"Selecione o {label}:", opcoes, default=["Todos"])
        if selecionadas and "Todos" not in selecionadas:
            df_filtrado = df_filtrado[df_filtrado[col_name].astype(str).isin(selecionadas)]

# Exibir o número de linhas e colunas do DataFrame filtrado e a soma do valor total
st.sidebar.write(f"Número de linhas: {df_filtrado.shape[0]}")
st.sidebar.write(f"Número de colunas: {df_filtrado.shape[1]}")
st.sidebar.write(f"Soma do Valor total: R$ {df_filtrado['Valor'].sum():,.2f}")

# Monitoramento de cache e memória
st.sidebar.markdown("---")
st.sidebar.subheader("💾 Status do Sistema")

# Informações de cache
try:
    import sys
    
    # Tamanho do DataFrame em memória
    df_size_mb = sys.getsizeof(df_filtrado) / (1024 * 1024)
    st.sidebar.write(f"**Dados filtrados:** {df_size_mb:.1f}MB")
    
    # Status do cache
    st.sidebar.write(f"**Cache ativo:** ✅ 30min TTL")
    st.sidebar.write(f"**Otimização:** ✅ Tipos compactados")
    
    # Botão de limpeza de cache
    if st.sidebar.button("🧹 Limpar Cache", help="Limpa cache para liberar memória"):
        st.cache_data.clear()
        import gc
        gc.collect()
        st.sidebar.success("✅ Cache limpo!")
        st.rerun()
        
except Exception as e:
    st.sidebar.error(f"Erro no monitoramento: {e}")

# Seção administrativa (apenas para admin)
if eh_administrador():
    st.sidebar.markdown("---")
    st.sidebar.subheader("👑 Área Administrativa")

    # Carregar usuários do novo sistema
    usuarios = get_usuarios_cloud()

    # Informar sobre limitações baseado no ambiente
    if is_cloud:
        st.sidebar.info(
            "☁️ **Modo Cloud:** Usuários são gerenciados via Streamlit Secrets. "
            "Configure em Settings > Secrets no painel do Streamlit Cloud."
        )
    else:
        st.sidebar.info(
            "💻 **Modo Local:** Sistema de autenticação simplificado com "
            "usuários de demonstração."
        )

    # Status atual dos usuários
    total_usuarios = len(usuarios)
    usuarios_aprovados = len([u for u in usuarios.values()
                              if u.get('status') == 'aprovado'])
    usuarios_pendentes = len([u for u in usuarios.values()
                              if u.get('status') == 'pendente'])

    st.sidebar.metric("👥 Total", total_usuarios)
    st.sidebar.metric("✅ Aprovados", usuarios_aprovados)
    st.sidebar.metric("⏳ Pendentes", usuarios_pendentes)

    # Listar usuários
    st.sidebar.markdown("---")
    st.sidebar.subheader("📋 Usuários Cadastrados")

    for usuario, dados in usuarios.items():
        tipo_icon = "👑" if dados.get('tipo') == 'administrador' else "👥"
        tipo_text = "Admin" if dados.get('tipo') == 'administrador' else "User"
        status_icon = "✅" if dados.get('status') == 'aprovado' else "⏳"
        
        st.sidebar.write(f"{tipo_icon} {status_icon} **{usuario}** - {tipo_text}")

else:
    st.sidebar.markdown("---")
    st.sidebar.info("🔒 Apenas o administrador pode gerenciar usuários.")

# Gráfico de barras para a soma dos valores por 'Período'
@st.cache_data(ttl=900, max_entries=2)
def create_period_chart(df_data):
    """Cria gráfico otimizado"""
    try:
        chart_data = df_data.groupby('Período')['Valor'].sum().reset_index()
        
        grafico_barras = alt.Chart(chart_data).mark_bar().encode(
            x=alt.X('Período:N', title='Período'),
            y=alt.Y('Valor:Q', title='Soma do Valor'),
            color=alt.Color('Valor:Q', title='Valor', scale=alt.Scale(scheme='redyellowgreen', reverse=True)),
            tooltip=['Período:N', 'Valor:Q']
        ).properties(
            title='Soma do Valor por Período'
        )
        
        return grafico_barras
    except Exception as e:
        st.error(f"Erro ao criar gráfico: {e}")
        return None

# Criar e exibir gráfico
grafico_barras = create_period_chart(df_filtrado)
if grafico_barras:
    # Adicionar rótulos com valores nas barras
    rotulos = grafico_barras.mark_text(
        align='center',
        baseline='middle',
        dy=-10,  # Ajuste vertical
        color='black',
        fontSize=12
    ).encode(
        text=alt.Text('Valor:Q', format=',.2f')
    )
    
    # Combinar gráfico com rótulos
    grafico_completo = grafico_barras + rotulos
    st.altair_chart(grafico_completo, use_container_width=True)

# Gráficos adicionais por Type
st.subheader("📊 Análise por Categorias")

# Gráfico por Type 05
if 'Type 05' in df_filtrado.columns:
    @st.cache_data(ttl=900, max_entries=2)
    def create_type05_chart(df_data):
        try:
            type05_data = df_data.groupby('Type 05')['Valor'].sum().reset_index()
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
            type06_data = df_data.groupby('Type 06')['Valor'].sum().reset_index()
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
df_pivot = df_filtrado.pivot_table(index='USI', columns='Período', values='Valor', aggfunc='sum', margins=True, margins_name='Total', fill_value=0)
st.subheader("Tabela Dinâmica - Soma do Valor por USI e Período")

# Aplicar formatação com cores (verde para positivo, vermelho para negativo)
def colorir_valores(val):
    if isinstance(val, (int, float)):
        if val < 0:
            return 'color: #e74c3c; font-weight: bold;'  # Vermelho para negativo
        elif val > 0:
            return 'color: #27ae60; font-weight: bold;'  # Verde para positivo
    return ''

styled_pivot = df_pivot.style.format('R$ {:,.2f}').map(colorir_valores, subset=pd.IndexSlice[:, :])
st.dataframe(styled_pivot, use_container_width=True)

# Botão de download da Tabela Dinâmica (logo abaixo da tabela)
if st.button("📥 Baixar Tabela Dinâmica (Excel)", use_container_width=True, key="download_pivot"):
    with st.spinner("Gerando arquivo da tabela dinâmica..."):
        # Função para exportar para Excel
        def exportar_excel_pivot(df, nome_arquivo):
            from io import BytesIO
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=True, sheet_name='Tabela_Dinamica')
            output.seek(0)
            return output.getvalue()
        
        excel_data_pivot = exportar_excel_pivot(df_pivot, 'KE5Z_tabela_dinamica.xlsx')
        
        # Forçar download usando JavaScript
        import base64
        b64 = base64.b64encode(excel_data_pivot).decode()
        href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="KE5Z_tabela_dinamica.xlsx">💾 Clique aqui para baixar a Tabela Dinâmica</a>'
        st.markdown(href, unsafe_allow_html=True)
        st.success("✅ Tabela Dinâmica gerada! Clique no link acima para baixar.")

# Exibir o DataFrame filtrado (limitado para performance)
st.subheader("Tabela Filtrada")
display_limit = 500 if is_cloud else 2000
if len(df_filtrado) > display_limit:
    st.info(f"📊 Mostrando {display_limit:,} de {len(df_filtrado):,} registros para otimizar performance")
    df_display = df_filtrado.head(display_limit)
else:
    df_display = df_filtrado

st.dataframe(df_display, use_container_width=True)

# Botão de download da Tabela Filtrada (logo abaixo da tabela)
if st.button("📥 Baixar Tabela Filtrada (Excel)", use_container_width=True, key="download_filtered"):
    with st.spinner("Gerando arquivo da tabela filtrada..."):
        # Função para exportar tabela filtrada
        def exportar_excel_filtrada(df, nome_arquivo):
            from io import BytesIO
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Dados_Filtrados')
            output.seek(0)
            return output.getvalue()
        
        excel_data_filtrada = exportar_excel_filtrada(df_filtrado, 'KE5Z_tabela_filtrada.xlsx')
        
        # Forçar download usando JavaScript
        import base64
        b64 = base64.b64encode(excel_data_filtrada).decode()
        href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="KE5Z_tabela_filtrada.xlsx">💾 Clique aqui para baixar a Tabela Filtrada</a>'
        st.markdown(href, unsafe_allow_html=True)
        st.success("✅ Tabela Filtrada gerada! Clique no link acima para baixar.")

# Tabela de soma por Types (funcionalidade original restaurada)
if all(col in df_filtrado.columns for col in ['Type 05', 'Type 06', 'Type 07']):
    st.markdown("---")
    st.subheader("📊 Soma dos Valores por Type 05, Type 06 e Type 07")
    
    # Criar tabela com soma por types
    soma_por_type = (df_filtrado.groupby(['Type 05', 'Type 06', 'Type 07'])['Valor']
                     .sum().reset_index())
    
    # Adicionar linha de total
    soma_total = pd.DataFrame({
        'Type 05': ['Total'],
        'Type 06': [''],
        'Type 07': [''],
        'Valor': [soma_por_type['Valor'].sum()]
    })
    soma_por_type_completa = pd.concat([soma_por_type, soma_total], ignore_index=True)
    
    # Aplicar formatação com cores
    def colorir_valores_type(val):
        if isinstance(val, (int, float)):
            if val < 0:
                return 'color: #e74c3c; font-weight: bold;'  # Vermelho para negativo
            elif val > 0:
                return 'color: #27ae60; font-weight: bold;'  # Verde para positivo
        return ''
    
    styled_type = soma_por_type_completa.style.format({'Valor': 'R$ {:,.2f}'}).map(
        colorir_valores_type, subset=['Valor'])
    
    st.dataframe(styled_type, use_container_width=True)
    
    # Botão de download da Tabela de Soma por Types (logo abaixo da tabela)
    if st.button("📥 Baixar Soma por Types (Excel)", use_container_width=True, key="download_types"):
        with st.spinner("Gerando arquivo da soma por types..."):
            # Função para exportar soma por types
            def exportar_excel_types(df, nome_arquivo):
                from io import BytesIO
                output = BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False, sheet_name='Soma_por_Types')
                output.seek(0)
                return output.getvalue()
            
            excel_data_types = exportar_excel_types(soma_por_type_completa, 'KE5Z_soma_por_types.xlsx')
            
            # Forçar download usando JavaScript
            import base64
            b64 = base64.b64encode(excel_data_types).decode()
            href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="KE5Z_soma_por_types.xlsx">💾 Clique aqui para baixar a Soma por Types</a>'
            st.markdown(href, unsafe_allow_html=True)
            st.success("✅ Soma por Types gerada! Clique no link acima para baixar.")

# Footer
st.markdown("---")
st.info("💡 Dashboard KE5Z com otimizações de cache e memória")

# Informações de funcionalidades restauradas
col1, col2, col3 = st.columns(3)
with col1:
    st.success("✅ Exportação Excel")
with col2:
    st.success("✅ Gráficos Coloridos")
with col3:
    st.success("✅ Tabelas com Cores")

if is_cloud:
    st.success("☁️ Executando no Streamlit Cloud com otimizações")
else:
    st.success("💻 Executando localmente com performance máxima")
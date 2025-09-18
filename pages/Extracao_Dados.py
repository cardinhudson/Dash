import streamlit as st
import pandas as pd
import os
from datetime import datetime
from auth import (verificar_autenticacao, exibir_header_usuario,
                  verificar_status_aprovado, eh_administrador)

# Configuração da página
st.set_page_config(
    page_title="Extração de Dados - Dashboard KE5Z",
    page_icon="📥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Verificar autenticação
verificar_autenticacao()

# Verificar se o usuário está aprovado
if ('usuario_nome' in st.session_state and 
    not verificar_status_aprovado(st.session_state.usuario_nome)):
    st.warning("⏳ Sua conta ainda está pendente de aprovação.")
    st.stop()

# Verificar se é administrador (apenas admin pode fazer extração)
if not eh_administrador():
    st.error("🔒 **Acesso Restrito**")
    st.error("Apenas administradores podem acessar a página de extração de dados.")
    st.info("💡 Entre em contato com o administrador do sistema se precisar de acesso.")
    st.stop()

# Header
st.title("📥 Extração de Dados KE5Z")
st.subheader("Processamento e consolidação de arquivos Excel")

# Exibir header do usuário
exibir_header_usuario()

st.markdown("---")

# Detectar ambiente (cloud vs local)
try:
    base_url = st.get_option('server.baseUrlPath') or ''
    is_cloud = 'share.streamlit.io' in base_url
except Exception:
    is_cloud = False

# Aviso sobre limitações no cloud
if is_cloud:
    st.warning("☁️ **Modo Cloud Detectado**")
    st.warning("A extração automática não funciona no Streamlit Cloud devido a limitações de segurança.")
    
    st.markdown("---")
    st.subheader("📤 Upload Manual de Dados")
    st.info("💡 **No Streamlit Cloud, use upload manual:**")
    
    # Interface de upload para cloud
    uploaded_files = st.file_uploader(
        "Selecione arquivos Excel para processar:",
        type=['xlsx', 'xls'],
        accept_multiple_files=True,
        help="Selecione os arquivos KE5Z em formato Excel"
    )
    
    if uploaded_files:
        st.success(f"✅ {len(uploaded_files)} arquivo(s) carregado(s)")
        
        if st.button("🔄 Processar Arquivos Carregados", type="primary"):
            try:
                # Processar arquivos carregados
                dataframes = []
                progress_bar = st.progress(0)
                
                for i, uploaded_file in enumerate(uploaded_files):
                    st.write(f"📄 Processando: {uploaded_file.name}")
                    df = pd.read_excel(uploaded_file)
                    dataframes.append(df)
                    progress_bar.progress((i + 1) / len(uploaded_files))
                
                # Consolidar dados
                df_total = pd.concat(dataframes, ignore_index=True)
                
                # Mostrar preview
                st.success("✅ Dados processados com sucesso!")
                st.metric("Total de Registros", f"{len(df_total):,}")
                st.dataframe(df_total.head(10))
                
                # Download do arquivo processado
                @st.cache_data
                def convert_df(df):
                    return df.to_csv(index=False).encode('utf-8')
                
                csv_data = convert_df(df_total)
                
                st.download_button(
                    label="📥 Baixar Dados Processados (CSV)",
                    data=csv_data,
                    file_name=f'KE5Z_processado_{datetime.now().strftime("%Y%m%d_%H%M")}.csv',
                    mime='text/csv'
                )
                
                st.info("💡 **Próximos passos:**")
                st.info("1. Baixe o arquivo CSV processado")
                st.info("2. Converta para Parquet localmente se necessário")
                st.info("3. Faça commit no repositório para atualizar o dashboard")
                
            except Exception as e:
                st.error(f"❌ Erro ao processar arquivos: {str(e)}")
    
    st.markdown("---")
    st.subheader("📋 Instruções para Cloud")
    
    with st.expander("🌐 Como atualizar dados no Streamlit Cloud"):
        st.markdown("""
        ### 📤 **Método 1: Upload Manual (Recomendado)**
        1. Use o upload acima para processar arquivos
        2. Baixe o arquivo CSV processado
        3. Converta para Parquet localmente:
           ```python
           import pandas as pd
           df = pd.read_csv('arquivo.csv')
           df.to_parquet('KE5Z/KE5Z.parquet')
           ```
        4. Faça commit no GitHub
        5. Deploy automático atualizará o dashboard
        
        ### 🖥️ **Método 2: Processamento Local**
        1. Execute o dashboard localmente
        2. Use esta página para extrair dados
        3. Faça commit dos arquivos gerados
        4. Deploy automático no cloud
        
        ### 📊 **Método 3: Arquivo Direto**
        1. Execute `Extração.py` localmente
        2. Copie `KE5Z.parquet` para o repositório
        3. Faça commit e push
        4. Dashboard cloud será atualizado
        """)
    
    st.stop()

# Interface de extração
st.info("💻 **Modo Local Detectado** - Extração disponível")

# Configurações de pastas
st.subheader("📁 Configuração de Pastas")

# Pastas padrão baseadas no código original
pasta_opcoes_default = [
    os.path.join(
        os.path.expanduser("~"),
        "Stellantis", "GEIB - General", "GEIB", "Partagei_2025",
        "1 - SÍNTESE", "11 - SAPIENS", "02 - Extrações", "KE5Z"
    ),
    os.path.join(
        os.path.expanduser("~"),
        "Stellantis", "GEIB - GEIB", "Partagei_2025",
        "1 - SÍNTESE", "11 - SAPIENS", "02 - Extrações", "KE5Z"
    ),
]

# Permitir pasta personalizada
col1, col2 = st.columns([2, 1])

with col1:
    usar_pasta_personalizada = st.checkbox("Usar pasta personalizada")
    
    if usar_pasta_personalizada:
        pasta_origem = st.text_input(
            "Pasta de origem dos arquivos Excel:",
            placeholder="C:\\caminho\\para\\pasta\\KE5Z"
        )
    else:
        st.info("Usando pastas padrão do sistema Stellantis")
        pasta_origem = None

with col2:
    st.markdown("### 📋 Pastas Padrão:")
    for i, pasta in enumerate(pasta_opcoes_default, 1):
        if os.path.exists(pasta):
            st.success(f"✅ Opção {i}: Encontrada")
        else:
            st.error(f"❌ Opção {i}: Não encontrada")

# Verificar pasta de origem
pasta_encontrada = None

if not usar_pasta_personalizada:
    for pasta_opcao in pasta_opcoes_default:
        if os.path.exists(pasta_opcao):
            pasta_encontrada = pasta_opcao
            break
else:
    if pasta_origem and os.path.exists(pasta_origem):
        pasta_encontrada = pasta_origem

# Mostrar status da pasta
if pasta_encontrada:
    st.success(f"✅ **Pasta encontrada:** `{pasta_encontrada}`")
    
    # Listar arquivos Excel na pasta
    try:
        arquivos_excel = [f for f in os.listdir(pasta_encontrada) if f.endswith(('.xlsx', '.xls'))]
        
        if arquivos_excel:
            st.info(f"📄 **{len(arquivos_excel)} arquivos Excel encontrados:**")
            
            # Mostrar lista de arquivos em colunas
            cols = st.columns(3)
            for i, arquivo in enumerate(arquivos_excel):
                with cols[i % 3]:
                    st.write(f"• {arquivo}")
        else:
            st.warning("⚠️ Nenhum arquivo Excel encontrado na pasta")
            
    except Exception as e:
        st.error(f"❌ Erro ao listar arquivos: {str(e)}")
        
else:
    st.error("❌ **Pasta não encontrada**")
    if not usar_pasta_personalizada:
        st.error("Nenhuma das pastas padrão foi encontrada no sistema")
    else:
        st.error("Pasta personalizada não existe ou não foi especificada")

# Configurações de saída
st.markdown("---")
st.subheader("💾 Configuração de Saída")

col1, col2 = st.columns(2)

with col1:
    salvar_local = st.checkbox("Salvar na pasta do dashboard (KE5Z/)", value=True)
    
with col2:
    salvar_excel_separado = st.checkbox("Gerar arquivos Excel por USI", value=False)

# Botão de extração
st.markdown("---")
st.subheader("🚀 Executar Extração")

if pasta_encontrada:
    if st.button("📥 Iniciar Extração de Dados", type="primary", use_container_width=True):
        
        # Barra de progresso
        progress_bar = st.progress(0)
        status_text = st.empty()
        log_container = st.container()
        
        try:
            with log_container:
                st.write("**📋 Log de Execução:**")
                log_placeholder = st.empty()
                logs = []
                
                # Função para adicionar log
                def add_log(message):
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    logs.append(f"[{timestamp}] {message}")
                    log_placeholder.text("\n".join(logs[-10:]))  # Mostrar últimas 10 linhas
                
                # Iniciar processamento
                add_log("🚀 Iniciando extração de dados...")
                progress_bar.progress(10)
                
                # Lista para armazenar DataFrames
                dataframes = []
                arquivos_processados = 0
                
                # Processar cada arquivo Excel
                for arquivo in arquivos_excel:
                    try:
                        caminho_arquivo = os.path.join(pasta_encontrada, arquivo)
                        add_log(f"📄 Processando: {arquivo}")
                        
                        # Ler arquivo Excel
                        df = pd.read_excel(caminho_arquivo)
                        dataframes.append(df)
                        arquivos_processados += 1
                        
                        progress = 10 + (arquivos_processados / len(arquivos_excel)) * 60
                        progress_bar.progress(int(progress))
                        
                    except Exception as e:
                        add_log(f"❌ Erro ao processar {arquivo}: {str(e)}")
                
                if not dataframes:
                    st.error("❌ Nenhum arquivo foi processado com sucesso")
                    st.stop()
                
                # Consolidar dados
                add_log("🔄 Consolidando dados...")
                progress_bar.progress(75)
                
                df_total = pd.concat(dataframes, ignore_index=True)
                add_log(f"✅ {len(dataframes)} arquivos consolidados")
                add_log(f"📊 Total de registros: {len(df_total)}")
                
                # Processamento dos dados (baseado no código original)
                add_log("⚙️ Processando dados...")
                
                # Renomear colunas conforme código original
                renomeacoes = {
                    'Texto': 'Texto breve',
                    'Qtd.': 'QTD',
                    'Nº conta': 'Nºconta',
                    'Centro cst': 'Centrocst',
                    'doc.ref': 'Nºdoc.ref.',
                    'Type 07': 'Account',
                    'Período': 'Mes'
                }
                
                for old_name, new_name in renomeacoes.items():
                    if old_name in df_total.columns:
                        df_total.rename(columns={old_name: new_name}, inplace=True)
                
                # Criar coluna de período em texto
                if 'Mes' in df_total.columns:
                    meses = {
                        1: 'janeiro', 2: 'fevereiro', 3: 'março', 4: 'abril',
                        5: 'maio', 6: 'junho', 7: 'julho', 8: 'agosto',
                        9: 'setembro', 10: 'outubro', 11: 'novembro', 12: 'dezembro'
                    }
                    df_total['Período'] = df_total['Mes'].map(meses)
                
                # Reordenar colunas
                if 'Mes' in df_total.columns and 'Período' in df_total.columns:
                    outras_colunas = [col for col in df_total.columns if col not in ['Mes', 'Período']]
                    df_total = df_total[['Mes', 'Período'] + outras_colunas]
                
                progress_bar.progress(90)
                
                # Salvar arquivos
                add_log("💾 Salvando arquivos...")
                
                if salvar_local:
                    # Salvar arquivo principal
                    caminho_parquet = os.path.join("KE5Z", "KE5Z.parquet")
                    df_total.to_parquet(caminho_parquet, index=False)
                    add_log(f"✅ Arquivo Parquet salvo: {caminho_parquet}")
                    
                    # Salvar Excel também
                    caminho_excel = os.path.join("KE5Z", "KE5Z.xlsx")
                    df_total.to_excel(caminho_excel, index=False)
                    add_log(f"✅ Arquivo Excel salvo: {caminho_excel}")
                
                # Salvar arquivos por USI se solicitado
                if salvar_excel_separado and 'USI' in df_total.columns:
                    usis_unicas = df_total['USI'].dropna().unique()
                    for usi in usis_unicas:
                        df_usi = df_total[df_total['USI'] == usi]
                        nome_arquivo = f"KE5Z_{usi.lower().replace(' ', '_')}.xlsx"
                        caminho_usi = os.path.join("KE5Z", nome_arquivo)
                        df_usi.to_excel(caminho_usi, index=False)
                        add_log(f"✅ Arquivo USI salvo: {nome_arquivo}")
                
                progress_bar.progress(100)
                add_log("🎉 Extração concluída com sucesso!")
                
                # Mostrar resumo
                st.success("✅ **Extração Concluída!**")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Arquivos Processados", arquivos_processados)
                with col2:
                    st.metric("Total de Registros", f"{len(df_total):,}")
                with col3:
                    st.metric("Colunas", len(df_total.columns))
                
                # Mostrar preview dos dados
                st.subheader("👀 Preview dos Dados")
                st.dataframe(df_total.head(10), use_container_width=True)
                
                # Informações das colunas
                st.subheader("📊 Informações das Colunas")
                col_info = pd.DataFrame({
                    'Coluna': df_total.columns,
                    'Tipo': [str(dtype) for dtype in df_total.dtypes],
                    'Não Nulos': [df_total[col].notna().sum() for col in df_total.columns],
                    'Valores Únicos': [df_total[col].nunique() for col in df_total.columns]
                })
                st.dataframe(col_info, use_container_width=True)
                
        except Exception as e:
            st.error(f"❌ **Erro durante a extração:** {str(e)}")
            add_log(f"❌ Erro crítico: {str(e)}")

else:
    st.warning("⚠️ Configure uma pasta válida antes de executar a extração")

# Informações adicionais
st.markdown("---")
st.subheader("ℹ️ Informações")

with st.expander("📖 Como usar esta página"):
    st.markdown("""
    ### 🎯 **Objetivo**
    Esta página substitui o arquivo `Extração.py` e permite processar arquivos Excel diretamente no dashboard.
    
    ### 📋 **Passos para usar:**
    1. **Configure a pasta** onde estão os arquivos Excel
    2. **Verifique** se os arquivos foram encontrados
    3. **Configure as opções** de saída
    4. **Execute a extração** clicando no botão
    
    ### 📁 **Arquivos gerados:**
    - `KE5Z/KE5Z.parquet` - Arquivo principal para o dashboard
    - `KE5Z/KE5Z.xlsx` - Arquivo Excel consolidado
    - Arquivos por USI (se habilitado)
    
    ### 🔒 **Segurança:**
    - Apenas administradores podem acessar esta página
    - Funciona apenas em ambiente local (não no cloud)
    - Todos os arquivos são salvos na pasta do projeto
    
    ### 💡 **Vantagens:**
    - ✅ Não usa subprocess (compatível com cloud se adaptado)
    - ✅ Interface visual com progresso
    - ✅ Logs detalhados de execução
    - ✅ Preview dos dados processados
    - ✅ Tratamento de erros robusto
    """)

with st.expander("🔧 Configurações Técnicas"):
    st.markdown(f"""
    ### 🖥️ **Ambiente Atual:**
    - **Modo**: {'☁️ Cloud' if is_cloud else '💻 Local'}
    - **Usuário**: {st.session_state.get('usuario_nome', 'N/A')}
    - **Admin**: {'✅ Sim' if eh_administrador() else '❌ Não'}
    
    ### 📁 **Pastas Monitoradas:**
    """)
    
    for i, pasta in enumerate(pasta_opcoes_default, 1):
        status = "✅ Existe" if os.path.exists(pasta) else "❌ Não existe"
        st.code(f"Opção {i}: {status}\n{pasta}")

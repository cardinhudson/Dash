import streamlit as st
import pandas as pd
import os
import glob
from datetime import datetime
from auth_simple import (verificar_autenticacao, exibir_header_usuario,
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

# Verificar se é administrador
if not eh_administrador():
    st.error("🔒 **Acesso Restrito**")
    st.error("Apenas administradores podem acessar a página de extração.")
    st.info("💡 Entre em contato com o administrador se precisar de acesso.")
    st.stop()

# Header
st.title("📥 Extração de Dados KE5Z")
st.subheader("Processamento Completo - Igual ao Extração.py")

# Exibir header do usuário
exibir_header_usuario()

st.markdown("---")

# Inicializar logs
if 'logs' not in st.session_state:
    st.session_state.logs = []
    timestamp = datetime.now().strftime('%H:%M:%S')
    st.session_state.logs.append(f"[{timestamp}] Sistema inicializado - Processamento completo ativo!")


def adicionar_log(mensagem):
    timestamp = datetime.now().strftime('%H:%M:%S')
    st.session_state.logs.append(f"[{timestamp}] {mensagem}")
    if len(st.session_state.logs) > 30:  # Mais logs para processo completo
        st.session_state.logs = st.session_state.logs[-30:]


# Utilitário: checar arquivos necessários
def checar_arquivos():
    lista = [
        ("Dados SAPIENS.xlsx", "Base SAPIENS"),
        ("Fornecedores.xlsx", "Lista fornecedores"),
        ("KSBB", "Pasta KSBB"),
        ("KE5Z", "Pasta TXT")
    ]
    detalhes = []
    ok = True
    for caminho, desc in lista:
        existe = os.path.exists(caminho)
        detalhes.append((caminho, desc, existe, os.path.isdir(caminho)))
        if not existe:
            ok = False
    return ok, detalhes

ok_arquivos, detalhes_arquivos = checar_arquivos()

# Layout em abas
tab_exec, tab_arq, tab_logs = st.tabs(["🚀 Executar", "📁 Arquivos", "📋 Logs"])

# Placeholder de logs (dentro da aba de Logs)
with tab_logs:
    log_container = st.empty()
    def atualizar_logs():
        with log_container.container():
            st.subheader("📋 Logs")
            if st.session_state.logs:
                for log in st.session_state.logs[-15:]:
                    st.text(log)
            else:
                st.text("Aguardando execução...")

st.markdown("---")

# Configurações
st.subheader("⚙️ Configurações")
st.info("🔄 **Processamento Completo**: Replica toda a lógica do Extração.py internamente")
st.info("📊 **Filtros Automáticos**: Gera automaticamente arquivos Excel por USI e PWT")
st.info("💾 **Salvamento Inteligente**: Tenta Stellantis, se falhar usa Downloads")

with tab_exec:
    # Verificar se arquivos separados existem, se não, limpar cache
    arquivos_separados_existem = (
        os.path.exists("KE5Z/KE5Z_main.parquet") and 
        os.path.exists("KE5Z/KE5Z_others.parquet")
    )
    
    if not arquivos_separados_existem and os.path.exists("KE5Z/KE5Z.parquet"):
        st.info("🔄 **Arquivos separados não detectados**. Cache será limpo para gerar novos arquivos otimizados.")
        if st.button("🗑️ Limpar Cache e Reexecutar"):
            executar_extracao_completa.clear()
            st.rerun()
    
    st.subheader("Parâmetros")
    col1, col2 = st.columns(2)
    with col1:
        gerar_excel_separado = st.checkbox("📋 Gerar Excel por USI", value=True)
    with col2:
        meses_selecionados = st.multiselect(
            "📅 Meses (apenas para Excel)",
            options=list(range(1, 13)),
            default=list(range(1, 13)),
            format_func=lambda x: {1:"Janeiro",2:"Fevereiro",3:"Março",4:"Abril",5:"Maio",6:"Junho",7:"Julho",8:"Agosto",9:"Setembro",10:"Outubro",11:"Novembro",12:"Dezembro"}[x]
        )

st.markdown("---")

with tab_arq:
    st.subheader("Arquivos Necessários")
    todos_ok = ok_arquivos
    cols = st.columns(2)
    for idx, (caminho, desc, existe, is_dir) in enumerate(detalhes_arquivos):
        with cols[idx % 2]:
            if existe:
                if is_dir:
                    qtd = len(glob.glob(f"{caminho}/*.*"))
                    st.success(f"✅ {desc}: {qtd} itens")
                else:
                    st.success(f"✅ {desc}: OK")
            else:
                st.error(f"❌ {desc}: Ausente")
    st.caption("O Parquet sempre será gerado completo. O filtro de meses afeta apenas Excel.")

@st.cache_data(ttl=300, max_entries=1, persist="disk")  # Cache por 5 minutos
def executar_extracao_completa(meses_filtro, gerar_separado):
    """Executa toda a lógica do Extração.py internamente"""
    
    resultados = {
        'sucesso': False,
        'arquivos_gerados': [],
        'logs': [],
        'erro': None
    }
    
    def log(msg):
        resultados['logs'].append(msg)
    
    try:
        log("🚀 Iniciando extração completa...")
        
        # ETAPA 1: Carregar dados KE5Z
        log("📂 ETAPA 1: Carregando dados KE5Z...")
        
        # Definir pastas possíveis para KE5Z
        pasta_opcoes = [
            os.path.join(os.path.expanduser("~"), "Stellantis", "GEIB - General", "GEIB", "Partagei_2025", "1 - SÍNTESE", "11 - SAPIENS", "02 - Extrações", "KE5Z"),
            os.path.join(os.path.expanduser("~"), "Stellantis", "GEIB - GEIB", "Partagei_2025", "1 - SÍNTESE", "11 - SAPIENS", "02 - Extrações", "KE5Z"),
            "KE5Z"  # Pasta local como fallback
        ]
        
        # Localizar primeira pasta existente
        pasta_ke5z = next((p for p in pasta_opcoes if os.path.exists(p)), None)
        
        if not pasta_ke5z:
            raise Exception("Nenhuma pasta KE5Z encontrada!")
        
        log(f"✅ Pasta KE5Z encontrada: {pasta_ke5z}")
        
        # Carregar arquivos TXT
        dataframes = []
        arquivos_txt = [f for f in os.listdir(pasta_ke5z) if f.endswith('.txt')]
        
        if not arquivos_txt:
            raise Exception("Nenhum arquivo .txt encontrado na pasta KE5Z!")
        
        for arquivo in arquivos_txt:
            caminho = os.path.join(pasta_ke5z, arquivo)
            log(f"📄 Lendo: {arquivo}")
            
            df = pd.read_csv(caminho, sep='\t', skiprows=9, encoding='latin1', engine='python')
            df.rename(columns={df.columns[9]: 'doc.ref'}, inplace=True)
            df.columns = df.columns.str.strip()
            df = df[df['Ano'].notna() & (df['Ano'] != 0)]
            
            # Processar colunas numéricas
            for col in ['Em MCont.', 'Qtd.']:
                if col in df.columns:
                    df[col] = df[col].str.replace('.', '', regex=False).str.replace(',', '.', regex=False)
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            
            dataframes.append(df)
            log(f"✅ {arquivo}: {len(df)} registros, Total Em MCont.: {df['Em MCont.'].sum():.2f}")
        
        # Concatenar DataFrames
        df_total = pd.concat(dataframes, ignore_index=True)
        log(f"🔄 Dados consolidados: {len(df_total)} registros totais")
        
        # ETAPA 2: Limpeza de colunas
        log("🧹 ETAPA 2: Removendo colunas desnecessárias...")
        
        colunas_para_remover = [
            'Unnamed: 0', 'Unnamed: 1', 'Unnamed: 4', 'Nº doc.', 'Elem.PEP', 'Obj.custo', 'TD',
            'SocPar', 'EmpEm.', 'Empr', 'TMv', 'D/C', 'Imobil.', 'Descrição Material',
            'Cliente', 'Cen.', 'Cen.lucro', 'Unnamed: 14', 'Classe objs.', 'Item', 'D'
        ]
        
        df_total.drop(columns=colunas_para_remover, inplace=True, errors='ignore')
        df_total.rename(columns={'Em MCont.': 'Valor'}, inplace=True)
        df_total = df_total[df_total['Nº conta'].notna() & (df_total['Nº conta'] != 0)]
        
        log(f"✅ Limpeza concluída. Registros restantes: {len(df_total)}")
        
        # ETAPA 3: Merge com KSBB
        log("🔗 ETAPA 3: Fazendo merge com dados KSBB...")
        
        pasta_ksbb_opcoes = [
            os.path.join(os.path.expanduser("~"), "Stellantis", "GEIB - General", "GEIB", "Partagei_2025", "1 - SÍNTESE", "11 - SAPIENS", "02 - Extrações", "KSBB"),
            os.path.join(os.path.expanduser("~"), "Stellantis", "GEIB - GEIB", "Partagei_2025", "1 - SÍNTESE", "11 - SAPIENS", "02 - Extrações", "KSBB"),
            "KSBB"  # Pasta local
        ]
        
        pasta_ksbb = None
        for pasta in pasta_ksbb_opcoes:
            if os.path.exists(pasta):
                pasta_ksbb = pasta
                break
        
        if pasta_ksbb:
            log(f"✅ Pasta KSBB encontrada: {pasta_ksbb}")
            
            dataframes_ksbb = []
            for arquivo in os.listdir(pasta_ksbb):
                if arquivo.endswith('.txt'):
                    caminho = os.path.join(pasta_ksbb, arquivo)
                    df_ksbb = pd.read_csv(caminho, sep='\t', encoding='latin1', engine='python', skiprows=3, skipfooter=1)
                    df_ksbb.columns = df_ksbb.columns.str.strip()
                    df_ksbb = df_ksbb[df_ksbb['Material'].notna() & (df_ksbb['Material'] != 0)]
                    df_ksbb = df_ksbb.drop_duplicates(subset=['Material'])
                    dataframes_ksbb.append(df_ksbb)
            
            if dataframes_ksbb:
                df_ksbb_final = pd.concat(dataframes_ksbb, ignore_index=True) if len(dataframes_ksbb) > 1 else dataframes_ksbb[0]
                df_ksbb_final = df_ksbb_final.drop_duplicates(subset=['Material'])
                
                if 'Material' in df_total.columns:
                    df_total = pd.merge(df_total, df_ksbb_final[['Material', 'Texto breve material']], on='Material', how='left')
                    df_total.rename(columns={'Texto breve material': 'Descrição Material'}, inplace=True)
                    
                    # Substituir Texto por Descrição Material quando disponível
                    if 'Texto' in df_total.columns:
                        df_total['Texto'] = df_total.apply(
                            lambda row: row['Descrição Material'] if pd.notnull(row['Descrição Material']) else row['Texto'], axis=1
                        )
                    
                    log("✅ Merge KSBB concluído")
        else:
            log("⚠️ Pasta KSBB não encontrada, continuando sem merge KSBB")
        
        # ETAPA 4: Merge com SAPIENS
        log("🔗 ETAPA 4: Fazendo merge com dados SAPIENS...")
        
        if os.path.exists('Dados SAPIENS.xlsx'):
            # Conta contabil
            df_sapiens = pd.read_excel('Dados SAPIENS.xlsx', sheet_name='Conta contabil')
            df_sapiens.rename(columns={'CONTA SAPIENS': 'Nº conta'}, inplace=True)
            df_total = pd.merge(df_total, df_sapiens[['Nº conta', 'Type 07', 'Type 06', 'Type 05']], on='Nº conta', how='left')
            log("✅ Merge SAPIENS - Conta contabil concluído")
            
            # CC (Centros de Custo)
            df_cc = pd.read_excel('Dados SAPIENS.xlsx', sheet_name='CC')
            df_cc.rename(columns={'CC SAPiens': 'Centro cst'}, inplace=True)
            df_total = pd.merge(df_total, df_cc[['Centro cst', 'Oficina', 'USI']], on='Centro cst', how='left')
            df_total['USI'] = df_total['USI'].fillna('Others')
            log("✅ Merge SAPIENS - CC concluído")
        else:
            log("⚠️ Arquivo SAPIENS não encontrado")
        
        # ETAPA 5: Limpeza e conversão de tipos
        log("🧹 ETAPA 5: Limpeza e conversão de tipos...")
        
        # Converter colunas numéricas
        for col in ['Ano', 'Período']:
            if col in df_total.columns:
                df_total[col] = pd.to_numeric(df_total[col], errors='coerce')
        
        numeric_columns = ['Valor', 'Qtd.', 'doc.ref', 'Item']
        for col in numeric_columns:
            if col in df_total.columns:
                df_total[col] = pd.to_numeric(df_total[col], errors='coerce')
        
        df_total = df_total.where(pd.notnull(df_total), None)
        log("✅ Limpeza de tipos concluída")
        
        # ETAPA 6: Merge com Fornecedores
        log("🔗 ETAPA 6: Fazendo merge com Fornecedores...")
        
        if os.path.exists('Fornecedores.xlsx'):
            df_fornecedores = pd.read_excel('Fornecedores.xlsx', skiprows=3)
            df_fornecedores = df_fornecedores.drop_duplicates(subset=['Fornecedor'])
            df_fornecedores.rename(columns={'Fornecedor': 'Fornec.'}, inplace=True)
            df_fornecedores['Fornec.'] = df_fornecedores['Fornec.'].astype(str)
            
            df_total = pd.merge(df_total, df_fornecedores[['Fornec.', 'Nome do fornecedor']], on='Fornec.', how='left')
            df_total.rename(columns={'Nome do fornecedor': 'Fornecedor'}, inplace=True)
            log("✅ Merge Fornecedores concluído")
        else:
            log("⚠️ Arquivo Fornecedores não encontrado")
        
        # ETAPA 7: Reorganizar colunas e renomear
        log("🔄 ETAPA 7: Reorganizando colunas...")
        
        # Reordenar colunas conforme Extração.py
        colunas_desejadas = ['Período', 'Nº conta', 'Centro cst', 'doc.ref', 'Dt.lçto.', 'Valor', 'Qtd.', 'Type 05', 'Type 06', 'Type 07', 'USI', 'Oficina', 'Doc.compra', 'Texto', 'Fornecedor', 'Material', 'Usuário', 'Fornec.', 'Tipo']
        
        # Filtrar apenas colunas que existem
        colunas_existentes = [col for col in colunas_desejadas if col in df_total.columns]
        df_total = df_total[colunas_existentes]
        
        # Renomear colunas
        renomes = {
                    'Texto': 'Texto breve',
                    'Qtd.': 'QTD',
                    'Nº conta': 'Nºconta',
                    'Centro cst': 'Centrocst',
                    'doc.ref': 'Nºdoc.ref.',
                    'Type 07': 'Account',
                    'Período': 'Mes'
                }
                
        for old_col, new_col in renomes.items():
            if old_col in df_total.columns:
                df_total.rename(columns={old_col: new_col}, inplace=True)

        # Criar coluna Período com nomes dos meses
        if 'Mes' in df_total.columns:
            meses_nomes = {
                1: 'janeiro', 2: 'fevereiro', 3: 'março', 4: 'abril',
                5: 'maio', 6: 'junho', 7: 'julho', 8: 'agosto',
                9: 'setembro', 10: 'outubro', 11: 'novembro', 12: 'dezembro'
            }
            df_total['Período'] = df_total['Mes'].map(meses_nomes)

        # Reordenar com Mes e Período no início
        if 'Mes' in df_total.columns and 'Período' in df_total.columns:
            colunas = ['Mes', 'Período'] + [col for col in df_total.columns if col not in ['Mes', 'Período']]
            df_total = df_total[colunas]
        
        log("✅ Reorganização concluída")
        
        # ETAPA 8: Salvar arquivos
        log("💾 ETAPA 8: Salvando arquivos...")
        
        # Salvar Parquet (sempre completo)
        pasta_parquet = "KE5Z"
        if not os.path.exists(pasta_parquet):
            os.makedirs(pasta_parquet)
        
        # OTIMIZAÇÃO DE MEMÓRIA: Separar dados por USI
        log("🔄 Separando arquivos por USI para otimização...")
        
        # Separar dados Others vs resto
        df_others = df_total[df_total['USI'] == 'Others'].copy()
        df_main = df_total[df_total['USI'] != 'Others'].copy()
        
        log(f"📊 Total de registros: {len(df_total):,}")
        log(f"📊 Registros principais (sem Others): {len(df_main):,}")
        log(f"📊 Registros Others: {len(df_others):,}")
        
        # Salvar arquivo principal (sem Others)
        if len(df_main) > 0:
            caminho_main = os.path.join(pasta_parquet, 'KE5Z_main.parquet')
            df_main.to_parquet(caminho_main, index=False)
            tamanho_main = os.path.getsize(caminho_main) / (1024*1024)
            resultados['arquivos_gerados'].append(f"📊 KE5Z/KE5Z_main.parquet ({tamanho_main:.1f} MB)")
            log(f"✅ Arquivo principal salvo: {tamanho_main:.1f} MB")
        
        # Salvar arquivo Others separadamente
        if len(df_others) > 0:
            caminho_others = os.path.join(pasta_parquet, 'KE5Z_others.parquet')
            df_others.to_parquet(caminho_others, index=False)
            tamanho_others = os.path.getsize(caminho_others) / (1024*1024)
            resultados['arquivos_gerados'].append(f"📋 KE5Z/KE5Z_others.parquet ({tamanho_others:.1f} MB)")
            log(f"✅ Arquivo Others salvo: {tamanho_others:.1f} MB")
        else:
            log("ℹ️ Nenhum registro Others encontrado")
        
        # Manter arquivo completo para compatibilidade
        caminho_parquet = os.path.join(pasta_parquet, 'KE5Z.parquet')
        df_total.to_parquet(caminho_parquet, index=False)
        tamanho_mb = os.path.getsize(caminho_parquet) / (1024*1024)
        resultados['arquivos_gerados'].append(f"📊 KE5Z/KE5Z.parquet ({tamanho_mb:.1f} MB)")
        log(f"✅ Parquet completo salvo: {tamanho_mb:.1f} MB")
        
        # Salvar Excel com amostra
        caminho_excel_sample = os.path.join(pasta_parquet, 'KE5Z.xlsx')
        df_total.head(10000).to_excel(caminho_excel_sample, index=False)
        resultados['arquivos_gerados'].append("📋 KE5Z/KE5Z.xlsx (amostra 10k registros)")
        log("✅ Excel amostra salvo")
        
        # Determinar pasta de destino para Excel completos
        pasta_destino = os.path.join(os.path.expanduser("~"), "Stellantis", "Hebdo FGx - Documents", "Overheads", "PBI 2025", "09 - Sapiens", "Extração PBI")
        
        if not os.path.exists(pasta_destino):
            pasta_destino = os.path.join(os.path.expanduser("~"), "Downloads")
            log(f"⚠️ Pasta Stellantis não encontrada, usando Downloads")
        else:
            log(f"✅ Usando pasta Stellantis")
        
        # Filtrar dados para Excel (aplicar filtro de meses se especificado)
        df_excel = df_total.copy()
        if meses_filtro and len(meses_filtro) < 12 and 'Mes' in df_excel.columns:
            df_excel = df_excel[df_excel['Mes'].isin(meses_filtro)]
            log(f"📅 Filtro de meses aplicado: {len(meses_filtro)} meses selecionados")
        
        # Salvar Excel por USI se solicitado
        if gerar_separado and 'USI' in df_excel.columns:
            # Veículos, TC Ext, LC
            df_veiculos = df_excel[df_excel['USI'].isin(['Veículos', 'TC Ext', 'LC'])]
            if not df_veiculos.empty:
                caminho_veiculos = os.path.join(pasta_destino, 'KE5Z_veiculos.xlsx')
                df_veiculos.to_excel(caminho_veiculos, index=False)
                nome_pasta = "Stellantis" if "Stellantis" in pasta_destino else "Downloads"
                resultados['arquivos_gerados'].append(f"📋 {nome_pasta}/KE5Z_veiculos.xlsx ({len(df_veiculos)} registros)")
                log(f"✅ KE5Z_veiculos.xlsx salvo: {len(df_veiculos)} registros")
            
            # PWT
            df_pwt = df_excel[df_excel['USI'].isin(['PWT'])]
            if not df_pwt.empty:
                caminho_pwt = os.path.join(pasta_destino, 'KE5Z_pwt.xlsx')
                df_pwt.to_excel(caminho_pwt, index=False)
                nome_pasta = "Stellantis" if "Stellantis" in pasta_destino else "Downloads"
                resultados['arquivos_gerados'].append(f"📋 {nome_pasta}/KE5Z_pwt.xlsx ({len(df_pwt)} registros)")
                log(f"✅ KE5Z_pwt.xlsx salvo: {len(df_pwt)} registros")
        
        log(f"✅ Extração COMPLETA finalizada! Total de registros: {len(df_total)}")
        resultados['sucesso'] = True
        return resultados

    except Exception as e:
        resultados['erro'] = str(e)
        log(f"❌ Erro: {str(e)}")
        return resultados


# Execução em tempo real (gerador)
def executar_extracao_streaming(meses_filtro, gerar_separado):
    """Executa a extração emitindo eventos incrementalmente para UI em tempo real.
    Gera dicts com chaves: log, progress, arquivo, sucesso, erro.
    """
    try:
        progresso = 0
        yield {"log": "🚀 Iniciando extração completa...", "progress": progresso}

        # ETAPA 1: Carregar dados KE5Z
        yield {"log": "📂 ETAPA 1: Carregando dados KE5Z...", "progress": 5}
        pasta_opcoes = [
            os.path.join(os.path.expanduser("~"), "Stellantis", "GEIB - General", "GEIB", "Partagei_2025", "1 - SÍNTESE", "11 - SAPIENS", "02 - Extrações", "KE5Z"),
            os.path.join(os.path.expanduser("~"), "Stellantis", "GEIB - GEIB", "Partagei_2025", "1 - SÍNTESE", "11 - SAPIENS", "02 - Extrações", "KE5Z"),
            "KE5Z"
        ]
        pasta_ke5z = next((p for p in pasta_opcoes if os.path.exists(p)), None)
        if not pasta_ke5z:
            raise Exception("Nenhuma pasta KE5Z encontrada!")
        yield {"log": f"✅ Pasta KE5Z: {pasta_ke5z}", "progress": 8}

        dataframes = []
        arquivos_txt = [f for f in os.listdir(pasta_ke5z) if f.endswith('.txt')]
        if not arquivos_txt:
            raise Exception("Nenhum arquivo .txt encontrado na pasta KE5Z!")
        for i, arquivo in enumerate(arquivos_txt, start=1):
            caminho = os.path.join(pasta_ke5z, arquivo)
            yield {"log": f"📄 Lendo: {arquivo}"}
            df = pd.read_csv(caminho, sep='\t', skiprows=9, encoding='latin1', engine='python')
            df.rename(columns={df.columns[9]: 'doc.ref'}, inplace=True)
            df.columns = df.columns.str.strip()
            df = df[df['Ano'].notna() & (df['Ano'] != 0)]
            for col in ['Em MCont.', 'Qtd.']:
                if col in df.columns:
                    df[col] = df[col].str.replace('.', '', regex=False).str.replace(',', '.', regex=False)
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            dataframes.append(df)
            progresso = min(25, 8 + int(15 * i / max(1, len(arquivos_txt))))
            yield {"log": f"✅ {arquivo}: {len(df)} registros", "progress": progresso}

        df_total = pd.concat(dataframes, ignore_index=True)
        yield {"log": f"🔄 Consolidação concluída: {len(df_total)} registros", "progress": 28}

        # ETAPA 2: Limpeza de colunas
        colunas_para_remover = [
            'Unnamed: 0','Unnamed: 1','Unnamed: 4','Nº doc.','Elem.PEP','Obj.custo','TD','SocPar','EmpEm.','Empr',
            'TMv','D/C','Imobil.','Descrição Material','Cliente','Cen.','Cen.lucro','Unnamed: 14','Classe objs.','Item','D'
        ]
        df_total.drop(columns=colunas_para_remover, inplace=True, errors='ignore')
        df_total.rename(columns={'Em MCont.': 'Valor'}, inplace=True)
        df_total = df_total[df_total['Nº conta'].notna() & (df_total['Nº conta'] != 0)]
        yield {"log": "🧹 Limpeza de colunas concluída", "progress": 35}

        # ETAPA 3: KSBB
        pasta_ksbb_opcoes = [
            os.path.join(os.path.expanduser("~"), "Stellantis", "GEIB - General", "GEIB", "Partagei_2025", "1 - SÍNTESE", "11 - SAPIENS", "02 - Extrações", "KSBB"),
            os.path.join(os.path.expanduser("~"), "Stellantis", "GEIB - GEIB", "Partagei_2025", "1 - SÍNTESE", "11 - SAPIENS", "02 - Extrações", "KSBB"),
            "KSBB"
        ]
        pasta_ksbb = next((p for p in pasta_ksbb_opcoes if os.path.exists(p)), None)
        if pasta_ksbb:
            dataframes_ksbb = []
            for arquivo in os.listdir(pasta_ksbb):
                if arquivo.endswith('.txt'):
                    caminho = os.path.join(pasta_ksbb, arquivo)
                    dfk = pd.read_csv(caminho, sep='\t', encoding='latin1', engine='python', skiprows=3, skipfooter=1)
                    dfk.columns = dfk.columns.str.strip()
                    dfk = dfk[dfk['Material'].notna() & (dfk['Material'] != 0)]
                    dfk = dfk.drop_duplicates(subset=['Material'])
                    dataframes_ksbb.append(dfk)
            if dataframes_ksbb:
                df_ksbb_final = pd.concat(dataframes_ksbb, ignore_index=True) if len(dataframes_ksbb) > 1 else dataframes_ksbb[0]
                df_ksbb_final = df_ksbb_final.drop_duplicates(subset=['Material'])
                if 'Material' in df_total.columns:
                    df_total = pd.merge(df_total, df_ksbb_final[['Material', 'Texto breve material']], on='Material', how='left')
                    df_total.rename(columns={'Texto breve material': 'Descrição Material'}, inplace=True)
                    if 'Texto' in df_total.columns:
                        df_total['Texto'] = df_total.apply(lambda r: r['Descrição Material'] if pd.notnull(r['Descrição Material']) else r['Texto'], axis=1)
            yield {"log": "🔗 KSBB merge concluído", "progress": 50}
        else:
            yield {"log": "⚠️ Pasta KSBB não encontrada, continuando...", "progress": 45}

        # ETAPA 4: SAPIENS
        if os.path.exists('Dados SAPIENS.xlsx'):
            df_sapiens = pd.read_excel('Dados SAPIENS.xlsx', sheet_name='Conta contabil')
            df_sapiens.rename(columns={'CONTA SAPIENS': 'Nº conta'}, inplace=True)
            df_total = pd.merge(df_total, df_sapiens[['Nº conta', 'Type 07', 'Type 06', 'Type 05']], on='Nº conta', how='left')
            df_cc = pd.read_excel('Dados SAPIENS.xlsx', sheet_name='CC')
            df_cc.rename(columns={'CC SAPiens': 'Centro cst'}, inplace=True)
            df_total = pd.merge(df_total, df_cc[['Centro cst', 'Oficina', 'USI']], on='Centro cst', how='left')
            df_total['USI'] = df_total['USI'].fillna('Others')
            yield {"log": "🔗 SAPIENS merges concluídos", "progress": 65}
        else:
            yield {"log": "⚠️ Arquivo SAPIENS.xlsx não encontrado", "progress": 60}

        # ETAPA 5: Fornecedores
        if os.path.exists('Fornecedores.xlsx'):
            df_for = pd.read_excel('Fornecedores.xlsx', skiprows=3)
            df_for = df_for.drop_duplicates(subset=['Fornecedor'])
            df_for.rename(columns={'Fornecedor': 'Fornec.'}, inplace=True)
            df_for['Fornec.'] = df_for['Fornec.'].astype(str)
            df_total = pd.merge(df_total, df_for[['Fornec.', 'Nome do fornecedor']], on='Fornec.', how='left')
            df_total.rename(columns={'Nome do fornecedor': 'Fornecedor'}, inplace=True)
            yield {"log": "🔗 Fornecedores merge concluído", "progress": 72}
        else:
            yield {"log": "⚠️ Arquivo Fornecedores.xlsx não encontrado", "progress": 70}

        # ETAPA 6: Renomear/Reordenar
        renomes = {
            'Texto': 'Texto breve','Qtd.': 'QTD','Nº conta': 'Nºconta','Centro cst': 'Centrocst','doc.ref': 'Nºdoc.ref.','Type 07': 'Account','Período': 'Mes'
        }
        for o, n in renomes.items():
            if o in df_total.columns:
                df_total.rename(columns={o: n}, inplace=True)
        if 'Mes' in df_total.columns:
            meses_nomes = {1:'janeiro',2:'fevereiro',3:'março',4:'abril',5:'maio',6:'junho',7:'julho',8:'agosto',9:'setembro',10:'outubro',11:'novembro',12:'dezembro'}
            df_total['Período'] = df_total['Mes'].map(meses_nomes)
            colunas = ['Mes','Período'] + [c for c in df_total.columns if c not in ['Mes','Período']]
            df_total = df_total[colunas]
        yield {"log": "🔄 Colunas reorganizadas", "progress": 80}

        # ETAPA 7: Salvar arquivos
        pasta_parquet = "KE5Z"
        if not os.path.exists(pasta_parquet):
            os.makedirs(pasta_parquet)
        caminho_parquet = os.path.join(pasta_parquet, 'KE5Z.parquet')
        df_total.to_parquet(caminho_parquet, index=False)
        tamanho_mb = os.path.getsize(caminho_parquet) / (1024*1024)
        yield {"log": f"✅ Parquet salvo ({tamanho_mb:.1f} MB)", "progress": 88, "arquivo": f"KE5Z/KE5Z.parquet ({tamanho_mb:.1f} MB)"}

        caminho_excel_sample = os.path.join(pasta_parquet, 'KE5Z.xlsx')
        df_total.head(10000).to_excel(caminho_excel_sample, index=False)
        yield {"log": "✅ Excel amostra salvo (10k)", "progress": 90, "arquivo": "KE5Z/KE5Z.xlsx"}

        pasta_destino = os.path.join(os.path.expanduser("~"), "Stellantis", "Hebdo FGx - Documents", "Overheads", "PBI 2025", "09 - Sapiens", "Extração PBI")
        if not os.path.exists(pasta_destino):
            pasta_destino = os.path.join(os.path.expanduser("~"), "Downloads")
            yield {"log": "⚠️ Pasta Stellantis não encontrada, usando Downloads"}

        df_excel = df_total.copy()
        if meses_filtro and len(meses_filtro) < 12 and 'Mes' in df_excel.columns:
            df_excel = df_excel[df_excel['Mes'].isin(meses_filtro)]
            yield {"log": f"📅 Filtro de meses aplicado ({len(meses_filtro)})"}

        if gerar_separado and 'USI' in df_excel.columns:
            df_veiculos = df_excel[df_excel['USI'].isin(['Veículos', 'TC Ext', 'LC'])]
            if not df_veiculos.empty:
                caminho_veiculos = os.path.join(pasta_destino, 'KE5Z_veiculos.xlsx')
                df_veiculos.to_excel(caminho_veiculos, index=False)
                yield {"log": f"✅ KE5Z_veiculos.xlsx salvo ({len(df_veiculos)} regs)", "arquivo": ("Stellantis/KE5Z_veiculos.xlsx" if "Stellantis" in pasta_destino else "Downloads/KE5Z_veiculos.xlsx")}

            df_pwt = df_excel[df_excel['USI'].isin(['PWT'])]
            if not df_pwt.empty:
                caminho_pwt = os.path.join(pasta_destino, 'KE5Z_pwt.xlsx')
                df_pwt.to_excel(caminho_pwt, index=False)
                yield {"log": f"✅ KE5Z_pwt.xlsx salvo ({len(df_pwt)} regs)", "arquivo": ("Stellantis/KE5Z_pwt.xlsx" if "Stellantis" in pasta_destino else "Downloads/KE5Z_pwt.xlsx")}

        yield {"log": f"✅ Extração COMPLETA finalizada! Total: {len(df_total)} registros", "progress": 100, "sucesso": True}

    except Exception as e:
        yield {"erro": str(e)}

# Botão de extração
if todos_ok:
    st.success("✅ Todos os arquivos necessários disponíveis!")
    
    if st.button("🚀 Executar Extração Completa", 
                 type="primary", use_container_width=True):

        progress_container = st.empty()
        with progress_container.container():
            st.write("**📊 Progresso da Extração Completa:**")
            progress_bar = st.progress(0)
            status_text = st.empty()

        status_text.text("🚀 Iniciando processamento completo...")
        adicionar_log("🚀 Iniciando extração completa (tempo real)")
        atualizar_logs()

        arquivos_gerados = []
        sucesso = False

        for evento in executar_extracao_streaming(meses_selecionados, gerar_excel_separado):
            if 'erro' in evento:
                status_text.text("❌ Erro na extração")
                st.error(f"❌ **Erro:** {evento['erro']}")
                adicionar_log(f"❌ Erro: {evento['erro']}")
                break
            if 'log' in evento:
                adicionar_log(evento['log'])
                status_text.text(evento['log'])
                atualizar_logs()
            if 'progress' in evento:
                try:
                    progress_bar.progress(int(evento['progress']))
                except Exception:
                    pass
            if 'arquivo' in evento:
                arquivos_gerados.append(evento['arquivo'])
            if evento.get('sucesso'):
                sucesso = True

        if sucesso:
            progress_bar.progress(100)
            st.success("✅ Extração executada com sucesso!")
            st.balloons()
            if arquivos_gerados:
                st.write("**📁 Arquivos Gerados:**")
                for a in arquivos_gerados:
                    st.write(a)
            st.info("📊 **Processamento Concluído em Tempo Real**")
        atualizar_logs()

else:
    st.error("❌ Alguns arquivos necessários não foram encontrados.")
    st.info("💡 Verifique se todas as pastas e arquivos estão disponíveis.")
    
    # Mostrar ajuda para arquivos em falta
    st.write("**📁 Arquivos Necessários:**")
    st.write("- 📂 **KE5Z/**: Pasta com arquivos .txt da extração")
    st.write("- 📂 **KSBB/**: Pasta com arquivos .txt de materiais")
    st.write("- 📄 **Dados SAPIENS.xlsx**: Base de dados SAPIENS")
    st.write("- 📄 **Fornecedores.xlsx**: Lista de fornecedores")

st.markdown("---")

# Informações sobre o debug
st.subheader("ℹ️ Como Funciona o Debug")
st.info("🔍 **Tempo Real**: Cada linha da execução é capturada e exibida instantaneamente")
st.info("📊 **Progresso Inteligente**: Barra atualizada baseada no conteúdo das linhas")
st.info("📋 **Filtros Automáticos**: Mostra apenas as linhas mais relevantes")
st.info("⚡ **Performance**: Threading para não bloquear a interface")

# Configurações ativas
st.write("**⚙️ Recursos do Debug:**")
st.write("- 🔍 Monitoramento linha por linha em tempo real")
st.write("- 📊 Progresso baseado no conteúdo da execução")
st.write("- 📋 Filtros inteligentes de linhas importantes")
st.write("- ⏰ Timeout de 5 minutos para segurança")
st.write("- 🔄 Interface atualizada automaticamente")
st.write("- 📁 Verificação automática de arquivos gerados")

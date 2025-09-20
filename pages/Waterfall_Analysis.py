import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os
import sys

# Adicionar diretório pai ao path para importar auth_simple
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from auth_simple import (verificar_autenticacao, exibir_header_usuario, 
                         verificar_status_aprovado, is_modo_cloud, get_modo_operacao)

st.set_page_config(page_title="Análise Waterfall - KE5Z", page_icon="🌊", layout="wide", initial_sidebar_state="auto")
verificar_autenticacao()
exibir_header_usuario()
st.title("🌊 Análise Waterfall - KE5Z")
st.markdown("---")

PT_MESES = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"]
MES_POS = {m: i + 1 for i, m in enumerate(PT_MESES)}

def sort_mes_unique(values):
    vals = list(pd.Series(values).dropna().unique())
    try:
        return sorted(vals, key=lambda x: int(x))
    except Exception:
        return sorted(vals, key=lambda x: MES_POS.get(str(x).lower(), 99))

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

# Widget de seleção
opcao_selecionada = st.sidebar.selectbox(
    "Escolha o conjunto de dados:",
    options=[op[1] for op in opcoes_dados],
    format_func=lambda x: next(op[0] for op in opcoes_dados if op[1] == x),
    index=0  # Padrão: primeiro disponível
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

@st.cache_data(ttl=3600, max_entries=3, persist="disk")
def load_df(arquivo_tipo="completo") -> pd.DataFrame:
    """Carrega dados com otimização inteligente de memória - WATERFALL OTIMIZADO"""
    
    # PRIORIDADE 1: Tentar arquivo waterfall otimizado (72% menor!)
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
            
            st.sidebar.success("⚡ **WATERFALL OTIMIZADO**\nUsando arquivo 72% menor!")
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
    caminho = os.path.join("KE5Z", nome_arquivo)
    
    if not os.path.exists(caminho):
        # Se arquivo específico não existe, tentar arquivo completo
        if arquivo_tipo != "completo":
            st.warning(f"⚠️ Arquivo {nome_arquivo} não encontrado, carregando dados completos...")
            return load_df("completo")
        st.error(f"❌ Arquivo não encontrado: {caminho}")
        return pd.DataFrame()
    
    try:
        df = pd.read_parquet(caminho)
        # Compactar memória sem alterar dados
        try:
            for col in df.columns:
                if df[col].dtype == 'object':
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
    except Exception as exc:
        st.error(f"Erro ao ler parquet: {exc}")
        return pd.DataFrame()

# Carregar dados
df_base = load_df(opcao_selecionada)
if df_base.empty:
    st.stop()

# Mostrar informações de carregamento
st.sidebar.success("✅ Dados carregados com sucesso")
if not is_cloud:
    st.sidebar.info(f"📊 {len(df_base)} registros carregados")

# Aplicar filtros padrão do projeto
st.sidebar.title("Filtros")

# Filtro 1: USINA
usina_opcoes = ["Todos"] + sorted(df_base['USI'].dropna().astype(str).unique().tolist()) if 'USI' in df_base.columns else ["Todos"]
default_usina = ["Veículos"] if "Veículos" in usina_opcoes else ["Todos"]
usina_selecionada = st.sidebar.multiselect("Selecione a USINA:", usina_opcoes, default=default_usina)

# Filtrar o DataFrame com base na USI
if "Todos" in usina_selecionada or not usina_selecionada:
    df_filtrado = df_base.copy()
else:
    df_filtrado = df_base[df_base['USI'].astype(str).isin(usina_selecionada)]

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

# Exibir informações dos filtros
st.sidebar.write(f"Número de linhas: {df_filtrado.shape[0]}")
st.sidebar.write(f"Número de colunas: {df_filtrado.shape[1]}")
st.sidebar.write(f"Soma do Valor total: R$ {df_filtrado['Valor'].sum():,.2f}")

# --- Configurações do waterfall ---
mes_unicos = sort_mes_unique(df_filtrado["Período"].astype(str)) if "Período" in df_filtrado.columns else sort_mes_unique(df_filtrado["mes"].astype(str))
col_valor = next((c for c in ["valor", "Valor", "Total_Value"] if c in df_filtrado.columns), None)
col_mes = "Período" if "Período" in df_filtrado.columns else ("mes" if "mes" in df_filtrado.columns else None)

# Dimensão de categoria no mesmo padrão da IA_Unificada
dims_cat = [c for c in ["categoria", "Type 05", "Type 06", "Type 07", "Fornecedor", "USI"] if c in df_filtrado.columns]
if not dims_cat or not col_valor or not col_mes:
    st.error("Colunas necessárias não encontradas.")
    st.stop()
chosen_dim = st.selectbox("Dimensão da categoria:", dims_cat, index=0)

col_a, col_b = st.columns(2)
with col_a:
    mes_inicial = st.selectbox("Mês inicial:", mes_unicos, index=0)
with col_b:
    mes_final = st.selectbox("Mês final:", mes_unicos, index=len(mes_unicos) - 1)

# Normalizar categorias (strings limpas) e garantir defaults válidos
cats_all = sorted([str(x).strip() for x in df_filtrado[chosen_dim].dropna().unique().tolist() if str(x).strip() != ""])
total_cats = max(1, len(cats_all))
max_cats = st.slider(f"Quantidade de categorias a exibir (Top N) (Total: {total_cats}):", 1, total_cats, total_cats)
vol_mf = (df_filtrado[df_filtrado[col_mes].astype(str) == str(mes_final)].groupby(chosen_dim)[col_valor].sum().sort_values(ascending=False))
vol_index = [str(c).strip() for c in list(vol_mf.index)]
default_cats = vol_index[:max_cats] if len(vol_index) else cats_all[:max_cats]

cats_options = ["Todos"] + cats_all
# Filtrar defaults não presentes; fallback seguro
default_cats = [c for c in default_cats if c in cats_all]
if not default_cats:
    default_cats = cats_all[:min(10, len(cats_all))]

cats_sel_raw = st.multiselect("Categorias (uma ou mais):", cats_options, default=default_cats)
if (not cats_sel_raw) or ("Todos" in cats_sel_raw):
    # Quando "Todos" é selecionado, usar TODAS as categorias disponíveis (limitado pelo slider max_cats)
    cats_sel = cats_all[:max_cats] if max_cats < len(cats_all) else cats_all
else:
    cats_sel = cats_sel_raw

if mes_inicial == mes_final:
    st.info("Selecione meses diferentes para comparar.")
    st.stop()

# Totais de mês (todas as categorias do df_filtrado)
total_m1_all = float(df_filtrado[df_filtrado[col_mes].astype(str) == str(mes_inicial)][col_valor].sum())
total_m2_all = float(df_filtrado[df_filtrado[col_mes].astype(str) == str(mes_final)][col_valor].sum())
change_all = total_m2_all - total_m1_all

# Filtrar pelas selecionadas
dff = df_filtrado[df_filtrado[chosen_dim].astype(str).isin(cats_sel)].copy()

g1 = (dff[dff[col_mes].astype(str) == str(mes_inicial)].groupby(chosen_dim)[col_valor].sum())
g2 = (dff[dff[col_mes].astype(str) == str(mes_final)].groupby(chosen_dim)[col_valor].sum())

labels_cats, values_cats = [], []
for cat in sorted(set(g1.index).union(set(g2.index))):
    delta = float(g2.get(cat, 0.0)) - float(g1.get(cat, 0.0))
    if abs(delta) > 1e-9:
        labels_cats.append(str(cat))
        values_cats.append(delta)

original_len = len(labels_cats)
if len(labels_cats) > max_cats:
    idx = sorted(range(len(values_cats)), key=lambda i: abs(values_cats[i]), reverse=True)[:max_cats]
    labels_cats = [labels_cats[i] for i in idx]
    values_cats = [values_cats[i] for i in idx]
cropped = len(labels_cats) < original_len

remainder = round(change_all - sum(values_cats), 2)
# Mostrar "Outros" quando há mais categorias do que as exibidas ou quando foi aplicado filtro Top N
all_selected = len(cats_sel) >= len(cats_all)
show_outros = (abs(remainder) >= 0.01) and (cropped or not all_selected or len(cats_sel) < len(cats_all))
if show_outros:
    labels_cats.append("Outros")
    values_cats.append(remainder)

labels = [f"Mês {mes_inicial}"] + labels_cats + [f"Mês {mes_final}"]
values = [total_m1_all] + values_cats + [total_m2_all]
measures = ["absolute"] + ["relative"] * len(values_cats) + ["total"]

# Tema do Streamlit para cores
theme_base = st.get_option("theme.base") or "light"
text_color = st.get_option("theme.textColor") or ("#FAFAFA" if theme_base == "dark" else "#000000")
grid_color = "rgba(255,255,255,0.12)" if theme_base == "dark" else "rgba(0,0,0,0.12)"
connector_color = "rgba(255,255,255,0.35)" if theme_base == "dark" else "rgba(0,0,0,0.35)"

# Waterfall principal
fig = go.Figure(go.Waterfall(
    name="Variação",
    orientation="v",
    measure=measures,
    x=labels,
    y=values,
    text=[f"R$ {v:,.2f}" for v in values],
    textposition="outside",
    connector={"line": {"color": connector_color}},
    increasing={"marker": {"color": "#27ae60"}},
    decreasing={"marker": {"color": "#e74c3c"}},
    totals={"marker": {"color": "#4e79a7"}},
))

# Rótulos de dados: branco no dark, preto no light
fig.update_traces(textfont=dict(color=text_color))

# Overlay 'Outros' em preto
if show_outros:
    prev_sum = sum(v for lab, v in zip(labels_cats, values_cats) if lab != "Outros")
    cum_before = total_m1_all + prev_sum
    base_val = cum_before if remainder >= 0 else cum_before + remainder
    height = abs(remainder)
    fig.add_trace(go.Bar(x=["Outros"], y=[height], base=[base_val], marker_color="#ff9800", opacity=1.0, hoverinfo="skip", showlegend=False))
    fig.update_layout(barmode="overlay")

# Template e fundos transparentes para herdar cor do app
fig.update_layout(template="plotly_dark" if theme_base == "dark" else "plotly_white")
fig.update_layout(
    title={"text": f"Variação Financeira - Mês {mes_inicial} para Mês {mes_final}", "x": 0.5},
    xaxis_title="Mês / Categoria",
    yaxis_title="Valor (R$)",
    height=560,
    showlegend=False,
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    font=dict(color=text_color),
    xaxis=dict(gridcolor=grid_color, zerolinecolor=grid_color, linecolor=grid_color),
    yaxis=dict(gridcolor=grid_color, zerolinecolor=grid_color, linecolor=grid_color),
)
fig.update_yaxes(tickformat=",.0f", tickprefix="R$ ")

st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.markdown("**📊 Dashboard KE5Z - Análise Waterfall** | Desenvolvido com Streamlit")
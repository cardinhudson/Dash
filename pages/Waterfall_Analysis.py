import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os
from auth_simple import verificar_autenticacao, exibir_header_usuario

st.set_page_config(page_title="Análise Waterfall - KE5Z", page_icon="🌊", layout="wide", initial_sidebar_state="expanded")
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

# Sistema de cache otimizado para Waterfall_Analysis
@st.cache_data(
    show_spinner=True,
    max_entries=1,
    ttl=1800,  # Cache por 30 minutos
    persist="disk"  # Salvar em disco para liberar RAM
)
def load_df() -> pd.DataFrame:
    """Carrega dados com otimização de performance para Waterfall"""
    caminho = os.path.join("KE5Z", "KE5Z.parquet")
    if not os.path.exists(caminho):
        st.error("❌ Arquivo KE5Z/KE5Z.parquet não encontrado.")
        return pd.DataFrame()
    try:
        df = pd.read_parquet(caminho)
        
        # Otimizar tipos de dados para melhor performance
        for col in df.columns:
            if df[col].dtype == 'object':
                unique_ratio = df[col].nunique() / len(df)
                if unique_ratio < 0.5:
                    df[col] = df[col].astype('category')
        
        return df
    except Exception as exc:
        st.error(f"Erro ao ler parquet: {exc}")
        return pd.DataFrame()

df_base = load_df()
if df_base.empty:
    st.stop()

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

# Filtros adicionais
for col_name, label in [("Fornecedor", "Fornecedor"), ("Fornec.", "Fornec."), ("Tipo", "Tipo"), ("Type 05", "Type 05"), ("Type 06", "Type 06"), ("Type 07", "Type 07")]:
    if col_name in df_filtrado.columns:
        opcoes = ["Todos"] + sorted(df_filtrado[col_name].dropna().astype(str).unique().tolist())
        selecionadas = st.sidebar.multiselect(f"Selecione o {label}:", opcoes, default=["Todos"])
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

cats_all = sorted(df_base[chosen_dim].dropna().astype(str).unique().tolist())
total_cats = max(1, len(cats_all))
max_cats = st.slider(f"Quantidade de categorias a exibir (Top N) (Total: {total_cats}):", 1, total_cats, total_cats)
vol_mf = (df_base[df_base[col_mes].astype(str) == str(mes_final)].groupby(chosen_dim)[col_valor].sum().sort_values(ascending=False))
default_cats = [c for c in vol_mf.index[:max_cats]] if len(vol_mf) else cats_all[:max_cats]

cats_options = ["Todos"] + cats_all
cats_sel_raw = st.multiselect("Categorias (uma ou mais):", cats_options, default=default_cats)
if (not cats_sel_raw) or ("Todos" in cats_sel_raw):
    cats_sel = cats_all
else:
    cats_sel = cats_sel_raw

if mes_inicial == mes_final:
    st.info("Selecione meses diferentes para comparar.")
    st.stop()

# Totais de mês (todas as categorias)
total_m1_all = float(df_base[df_base[col_mes].astype(str) == str(mes_inicial)][col_valor].sum())
total_m2_all = float(df_base[df_base[col_mes].astype(str) == str(mes_final)][col_valor].sum())
change_all = total_m2_all - total_m1_all

# Filtrar pelas selecionadas
dff = df_base[df_base[chosen_dim].astype(str).isin(cats_sel)].copy()

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
all_selected = set(cats_sel) == set(cats_all)
show_outros = (abs(remainder) >= 0.01) and (not all_selected or cropped)
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
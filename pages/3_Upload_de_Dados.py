import sys
from pathlib import Path

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import streamlit as st

sys.path.append(str(Path(__file__).parent.parent))

from utils import moeda

st.set_page_config(page_title="Upload de Dados", page_icon="📁", layout="wide")
sns.set_theme(style="whitegrid")

st.title("📁 Upload de apurações (CSV)")
st.markdown(
    "**Problema:** o escritório recebe planilhas de faturamento dos clientes e precisa de uma análise rápida. "
    "Envie um CSV com as colunas **competencia** (AAAA-MM), **faturamento** e **despesas**."
)

modelo = pd.DataFrame({
    "competencia": ["2026-01", "2026-02", "2026-03"],
    "faturamento": [50000, 52000, 61000],
    "despesas": [32000, 33000, 40000],
})
st.download_button("Baixar modelo de CSV", modelo.to_csv(index=False).encode("utf-8"), "modelo_apuracoes.csv")

arquivo = st.file_uploader("Selecione o arquivo CSV", type=["csv"])

if arquivo is not None:
    try:
        dados = pd.read_csv(arquivo)
    except Exception as erro:
        st.error(f"Não foi possível ler o arquivo: {erro}")
        st.stop()

    faltando = {"competencia", "faturamento", "despesas"} - set(dados.columns)
    if faltando:
        st.error(f"Colunas ausentes: {', '.join(sorted(faltando))}")
        st.stop()

    dados["faturamento"] = pd.to_numeric(dados["faturamento"], errors="coerce")
    dados["despesas"] = pd.to_numeric(dados["despesas"], errors="coerce")
    dados = dados.dropna(subset=["competencia", "faturamento", "despesas"])
    dados["lucro"] = dados["faturamento"] - dados["despesas"]
    dados["margem_%"] = dados["lucro"] / dados["faturamento"] * 100

    c1, c2, c3 = st.columns(3)
    c1.metric("Faturamento total", moeda(dados["faturamento"].sum()))
    c2.metric("Lucro total", moeda(dados["lucro"].sum()))
    c3.metric("Margem média", f"{dados['margem_%'].mean():.1f}%")

    st.dataframe(dados, use_container_width=True, hide_index=True)

    fig, ax = plt.subplots(figsize=(10, 4))
    sns.barplot(data=dados, x="competencia", y="faturamento", ax=ax, color="#4c78a8", label="Faturamento")
    sns.lineplot(data=dados, x="competencia", y="despesas", ax=ax, color="#e45756", marker="o", label="Despesas")
    ax.set_xlabel("Competência")
    ax.set_ylabel("Valor (R$)")
    st.pyplot(fig)

    pior = dados.loc[dados["margem_%"].idxmin()]
    st.info(
        f"**Interpretação:** a menor margem foi em {pior['competencia']} ({pior['margem_%']:.1f}%). "
        "Meses com margem baixa merecem revisão de despesas e do regime tributário."
    )
else:
    st.info("Aguardando o envio de um arquivo.")

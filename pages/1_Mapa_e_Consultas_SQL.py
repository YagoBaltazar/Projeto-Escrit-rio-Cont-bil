import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import streamlit as st

sys.path.append(str(Path(__file__).parent.parent))

from utils import INDICADORES, numero

st.set_page_config(page_title="Upload de CSV", page_icon="📁", layout="wide")
sns.set_theme(style="whitegrid")

COLUNAS = [
    "ano", "mes", "data", "regiao", "uf", "municipio", "expectativa_vida", "taxa_mortalidade",
    "taxa_internacao", "cobertura_vacinal", "medicos_por_1000", "leitos_hospitalares",
    "casos_doencas_cronicas", "nivel_criticidade",
]

st.title("📁 Upload de CSV")
st.markdown(
    "**Problema:** e se chegar uma nova base de indicadores de saúde? Envie um CSV com as mesmas colunas da base "
    "do projeto e veja uma análise rápida."
)
st.caption("Colunas esperadas: " + ", ".join(COLUNAS))

arquivo = st.file_uploader("Selecione o arquivo CSV", type=["csv"])

if arquivo is None:
    st.info("Aguardando o envio de um arquivo.")
    st.stop()

try:
    dados = pd.read_csv(arquivo, encoding="utf-8-sig")
except Exception as erro:
    st.error(f"Não foi possível ler o arquivo: {erro}")
    st.stop()

faltando = [c for c in COLUNAS if c not in dados.columns]
if faltando:
    st.error("Colunas ausentes: " + ", ".join(faltando))
    st.stop()

antes = len(dados)
dados = dados.drop_duplicates().dropna(subset=COLUNAS)
st.success(f"Arquivo carregado: {len(dados)} registros válidos ({antes - len(dados)} removidos na limpeza).")

c1, c2, c3 = st.columns(3)
c1.metric("Expectativa média de vida", f"{numero(dados['expectativa_vida'].mean())} anos")
c2.metric("Taxa média de mortalidade", numero(dados["taxa_mortalidade"].mean(), 2))
c3.metric("Cobertura vacinal média", f"{numero(dados['cobertura_vacinal'].mean())}%")

st.dataframe(dados.head(100), use_container_width=True, hide_index=True)

nome = st.selectbox("Indicador por região", list(INDICADORES), index=1)
col = INDICADORES[nome]
por_regiao = dados.groupby("regiao")[col].mean().reset_index().sort_values(col, ascending=False)
fig, ax = plt.subplots(figsize=(8, 4))
sns.barplot(data=por_regiao, x="regiao", y=col, hue="regiao", legend=False, ax=ax)
ax.set_xlabel("")
ax.set_ylabel(nome)
st.pyplot(fig)

topo = por_regiao.iloc[0]
st.info(f"**Interpretação:** a região com maior média de *{nome.lower()}* no arquivo enviado é {topo['regiao']} ({numero(topo[col], 2)}).")

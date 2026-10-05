import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import streamlit as st

sys.path.append(str(Path(__file__).parent.parent))

from tributos import SETOR_ANEXO, comparar
from utils import moeda

st.set_page_config(page_title="Simulador Tributário", page_icon="🧮", layout="wide")
sns.set_theme(style="whitegrid")

st.title("🧮 Simulador de Regimes Tributários")
st.markdown(
    "**Problema:** qual regime tributário gera menos imposto para uma empresa? "
    "Informe o faturamento e as despesas mensais e compare Simples Nacional, "
    "Lucro Presumido e Lucro Real."
)
st.warning(
    "Simulação didática e simplificada (sem créditos de PIS/COFINS/ICMS, sem fator R e sem "
    "particularidades municipais). Não substitui o cálculo de um contador."
)

col1, col2, col3 = st.columns(3)
setor = col1.selectbox("Setor", list(SETOR_ANEXO))
faturamento = col2.number_input("Faturamento mensal (R$)", min_value=1000.0, value=60000.0, step=1000.0)
despesas = col3.number_input("Despesas mensais (R$)", min_value=0.0, value=40000.0, step=1000.0)

resultado = comparar(faturamento, despesas, setor)

st.subheader("Comparativo")
tabela = resultado[["Regime", "Imposto mensal", "Carga tributária (%)"]].copy()
tabela["Imposto anual"] = tabela["Imposto mensal"] * 12
exibir = tabela.copy()
for coluna in ["Imposto mensal", "Imposto anual"]:
    exibir[coluna] = exibir[coluna].map(moeda)
exibir["Carga tributária (%)"] = exibir["Carga tributária (%)"].map(lambda v: f"{v:.2f}%")
st.dataframe(exibir, use_container_width=True, hide_index=True)

fig, ax = plt.subplots(figsize=(8, 4))
sns.barplot(data=resultado, x="Regime", y="Imposto mensal", hue="Regime", legend=False, ax=ax)
ax.set_xlabel("")
ax.set_ylabel("Imposto mensal (R$)")
st.pyplot(fig)

melhor = resultado.loc[resultado["Imposto mensal"].idxmin()]
pior = resultado.loc[resultado["Imposto mensal"].idxmax()]
economia = (pior["Imposto mensal"] - melhor["Imposto mensal"]) * 12
st.success(
    f"**Interpretação:** para este cenário, o regime mais vantajoso é **{melhor['Regime']}**, com carga de "
    f"{melhor['Carga tributária (%)']:.2f}%. A economia anual em relação ao mais caro "
    f"({pior['Regime']}) seria de {moeda(economia)}."
)

st.subheader("Composição dos impostos")
regime_detalhe = st.selectbox("Ver detalhe do regime", resultado["Regime"])
detalhe = resultado.loc[resultado["Regime"] == regime_detalhe, "Detalhe"].iloc[0]
st.dataframe(
    pd.DataFrame({"Tributo": list(detalhe), "Valor mensal": [moeda(v) for v in detalhe.values()]}),
    use_container_width=True, hide_index=True,
)

st.subheader("Como a carga muda com o faturamento")
faixas = pd.DataFrame({"faturamento": range(10000, 400001, 10000)})
linhas = []
for f in faixas["faturamento"]:
    comp = comparar(float(f), float(f) * (despesas / faturamento), setor)
    for _, l in comp.iterrows():
        linhas.append({"Faturamento mensal": f, "Regime": l["Regime"], "Carga (%)": l["Carga tributária (%)"]})
curva = pd.DataFrame(linhas)
fig2, ax2 = plt.subplots(figsize=(10, 4))
sns.lineplot(data=curva, x="Faturamento mensal", y="Carga (%)", hue="Regime", ax=ax2)
st.pyplot(fig2)

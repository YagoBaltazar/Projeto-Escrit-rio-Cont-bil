from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

BASE = Path(__file__).parent
IMAGENS = BASE / "imagens"
IMAGENS.mkdir(exist_ok=True)
sns.set_theme(style="whitegrid")

df = pd.read_csv(BASE / "dados" / "simulacao_saude_publica_brasil.csv", encoding="utf-8-sig")
colunas = ["expectativa_vida", "taxa_mortalidade", "taxa_internacao", "cobertura_vacinal",
           "medicos_por_1000", "leitos_hospitalares", "casos_doencas_cronicas"]

por_ano = df.groupby(["ano", "regiao"])["taxa_mortalidade"].mean().reset_index()
fig, ax = plt.subplots(figsize=(9, 4))
sns.lineplot(data=por_ano, x="ano", y="taxa_mortalidade", hue="regiao", marker="o", ax=ax)
ax.set_title("Taxa média de mortalidade por região (2015-2024)")
ax.set_xlabel("Ano")
ax.set_ylabel("Taxa de mortalidade")
fig.tight_layout()
fig.savefig(IMAGENS / "evolucao_mortalidade.png", dpi=130)
plt.close(fig)

por_uf = df.groupby(["uf", "regiao"])["taxa_mortalidade"].mean().reset_index().sort_values("taxa_mortalidade", ascending=False)
fig, ax = plt.subplots(figsize=(9, 4))
sns.barplot(data=por_uf, x="uf", y="taxa_mortalidade", hue="regiao", dodge=False, ax=ax)
ax.set_title("Mortalidade média por estado")
ax.set_xlabel("Estado")
ax.set_ylabel("Taxa de mortalidade")
fig.tight_layout()
fig.savefig(IMAGENS / "mortalidade_por_estado.png", dpi=130)
plt.close(fig)

tabela = df.pivot_table(index="uf", columns="ano", values="taxa_mortalidade", aggfunc="mean")
fig, ax = plt.subplots(figsize=(10, 6))
sns.heatmap(tabela, annot=True, fmt=".1f", cmap="YlOrRd", annot_kws={"size": 7}, ax=ax)
ax.set_title("Heatmap epidemiológico: mortalidade por estado e ano")
fig.tight_layout()
fig.savefig(IMAGENS / "heatmap_mortalidade.png", dpi=130)
plt.close(fig)

fig, ax = plt.subplots(figsize=(7, 4.5))
sns.scatterplot(data=df, x="cobertura_vacinal", y="taxa_mortalidade", hue="regiao", alpha=0.5, s=18, ax=ax)
sns.regplot(data=df, x="cobertura_vacinal", y="taxa_mortalidade", scatter=False, color="black", ax=ax)
ax.set_title("Vacinação x mortalidade")
ax.set_xlabel("Cobertura vacinal (%)")
ax.set_ylabel("Taxa de mortalidade")
fig.tight_layout()
fig.savefig(IMAGENS / "vacinacao_x_mortalidade.png", dpi=130)
plt.close(fig)

fig, ax = plt.subplots(figsize=(7, 5.5))
sns.heatmap(df[colunas].corr(), annot=True, fmt=".2f", cmap="coolwarm", center=0, annot_kws={"size": 7}, ax=ax)
ax.set_title("Correlação entre indicadores")
fig.tight_layout()
fig.savefig(IMAGENS / "correlacao.png", dpi=130)
plt.close(fig)
print("Imagens geradas")

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

BASE = Path(__file__).parent
sns.set_theme(style="whitegrid")

clientes = pd.read_csv(BASE / "dados" / "clientes.csv")
ap = pd.read_csv(BASE / "dados" / "apuracoes.csv", parse_dates=["competencia"])
df = ap.merge(clientes[["id", "uf", "setor", "regime"]], left_on="cliente_id", right_on="id", suffixes=("", "_c"))
df["carga"] = df["imposto"] / df["faturamento"] * 100

mensal = df.groupby("competencia")[["faturamento", "imposto"]].sum().reset_index()
fig, ax = plt.subplots(figsize=(9, 4))
sns.lineplot(data=mensal, x="competencia", y="faturamento", label="Faturamento", ax=ax)
sns.lineplot(data=mensal, x="competencia", y="imposto", label="Impostos", ax=ax)
ax.set_title("Faturamento e impostos por mês")
ax.set_xlabel("Competência")
ax.set_ylabel("R$")
fig.tight_layout()
fig.savefig(BASE / "imagens" / "evolucao_mensal.png", dpi=130)
plt.close(fig)

fig, ax = plt.subplots(figsize=(7, 4))
sns.boxplot(data=df, x="regime", y="carga", hue="regime", legend=False, ax=ax)
ax.set_title("Carga tributária por regime")
ax.set_xlabel("")
ax.set_ylabel("Carga (%)")
fig.tight_layout()
fig.savefig(BASE / "imagens" / "carga_por_regime.png", dpi=130)
plt.close(fig)

fig, ax = plt.subplots(figsize=(6, 4.5))
sns.heatmap(df[["faturamento", "despesas", "imposto", "honorario", "carga"]].corr(), annot=True, fmt=".2f", cmap="coolwarm", center=0, ax=ax)
ax.set_title("Correlação entre variáveis")
fig.tight_layout()
fig.savefig(BASE / "imagens" / "correlacao.png", dpi=130)
plt.close(fig)
print("Imagens geradas")

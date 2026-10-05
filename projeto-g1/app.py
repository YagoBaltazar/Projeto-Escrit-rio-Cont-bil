import matplotlib.pyplot as plt
import plotly.express as px
import seaborn as sns
import streamlit as st

from utils import COORDENADAS, carregar, filtros_laterais, moeda

st.set_page_config(page_title="Painel do Escritório Contábil", page_icon="📊", layout="wide")
sns.set_theme(style="whitegrid")

df = carregar()

st.title("📊 Painel Executivo de um Escritório de Contabilidade")
st.markdown(
    "**Problema:** um escritório de contabilidade precisa acompanhar a carteira de clientes, "
    "o faturamento apurado, os impostos de cada regime tributário, a receita de honorários e a "
    "inadimplência para decidir onde concentrar esforços. Este dashboard analisa uma base "
    "**fictícia** (sem dados reais de clientes) que simula essa rotina."
)

dados = filtros_laterais(df)

if dados.empty:
    st.warning("Nenhum dado para os filtros selecionados. Ajuste os filtros na barra lateral.")
    st.stop()

st.header("Indicadores (KPIs)")
clientes_ativos = dados["cliente_id"].nunique()
faturamento = dados["faturamento"].sum()
imposto = dados["imposto"].sum()
carga = imposto / faturamento * 100
honorarios = dados["honorario"].sum()
inadimplencia = dados["inadimplente"].mean() * 100
ticket = dados.groupby("cliente_id")["honorario"].mean().mean()

c1, c2, c3 = st.columns(3)
c1.metric("Clientes na seleção", clientes_ativos)
c2.metric("Faturamento apurado", moeda(faturamento))
c3.metric("Impostos apurados", moeda(imposto))
c4, c5, c6 = st.columns(3)
c4.metric("Carga tributária média", f"{carga:.1f}%")
c5.metric("Receita de honorários", moeda(honorarios))
c6.metric("Inadimplência de honorários", f"{inadimplencia:.1f}%")

aba1, aba2, aba3, aba4, aba5 = st.tabs(
    ["Evolução temporal", "Regimes e setores", "Mapa por estado", "Correlação", "Tabelas"]
)

with aba1:
    st.subheader("Faturamento e impostos por mês")
    mensal = dados.groupby("competencia")[["faturamento", "imposto", "honorario"]].sum().reset_index()
    fig, ax = plt.subplots(figsize=(10, 4))
    sns.lineplot(data=mensal, x="competencia", y="faturamento", label="Faturamento", ax=ax)
    sns.lineplot(data=mensal, x="competencia", y="imposto", label="Impostos", ax=ax)
    ax.set_xlabel("Competência")
    ax.set_ylabel("Valor (R$)")
    ax.legend()
    st.pyplot(fig)

    mensal["media_movel_3m"] = mensal["faturamento"].rolling(3).mean()
    mensal["variacao_mensal_%"] = mensal["faturamento"].pct_change() * 100
    fig2 = px.line(mensal, x="competencia", y=["faturamento", "media_movel_3m"],
                   title="Faturamento mensal e média móvel de 3 meses (interativo)")
    st.plotly_chart(fig2, use_container_width=True)

    melhor = mensal.loc[mensal["faturamento"].idxmax()]
    st.info(
        f"**Interpretação:** o maior faturamento da seleção foi em {melhor['competencia']:%m/%Y} "
        f"({moeda(melhor['faturamento'])}). A série mostra sazonalidade e tendência de crescimento, "
        "o que ajuda a prever a carga de trabalho do escritório ao longo do ano."
    )

with aba2:
    col_a, col_b = st.columns(2)
    por_regime = dados.groupby("regime").agg(
        faturamento=("faturamento", "sum"), imposto=("imposto", "sum"), clientes=("cliente_id", "nunique")
    ).reset_index()
    por_regime["carga_%"] = por_regime["imposto"] / por_regime["faturamento"] * 100

    with col_a:
        st.subheader("Carga tributária por regime")
        fig, ax = plt.subplots(figsize=(6, 4))
        sns.barplot(data=por_regime, x="regime", y="carga_%", hue="regime", legend=False, ax=ax)
        ax.set_xlabel("")
        ax.set_ylabel("Carga tributária (%)")
        st.pyplot(fig)

    with col_b:
        st.subheader("Honorários por setor")
        por_setor = dados.groupby("setor")["honorario"].sum().reset_index().sort_values("honorario", ascending=False)
        fig, ax = plt.subplots(figsize=(6, 4))
        sns.barplot(data=por_setor, x="setor", y="honorario", hue="setor", legend=False, ax=ax)
        ax.set_xlabel("")
        ax.set_ylabel("Honorários (R$)")
        st.pyplot(fig)

    st.subheader("Distribuição da carga tributária por regime")
    fig, ax = plt.subplots(figsize=(10, 4))
    sns.boxplot(data=dados, x="regime", y="carga_tributaria", hue="regime", legend=False, ax=ax)
    ax.set_xlabel("")
    ax.set_ylabel("Carga tributária (%)")
    st.pyplot(fig)

    menor = por_regime.loc[por_regime["carga_%"].idxmin()]
    maior = por_regime.loc[por_regime["carga_%"].idxmax()]
    st.info(
        f"**Interpretação:** na seleção atual, {menor['regime']} tem a menor carga média "
        f"({menor['carga_%']:.1f}%) e {maior['regime']} a maior ({maior['carga_%']:.1f}%). "
        "Isso reforça a importância do planejamento tributário: o regime escolhido muda muito o imposto pago."
    )

with aba3:
    st.subheader("Clientes, faturamento e inadimplência por estado")
    por_uf = dados.groupby("uf").agg(
        faturamento=("faturamento", "sum"),
        clientes=("cliente_id", "nunique"),
        inadimplencia=("inadimplente", "mean"),
    ).reset_index()
    por_uf["inadimplencia"] = por_uf["inadimplencia"] * 100
    por_uf["lat"] = por_uf["uf"].map(lambda u: COORDENADAS[u][0])
    por_uf["lon"] = por_uf["uf"].map(lambda u: COORDENADAS[u][1])
    mapa = px.scatter_geo(
        por_uf, lat="lat", lon="lon", size="faturamento", color="inadimplencia",
        hover_name="uf", hover_data={"clientes": True, "lat": False, "lon": False},
        color_continuous_scale="OrRd", scope="south america", size_max=50,
    )
    mapa.update_geos(fitbounds="locations", showcountries=True)
    st.plotly_chart(mapa, use_container_width=True)
    top = por_uf.loc[por_uf["faturamento"].idxmax()]
    st.info(
        f"**Interpretação:** {top['uf']} concentra o maior faturamento da seleção. "
        "O tamanho da bolha indica faturamento e a cor indica a inadimplência de honorários."
    )

with aba4:
    st.subheader("Correlação entre variáveis")
    colunas = ["faturamento", "despesas", "imposto", "honorario", "carga_tributaria", "inadimplente"]
    corr = dados[colunas].corr()
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", center=0, ax=ax)
    st.pyplot(fig)
    st.info(
        f"**Interpretação:** a correlação entre faturamento e imposto é {corr.loc['faturamento', 'imposto']:.2f}, "
        f"e entre faturamento e honorário é {corr.loc['faturamento', 'honorario']:.2f}. "
        "Clientes maiores pagam mais imposto e mais honorários, mas a relação com inadimplência é fraca."
    )

with aba5:
    st.subheader("Maiores clientes por faturamento")
    ranking = dados.groupby(["razao_social", "regime", "setor", "uf"]).agg(
        faturamento=("faturamento", "sum"), imposto=("imposto", "sum"), honorarios=("honorario", "sum")
    ).reset_index().sort_values("faturamento", ascending=False).head(15)
    st.dataframe(ranking, use_container_width=True)
    st.subheader("Base filtrada")
    st.dataframe(dados.drop(columns=["cnpj"]), use_container_width=True)
    st.download_button("Baixar base filtrada (CSV)", dados.to_csv(index=False).encode("utf-8"), "base_filtrada.csv")

st.header("Conclusão executiva")
st.success(
    f"Na seleção atual, a carteira tem {clientes_ativos} clientes, {moeda(faturamento)} de faturamento apurado e "
    f"carga tributária média de {carga:.1f}%. A inadimplência de honorários é {inadimplencia:.1f}%. "
    "Recomenda-se: (1) revisar o regime tributário dos clientes com maior carga, (2) acompanhar de perto "
    "os estados e regimes com mais inadimplência e (3) usar a sazonalidade do faturamento para planejar "
    "a equipe nos meses de maior movimento. Use o menu lateral para simular regimes e consultar CNPJs."
)
st.caption("Projeto educacional com dados fictícios — Análise e Visualização de Dados com Python.")

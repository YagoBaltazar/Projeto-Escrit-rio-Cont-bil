import pandas as pd
import streamlit as st

from db import banco_existe, carregar_dados, criar_banco, ler_csv

ORDEM_CRITICIDADE = ["Baixo", "Médio", "Alto", "Crítico"]
CRITICIDADE_NUM = {"Baixo": 1, "Médio": 2, "Alto": 3, "Crítico": 4}
MESES = {1: "Jan", 2: "Fev", 3: "Mar", 4: "Abr", 5: "Mai", 6: "Jun",
         7: "Jul", 8: "Ago", 9: "Set", 10: "Out", 11: "Nov", 12: "Dez"}

INDICADORES = {
    "Expectativa de vida": "expectativa_vida",
    "Taxa de mortalidade": "taxa_mortalidade",
    "Taxa de internação": "taxa_internacao",
    "Cobertura vacinal (%)": "cobertura_vacinal",
    "Médicos por 1000 hab.": "medicos_por_1000",
    "Leitos hospitalares": "leitos_hospitalares",
    "Casos de doenças crônicas": "casos_doencas_cronicas",
}

COORDENADAS_UF = {
    "AM": (-3.12, -60.02), "PA": (-1.46, -48.5), "RO": (-8.76, -63.9), "TO": (-10.18, -48.33),
    "BA": (-12.97, -38.5), "CE": (-3.73, -38.52), "MA": (-2.53, -44.3), "PB": (-7.12, -34.86),
    "PE": (-8.05, -34.88), "DF": (-15.79, -47.88), "GO": (-16.68, -49.25), "MS": (-20.47, -54.62),
    "MT": (-15.6, -56.1), "ES": (-20.32, -40.34), "MG": (-19.92, -43.94), "RJ": (-22.9, -43.2),
    "SP": (-23.55, -46.63), "PR": (-25.43, -49.27), "RS": (-30.03, -51.23), "SC": (-27.6, -48.55),
}


def preparar(df):
    df = df.copy()
    df["data"] = pd.to_datetime(df["data"])
    df["criticidade_num"] = df["nivel_criticidade"].map(CRITICIDADE_NUM)
    df["nivel_criticidade"] = pd.Categorical(df["nivel_criticidade"], categories=ORDEM_CRITICIDADE, ordered=True)
    return df


@st.cache_data(show_spinner="Carregando dados...")
def carregar():
    try:
        if not banco_existe():
            criar_banco(ler_csv())
        df = carregar_dados()
    except Exception:
        df = ler_csv()
    return preparar(df)


def numero(valor, casas=1):
    texto = f"{valor:,.{casas}f}"
    return texto.replace(",", "X").replace(".", ",").replace("X", ".")


def forca_correlacao(r):
    valor = abs(r)
    if valor < 0.1:
        return "praticamente inexistente"
    if valor < 0.3:
        return "fraca"
    if valor < 0.6:
        return "moderada"
    return "forte"


def indice_vulnerabilidade(df):
    g = df.groupby("uf").agg(
        regiao=("regiao", "first"),
        mortalidade=("taxa_mortalidade", "mean"),
        internacao=("taxa_internacao", "mean"),
        vacinacao=("cobertura_vacinal", "mean"),
        expectativa=("expectativa_vida", "mean"),
        medicos=("medicos_por_1000", "mean"),
        leitos=("leitos_hospitalares", "mean"),
    )

    def norm(serie):
        amplitude = serie.max() - serie.min()
        return (serie - serie.min()) / amplitude if amplitude > 0 else serie * 0 + 0.5

    g["indice_vulnerabilidade"] = (
        norm(g["mortalidade"]) + norm(g["internacao"]) + (1 - norm(g["vacinacao"]))
        + (1 - norm(g["expectativa"])) + (1 - norm(g["medicos"]))
    ) / 5
    return g.sort_values("indice_vulnerabilidade", ascending=False).reset_index()


def filtros_laterais(df):
    st.sidebar.header("Filtros")
    ano_ini, ano_fim = st.sidebar.select_slider(
        "Ano", options=sorted(df["ano"].unique()), value=(df["ano"].min(), df["ano"].max())
    )
    meses = st.sidebar.multiselect(
        "Mês", list(MESES), default=list(MESES), format_func=lambda m: MESES[m]
    )
    regioes = st.sidebar.multiselect("Região", sorted(df["regiao"].unique()), default=sorted(df["regiao"].unique()))

    ufs_opcoes = sorted(df[df["regiao"].isin(regioes)]["uf"].unique())
    ufs = st.sidebar.multiselect("Estado (UF)", ufs_opcoes, default=ufs_opcoes)

    mun_opcoes = sorted(df[df["uf"].isin(ufs)]["municipio"].unique())
    municipios = st.sidebar.multiselect("Município", mun_opcoes, default=mun_opcoes)

    criticidades = st.sidebar.multiselect("Nível de criticidade", ORDEM_CRITICIDADE, default=ORDEM_CRITICIDADE)

    return df[
        df["ano"].between(ano_ini, ano_fim)
        & df["mes"].isin(meses)
        & df["regiao"].isin(regioes)
        & df["uf"].isin(ufs)
        & df["municipio"].isin(municipios)
        & df["nivel_criticidade"].isin(criticidades)
    ]

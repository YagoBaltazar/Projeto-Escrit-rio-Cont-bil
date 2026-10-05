import pandas as pd
import streamlit as st

from db import banco_existe, carregar_clientes, carregar_dados
from gerar_dados import gerar

COORDENADAS = {
    "RJ": (-22.9, -43.2),
    "SP": (-23.55, -46.63),
    "MG": (-19.92, -43.94),
    "ES": (-20.32, -40.34),
    "BA": (-12.97, -38.5),
}


@st.cache_data(show_spinner="Carregando dados do banco...")
def carregar(versao=0):
    if not banco_existe():
        gerar(salvar_csv=True, criar_sqlite=True)
    df = carregar_dados()
    df["carga_tributaria"] = df["imposto"] / df["faturamento"] * 100
    df["lucro_bruto"] = df["faturamento"] - df["despesas"]
    df["ano"] = df["competencia"].dt.year
    df["mes"] = df["competencia"].dt.month
    df["inadimplente"] = 1 - df["pago"]
    return df


def moeda(valor):
    texto = f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {texto}"


def filtros_laterais(df):
    st.sidebar.header("Filtros")
    ufs = st.sidebar.multiselect("Estado (UF)", sorted(df["uf"].unique()), default=sorted(df["uf"].unique()))
    regimes = st.sidebar.multiselect("Regime tributário", sorted(df["regime"].unique()), default=sorted(df["regime"].unique()))
    setores = st.sidebar.multiselect("Setor", sorted(df["setor"].unique()), default=sorted(df["setor"].unique()))
    portes = st.sidebar.multiselect("Porte", sorted(df["porte"].unique()), default=sorted(df["porte"].unique()))
    competencias = sorted(df["competencia"].dt.strftime("%Y-%m").unique())
    inicio, fim = st.sidebar.select_slider("Período", options=competencias, value=(competencias[0], competencias[-1]))

    filtrado = df[
        df["uf"].isin(ufs)
        & df["regime"].isin(regimes)
        & df["setor"].isin(setores)
        & df["porte"].isin(portes)
        & (df["competencia"].dt.strftime("%Y-%m") >= inicio)
        & (df["competencia"].dt.strftime("%Y-%m") <= fim)
    ]
    return filtrado

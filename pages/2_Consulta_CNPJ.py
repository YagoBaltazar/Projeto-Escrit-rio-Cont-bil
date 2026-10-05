import re
import sys
from pathlib import Path

import requests
import streamlit as st

sys.path.append(str(Path(__file__).parent.parent))

from db import carregar_clientes, inserir_cliente
from tributos import REGIMES, SETOR_ANEXO
from utils import carregar

st.set_page_config(page_title="Consulta CNPJ", page_icon="🔎", layout="wide")

st.title("🔎 Consulta de CNPJ (API) e cadastro de clientes")
st.markdown(
    "**Problema:** ao receber um novo cliente, o escritório precisa conferir os dados cadastrais da empresa. "
    "Esta página consome a API pública **BrasilAPI** (requests) e permite cadastrar o cliente no banco SQLite."
)

carregar()

cnpj_digitado = st.text_input("CNPJ (somente números ou com pontuação)", placeholder="00.000.000/0001-91")

if st.button("Consultar"):
    numeros = re.sub(r"\D", "", cnpj_digitado)
    if len(numeros) != 14:
        st.error("Informe um CNPJ com 14 dígitos.")
    else:
        try:
            resposta = requests.get(f"https://brasilapi.com.br/api/cnpj/v1/{numeros}", timeout=15)
            if resposta.status_code == 200:
                st.session_state["empresa"] = resposta.json()
            else:
                st.session_state.pop("empresa", None)
                st.error(f"CNPJ não encontrado ou API indisponível (código {resposta.status_code}).")
        except requests.RequestException as erro:
            st.session_state.pop("empresa", None)
            st.error(f"Falha ao acessar a API: {erro}")

empresa = st.session_state.get("empresa")

if empresa:
    st.subheader(empresa.get("razao_social", "Empresa"))
    c1, c2, c3 = st.columns(3)
    c1.metric("Situação", empresa.get("descricao_situacao_cadastral", "-"))
    c2.metric("Porte", empresa.get("porte", "-"))
    c3.metric("UF", empresa.get("uf", "-"))
    st.write(f"**Atividade principal (CNAE):** {empresa.get('cnae_fiscal_descricao', '-')}")
    st.write(f"**Município:** {empresa.get('municipio', '-')}")
    st.write(f"**Abertura:** {empresa.get('data_inicio_atividade', '-')}")

    st.subheader("Cadastrar como cliente do escritório")
    col1, col2, col3 = st.columns(3)
    setor = col1.selectbox("Setor", list(SETOR_ANEXO))
    regime = col2.selectbox("Regime tributário", REGIMES)
    honorario = col3.number_input("Honorário mensal (R$)", min_value=0.0, value=800.0, step=50.0)
    if st.button("Salvar no banco"):
        porte = empresa.get("porte", "ME") or "ME"
        ok = inserir_cliente(
            cnpj=empresa.get("cnpj", ""),
            razao_social=empresa.get("razao_social", ""),
            uf=empresa.get("uf", "RJ"),
            setor=setor,
            porte=porte[:20],
            regime=regime,
            honorario=honorario,
        )
        if ok:
            st.success("Cliente cadastrado com sucesso.")
        else:
            st.info("Este CNPJ já está cadastrado.")

st.subheader("Clientes cadastrados")
st.dataframe(carregar_clientes(), use_container_width=True, hide_index=True)

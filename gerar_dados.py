from pathlib import Path

import numpy as np
import pandas as pd

from tributos import imposto_total

BASE_DIR = Path(__file__).parent
DADOS_DIR = BASE_DIR / "dados"

UFS = {"RJ": 0.45, "SP": 0.25, "MG": 0.15, "ES": 0.10, "BA": 0.05}
SETORES = {"Comércio": 0.35, "Serviços": 0.35, "Indústria": 0.12, "Tecnologia": 0.18}
PREFIXOS = ["Alfa", "Beta", "Delta", "Orion", "Atlântica", "Brasil", "Central", "Nova", "Prime",
            "Sul", "Norte", "Real", "Ponto", "Vale", "Mar", "Sol", "Lume", "Forte", "Ágil", "Top"]
SUFIXOS = {"Comércio": "Comércio de Produtos Ltda", "Serviços": "Serviços Empresariais Ltda",
           "Indústria": "Indústria e Embalagens Ltda", "Tecnologia": "Soluções em Tecnologia Ltda"}


def gerar_clientes(n=60, semente=42):
    rng = np.random.default_rng(semente)
    linhas = []
    for i in range(1, n + 1):
        setor = rng.choice(list(SETORES), p=list(SETORES.values()))
        uf = rng.choice(list(UFS), p=list(UFS.values()))
        base = float(np.clip(rng.lognormal(np.log(45000), 0.8), 8000, 900000))
        anual = base * 12
        if anual <= 4800000:
            regime = rng.choice(["Simples Nacional", "Lucro Presumido", "Lucro Real"], p=[0.70, 0.25, 0.05])
        else:
            regime = rng.choice(["Lucro Presumido", "Lucro Real"], p=[0.6, 0.4])
        if anual <= 360000:
            porte = "ME"
        elif anual <= 4800000:
            porte = "EPP"
        else:
            porte = "Médio/Grande"
        fator = {"Simples Nacional": 0.012, "Lucro Presumido": 0.016, "Lucro Real": 0.022}[regime]
        honorario = round(350 + base * fator, 2)
        cnpj = "".join(str(d) for d in rng.integers(0, 10, 8)) + "0001" + "".join(str(d) for d in rng.integers(0, 10, 2))
        cnpj = f"{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:]}"
        entrada = pd.Timestamp("2019-01-01") + pd.Timedelta(days=int(rng.integers(0, 2400)))
        linhas.append({
            "id": i,
            "cnpj": cnpj,
            "razao_social": f"{rng.choice(PREFIXOS)} {SUFIXOS[setor]}",
            "uf": uf,
            "setor": setor,
            "porte": porte,
            "regime": regime,
            "honorario_mensal": honorario,
            "data_entrada": str(entrada.date()),
            "_base": base,
            "_despesa": float(rng.uniform(0.50, 0.82)),
        })
    return pd.DataFrame(linhas)


def gerar_apuracoes(clientes, meses=24, fim="2026-09", semente=7):
    rng = np.random.default_rng(semente)
    competencias = pd.period_range(end=fim, periods=meses, freq="M")
    prob_inad = {"Simples Nacional": 0.07, "Lucro Presumido": 0.09, "Lucro Real": 0.12}
    linhas = []
    contador = 1
    for _, c in clientes.iterrows():
        for k, comp in enumerate(competencias):
            sazonal = 1 + 0.15 * np.sin((comp.month - 3) / 12 * 2 * np.pi)
            crescimento = 1 + 0.008 * k
            ruido = rng.normal(1, 0.08)
            fat = round(c["_base"] * sazonal * crescimento * ruido, 2)
            desp = round(fat * c["_despesa"] * rng.normal(1, 0.04), 2)
            imp = round(imposto_total(c["regime"], fat, desp, c["setor"]), 2)
            p = prob_inad[c["regime"]] + (0.05 if k >= meses - 2 else 0)
            pago = int(rng.random() > p)
            linhas.append({
                "id": contador,
                "cliente_id": int(c["id"]),
                "competencia": str(comp),
                "faturamento": fat,
                "despesas": desp,
                "imposto": imp,
                "honorario": c["honorario_mensal"],
                "pago": pago,
            })
            contador += 1
    return pd.DataFrame(linhas)


def gerar(salvar_csv=True, criar_sqlite=True):
    clientes = gerar_clientes()
    apuracoes = gerar_apuracoes(clientes)
    clientes_final = clientes.drop(columns=["_base", "_despesa"])
    if salvar_csv:
        DADOS_DIR.mkdir(exist_ok=True)
        clientes_final.to_csv(DADOS_DIR / "clientes.csv", index=False)
        apuracoes.to_csv(DADOS_DIR / "apuracoes.csv", index=False)
    if criar_sqlite:
        from db import criar_banco
        criar_banco(clientes_final, apuracoes.drop(columns=["id"]))
    return clientes_final, apuracoes


if __name__ == "__main__":
    gerar()
    print("Dados gerados em dados/ e database/escritorio.db")

import pandas as pd

LIMITES = [180000, 360000, 720000, 1800000, 3600000, 4800000]

ANEXOS = {
    "Comércio (Anexo I)": [
        (0.0400, 0), (0.0730, 5940), (0.0950, 13860),
        (0.1070, 22500), (0.1430, 87300), (0.1900, 378000),
    ],
    "Indústria (Anexo II)": [
        (0.0450, 0), (0.0780, 5940), (0.1000, 13860),
        (0.1120, 22500), (0.1470, 85500), (0.3000, 720000),
    ],
    "Serviços (Anexo III)": [
        (0.0600, 0), (0.1120, 9360), (0.1350, 17640),
        (0.1600, 35640), (0.2100, 125640), (0.3300, 648000),
    ],
    "Serviços (Anexo V)": [
        (0.1550, 0), (0.1800, 4500), (0.1950, 9900),
        (0.2050, 17100), (0.2300, 62100), (0.3050, 540000),
    ],
}

SETOR_ANEXO = {
    "Comércio": "Comércio (Anexo I)",
    "Indústria": "Indústria (Anexo II)",
    "Serviços": "Serviços (Anexo III)",
    "Tecnologia": "Serviços (Anexo V)",
}

SETOR_TIPO = {
    "Comércio": "comercio",
    "Indústria": "comercio",
    "Serviços": "servico",
    "Tecnologia": "servico",
}

REGIMES = ["Simples Nacional", "Lucro Presumido", "Lucro Real"]


def aliquota_efetiva_simples(rbt12, anexo):
    tabela = ANEXOS[anexo]
    for limite, (aliq, ded) in zip(LIMITES, tabela):
        if rbt12 <= limite:
            return (rbt12 * aliq - ded) / rbt12
    aliq, ded = tabela[-1]
    return (rbt12 * aliq - ded) / rbt12


def simples(faturamento, setor):
    anexo = SETOR_ANEXO[setor]
    rbt12 = faturamento * 12
    aliq = aliquota_efetiva_simples(rbt12, anexo)
    return {"DAS (Simples)": faturamento * aliq}


def _adicional_irpj(base):
    return 0.15 * base + 0.10 * max(0, base - 20000)


def presumido(faturamento, despesas, setor):
    tipo = SETOR_TIPO[setor]
    if tipo == "servico":
        perc_irpj, perc_csll = 0.32, 0.32
        iss_icms = 0.05 * faturamento
        nome = "ISS"
    else:
        perc_irpj, perc_csll = 0.08, 0.12
        iss_icms = 0.18 * max(0, faturamento - despesas)
        nome = "ICMS"
    return {
        "IRPJ": _adicional_irpj(faturamento * perc_irpj),
        "CSLL": 0.09 * faturamento * perc_csll,
        "PIS": 0.0065 * faturamento,
        "COFINS": 0.03 * faturamento,
        nome: iss_icms,
    }


def real(faturamento, despesas, setor):
    tipo = SETOR_TIPO[setor]
    lucro = max(0, faturamento - despesas)
    if tipo == "servico":
        iss_icms = 0.05 * faturamento
        nome = "ISS"
    else:
        iss_icms = 0.18 * lucro
        nome = "ICMS"
    return {
        "IRPJ": _adicional_irpj(lucro),
        "CSLL": 0.09 * lucro,
        "PIS": 0.0165 * lucro,
        "COFINS": 0.076 * lucro,
        nome: iss_icms,
    }


def calcular(regime, faturamento, despesas, setor):
    if regime == "Simples Nacional":
        return simples(faturamento, setor)
    if regime == "Lucro Presumido":
        return presumido(faturamento, despesas, setor)
    return real(faturamento, despesas, setor)


def imposto_total(regime, faturamento, despesas, setor):
    return sum(calcular(regime, faturamento, despesas, setor).values())


def comparar(faturamento, despesas, setor):
    linhas = []
    for regime in REGIMES:
        if regime == "Simples Nacional" and faturamento * 12 > 4800000:
            continue
        detalhe = calcular(regime, faturamento, despesas, setor)
        total = sum(detalhe.values())
        linhas.append({
            "Regime": regime,
            "Imposto mensal": total,
            "Carga tributária (%)": total / faturamento * 100 if faturamento else 0,
            "Detalhe": detalhe,
        })
    return pd.DataFrame(linhas)

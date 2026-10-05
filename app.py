import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import streamlit as st

from utils import (INDICADORES, ORDEM_CRITICIDADE, carregar, filtros_laterais,
                   forca_correlacao, indice_vulnerabilidade, numero)

st.set_page_config(page_title="Saúde Pública no Brasil", page_icon="🏥", layout="wide")
sns.set_theme(style="whitegrid")

df = carregar()

st.title("🏥 Indicadores de Saúde Pública no Brasil (2015–2024)")
st.markdown(
    "**Problema:** indicadores de saúde pública ajudam a avaliar a qualidade de vida da população e a apoiar "
    "decisões de governo. Este dashboard investiga a evolução dos indicadores, compara regiões e estados, "
    "avalia a capacidade hospitalar e identifica as áreas mais vulneráveis. "
    "A base é **simulada** e foi fornecida pelo professor, então os resultados servem para fins educacionais."
)

dados = filtros_laterais(df)

if dados.empty:
    st.warning("Nenhum dado para os filtros selecionados. Ajuste os filtros na barra lateral.")
    st.stop()

ranking = indice_vulnerabilidade(dados)
mais_vulneravel = ranking.iloc[0]

st.header("Indicadores (KPIs)")
c1, c2, c3 = st.columns(3)
c1.metric("Expectativa média de vida", f"{numero(dados['expectativa_vida'].mean())} anos")
c2.metric("Taxa média de mortalidade", numero(dados["taxa_mortalidade"].mean(), 2))
c3.metric("Cobertura vacinal média", f"{numero(dados['cobertura_vacinal'].mean())}%")
c4, c5, c6 = st.columns(3)
c4.metric("Estado mais vulnerável", f"{mais_vulneravel['uf']} ({mais_vulneravel['regiao']})")
c5.metric("Média de leitos hospitalares", numero(dados["leitos_hospitalares"].mean(), 0))
c6.metric("Total de internações (soma das taxas)", numero(dados["taxa_internacao"].sum(), 0))
st.caption(
    "O estado mais vulnerável é o de maior índice de vulnerabilidade (0 a 1), que combina mortalidade e internação "
    "altas com vacinação, expectativa de vida e médicos baixos. O total de internações soma a taxa de internação "
    "dos registros filtrados, pois a base traz taxas e não contagens absolutas."
)

abas = st.tabs([
    "Evolução temporal", "Regiões e estados", "Infraestrutura",
    "Epidemiologia", "Criticidade", "Tabela dinâmica",
])

with abas[0]:
    st.subheader("Evolução dos indicadores ao longo do tempo")
    nome = st.selectbox("Indicador", list(INDICADORES), key="ind_tempo")
    col = INDICADORES[nome]
    por_ano = dados.groupby(["ano", "regiao"])[col].mean().reset_index()
    fig, ax = plt.subplots(figsize=(10, 4))
    sns.lineplot(data=por_ano, x="ano", y=col, hue="regiao", marker="o", ax=ax)
    ax.set_xlabel("Ano")
    ax.set_ylabel(nome)
    ax.legend(title="Região", bbox_to_anchor=(1.02, 1), loc="upper left")
    st.pyplot(fig)

    st.markdown("**Variação entre o primeiro e o último ano do filtro**")
    primeiro, ultimo = dados["ano"].min(), dados["ano"].max()
    linhas = []
    for rotulo, coluna in INDICADORES.items():
        inicio = dados.loc[dados["ano"] == primeiro, coluna].mean()
        fim = dados.loc[dados["ano"] == ultimo, coluna].mean()
        linhas.append({"Indicador": rotulo, f"Média {primeiro}": round(inicio, 2),
                       f"Média {ultimo}": round(fim, 2), "Variação (%)": round((fim - inicio) / inicio * 100, 2)})
    st.dataframe(pd.DataFrame(linhas), use_container_width=True, hide_index=True)

    serie = dados.groupby("ano")[col].mean()
    amplitude = (serie.max() - serie.min()) / serie.mean() * 100
    st.info(
        f"**Interpretação:** a média anual de *{nome.lower()}* foi mais alta em {serie.idxmax()} e mais baixa em "
        f"{serie.idxmin()}, uma amplitude de {amplitude:.1f}% sobre a média do período. "
        + ("Como a oscilação é pequena, não há tendência clara de melhora ou piora nesse indicador."
           if amplitude < 5 else "A oscilação é relevante e merece investigação por região.")
    )

with abas[1]:
    st.subheader("Comparação entre regiões e estados")
    nome = st.selectbox("Indicador", list(INDICADORES), index=1, key="ind_reg")
    col = INDICADORES[nome]
    por_uf = dados.groupby(["uf", "regiao"])[col].mean().reset_index().sort_values(col, ascending=False)
    fig, ax = plt.subplots(figsize=(11, 4))
    sns.barplot(data=por_uf, x="uf", y=col, hue="regiao", dodge=False, ax=ax)
    ax.set_xlabel("Estado")
    ax.set_ylabel(f"{nome} (média)")
    ax.legend(title="Região", bbox_to_anchor=(1.02, 1), loc="upper left")
    st.pyplot(fig)

    ca, cb = st.columns(2)
    with ca:
        por_regiao = dados.groupby("regiao")[col].mean().reset_index().sort_values(col, ascending=False)
        fig, ax = plt.subplots(figsize=(6, 4))
        sns.barplot(data=por_regiao, x="regiao", y=col, hue="regiao", legend=False, ax=ax)
        ax.set_xlabel("")
        ax.set_ylabel(f"{nome} (média)")
        ax.set_title("Média por região")
        plt.setp(ax.get_xticklabels(), rotation=20)
        st.pyplot(fig)
    with cb:
        fig, ax = plt.subplots(figsize=(6, 4))
        sns.boxplot(data=dados, x="regiao", y=col, hue="regiao", legend=False, ax=ax)
        ax.set_xlabel("")
        ax.set_ylabel(nome)
        ax.set_title("Distribuição por região")
        plt.setp(ax.get_xticklabels(), rotation=20)
        st.pyplot(fig)

    topo, base = por_uf.iloc[0], por_uf.iloc[-1]
    dif = (topo[col] - base[col]) / base[col] * 100 if base[col] else 0
    st.info(
        f"**Interpretação:** para *{nome.lower()}*, o maior valor médio está em {topo['uf']} ({numero(topo[col], 2)}) "
        f"e o menor em {base['uf']} ({numero(base[col], 2)}), uma diferença de {dif:.1f}%. "
        "Diferenças pequenas entre regiões indicam pouca desigualdade regional nesse indicador."
    )

with abas[2]:
    st.subheader("Capacidade hospitalar")
    ca, cb = st.columns(2)
    leitos = dados.groupby("uf")["leitos_hospitalares"].mean().reset_index().sort_values("leitos_hospitalares", ascending=False)
    medicos = dados.groupby("uf")["medicos_por_1000"].mean().reset_index().sort_values("medicos_por_1000", ascending=False)
    with ca:
        fig, ax = plt.subplots(figsize=(6, 5))
        sns.barplot(data=leitos, y="uf", x="leitos_hospitalares", hue="uf", legend=False, ax=ax)
        ax.set_xlabel("Leitos hospitalares (média)")
        ax.set_ylabel("")
        st.pyplot(fig)
    with cb:
        fig, ax = plt.subplots(figsize=(6, 5))
        sns.barplot(data=medicos, y="uf", x="medicos_por_1000", hue="uf", legend=False, ax=ax)
        ax.set_xlabel("Médicos por 1000 habitantes (média)")
        ax.set_ylabel("")
        st.pyplot(fig)

    infra = dados.groupby("regiao").agg(
        leitos_medios=("leitos_hospitalares", "mean"),
        medicos_por_1000=("medicos_por_1000", "mean"),
        internacao_media=("taxa_internacao", "mean"),
    ).round(2).reset_index()
    st.dataframe(infra, use_container_width=True, hide_index=True)
    r = dados["leitos_hospitalares"].corr(dados["taxa_internacao"])
    st.info(
        f"**Interpretação:** {leitos.iloc[0]['uf']} tem a maior média de leitos ({numero(leitos.iloc[0]['leitos_hospitalares'], 0)}) "
        f"e {leitos.iloc[-1]['uf']} a menor ({numero(leitos.iloc[-1]['leitos_hospitalares'], 0)}). "
        f"A correlação entre leitos e taxa de internação é {r:.2f} ({forca_correlacao(r)}), "
        "ou seja, maior capacidade não está associada a mais ou menos internações nesta base."
    )

with abas[3]:
    st.subheader("Análise epidemiológica")
    nome = st.selectbox("Indicador do heatmap", list(INDICADORES), index=1, key="ind_heat")
    col = INDICADORES[nome]
    tabela = dados.pivot_table(index="uf", columns="ano", values=col, aggfunc="mean")
    fig, ax = plt.subplots(figsize=(12, 6))
    formato = ".0f" if tabela.values.mean() > 1000 else ".1f"
    sns.heatmap(tabela, annot=True, fmt=formato, cmap="YlOrRd", ax=ax, annot_kws={"size": 7})
    ax.set_xlabel("Ano")
    ax.set_ylabel("Estado")
    ax.set_title(f"{nome}: média por estado e ano")
    st.pyplot(fig)

    ca, cb = st.columns(2)
    r = dados["cobertura_vacinal"].corr(dados["taxa_mortalidade"])
    with ca:
        st.markdown("**Vacinação x mortalidade**")
        fig, ax = plt.subplots(figsize=(6, 4.5))
        sns.scatterplot(data=dados, x="cobertura_vacinal", y="taxa_mortalidade", hue="regiao", alpha=0.5, s=18, ax=ax)
        sns.regplot(data=dados, x="cobertura_vacinal", y="taxa_mortalidade", scatter=False, color="black", ax=ax)
        ax.set_xlabel("Cobertura vacinal (%)")
        ax.set_ylabel("Taxa de mortalidade")
        ax.legend(title="Região", fontsize=7)
        st.pyplot(fig)
    with cb:
        st.markdown("**Correlação entre indicadores**")
        fig, ax = plt.subplots(figsize=(6, 4.5))
        sns.heatmap(dados[list(INDICADORES.values())].corr(), annot=True, fmt=".2f", cmap="coolwarm", center=0,
                    annot_kws={"size": 7}, ax=ax)
        st.pyplot(fig)

    sentido = "negativa" if r < 0 else "positiva"
    st.info(
        f"**Interpretação:** a correlação entre cobertura vacinal e mortalidade é {r:.2f}, de força "
        f"{forca_correlacao(r)} ({sentido}). "
        + ("Isso significa que, nesta base simulada, não há evidência de que mais vacinação reduza a mortalidade."
           if abs(r) < 0.1 else "Existe alguma relação, que deve ser investigada com mais cuidado.")
        + " Correlação não implica causalidade."
    )

with abas[4]:
    st.subheader("Níveis de criticidade")
    ca, cb = st.columns(2)
    with ca:
        prop = (dados.groupby(["regiao", "nivel_criticidade"], observed=True).size()
                .unstack(fill_value=0).reindex(columns=ORDEM_CRITICIDADE, fill_value=0))
        prop = prop.div(prop.sum(axis=1), axis=0) * 100
        fig, ax = plt.subplots(figsize=(6, 4.5))
        prop.plot(kind="bar", stacked=True, colormap="RdYlGn_r", ax=ax)
        ax.set_xlabel("")
        ax.set_ylabel("% dos registros")
        ax.legend(title="Criticidade", fontsize=7)
        plt.setp(ax.get_xticklabels(), rotation=20)
        st.pyplot(fig)
    with cb:
        fig, ax = plt.subplots(figsize=(6, 4.5))
        sns.countplot(data=dados, x="nivel_criticidade", order=ORDEM_CRITICIDADE, hue="nivel_criticidade",
                      palette="RdYlGn_r", legend=False, ax=ax)
        ax.set_xlabel("Nível de criticidade")
        ax.set_ylabel("Registros")
        st.pyplot(fig)

    st.markdown("**Ranking de vulnerabilidade por estado**")
    exibir = ranking.copy()
    for coluna in ["mortalidade", "internacao", "vacinacao", "expectativa", "medicos", "leitos", "indice_vulnerabilidade"]:
        exibir[coluna] = exibir[coluna].round(2)
    st.dataframe(exibir, use_container_width=True, hide_index=True)
    pct_critico = (dados["nivel_criticidade"] == "Crítico").mean() * 100
    reg_critica = prop["Crítico"].idxmax()
    st.info(
        f"**Interpretação:** {pct_critico:.1f}% dos registros filtrados estão no nível Crítico. "
        f"A região com maior proporção de registros críticos é {reg_critica} ({prop.loc[reg_critica, 'Crítico']:.1f}%). "
        f"O estado mais vulnerável pelo índice é {mais_vulneravel['uf']}, mas as diferenças entre estados são moderadas."
    )

with abas[5]:
    st.subheader("Tabela dinâmica")
    ca, cb, cc, cd = st.columns(4)
    linhas = ca.selectbox("Linhas", ["regiao", "uf", "municipio", "ano", "mes"], index=1)
    colunas = cb.selectbox("Colunas", ["(nenhuma)", "nivel_criticidade", "ano", "regiao", "mes"], index=1)
    valor_nome = cc.selectbox("Valor", list(INDICADORES), index=1)
    funcao = cd.selectbox("Função", ["mean", "sum", "max", "min", "count"])
    try:
        pivo = dados.pivot_table(
            index=linhas, columns=None if colunas == "(nenhuma)" else colunas,
            values=INDICADORES[valor_nome], aggfunc=funcao, observed=True,
        ).round(2)
        st.dataframe(pivo, use_container_width=True)
        st.download_button("Baixar tabela (CSV)", pivo.to_csv().encode("utf-8"), "tabela_dinamica.csv")
    except Exception as erro:
        st.error(f"Não foi possível montar a tabela com essa combinação: {erro}")
    with st.expander("Ver dados filtrados"):
        st.dataframe(dados, use_container_width=True)
        st.download_button("Baixar dados filtrados (CSV)", dados.to_csv(index=False).encode("utf-8"), "dados_filtrados.csv")

st.header("Conclusão executiva")
r_vac = dados["cobertura_vacinal"].corr(dados["taxa_mortalidade"])
reg_mort = dados.groupby("regiao")["taxa_mortalidade"].mean().idxmax()
st.success(
    f"Na seleção atual ({len(dados):,} registros), a expectativa média de vida é {numero(dados['expectativa_vida'].mean())} anos, "
    f"a mortalidade média é {numero(dados['taxa_mortalidade'].mean(), 2)} e a cobertura vacinal média é "
    f"{numero(dados['cobertura_vacinal'].mean())}%. A região com maior mortalidade média é {reg_mort} e o estado mais "
    f"vulnerável é {mais_vulneravel['uf']}. A correlação entre vacinação e mortalidade é {forca_correlacao(r_vac)} "
    f"({r_vac:.2f}). Recomenda-se priorizar os estados no topo do ranking de vulnerabilidade, ampliar a cobertura "
    "vacinal onde ela é mais baixa e acompanhar a capacidade hospitalar. Por ser uma base simulada, as conclusões "
    "são ilustrativas e não representam a situação real do país."
)
st.caption("Projeto educacional — Análise e Visualização de Dados com Python.")

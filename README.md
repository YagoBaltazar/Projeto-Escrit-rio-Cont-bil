# Indicadores de Saúde Pública no Brasil (2015–2024)

Projeto — Linguagem de Programação: Análise e Visualização de Dados com Python (Tema 23)  
**Aluno:** Yago Baltazar Ferreira | **Professor:** Alexandre Neves Louzada

## Problema
Indicadores de saúde pública ajudam a avaliar a qualidade de vida da população e a apoiar decisões de governo. O projeto analisa uma base **simulada** (fornecida pelo professor) para investigar a evolução dos indicadores, comparar regiões e estados, avaliar a capacidade hospitalar e identificar áreas vulneráveis.

## Base de dados
`dados/simulacao_saude_publica_brasil.csv`: 4.440 registros, 20 estados, 37 municípios, de 2015 a 2024 (expectativa de vida, mortalidade, internação, vacinação, médicos, leitos, doenças crônicas e nível de criticidade).

## Tecnologias
Python, Pandas, NumPy, Matplotlib, Seaborn, Streamlit, Plotly, SQLAlchemy, SQLite, GitHub, GitHub Pages, Streamlit Community Cloud.

## Funcionalidades
- **Dashboard (`app.py`):** KPIs, filtros (ano, mês, região, estado, município e criticidade), gráficos temporais, comparação regional, infraestrutura hospitalar, heatmap epidemiológico, dispersão vacinação x mortalidade, correlação, tabela dinâmica, interpretação textual e conclusão executiva.
- **Página Mapa e Consultas SQL:** mapa interativo (Plotly) e consultas SQL com SQLAlchemy.
- **Página Upload de CSV:** análise rápida de um novo arquivo com as mesmas colunas.
- **Persistência:** os dados do CSV são carregados em um banco SQLite (`database/saude_publica.db`), criado automaticamente na primeira execução.

## Estrutura
```
├── app.py
├── pages/
│   ├── 1_Mapa_e_Consultas_SQL.py
│   └── 2_Upload_de_CSV.py
├── db.py
├── utils.py
├── gerar_imagens.py
├── requirements.txt
├── README.md
├── index.html
├── dados/simulacao_saude_publica_brasil.csv
├── notebooks/analise_saude_publica.ipynb
├── database/
└── imagens/
```

## Como executar
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Aviso
Os dados são simulados e as conclusões são apenas educacionais.

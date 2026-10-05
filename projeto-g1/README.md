# Painel Executivo de um Escritório de Contabilidade

Projeto G1 — Linguagem de Programação: Análise e Visualização de Dados com Python  
**Aluno:** Yago Baltazar Ferreira | **Professor:** Alexandre Neves Louzada

## Problema
Um escritório de contabilidade precisa acompanhar clientes, faturamento, impostos por regime tributário, honorários e inadimplência. O projeto usa uma base **fictícia** (sem dados reais de clientes) e entrega análise, dashboard interativo e simulador tributário.

## Tecnologias
Python, Pandas, NumPy, Matplotlib, Seaborn, Streamlit, Plotly, SQLAlchemy, SQLite, Requests, GitHub, GitHub Pages, Streamlit Community Cloud.

## Funcionalidades
- **Intermediárias:** filtros múltiplos, KPIs dinâmicos, análise temporal, dashboard em seções (abas), visualizações comparativas, análise geográfica, upload de arquivos.
- **Avançadas:** consumo de API (BrasilAPI), persistência em banco (SQLAlchemy + SQLite), modelagem relacional, dashboard multipágina, mapa interativo (Plotly), correlação estatística, integração de múltiplas fontes (API + CSV + banco).

## Estrutura
```
projeto-g1/
├── app.py                      # página principal do dashboard
├── pages/                      # páginas extras (multipágina)
├── tributos.py                 # cálculo dos regimes tributários
├── db.py                       # modelos SQLAlchemy e acesso ao SQLite
├── gerar_dados.py              # gera os dados fictícios (CSV + SQLite)
├── gerar_imagens.py            # gera os gráficos para o index.html
├── utils.py                    # funções compartilhadas e filtros
├── requirements.txt
├── index.html                  # página do projeto (GitHub Pages)
├── dados/                      # clientes.csv e apuracoes.csv
├── database/                   # escritorio.db (criado automaticamente)
├── notebooks/                  # analise_escritorio_contabil.ipynb
└── imagens/
```

## Como executar
```bash
pip install -r requirements.txt
python gerar_dados.py      # opcional: o app cria o banco sozinho na primeira execução
streamlit run app.py
```

## Aviso
Os cálculos tributários são **simplificados e didáticos**, não substituem o trabalho de um contador.

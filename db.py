from pathlib import Path

import pandas as pd
from sqlalchemy import Float, Integer, String, create_engine, text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

BASE_DIR = Path(__file__).parent
CSV_PATH = BASE_DIR / "dados" / "simulacao_saude_publica_brasil.csv"
DB_PATH = BASE_DIR / "database" / "saude_publica.db"
DB_PATH.parent.mkdir(exist_ok=True)

engine = create_engine(f"sqlite:///{DB_PATH}")


class Base(DeclarativeBase):
    pass


class Indicador(Base):
    __tablename__ = "indicadores_saude"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ano: Mapped[int] = mapped_column(Integer)
    mes: Mapped[int] = mapped_column(Integer)
    data: Mapped[str] = mapped_column(String(10))
    regiao: Mapped[str] = mapped_column(String(20))
    uf: Mapped[str] = mapped_column(String(2))
    municipio: Mapped[str] = mapped_column(String(60))
    expectativa_vida: Mapped[float] = mapped_column(Float)
    taxa_mortalidade: Mapped[float] = mapped_column(Float)
    taxa_internacao: Mapped[float] = mapped_column(Float)
    cobertura_vacinal: Mapped[float] = mapped_column(Float)
    medicos_por_1000: Mapped[float] = mapped_column(Float)
    leitos_hospitalares: Mapped[int] = mapped_column(Integer)
    casos_doencas_cronicas: Mapped[int] = mapped_column(Integer)
    nivel_criticidade: Mapped[str] = mapped_column(String(10))


def ler_csv(arquivo=CSV_PATH):
    return pd.read_csv(arquivo, encoding="utf-8-sig")


def criar_banco(df):
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    df.to_sql("indicadores_saude", engine, if_exists="append", index=False)


def banco_existe():
    if not DB_PATH.exists():
        return False
    try:
        with engine.connect() as conexao:
            total = conexao.execute(text("SELECT COUNT(*) FROM indicadores_saude")).scalar()
        return total > 0
    except Exception:
        return False


def carregar_dados():
    return pd.read_sql("SELECT * FROM indicadores_saude", engine)


def consultar(sql, parametros=None):
    return pd.read_sql(text(sql), engine, params=parametros or {})

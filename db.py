from pathlib import Path

import pandas as pd
from sqlalchemy import ForeignKey, Float, Integer, String, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, relationship

BASE_DIR = Path(__file__).parent
DB_PATH = BASE_DIR / "database" / "escritorio.db"
DB_PATH.parent.mkdir(exist_ok=True)

engine = create_engine(f"sqlite:///{DB_PATH}")


class Base(DeclarativeBase):
    pass


class Cliente(Base):
    __tablename__ = "clientes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    cnpj: Mapped[str] = mapped_column(String(18), unique=True)
    razao_social: Mapped[str] = mapped_column(String(120))
    uf: Mapped[str] = mapped_column(String(2))
    setor: Mapped[str] = mapped_column(String(30))
    porte: Mapped[str] = mapped_column(String(20))
    regime: Mapped[str] = mapped_column(String(30))
    honorario_mensal: Mapped[float] = mapped_column(Float)
    data_entrada: Mapped[str] = mapped_column(String(10))

    apuracoes: Mapped[list["Apuracao"]] = relationship(back_populates="cliente")


class Apuracao(Base):
    __tablename__ = "apuracoes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    cliente_id: Mapped[int] = mapped_column(ForeignKey("clientes.id"))
    competencia: Mapped[str] = mapped_column(String(7))
    faturamento: Mapped[float] = mapped_column(Float)
    despesas: Mapped[float] = mapped_column(Float)
    imposto: Mapped[float] = mapped_column(Float)
    honorario: Mapped[float] = mapped_column(Float)
    pago: Mapped[int] = mapped_column(Integer)

    cliente: Mapped["Cliente"] = relationship(back_populates="apuracoes")


def criar_banco(clientes_df, apuracoes_df):
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    with Session(engine) as sessao:
        for linha in clientes_df.to_dict("records"):
            sessao.add(Cliente(**linha))
        sessao.flush()
        for linha in apuracoes_df.to_dict("records"):
            sessao.add(Apuracao(**linha))
        sessao.commit()


def banco_existe():
    if not DB_PATH.exists():
        return False
    try:
        with Session(engine) as sessao:
            return sessao.execute(select(Cliente).limit(1)).first() is not None
    except Exception:
        return False


def carregar_dados():
    consulta = (
        "SELECT a.id, a.cliente_id, a.competencia, a.faturamento, a.despesas, "
        "a.imposto, a.honorario, a.pago, c.cnpj, c.razao_social, c.uf, c.setor, "
        "c.porte, c.regime, c.data_entrada "
        "FROM apuracoes a JOIN clientes c ON c.id = a.cliente_id"
    )
    df = pd.read_sql(consulta, engine)
    df["competencia"] = pd.to_datetime(df["competencia"] + "-01")
    return df


def carregar_clientes():
    return pd.read_sql("SELECT * FROM clientes", engine)


def inserir_cliente(cnpj, razao_social, uf, setor, porte, regime, honorario):
    with Session(engine) as sessao:
        existe = sessao.execute(select(Cliente).where(Cliente.cnpj == cnpj)).first()
        if existe:
            return False
        sessao.add(Cliente(
            cnpj=cnpj,
            razao_social=razao_social,
            uf=uf,
            setor=setor,
            porte=porte,
            regime=regime,
            honorario_mensal=honorario,
            data_entrada=str(pd.Timestamp.today().date()),
        ))
        sessao.commit()
        return True

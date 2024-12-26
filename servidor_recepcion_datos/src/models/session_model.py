from sqlmodel import Field, SQLModel
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class StatefulSession(Base):
    """
    Esta clase sirve para guardar las sesiones que se realizan en el contexto de DATEX-II en
    la base de datos postgres, de tal forma que en caso de caerse la conexión, esta se pueda
    restablecer cuando se inicia de nuevo el proceso
    """
    __tablename__ = 'stateful_sessions'
    id = Column(String, primary_key=True)
    agency = Column(String)
    status = Column(String)
    startSession = Column(DateTime)


Base.metadata.create_all()


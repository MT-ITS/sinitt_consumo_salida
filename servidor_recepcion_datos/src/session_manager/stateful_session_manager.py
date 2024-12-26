from services.singleton import Singleton
import logging
from services.singleton import Singleton
from settings import settings
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import Session

logging.basicConfig(level=logging.INFO)


class StatefulSessionManager(metaclass=Singleton):
    """
    Clase para manejar las sesiones que se establecen a través de DATEX-II.
    """
    Base = declarative_base()

    class StatefulSession(Base):
        __tablename__ = 'sesiones_stateful'
        id = Column(String, primary_key=True)
        agency = Column(String)
        status = Column(String)
        start_session = Column(DateTime)

    def __init__(self):
        #Base.metadata.create_all()
        if not hasattr(self, 'conn'):
            self.conn = create_engine(settings.sqlalchemy_pg, echo=True, pool_size=settings.postgres_pool_size)
            self.Session = Session(bind=self.conn)

    def open_session(self, session_id, agency_name, s_session):
        stateful_session = self.StatefulSession(id=session_id, agency=agency_name, status='ON', start_session=s_session)
        try:
            self.Session.add(stateful_session)
            self.Session.commit()
        except Exception as e:
            logging.error(e)
            self.Session.rollback()

    def query_if_session_active(self, session_id):
        stateful_session = self.Session.query(self.StatefulSession).filter_by(id=session_id).first()
        return stateful_session

    def refresh_session(self, session_id):
        stateful_session = self.Session.query(self.StatefulSession).filter_by(id=session_id).first()
        stateful_session.status = 'ON'
        try:
            self.Session.add(stateful_session)
            self.Session.commit()
        except Exception as e:
            logging.error(e)
            self

    def close_session(self, session_id):
        stateful_session = self.Session.query(self.StatefulSession).filter_by(id=session_id).first()
        stateful_session.status = 'OFF'
        try:
            self.Session.add(stateful_session)
            self.Session.commit()
        except Exception as e:
            logging.error(e)
            self


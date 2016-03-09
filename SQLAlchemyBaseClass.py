__author__ = 'Toni'
__version__ = "1.0.0"

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
engine = None
Base = declarative_base()

from sqlalchemy.orm import sessionmaker

class DefaultTableOperations(object):
    def __init__(self):
        super().__init__()

    def set_session(self, session):
        self.session = session

    def get_class(self) -> Base:
        return self.__class__

    def add_and_commit(self, row):
        self.session.add(row)
        self.session.commit()

    def find(self, id):
        c = self.get_class()
        query = self.session.query(c).filter(c.id == id)
        instance = query.first()
        return instance

    def find_all(self, id):
        c = self.get_class()
        query = self.session.query(c).filter(c.id == id)
        instance = query.all()
        return instance

    def get_all(self):
        c = self.get_class()
        query = self.session.query(c).order_by(c.id)
        return query.all()

class dbManager(object):
    def __init__(self, db_name = 'sqlite:///database.db', echo=False):
        engine = create_engine(db_name, echo=echo)
        Session = sessionmaker(bind=engine)
        self.session = Session()
        Base.metadata.create_all(engine)


        self.databases = {}

    def __del__(self):
        self.session.close()

def main():
    dbManager()

if __name__ == '__main__':
    main()

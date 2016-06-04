from __future__ import print_function
__author__ = 'Toni'




try:
    from sqlalchemy import create_engine
    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy import and_
except ImportError:
    print('cant import sqlAlchemy')
from random import randrange

engine = create_engine('sqlite:///generator_database.db', echo=False)
Base = declarative_base()

from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import sessionmaker
from SQLAlchemyBaseClass import DefaultTableOperations

class CharacterTable(Base, DefaultTableOperations):
    __tablename__ = "characters"
    character_id = Column(Integer, primary_key=True)
    fname = Column(String)
    lname = Column(String)
    gender = Column(String)
    alias = Column(String)

    def add(self, fname, lname, gender, alias):

        self.get_class()(fname=fname, lname=lname, gender=gender, alias=alias)
        # should maybe add more stuff?

class NameTable(Base, DefaultTableOperations):
    __tablename__ = 'name_table'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    name_group = Column(String)
    gender = Column(String)
    type = Column(String, nullable=False)
    __mapper_args__ = {'polymorphic_on': type, 'polymorphic_identity': 'table'}


    def add_name(self, name, group='default', gender='male'):
        row = self.get_class()(name=name, name_group=group, gender=gender)
        self.add_and_commit(row)

    def add_all(self, names:[], group='default', gender='male'):
        array = []
        for name in names:
            instance = self.get_class()(name=name, name_group=group, gender=gender)
            array.append(instance)
        self.session.add_all(array)
        self.session.commit()
        print("add_all complete")


    def search(self, name, group, gender, case_sensitive=True):
        c = self.get_class()

        if case_sensitive:
            query = self.session.query(c). \
                filter(c.name == name). \
                filter(c.name_group == group). \
                filter(c.gender == gender)
            instance = query.first()
            return instance
        else:
            query = self.session.query(c). \
                filter(c.name == name). \
                filter(c.name_group == group). \
                filter(c.gender == gender)
            instance = query.first()
            return instance

    def get_males(self):
        c = self.get_class()
        query = self.session.query(c). \
            filter(c.gender == 'male'). \
            filter(c.name_group == "default")
        instance = query.all()
        return instance

    def get_females(self):
        c = self.get_class()
        query = self.session.query(c). \
            filter(c.gender == 'female'). \
            filter(c.name_group == "default")
        instance = query.all()
        return instance

    def filter_by(self, group:str, gender:str):
        c = self.get_class()
        print(str(c))
        query = object()
        if group and gender:
            # print(group)
            # print(gender)
            query = self.session.query(c). \
                filter(c.gender == gender). \
                filter(c.name_group == group)
            # instance = query.all()

            # print(str(query))
            # print(instance)
            # print("query with group and gender")
        elif group:
            query = self.session.query(c). \
                filter(c.name_group == group)
        instance = query.all()
        # print(instance[0].group)
        # print(instance[0].gender)
        # print(instance)
        return instance

    '''def __repr__(self):
        table = str(self.type)
        return "<" + table + "(name='%s', group='%s', gender='%s')>" % (self.name, self.name_group, self.gender)'''


class FirstNames(NameTable):
    __mapper_args__ = {'polymorphic_identity': 'first_names'}


class LastNames(NameTable):
    __mapper_args__ = {'polymorphic_identity': 'last_names'}


class FirstAliases(NameTable):
    __mapper_args__ = {'polymorphic_identity': 'first_aliases'}


class LastAliases(NameTable):
    __mapper_args__ = {'polymorphic_identity': 'last_aliases'}


class dbManager(object):
    def __init__(self):
        Session = sessionmaker(bind=engine)
        self.session = Session()
        Base.metadata.create_all(engine)
        self.first_names = FirstNames()
        self.last_names = LastNames()
        self.first_aliases = FirstAliases()
        self.last_aliases = LastAliases()

        self.first_names.set_session(self.session)
        self.last_names.set_session(self.session)
        self.first_aliases.set_session(self.session)
        self.last_aliases.set_session(self.session)

        self.databases = {'first_names': self.first_names, 'last_names': self.last_names,
                          'first_aliases': self.first_aliases, 'last_aliases': self.last_aliases}

    def __del__(self):
        self.session.close()





class Dice(object):
    def __init__(self, dices:int, sides:int):
        self.dices = dices
        self.sides = sides
        self.last_roll = 0

    def roll(self, use_randrange=True) -> int:
        result = 0
        if use_randrange:
            self.last_roll = sum(randrange(self.sides) + 1 for die in range(self.dices))
            result = self.last_roll
        return result


class TableRow(object):
    def __init__(self, data:{}):
        self.data = data

    def add(self, name, value):
        self.data[name] = value


class TableModel(object):
    def __init__(self):

        self.rows = {}

    def add_row(self, name:str, data:TableRow):
        self.rows[name] = data

    def load_table(self, table_name:str, gender_filter:str=None, group_filter:str=None):
        db = dbManager()
        dbtable = db.databases[table_name]
        table_data = object()
        if gender_filter or group_filter:
            table_data = dbtable.filter_by(group=group_filter, gender=gender_filter)
            # print(table_data)
        else:
            table_data = dbtable.get_all()

        i = 0
        for instance in table_data:
            row = TableRow(
                {'id': instance.id, 'name': instance.name, 'group': instance.name_group, 'gender': instance.gender})
            self.add_row(i, row)
            i += 1

            # print(str(self.rows[0].data))

    def load_gender(self, gender):
        db = dbManager()
        dbtable = db.databases['first_names']
        table_data = object()
        if gender is 'female':
            table_data = dbtable.get_females()
        else:
            table_data = dbtable.get_males()
        i = 0
        for instance in table_data:
            row = TableRow(
                {'id': instance.id, 'name': instance.name, 'group': instance.name_group, 'gender': instance.gender})
            self.add_row(i, row)
            i += 1

        if len(self.rows) == 0:
            print('error loading gender ' + gender)
        print('i was handled ' + str(i) + ' times')


    def get_random_choice(self) -> TableRow:
        row_count = len(self.rows)
        dice = Dice(1, row_count - 1)
        num = dice.roll()
        return self.rows[num]





def main():
    db_manager = dbManager()


if __name__ == '__main__':
    main()

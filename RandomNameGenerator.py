__author__ = 'Toni'

from tkinter import *
from tkinter import ttk
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import and_
from random import randrange

engine = create_engine('sqlite:///generator_database.db', echo=False)
Base = declarative_base()

from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import sessionmaker

class NameTable(Base):
    __tablename__ = 'name_table'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    name_group = Column(String)
    gender = Column(String)
    type = Column(String, nullable=False)
    __mapper_args__ = {'polymorphic_on': type, 'polymorphic_identity': 'table'}

    def set_session(self, session):

        self.session = session
        '''for row in self.get_all():
            print(row)'''


    def get_class(self) -> Base:
        if isinstance(self, FirstNames):
            return FirstNames
        elif isinstance(self, LastNames):
            return LastNames
        elif isinstance(self, FirstAliases):
            return FirstAliases
        elif isinstance(self, LastAliases):
            return LastAliases
        else:
            return NameTable

    def add_and_commit(self, row):
        self.session.add(row)
        self.session.commit()

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

    def find(self, id):
        c = self.get_class()
        query = self.session.query(c).filter(c.id == id)
        instance = query.first()
        return instance

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

    def get_all(self):
        c = self.get_class()
        query = self.session.query(c).order_by(c.id)
        return query.all()

    def get_males(self):
        c = self.get_class()
        query = self.session.query(c) . \
            filter(c.gender == 'male') . \
            filter(c.name_group == "default")
        instance = query.all()
        return instance

    def get_females(self):
        c = self.get_class()
        query = self.session.query(c) . \
            filter(c.gender == 'female') . \
            filter(c.name_group == "default")
        instance = query.all()
        return instance

    def filter_by(self, group:str, gender:str):
        c = self.get_class()
        print(str(c))
        query = object()
        if group and gender:
            print(group)
            print(gender)
            query = self.session.query(c) . \
                filter(c.gender == gender) . \
                filter(c.name_group == group)
            # instance = query.all()

            # print(str(query))
            # print(instance)
            # print("query with group and gender")
        elif group:
            query = self.session.query(c) . \
                filter(c.name_group == group)
        instance = query.all()
        # print(instance[0].group)
        # print(instance[0].gender)
        # print(instance)
        return instance

    def __repr__(self):
        table = str(self.type)
        return "<" + table + "(name='%s', group='%s', gender='%s')>" % (self.name, self.name_group, self.gender)

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

        self.databases = {'first_names':self.first_names, 'last_names':self.last_names,
                          'first_aliases':self.first_aliases, 'last_aliases':self.last_aliases}

    def __del__(self):
        self.session.close()

class UIObject(object):
    '''Base class for all user interface components'''

    def __init__(self, master, controller='None'):
        self.frame = ttk.Frame(master)
        self.contr = controller

        self.frame.grid(column=0, row=0)

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
        super().__init__()
        self.data = data
    def add(self, name, value):
        self.data[name] = value

class TableModel(object):
    def __init__(self):
        super().__init__()
        self.rows = {}

    def add_row(self, name:str, data:TableRow):
        self.rows[name] = data

    def load_table(self, table_name:str, gender_filter:str = None, group_filter:str = None):
        db = dbManager()
        dbtable = db.databases[table_name]
        table_data = object()
        if gender_filter or group_filter:
            table_data = dbtable.filter_by(group=group_filter, gender=gender_filter)
            print(table_data)
        else:
            table_data = dbtable.get_all()

        i = 0
        for instance in table_data:
            row = TableRow({'id':instance.id, 'name':instance.name, 'group':instance.name_group, 'gender':instance.gender})
            self.add_row(i, row)
            i = i + 1

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
            row = TableRow({'id':instance.id, 'name':instance.name, 'group':instance.name_group, 'gender':instance.gender})
            self.add_row(i, row)
            i = i + 1

        if len(self.rows) == 0:
            print('error loading gender ' + gender)
        print('i was handled ' + str(i) + ' times')



    def get_random_choice(self) -> TableRow:
        row_count = len(self.rows)
        dice = Dice(1, row_count - 1)
        num = dice.roll()
        return self.rows[num]


class MenuBar(object):
    def __init__(self, root):
        self.root = root
        root.option_add('*tearOff', FALSE)

        menubar = Menu(root)
        root['menu'] = menubar

        menu_file = Menu(menubar)
        menu_settings = Menu(menubar)
        menubar.add_cascade(menu=menu_file, label='File')
        menubar.add_cascade(menu=menu_settings, label='Settings')
        menu_file.add_command(label='Quit', command=self.close)
        menu_settings.add_command(label='Import names', command=self.import_names)
        menu_settings.add_command(label='Name count', command=self.name_count)
        menu_settings.add_command(label='Add aliases', command=self.add_aliases)

    def close(self):
        pass

    def import_names(self):
        window = Toplevel(self.root)
        import_screen = importScreen(window)

    def name_count(self):
        window = Toplevel(self.root)
        count_screen = CountScreen(window)

    def add_aliases(self):
        window = Toplevel(self.root)
        add_screen = AddAliasScreen(window)



class UIdogTag(object):
    def __init__(self, component, reference_id, subsection):
        super().__init__()
        self.component = component
        self.reference_id = reference_id
        self.subsection = subsection


class CustomPanedWindow(UIObject):
    '''Paned'''

    def __init__(self, master, controller, vertical=True):
        super().__init__(master, controller)
        self.components = []
        if vertical:
            self.group = ttk.Panedwindow(self.frame, orient=VERTICAL)
            self.group.grid(column=0, row=0)
        else:
            self.group = ttk.Panedwindow(self.frame, orient=HORIZONTAL)
            self.group.grid(column=0, row=0)


    def add(self, reference_id, component_frame=None, component=None, subsection=None, from_array_to_labels=False,
            array=None):
        if from_array_to_labels:
            for cell in array:
                label = ttk.Label(self.group, text = cell)
                self.components.append(UIdogTag(component=label,
                                                reference_id=reference_id, subsection=subsection))
                self.group.add(label)
        else:
            self.components.append(UIdogTag(component=component, reference_id=reference_id, subsection=subsection))

            self.group.add(component_frame)


    def get(self, reference_id, subsection):
        for component in self.components:
            if component.reference_id == reference_id and component.subsection == subsection:
                return component
        return None

    def clear(self):
        self.components.clear()
        for child in self.group.panes():
            self.group.remove(child)


class CustomRadioGroup(UIObject):
    def __init__(self, master, controller, command=None, header=None):
        super().__init__(master, controller)
        self.label_frame = ttk.Labelframe(self.frame, text=header)
        self.pane = CustomPanedWindow(self.label_frame, None)
        self.variable = StringVar()
        self.command = command

        self.label_frame.grid(column=0, row=0)

    def add(self, text:str, value, use_command=False):
        radioButton = ttk.Radiobutton(self.pane.frame, text=text, variable=self.variable, value=value)
        if use_command:
            radioButton.configure(command=self.command)
        self.pane.add(reference_id=text, component=radioButton, component_frame=radioButton, subsection='radio')

class LabelAndValue(UIObject):
    '''label combined with another label reserved for changing value'''

    def __init__(self, master, controller, label_text, label_length=10, value_length=2):
        super().__init__(master, controller)
        self.variable = StringVar()
        self.lbl_text = ttk.Label(self.frame, text=label_text, width=label_length)
        self.lbl_value = ttk.Label(self.frame, textvariable=self.variable, width=value_length)
        self.lbl_text.grid(column=0, row=0)
        self.lbl_value.grid(column=1, row=0)

    def set(self, value):
        self.variable.set(value)
        # self.frame.update()

    def get(self):
        return self.variable.get()

class TextAndEntryfield(UIObject):
    '''Basic textlabel combined with entry-widged'''

    def __init__(self, master, topic, width_label=15, width_num=2, controller=None, command=None, trace=False):
        super().__init__(master, controller)
        self.variable = StringVar()
        self.textlabel = ttk.Label(self.frame, text=topic, width=width_label)
        self.entry = ttk.Entry(self.frame, textvariable=self.variable, width=width_num)

        self.textlabel.grid(column=0, row=0)
        self.entry.grid(column=1, row=0)
        self.command = command

        if trace:
            self.variable.trace("w", self.save)
            self.last_value = "None"

    def set(self, value):
        self.variable.set(value)

    def save(self, *args):
        # print('here we are')
        if self.command:
            value = self.variable.get()
            if value != self.last_value:
                self.command()
                #print('value: ' + value)

    def get(self):
        return self.variable.get()



class MainScreen(UIObject):
    def __init__(self, master):
        super().__init__(master, controller=None)
        self.gender_radio_group = CustomRadioGroup(self.frame, None)
        self.gender_radio_group.add("male", "male")
        self.gender_radio_group.add("female", "female")
        self.lbl_fname = LabelAndValue(self.frame, None, "name", label_length=10, value_length=40)
        self.lbl_falias = LabelAndValue(self.frame, None, "alias", label_length=10, value_length=40)
        self.btn_rnd = ttk.Button(self.frame, text="random", command=self.random_name)

        self.gender_radio_group.frame.grid(column=0, row=0, sticky=(W, N))
        self.lbl_fname.frame.grid(column=0, row=1)
        self.lbl_falias.frame.grid(column=0, row=2)
        self.btn_rnd.grid(column=0, row=3)

        self.male_fnames = TableModel()
        self.female_fnames = TableModel()
        self.last_names = TableModel()
        self.first_aliases = TableModel()
        self.last_aliases = TableModel()

        self.male_fnames.load_table('first_names', 'male', 'default')
        self.female_fnames.load_table('first_names', 'female', 'default')
        self.first_aliases.load_table('first_aliases', 'all', 'default')
        self.last_aliases.load_table('last_aliases', 'all', 'default')
        self.last_names.load_table('last_names', 'all', 'default')

        self.db = dbManager()


    def random_name(self, *args):
        full_name = ''
        if self.gender_radio_group.variable.get() == 'male':
            fname = self.male_fnames.get_random_choice()
            full_name = fname.data['name']
        else:
            fname = self.female_fnames.get_random_choice()
            full_name = fname.data['name']

        lname = self.last_names.get_random_choice().data['name']
        full_name = full_name + ' ' + lname
        self.lbl_fname.set(full_name)

        falias = self.first_aliases.get_random_choice()
        lalias = self.last_aliases.get_random_choice()
        alias = falias.data['name'] + " " + lalias.data['name']
        self.lbl_falias.set(alias)


class importScreen(UIObject):
    def __init__(self, master):
        super().__init__(master, controller=None)
        self.lbl_filepath = TextAndEntryfield(self.frame, "Filepath", width_num=20)
        self.lbl_group = TextAndEntryfield(self.frame, "Group", width_num=20)
        self.lbl_gender = TextAndEntryfield(self.frame, "Gender", width_num=20)
        self.lbl_db_name = TextAndEntryfield(self.frame, "Database Table", width_num=20)
        self.btn_import = ttk.Button(self.frame, text="Import", command=self.import_names)

        self.lbl_filepath.frame.grid(column=0, row=0)
        self.lbl_group.frame.grid(column=0, row=1)
        self.lbl_gender.frame.grid(column=0, row=2)
        self.lbl_db_name.frame.grid(column=0, row=3)
        self.btn_import.grid(column=0, row=4)

    def import_names(self):
        names = self.read_file(self.lbl_filepath.get())
        db = dbManager()
        db.databases[self.lbl_db_name.get()].add_all(names, group=self.lbl_group.get(), gender=self.lbl_gender.get())

    def read_file(self, filepath):
        f = open(filepath, 'r')
        array = []
        for line in f:
           row = line.strip()
           array.append(row)
        f.close()
        return array

class CountScreen(UIObject):
    def __init__(self, master):
        super().__init__(master, controller=None)
        self.elements = {}
        db =  dbManager()
        row_num=0
        for key, value in db.databases.items():
            self.elements[key] = ttk.Label(self.frame, text=key)
            self.elements[key].grid(column=0, row=row_num)
            number_of_names = len(db.databases[key].get_all())
            self.elements[key + 'value'] = ttk.Label(self.frame, text=str(number_of_names))
            self.elements[key + 'value'].grid(column=1, row=row_num)
            row_num = row_num + 1

        self.females = ttk.Label(self.frame, text='female names')
        self.males = ttk.Label(self.frame, text='male names')
        fems = str(len(db.databases['first_names'].filter_by(group='default', gender='female')))
        males = str(len(db.databases['first_names'].filter_by(group='default', gender='male')))
        self.fem_count = ttk.Label(self.frame, text=fems)
        self.men_count = ttk.Label(self.frame, text=males)
        self.females.grid(column=0, row=row_num + 1)
        self.fem_count.grid(column=1, row=row_num +1)
        self.males.grid(column=0, row=row_num +2)
        self.men_count.grid(column=1, row=row_num +2)

class AddAliasScreen(UIObject):
    def __init__(self, master):
        super().__init__(master, controller=None)
        self.lbl_falias = TextAndEntryfield(self.frame, 'first', command=self.search_first, trace=True, width_num=25)
        self.lbl_fresult = LabelAndValue(self.frame, None, 'result', value_length=15)
        self.lbl_lalias = TextAndEntryfield(self.frame, 'last', command=self.search_last, trace=True, width_num=25)
        self.lbl_lresult = LabelAndValue(self.frame, None, 'result', value_length=15)

        self.bnt_save_first = ttk.Button(self.frame, text = 'save', command=self.save_first)
        self.btn_save_last = ttk.Button(self.frame, text = 'save', command=self.save_last)

        self.lbl_falias.frame.grid(column=0, row=0, sticky=(N,W))
        self.lbl_fresult.frame.grid(column=0, row=1, sticky= (N, W))
        self.bnt_save_first.grid(column=1, row=0)

        self.lbl_lalias.frame.grid(column=0, row=2, sticky=(N,W))
        self.lbl_lresult.frame.grid(column=0, row=3, sticky=(N, W))
        self.btn_save_last.grid(column=1, row=2)

    def search_first(self):
        db = dbManager()
        instance = db.first_aliases.search(self.lbl_falias.variable.get(), group='default', gender='all', case_sensitive=False)
        self.lbl_fresult.variable.set(instance)

    def search_last(self):
        db = dbManager()
        instance = db.last_aliases.search(self.lbl_lalias.variable.get(), group='default', gender='all', case_sensitive=False)
        self.lbl_lresult.variable.set(instance)

    def save_first(self):
        db = dbManager()
        db.first_aliases.add_name(self.lbl_falias.variable.get(), group='default', gender='all')
        self.search_first()

    def save_last(self):
        db = dbManager()
        db.last_aliases.add_name(self.lbl_lalias.variable.get(), group='default', gender='all')
        self.search_last()

def main():
    root = Tk()
    root.title('Name Generator  1.0')
    menubar = MenuBar(root)
    app = MainScreen(root)
    root.mainloop()


if __name__ == '__main__':
    main()
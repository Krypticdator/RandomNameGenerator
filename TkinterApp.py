try:
    from tkinter import *
    from tkinter import ttk

try:
    from TkinterComponentFactory import TextAndEntryfield
    from TkinterComponentFactory import LabelAndValue
    from TkinterComponentFactory import CustomRadioGroup
    from TkinterComponentFactory import CustomPanedWindow
except ImportError:
    print('cant import TkinterComponentFactory')
except ImportError:
    print('cant import tkinter')

from RandomNameGenerator import dbManager, TableModel

class UIObject(object):
    '''Base class for all user interface components'''

    def __init__(self, master, controller='None'):
        self.frame = ttk.Frame(master)
        self.contr = controller

        self.frame.grid(column=0, row=0)

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
        self.frame.grid(row=0, column=0, sticky = (N, E, W, S))

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

    @staticmethod
    def read_file(filepath):
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
        db = dbManager()
        row_num = 0
        for key, value in db.databases.items():
            self.elements[key] = ttk.Label(self.frame, text=key)
            self.elements[key].grid(column=0, row=row_num)
            number_of_names = len(db.databases[key].get_all())
            self.elements[key + 'value'] = ttk.Label(self.frame, text=str(number_of_names))
            self.elements[key + 'value'].grid(column=1, row=row_num)
            row_num += 1

        self.females = ttk.Label(self.frame, text='female names')
        self.males = ttk.Label(self.frame, text='male names')
        fems = str(len(db.databases['first_names'].filter_by(group='default', gender='female')))
        males = str(len(db.databases['first_names'].filter_by(group='default', gender='male')))
        self.fem_count = ttk.Label(self.frame, text=fems)
        self.men_count = ttk.Label(self.frame, text=males)
        self.females.grid(column=0, row=row_num + 1)
        self.fem_count.grid(column=1, row=row_num + 1)
        self.males.grid(column=0, row=row_num + 2)
        self.men_count.grid(column=1, row=row_num + 2)


class AddAliasScreen(UIObject):
    def __init__(self, master):
        super().__init__(master, controller=None)
        self.lbl_falias = TextAndEntryfield(self.frame, 'first', command=self.search_first, trace=True, width_num=25)
        self.lbl_fresult = LabelAndValue(self.frame, None, 'result', value_length=15)
        self.lbl_lalias = TextAndEntryfield(self.frame, 'last', command=self.search_last, trace=True, width_num=25)
        self.lbl_lresult = LabelAndValue(self.frame, None, 'result', value_length=15)

        self.bnt_save_first = ttk.Button(self.frame, text='save', command=self.save_first)
        self.btn_save_last = ttk.Button(self.frame, text='save', command=self.save_last)

        self.lbl_falias.frame.grid(column=0, row=0, sticky=(N, W))
        self.lbl_fresult.frame.grid(column=0, row=1, sticky=(N, W))
        self.bnt_save_first.grid(column=1, row=0)

        self.lbl_lalias.frame.grid(column=0, row=2, sticky=(N, W))
        self.lbl_lresult.frame.grid(column=0, row=3, sticky=(N, W))
        self.btn_save_last.grid(column=1, row=2)

    def search_first(self):
        db = dbManager()
        instance = db.first_aliases.search(self.lbl_falias.variable.get(), group='default', gender='all',
                                           case_sensitive=False)
        self.lbl_fresult.variable.set(instance)

    def search_last(self):
        db = dbManager()
        instance = db.last_aliases.search(self.lbl_lalias.variable.get(), group='default', gender='all',
                                          case_sensitive=False)
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
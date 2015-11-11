__author__ = 'Toni'


from tkinter import *
from tkinter import ttk

class UIObject(object):
    '''Base class for all user interface components'''

    def __init__(self, master, controller='None'):
        self.frame = ttk.Frame(master)
        self.contr = controller

        self.frame.grid(column=0, row=0)

class UIIDComponent(object):
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
                label = ttk.Label(self.group, text=cell)
                self.components.append(UIIDComponent(component=label,
                                                reference_id=reference_id, subsection=subsection))
                self.group.add(label)
        else:
            self.components.append(UIIDComponent(component=component, reference_id=reference_id, subsection=subsection))

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
                # print('value: ' + value)

    def get(self):
        return self.variable.get()

class EntryField(UIObject):
    '''basic inputfield wrapped in a class'''

    def __init__(self, master, width_num=15):
        super().__init__(master)
        self.variable = StringVar()
        # self.frame = ttk.Frame(master)
        self.entry = ttk.Entry(self.frame, textvariable=self.variable, width=width_num)
        self.entry.grid(column=0, row=0)

    def set(self, value):
        self.variable.set(str(value))

    def get(self):
        return self.variable.get()
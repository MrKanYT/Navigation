from tkinter import *
import frontend.GUIConfig as cfg
from tkinter.ttk import *
from PIL import Image, ImageTk
from tkinter import Canvas


class Menubar(Frame):

    menuBar: Menu
    fileMenu: Menu

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.menuBar = Menu(self.master)
        self.fileMenu = Menu(self.menuBar, tearoff=False)

        self.master.config(menu=self.menuBar)

        self.fileMenu.add_command(label="Открыть")

        self.menuBar.add_cascade(label="Файл", menu=self.fileMenu)


class Dashboard(Frame):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.init_ui()

    def init_ui(self):
        b = Button(self, text="Hello World!")
        b.pack()


class Workspace(Frame):

    canvas:  Canvas

    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self.init_ui()

    def init_ui(self):
        canvas = Canvas(self, width=999, height=999)
        canvas.pack(fill=BOTH)

        pilImage = Image.open("image.png")
        image = ImageTk.PhotoImage(pilImage)
        imagesprite = canvas.create_image(400, 400, image=image)


class Main(Frame):

    dashboard: Dashboard
    workspace: Workspace
    separator: Separator

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.init_ui()

    def init_ui(self):
        self.dashboard = Dashboard(padding=20)
        self.dashboard.pack(fill=Y, side=LEFT)
        self.separator = Separator(orient=VERTICAL)
        self.separator.pack(fill=Y, side=LEFT)
        self.workspace = Workspace(self)
        self.workspace.pack(fill=BOTH, expand=TRUE, side=LEFT)


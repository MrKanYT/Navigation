from tkinter import *
from tkinter.ttk import *
from frontend.widgets import *
import frontend.GUIConfig as cfg

class App(Tk):

    TITLE = "Navigation"
    WIDTH = 1240
    HEIGHT = 720

    menubar: Menubar
    main: Main
    style: Style

    def __init__(self):
        super().__init__()
        self.run()

    def run(self):
        self.create_styles()
        self.apply_config()
        self.init_ui()
        self.mainloop()

    def apply_config(self):
        self.title(App.TITLE)
        self.geometry(f"{App.WIDTH}x{App.HEIGHT}")

    def create_styles(self):
        self.style = Style()

    def init_ui(self):
        self.menubar = Menubar()
        self.main = Main(self)
        self.main.pack(fill=BOTH, expand=True)









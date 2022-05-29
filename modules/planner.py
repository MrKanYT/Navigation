from tkinter import *
from tkinter.ttk import *
from PIL import Image, ImageTk


class AutoScrollbar(Scrollbar):

    def set(self, lo, hi):
        if float(lo) <= 0.0 and float(hi) >= 1.0:
            self.grid_remove()
        else:
            self.grid()
        Scrollbar.set(self, lo, hi)


    def place(self, **kw):
        raise TclError('Cannot use place with this widget')


class Toolbar(Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.save_button = Button(self, text="Save")
        self.save_button.grid(row=0, column=0, padx=10, pady=20, sticky="nswe")


class Area:
    id = 0
    points = [[]]

    def __init__(self, area_id, start_pos):
        self.id = area_id
        self.points = [start_pos]

    def modify(self, points):
        self.points = points

    def get_rectangle_points(self) -> tuple:
        pos0 = (min([p[0] for p in self.points]), min([p[1] for p in self.points]))
        pos1 = (max([p[0] for p in self.points]), max([p[1] for p in self.points]))
        return pos0, pos1


class Core:

    areas = {}

    def create_area(self, rect_id, start_pos):
        print(f"Create area: {start_pos=}")
        self.areas[rect_id] = Area(rect_id, start_pos)

    def modify_area(self, area_id, new_start_pos, new_end_pos):
        self.areas[area_id].modify()

    def get_coords(self, area_id):
        return self.areas[area_id]



class Zoom(Frame):

    selected = 0

    def on_begin_selection(self, event):
        cx = self.canvas.canvasx(event.x)
        cy = self.canvas.canvasx(event.y)
        self.selected = self.canvas.create_rectangle(cx, cy, cx, cy, fill="red")
        self.core.create_area(self.selected, (cx, cy))

    def on_selecting(self, event):
        old = self.core.get_coords()
        point = [self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)]
        new = [old[0], old[1], point[0], point[1]]
        print(f"New 0: {new}")
        new = [min(new[0], new[2]), min(new[1], new[3]), max(new[0], new[2]), max(new[1], new[3])]
        print(f"New 1: {new}")
        self.canvas.coords(self.selected, *new)
        self.core.modify_area(self.selected, new[:2], new[2:])

    def on_end_selection(self, event):
        pass

    def __init__(self, mainframe, path, core):

        self.core = core
        Frame.__init__(self, master=mainframe)
        self.master.title('Plan creation tool')

        self.toolbar = Toolbar()
        self.toolbar.grid(row=0, column=0, sticky="nswe")

        vbar = AutoScrollbar(self.master, orient='vertical')
        hbar = AutoScrollbar(self.master, orient='horizontal')
        vbar.grid(row=0, column=3, sticky='ns')
        hbar.grid(row=1, column=2, sticky='we')

        self.image = Image.open(path)

        self.canvas = Canvas(self.master, highlightthickness=0,
                                xscrollcommand=hbar.set, yscrollcommand=vbar.set)
        self.canvas.grid(row=0, column=2, sticky='nswe')

        vbar.configure(command=self.canvas.yview)
        hbar.configure(command=self.canvas.xview)

        self.master.columnconfigure(0, weight=1)
        self.master.rowconfigure(0, weight=3)
        self.master.columnconfigure(2, weight=3)

        #self.canvas.bind('<ButtonPress-2>', self.move_from)
        #self.canvas.bind('<B2-Motion>',     self.move_to)
        self.canvas.bind('<ButtonPress-1>', self.on_begin_selection)
        self.canvas.bind('<B1-Motion>', self.on_selecting)
        #self.canvas.bind('<MouseWheel>', self.wheel)

        self.imscale = 1.0
        self.imageid = None
        self.delta = 0.75

        # Text is used to set proper coordinates to the image. You can make it invisible.
        self.text = self.canvas.create_text(0, 0, anchor='nw', text='')
        self.show_image()
        self.canvas.configure(scrollregion=self.canvas.bbox('all'))

    def move_from(self, event):
        ''' Remember previous coordinates for scrolling with the mouse '''
        self.canvas.scan_mark(event.x, event.y)

    def move_to(self, event):
        ''' Drag (move) canvas to the new position '''
        self.canvas.scan_dragto(event.x, event.y, gain=1)

    def wheel(self, event):
        ''' Zoom with mouse wheel '''
        scale = 1.0
        # Respond to Linux (event.num) or Windows (event.delta) wheel event
        if event.num == 5 or event.delta == -120:
            scale *= self.delta
            self.imscale *= self.delta
        if event.num == 4 or event.delta == 120:
            scale /= self.delta
            self.imscale /= self.delta
        # Rescale all canvas objects
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        print(self.imscale)
        self.canvas.scale('all', x, y, scale, scale)
        self.show_image()
        self.canvas.configure(scrollregion=self.canvas.bbox('all'))

    def show_image(self):
        if self.imageid:
            self.canvas.delete(self.imageid)
            self.imageid = None
            self.canvas.imagetk = None  # delete previous image from the canvas
        width, height = self.image.size
        new_size = int(self.imscale * width), int(self.imscale * height)
        imagetk = ImageTk.PhotoImage(self.image.resize(new_size))
        # Use self.text object to set proper coordinates
        self.imageid = self.canvas.create_image(self.canvas.coords(self.text),
                                                anchor='nw', image=imagetk)
        self.canvas.lower(self.imageid)  # set it into background
        self.canvas.imagetk = imagetk  # keep an extra reference to prevent garbage-collection

def run():
    path = 'image.png'  # place path to your image here
    core = Core()
    root = Tk()
    root.geometry("1240x720")
    app = Zoom(root, path, core)
    root.mainloop()
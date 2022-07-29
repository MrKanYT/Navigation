from tkinter import *
from tkinter.ttk import *
from PIL import Image, ImageTk
import copy
from typing import List

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

        self.save_button = Button(self, text="Сохранить в файл")
        self.save_button.grid(row=0, column=0, padx=10, pady=20, sticky="nswe")

        self.gpl_entry_label = Label(self, text="GPS координаты: ")
        self.gpl_entry_label.grid(row=1, column=0, padx=10, pady=20, sticky="nswe")

        self.gps_entry = Entry(self, state=DISABLED)
        self.gps_entry.grid(row=1, column=1, padx=10, pady=20, sticky="nswe")

        self.save_gps_button = Button(self, text="Сохранить координаты")
        self.save_gps_button.grid(row=1, column=3, padx=10, pady=20, sticky="nswe")



class Area:
    id = 0
    points = [[0, 0], [0, 0]]

    def __init__(self, area_id, start_pos):
        self.id = area_id
        self.points = [copy.copy(start_pos), copy.copy(start_pos), copy.copy(start_pos), copy.copy(start_pos)]

    def modify(self, new_point):
        self.points[1][0] = self.points[3][0] = new_point[0]
        self.points[0][1] = self.points[2][1] = new_point[1]

    def get_rectangle_points(self) -> tuple:
        x0 = min(self.points[0][0], self.points[1][0])
        x1 = max(self.points[0][0], self.points[1][0])

        y0 = min(self.points[0][1], self.points[1][1])
        y1 = max(self.points[0][1], self.points[1][1])

        return [x0, y0], [x1, y1]

    def get_points(self) -> list:
        return self.points


class Core:

    areas = {}

    def create_area(self, rect_id, start_pos):
        print(f"Create area: {start_pos=}")
        self.areas[rect_id] = Area(rect_id, start_pos)

    def modify_area(self, area_id, pos):
        self.areas[area_id].modify(pos)

    def get_coords(self, area_id):
        return self.areas[area_id].get_points()



class Zoom(Frame):

    selected = 0

    points = {}
    polygons = {}

    def on_clicked_with_shift(self, event):
        point = [self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)]
        tag = self.canvas.create_oval(point[0]-3, point[1]-3, point[0]+3, point[1]+3, fill="red")
        self.points[tag] = [0, 0]
        self.canvas.tag_bind(tag, "<Alt-B1-Motion>", lambda e: self.on_move_point_with_alt(e, tag))
        self.canvas.tag_bind(tag, "<Alt-Button-1>", lambda e: self.on_click_point_with_alt(e, tag))
        self.canvas.tag_bind(tag, "<B1-Motion>", lambda e: self.on_move_point(e, tag))
        self.canvas.tag_bind(tag, "<Button-1>", lambda e: self.on_click_point(e, tag))

    def on_click_point_with_alt(self, event: Event, tag):
        point_tag = tag

        # проверяет, есть ли уже существующая исходящая линия, чтобы не допустить создания второй линии
        if self.find_connected_lines_for_point(point_tag)[1] != 0:
            return

        point_coords = self.canvas.coords(point_tag)
        line_tag = self.canvas.create_line(point_coords[0] + 3, point_coords[1] + 3, point_coords[0] + 3, point_coords[1] + 3, fill="blue", width=3)
        new_point_tag = self.canvas.create_oval(*point_coords, fill="red")
        self.canvas.tag_bind(new_point_tag, "<Alt-B1-Motion>", lambda e: self.on_move_point_with_alt(e, new_point_tag))
        self.canvas.tag_bind(new_point_tag, "<B1-Motion>", lambda e: self.on_move_point(e, new_point_tag))
        self.canvas.tag_bind(new_point_tag, "<Alt-Button-1>", lambda e: self.on_click_point_with_alt(e, new_point_tag))
        self.canvas.tag_bind(new_point_tag, "<Button-1>", lambda e: self.on_click_point(e, new_point_tag))
        self.canvas.tag_raise(point_tag)
        self.points[point_tag] = [line_tag, new_point_tag]
        self.selected = point_tag

    def on_move_point_with_alt(self, event, tag):
        mouse_pos = [self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)]

        if tag == 0:
            return
        start_point_coords = self.canvas.coords(tag)

        line_tag, end_point_tag = self.points.get(tag, [tag, tag])

        # проверяем, есть ли у конечной точки исходящая линия, чтобы не двигать занятую точку
        if self.find_connected_lines_for_point(end_point_tag)[1] != 0:
            return

        self.canvas.coords(line_tag, start_point_coords[0]+3, start_point_coords[1]+3, mouse_pos[0], mouse_pos[1])
        self.canvas.coords(end_point_tag, mouse_pos[0]-3, mouse_pos[1]-3, mouse_pos[0]+3, mouse_pos[1]+3)

        overlappings = self.canvas.find_overlapping(event.x, event.y, event.x, event.y)
        closest = 0
        for t in overlappings:
            if t in self.points.keys() and t != tag and t != end_point_tag:
                self.merge_points(t, end_point_tag)

    def merge_points(self, target, active_point):

        incoming_line_to_target = self.find_connected_lines_for_point(target)[0]
        lines_to_active_point = self.find_connected_lines_for_point(active_point)

        if incoming_line_to_target != 0:
            self.canvas.delete(incoming_line_to_target)
            connected_points_to_incoming_line = self.find_connected_points_for_line(incoming_line_to_target)
            self.points[connected_points_to_incoming_line[0]] = [0, 0]

        if lines_to_active_point[1] != 0:
            self.canvas.delete(lines_to_active_point[1])

        self.canvas.delete(active_point)
        incoming_line_to_active_coords = self.canvas.coords(lines_to_active_point[0])
        target_point_coords = self.canvas.coords(target)
        self.canvas.coords(lines_to_active_point[0], incoming_line_to_active_coords[0], incoming_line_to_active_coords[1], target_point_coords[0]+3, target_point_coords[1]+3)
        connected_points_to_incoming_line_to_active = self.find_connected_points_for_line(lines_to_active_point[0])
        self.points[connected_points_to_incoming_line_to_active[0]][1] = target
        if active_point in self.points.keys():
            del self.points[active_point]
        self.canvas.tag_raise(target)

        self.create_polygon(target)

    def create_polygon(self, point_tag: int) -> int:
        circuit = self.get_circuit(point_tag)
        if circuit[0] == circuit[-1]:
            del circuit[-1]
        else:
            return 0

        circuit_coords = [[i+3 for i in self.canvas.coords(c)[:2]] for c in circuit]

        polygon_tag = self.canvas.create_polygon(*circuit_coords, fill="green", stipple="gray75")
        print(circuit_coords)
        self.polygons[polygon_tag] = {t: circuit_coords[i] for i, t in enumerate(circuit)}
        for t in circuit:
            print(t)
            self.canvas.tag_raise(t)
            self.canvas.addtag_withtag(f"poly{polygon_tag}", t)
        return polygon_tag

    def get_circuit(self, point_tag: int) -> List[int]:
        circuit = [point_tag]
        if point_tag not in self.points.keys():
            return circuit
        else:
            start_point = self.points[point_tag]
        if 0 in start_point:
            return circuit

        next_point = start_point[1]
        while next_point != point_tag and next_point != 0 and next_point in self.points.keys():
            circuit.append(next_point)
            next_point = self.points[next_point][1]

        if next_point == point_tag:
            circuit.append(next_point)

        return circuit


    def on_click_point(self, event, tag):
        self.canvas.itemconfig(self.selected, fill="red")
        self.canvas.itemconfig(tag, fill="green")
        self.toolbar.gps_entry.configure(state=ACTIVE)
        self.selected = tag

    def on_move_point(self, event, tag, polygon_tag = 0):
        point_tag = tag
        self.canvas.coords(point_tag, event.x+3, event.y+3, event.x-3, event.y-3)

        incoming_line_tag, outgoing_line_tag = self.find_connected_lines_for_point(point_tag)

        # если входящая линия существует - двигаем
        if incoming_line_tag != 0:
            incoming_line_coords = self.canvas.coords(incoming_line_tag)
            self.canvas.coords(incoming_line_tag, incoming_line_coords[0], incoming_line_coords[1], event.x, event.y)

        # если исходящая линия существует - двигаем
        if outgoing_line_tag != 0:
            outgoing_line_coords = self.canvas.coords(outgoing_line_tag)
            self.canvas.coords(outgoing_line_tag, event.x, event.y, outgoing_line_coords[2], outgoing_line_coords[3])

        polygon_tag = 0
        for t in self.canvas.gettags(point_tag):
            if t.startswith("poly"):
                if t.replace("poly", "").isdigit():
                    polygon_tag = int(t.replace("poly", ""))

        if polygon_tag == 0:
            closest = 0
            overlappings = self.canvas.find_overlapping(event.x, event.y, event.x, event.y)
            for t in overlappings:
                if t in self.points.keys() and t != tag:
                    self.merge_points(t, tag)
        else:
            self.polygons[polygon_tag][point_tag][0], self.polygons[polygon_tag][point_tag][1] = event.x, event.y
            self.canvas.coords(polygon_tag, *[i for j in self.polygons[polygon_tag].values() for i in j])

    def find_connected_lines_for_point(self, tag: int) -> List[int]:
        # входящая линия, исходящая линия
        connected_lines = [0, 0]
        if tag in self.points.keys():
            connected_lines[1] = self.points[tag][0]

        for point in self.points.keys():
            if self.points[point][1] == tag:
                connected_lines[0] = self.points[point][0]

        return connected_lines

    def find_connected_points_for_line(self, tag: int) -> List[int]:
        # начальная точка, конечная точка
        connected_points = [0, 0]
        for point in self.points.keys():
            if self.points[point][0] == tag:
                connected_points = [point, self.points[point][1]]

        return connected_points


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
        #self.canvas.bind('<ButtonPress-1>', self.on_begin_selection)
        #self.canvas.bind('<B1-Motion>', self.on_selecting)
        self.canvas.bind("<Shift-Button-1>", self.on_clicked_with_shift)
        #self.canvas.bind("<B1-Motion>", self.on_move)
        #self.canvas.bind('<MouseWheel>', self.wheel)

        self.imscale = 1.0
        self.imageid = None
        self.delta = 0.75

        # Text is used to set proper coordinates to the image. You can make it invisible.
        self.text = self.canvas.create_text(0, 0, anchor='nw', text='')
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
    path = 'image1.jpg'  # place path to your image here
    core = Core()
    root = Tk()
    root.geometry("1240x720")
    app = Zoom(root, path, core)
    root.mainloop()


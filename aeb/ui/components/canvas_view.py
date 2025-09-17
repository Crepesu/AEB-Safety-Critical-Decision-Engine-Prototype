"""CanvasView: resizable road & object rendering component."""
from typing import List, Dict, Any
import tkinter as tk
from aeb.theme import THEME, FONT_VEHICLE, FONT_SMALL

SCALE_X = 5.0   # meters to px (base)
SCALE_Y = 20.0
VEHICLE_WIDTH = 32
VEHICLE_HEIGHT = 44

class CanvasView(tk.Frame):
    def __init__(self, master, width=720, height=360):
        super().__init__(master, bg=THEME.canvas_bg)
        self.base_width = width
        self.base_height = height
        self.canvas = tk.Canvas(self, bg=THEME.canvas_bg, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self._objects: List[Dict[str, Any]] = []
        self.bind("<Configure>", self._on_resize)
        self.draw_static()

    def set_objects(self, objects: List[Dict[str, Any]]):
        self._objects = objects
        self.redraw_dynamic()

    # ------------------------------------------------------------------
    # Drawing
    # ------------------------------------------------------------------
    def draw_static(self):
        self.canvas.delete("static")
        w = self.canvas.winfo_width() or self.base_width
        h = self.canvas.winfo_height() or self.base_height
        cy = h // 2
        road_h = int(h * 0.33)
        y1 = cy - road_h//2
        y2 = cy + road_h//2
        self.canvas.create_rectangle(0, y1, w, y2, fill=THEME.road, outline="", tags=("static",))
        dlen = 30
        gap = 60
        x = 40
        while x < w:
            self.canvas.create_line(x, cy, x+dlen, cy, fill="white", width=3, dash=(8,8), tags=("static",))
            x += gap

    def redraw_dynamic(self, ego_color=None):
        self.canvas.delete("dynamic")
        self._draw_vehicle(ego_color)
        for o in self._objects:
            self._draw_object(o)

    def _draw_vehicle(self, color=None):
        h = self.canvas.winfo_height() or self.base_height
        cy = h // 2
        x0 = 70
        y0 = cy - VEHICLE_HEIGHT//2
        x1 = x0 + VEHICLE_WIDTH
        y1 = cy + VEHICLE_HEIGHT//2
        col = color or THEME.primary
        self.canvas.create_rectangle(x0, y0, x1, y1, fill=col, outline="#003366", width=2, tags=("dynamic",))
        self.canvas.create_text((x0+x1)//2, y1+14, text="Vehicle", font=FONT_VEHICLE, fill=THEME.text, tags=("dynamic",))

    def _draw_object(self, obj):
        h = self.canvas.winfo_height() or self.base_height
        cy = h // 2
        # Use base scaling; could adapt with width ratio later
        x = 70 + obj['position'][0] * SCALE_X
        y = cy + obj['position'][1] * SCALE_Y
        color_map = {"pedestrian": "#FF4136", "cyclist": "#2ECC40", "vehicle": "#FFDC00"}
        col = color_map.get(str(obj['type']), "#AAAAAA")
        self.canvas.create_oval(x-9, y-5, x+9, y+11, fill="#888888", outline="", stipple="gray25", tags=("dynamic",))
        self.canvas.create_oval(x-10, y-10, x+10, y+10, fill=col, outline="#333", width=2, tags=("dynamic",))
        self.canvas.create_text(x, y-18, text=str(obj['type']).capitalize(), font=FONT_SMALL, fill=THEME.text, tags=("dynamic",))

    # ------------------------------------------------------------------
    # Resizing
    # ------------------------------------------------------------------
    def _on_resize(self, _evt):
        self.draw_static()
        self.redraw_dynamic()

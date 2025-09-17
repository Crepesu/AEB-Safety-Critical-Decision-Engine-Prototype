import tkinter as tk
from aeb.theme import FONT_SECTION, FONT_LABEL, FONT_LABEL_BOLD, COLOR_BG

class MetricsPanel(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg=COLOR_BG)
        tk.Label(self, text="Metrics", font=FONT_SECTION, bg=COLOR_BG).grid(row=0, column=0, columnspan=2, sticky="w")
        self.scenarios_var = tk.StringVar(value="0")
        self.threats_var = tk.StringVar(value="0")
        self.brakes_var = tk.StringVar(value="0")
        tk.Label(self, text="Scenarios:", font=FONT_LABEL, bg=COLOR_BG).grid(row=1, column=0, sticky="w")
        tk.Label(self, textvariable=self.scenarios_var, font=FONT_LABEL_BOLD, bg=COLOR_BG).grid(row=1, column=1, sticky="e")
        tk.Label(self, text="Threats:", font=FONT_LABEL, bg=COLOR_BG).grid(row=2, column=0, sticky="w")
        tk.Label(self, textvariable=self.threats_var, font=FONT_LABEL_BOLD, bg=COLOR_BG).grid(row=2, column=1, sticky="e")
        tk.Label(self, text="Brakes:", font=FONT_LABEL, bg=COLOR_BG).grid(row=3, column=0, sticky="w")
        tk.Label(self, textvariable=self.brakes_var, font=FONT_LABEL_BOLD, bg=COLOR_BG).grid(row=3, column=1, sticky="e")

    def update_values(self, scenarios, threats, brakes):
        self.scenarios_var.set(str(scenarios))
        self.threats_var.set(str(threats))
        self.brakes_var.set(str(brakes))

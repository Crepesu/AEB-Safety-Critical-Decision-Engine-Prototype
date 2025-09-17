import tkinter as tk
from tkinter import ttk
from aeb.theme import FONT_SECTION, COLOR_BG

class HistoryPanel(tk.Frame):
    """Panel to display and manage scenario history."""
    def __init__(self, master, on_replay, on_clear):
        super().__init__(master, bg=COLOR_BG)
        tk.Label(self, text="Scenario History", font=FONT_SECTION, bg=COLOR_BG).pack(anchor="w")
        self.listbox = tk.Listbox(self, height=6, activestyle="dotbox")
        self.listbox.pack(fill="x", pady=(2,4))
        btn_hist = tk.Frame(self, bg=COLOR_BG)
        btn_hist.pack(fill="x")
        ttk.Button(btn_hist, text="Replay Selected", command=lambda: on_replay(self.get_selected_index())).pack(side="left", expand=True, fill="x", padx=(0,4))
        ttk.Button(btn_hist, text="Clear Hist", command=on_clear).pack(side="left", expand=True, fill="x")

    def refresh(self, scenarios):
        self.listbox.delete(0, tk.END)
        for idx, scn in enumerate(scenarios):
            self.listbox.insert(tk.END, f"{idx+1}: n={len(scn)} objs")

    def get_selected_index(self):
        sel = self.listbox.curselection()
        if not sel:
            return None
        return sel[0]

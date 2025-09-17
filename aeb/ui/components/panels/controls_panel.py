import tkinter as tk
from tkinter import ttk
from aeb.theme import FONT_SECTION, FONT_LABEL, FONT_SMALL, COLOR_BG
from aeb.core.enums import WeatherCondition

class ControlsPanel(tk.Frame):
    """Panel containing scenario control buttons and environment settings.

    Exposes callbacks the main app supplies for actions.
    """
    def __init__(self, master, on_run_random, on_manual, on_run_anim, on_stop_anim, on_clear,
                 on_weather_changed, on_degradation_changed):
        super().__init__(master, bg=COLOR_BG)
        self.on_weather_changed = on_weather_changed
        self.on_degradation_changed = on_degradation_changed
        tk.Label(self, text="Scenario Controls", font=FONT_SECTION, bg=COLOR_BG).pack(anchor="w", pady=(0,4))
        ttk.Button(self, text="Run Random Scenario", command=on_run_random).pack(fill="x", pady=2)
        ttk.Button(self, text="Setup Manual Scenario", command=on_manual).pack(fill="x", pady=2)
        ttk.Button(self, text="Run Animated Scenario", command=on_run_anim).pack(fill="x", pady=2)
        ttk.Button(self, text="Stop Animation", command=on_stop_anim).pack(fill="x", pady=2)
        ttk.Button(self, text="Clear", command=on_clear).pack(fill="x", pady=2)

        # Environment frame
        wx_frame = tk.LabelFrame(self, text="Environment", bg=COLOR_BG, font=FONT_LABEL)
        wx_frame.pack(fill="x", pady=(10,4))
        tk.Label(wx_frame, text="Weather:", font=FONT_LABEL, bg=COLOR_BG).grid(row=0, column=0, sticky="w", pady=(2,0))
        self.weather_var = tk.StringVar(value=WeatherCondition.CLEAR.value)
        wx_combo = ttk.Combobox(wx_frame, state="readonly", width=14,
                                values=[w.value for w in WeatherCondition], textvariable=self.weather_var)
        wx_combo.grid(row=0, column=1, padx=4, sticky="e")
        wx_combo.bind("<<ComboboxSelected>>", lambda e: self.on_weather_changed(self.weather_var.get()))
        self.degrade_var = tk.BooleanVar(value=False)
        degrade_chk = ttk.Checkbutton(wx_frame, text="Degrade Detection", variable=self.degrade_var,
                                      command=lambda: self.on_degradation_changed())
        degrade_chk.grid(row=1, column=0, columnspan=2, sticky="w", pady=(4,0))
        # Degradation probability slider
        self.degrade_prob_var = tk.DoubleVar(value=0.35)
        self.degrade_scale = ttk.Scale(wx_frame, from_=0.0, to=1.0, orient="horizontal", variable=self.degrade_prob_var,
                                       command=lambda v: self.on_degradation_changed())
        self.degrade_scale.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(4,0))
        tk.Label(wx_frame, text="Drop Prob", font=FONT_SMALL, bg=COLOR_BG).grid(row=3, column=0, columnspan=2, sticky="w")

    def get_weather(self):
        return self.weather_var.get()

    def get_degradation_enabled(self):
        return bool(self.degrade_var.get())

    def get_degradation_probability(self):
        return float(self.degrade_prob_var.get()) if self.get_degradation_enabled() else 0.0

    def set_scale_state(self):
        state = "normal" if self.get_degradation_enabled() else "disabled"
        try:
            self.degrade_scale.state([state])
        except Exception:
            pass

import tkinter as tk
from aeb.theme import FONT_LABEL_BOLD, FONT_LABEL, COLOR_BG, COLOR_OK, COLOR_WARN, COLOR_ERR, COLOR_NEUTRAL

# Local minimal choose_color to avoid circular import with aeb.aeb_gui
STATE_OK_SET = {"operational", "monitor"}
STATE_WARN_SET = {"warning"}
STATE_ERR_SET = {"emergency_braking", "sensor_failure"}

def choose_color(value, ok_color, warn_color, err_color):
    if value is None:
        return COLOR_NEUTRAL
    if isinstance(value, bool):
        return ok_color if value else err_color
    if isinstance(value, str):
        norm = value.lower()
        if norm in STATE_OK_SET:
            return ok_color
        if norm in STATE_WARN_SET:
            return warn_color
        if norm in STATE_ERR_SET:
            return err_color
    return warn_color

class StatusPanel(tk.Frame):
    """Panel showing system state, warning, braking indicators."""
    def __init__(self, master):
        super().__init__(master, bg=COLOR_BG)
        self.state_label = tk.Label(self, text="System State: -", font=FONT_LABEL_BOLD, bg=COLOR_BG)
        self.state_label.pack(anchor="w", pady=(0,2))
        self.warning_label = tk.Label(self, text="Warning: -", font=FONT_LABEL, bg=COLOR_BG)
        self.warning_label.pack(anchor="w", pady=(0,2))
        self.brake_label = tk.Label(self, text="Braking: -", font=FONT_LABEL, bg=COLOR_BG)
        self.brake_label.pack(anchor="w", pady=(0,2))

    def update_status(self, result):
        if not result:
            self.state_label.config(text="System State: -", fg=COLOR_NEUTRAL)
            self.warning_label.config(text="Warning: -", fg=COLOR_NEUTRAL)
            self.brake_label.config(text="Braking: -", fg=COLOR_NEUTRAL)
            return
        sys_state = result['system_state']
        decision = result['decision']
        self.state_label.config(text=f"System State: {sys_state}", fg=choose_color(sys_state, COLOR_OK, COLOR_WARN, COLOR_ERR))
        self.warning_label.config(text=f"Warning: {decision['warning']}", fg=choose_color(decision['warning'], COLOR_WARN, COLOR_WARN, COLOR_OK))
        self.brake_label.config(text=f"Braking: {decision['braking']}", fg=choose_color(decision['braking'], COLOR_ERR, COLOR_WARN, COLOR_OK))

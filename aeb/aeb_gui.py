"""AEB Desktop GUI Prototype (Tkinter)
=====================================

Purpose:
    Provide a visual, interactive high‑fidelity prototype for the Autonomous
    Emergency Braking (AEB) decision engine. The GUI lets you:
        * Generate random traffic scenarios or enter a manual scenario
        * Visualize the ego vehicle, objects (pedestrian / cyclist / vehicle)
        * Observe system decisions (monitor, warning, emergency brake)
        * Inspect detailed log output (TTC, decision, braking, warning flags)

Structure Overview:
    AEBGuiApp (tk.Tk)
    ├─ create_widgets() : Builds UI (title bar, canvas, panels)
    ├─ CanvasView      : Encapsulates drawing & resize handling
        ├─ run_random_scenario() / setup_manual_scenario() : Scenario creation
        ├─ visualize_scenario() : One-shot execution & drawing pipeline
        ├─ display_log() : Textual decision + state reporting
        ├─ display_status() : Color-coded status indicators (refactored)

Design Choices:
    * Tkinter chosen for portability (no extra deps) – can be swapped for PyQt.
    * Supports both one‑shot and animated (time‑stepped) scenario evaluation.
    * Distance scaling: 1 m → 5 px horizontally; lateral 1 m → 20 px vertically.
    * Separation of rendering vs. system logic (AEBSystem provides decisions).

Future Extensions:
    * File export of animated traces / decision timeline
    * Heat‑map overlay of detection probabilities
    * Integration with replayable recorded scenarios
    * Ego deceleration modeling (current animation uses constant ego speed)
"""

import tkinter as tk
from tkinter import ttk, messagebox
import random
import logging
import os, sys

# Allow running this file directly via `python aeb/aeb_gui.py` without needing
# to install the package by ensuring the project root is on sys.path.
if __package__ is None or __package__ == "":  # executed as a script, not module
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

from aeb.core.system import AEBSystem
from aeb.core.constants import SafetyConstants
from aeb.core.enums import ObjectType, WeatherCondition
from aeb.theme import THEME, FONT_TITLE, FONT_SECTION, FONT_LABEL, FONT_LABEL_BOLD, FONT_SMALL, FONT_VEHICLE, FONT_MONO
from aeb.ui.components.canvas_view import CanvasView
from aeb.ui.components.panels.controls_panel import ControlsPanel
from aeb.ui.components.panels.status_panel import StatusPanel
from aeb.ui.components.panels.history_panel import HistoryPanel
from aeb.ui.components.panels.metrics_panel import MetricsPanel

###############################################################################
# Layout + Rendering Constants
###############################################################################
CANVAS_WIDTH = 720
CANVAS_HEIGHT = 360

###############################################################################
# Visual Style Constants (fonts / colors) – centralize to satisfy linter & ease
# future theming changes.
###############################################################################
COLOR_PRIMARY = THEME.primary
COLOR_BG = THEME.bg
COLOR_CANVAS_BG = THEME.canvas_bg
COLOR_ROAD = THEME.road
COLOR_TEXT_DARK = THEME.text
COLOR_OK = THEME.ok
COLOR_WARN = THEME.warn
COLOR_ERR = THEME.err
COLOR_NEUTRAL = THEME.neutral

###############################################################################
# Simulation / Animation Constants
###############################################################################
EGO_SPEED_MPS = 13.9          # ~50 km/h ego speed (constant in current model)
SIM_TICK_MS = 120             # GUI update tick interval (ms)
MAX_SIM_TIME_S = 10.0         # Failsafe to stop long simulations
COLLISION_DISTANCE_M = 0.5    # Threshold for declaring a collision
# (Placeholder for future braking dynamics if we simulate ego decel)
DECEL_EMERGENCY = -6.0        # m/s^2 (not yet applied)

# Status classification sets used for color resolution (kept small & declarative
# to minimize branching logic inside the rendering path and reduce cognitive
# complexity of the GUI status update routine).
STATE_OK_SET = {"operational", "monitor"}
STATE_WARN_SET = {"warning"}
STATE_ERR_SET = {"emergency_braking", "sensor_failure"}

def choose_color(value, ok_color, warn_color, err_color):
    """Return an appropriate color for a mixed *value* domain.

    The GUI status labels may supply: None, bool, or str states. To keep
    `display_status` simple (low cognitive complexity), the branching logic is
    consolidated here using small, easily-audited classification sets.

    Rules:
        * None → neutral gray
        * bool True  → ok_color
          bool False → err_color
        * str matched in STATE_OK_SET   → ok_color
        * str matched in STATE_WARN_SET → warn_color
        * str matched in STATE_ERR_SET  → err_color
        * anything else → warn_color (cautious default)
    """
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

"""GUI application.

Security / Quality Notes:
        * Uses SystemRandom (cryptographically strong) instead of default PRNG for
            simulation randomness to address Sonar rule S2245 (non‑crypto PRNG).
            While security strength is not required for simulation, this removes the
            hotspot without performance impact at current scale.
"""

RNG = random.SystemRandom()  # addresses Sonar hotspot (python:S2245)

class AEBGuiApp(tk.Tk):
    """Main Tkinter application window for the AEB prototype GUI."""
    def __init__(self):
        super().__init__()
        # Set up main window properties
        self.title("AEB Safety-Critical Prototype GUI")
        # Add more horizontal room for extended log + controls and vertical for larger canvas
        # Increased extra vertical padding from +90 to +180 for more space
        self.geometry(f"{CANVAS_WIDTH+340}x{CANVAS_HEIGHT+340}")
        self.resizable(True, True)
        self.minsize(900, 520)
        self.configure(bg=COLOR_BG)
        self.aeb_system = AEBSystem()  # Core AEB logic
        self.create_widgets()           # Build all UI widgets
        self.current_scenario = []      # Store current scenario for visualization
        # Animation state variables
        self.sim_running = False
        self.sim_elapsed = 0.0
        self._after_id = None
        self.animated_objects = []  # Mutable objects list during animation
        # Scenario history (simple ring buffer semantics)
        self.scenario_history = []
        self.max_history = 20
        # Metrics counters
        self.metric_total_scenarios = 0
        self.metric_threat_scenarios = 0
        self.metric_brake_events = 0
        # Animation flags for metric aggregation
        self._anim_threat_recorded = False
        self._anim_brake_recorded = False
    # Removed dynamic TTC label per user request
    # self.ttc_label = None


    def create_widgets(self):
        # Use grid layout
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Title bar
        title_bar = tk.Frame(self, bg=COLOR_PRIMARY, height=40)
        title_bar.grid(row=0, column=0, columnspan=3, sticky="nsew")
        title_bar.grid_propagate(False)
        tk.Label(title_bar, text="AEB Safety-Critical Prototype GUI", fg="white", bg=COLOR_PRIMARY, font=FONT_TITLE).pack(anchor="w", padx=12, pady=4)

        # Left controls frame (component)
        controls_frame = ControlsPanel(
            self,
            on_run_random=self.run_random_scenario,
            on_manual=self.setup_manual_scenario,
            on_run_anim=self.run_animated_scenario,
            on_stop_anim=self.stop_animation,
            on_clear=self.clear_canvas,
            on_weather_changed=lambda _: self._apply_weather(),
            on_degradation_changed=self._apply_degradation
        )
        controls_frame.grid(row=1, column=0, sticky="nsew", padx=(8,4), pady=(6,8))
        self.controls_panel = controls_frame
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=0)
        # Center canvas view container
        canvas_container = tk.Frame(self, bg=COLOR_BG)
        canvas_container.grid(row=1, column=1, sticky="nsew", pady=(6,8))
        self.grid_columnconfigure(1, weight=1)
        canvas_container.grid_rowconfigure(0, weight=1)
        canvas_container.grid_columnconfigure(0, weight=1)
        self.canvas_view = CanvasView(canvas_container, width=CANVAS_WIDTH, height=CANVAS_HEIGHT)
        self.canvas_view.grid(row=0, column=0, sticky="nsew")
        # Right side (log + status + history + metrics)
        side_frame = tk.Frame(self, bg=COLOR_BG)
        side_frame.grid(row=1, column=2, sticky="nsew", padx=(4,8), pady=(6,8))
        self.grid_columnconfigure(2, weight=0)

        # Link panel vars to legacy references for helper methods
        self.weather_var = controls_frame.weather_var
        self.degrade_var = controls_frame.degrade_var
        self.degrade_prob_var = controls_frame.degrade_prob_var
        self.degrade_scale = controls_frame.degrade_scale

        # --- Results/logs panel ---
        tk.Label(side_frame, text="System State / Log", font=FONT_SECTION, bg=COLOR_BG).pack(anchor="w", pady=(0,2))
        log_frame = tk.Frame(side_frame, bg=COLOR_BG)
        log_frame.pack(fill="both", expand=False)
        log_scroll = tk.Scrollbar(log_frame, orient="vertical")
        self.log_text = tk.Text(log_frame, width=34, height=16, state="disabled", bg="#f8f8f8", font=FONT_MONO, yscrollcommand=log_scroll.set)
        log_scroll.config(command=self.log_text.yview)
        self.log_text.grid(row=0, column=0, sticky="nsew")
        log_scroll.grid(row=0, column=1, sticky="ns")
        log_frame.grid_rowconfigure(0, weight=1)
        log_frame.grid_columnconfigure(0, weight=1)

        # --- Status indicators panel ---
        self.status_panel = StatusPanel(side_frame)
        self.status_panel.pack(fill="x", anchor="w", pady=(10,0))
        # (TTC label removed; status relocated under log)

        # --- History panel ---
        self.history_panel = HistoryPanel(side_frame, on_replay=lambda idx: self._replay_index(idx), on_clear=self.clear_history)
        self.history_panel.pack(fill="x", pady=(12,4))

        # --- Metrics panel ---
        self.metrics_panel = MetricsPanel(side_frame)
        self.metrics_panel.pack(fill="x", pady=(4,8))

    # (Degradation slider handled by ControlsPanel)

    # Canvas drawing now handled by CanvasView component

    def run_random_scenario(self):
        # Generate a random scenario with 1-3 objects of random type, distance, and lateral position
        num_objects = RNG.randint(1, 3)
        scenario = []
        for _ in range(num_objects):
            obj_type = RNG.choice(list(ObjectType))
            distance = RNG.uniform(5, SafetyConstants.MAX_DETECTION_RANGE)
            lateral = RNG.uniform(-2, 2)
            scenario.append({
                'type': obj_type.value,
                'position': [distance, lateral],
                'velocity': [RNG.uniform(-5, 5), 0],
                'size': [0.6, 1.8]
            })
        self._record_history(scenario)
        self.visualize_scenario(scenario)

    def setup_manual_scenario(self):
        # Dialog for manual scenario (add one object with user input)
        def add_object():
            try:
                obj_type = type_var.get()
                distance = float(dist_var.get())
                lateral = float(lat_var.get())
                scenario = [{
                    'type': obj_type,
                    'position': [distance, lateral],
                    'velocity': [0, 0],
                    'size': [0.6, 1.8]
                }]
                top.destroy()
                self.visualize_scenario(scenario)
                self._record_history(scenario)
            except Exception as e:
                messagebox.showerror("Input Error", str(e))
        # Create dialog window
        top = tk.Toplevel(self)
        top.title("Manual Scenario Setup")
        top.geometry("260x140")
        top.resizable(False, False)
        top.configure(bg="#f0f2f5")
        # Object type selection
        ttk.Label(top, text="Object Type:").grid(row=0, column=0, padx=6, pady=4, sticky="e")
        type_var = tk.StringVar(value="pedestrian")
        ttk.Combobox(top, textvariable=type_var, values=[t.value for t in ObjectType], width=14).grid(row=0, column=1, padx=6, pady=4)
        # Distance input
        ttk.Label(top, text="Distance (m):").grid(row=1, column=0, padx=6, pady=4, sticky="e")
        dist_var = tk.StringVar(value="15")
        ttk.Entry(top, textvariable=dist_var, width=16).grid(row=1, column=1, padx=6, pady=4)
        # Lateral input
        ttk.Label(top, text="Lateral (m):").grid(row=2, column=0, padx=6, pady=4, sticky="e")
        lat_var = tk.StringVar(value="0")
        ttk.Entry(top, textvariable=lat_var, width=16).grid(row=2, column=1, padx=6, pady=4)
        # Add button
        ttk.Button(top, text="Add Object", command=add_object).grid(row=3, column=0, columnspan=2, pady=8)

    def visualize_scenario(self, scenario):
        # Clear and redraw the canvas, then run the scenario through the AEB system
        self.clear_canvas()
        self.canvas_view.set_objects(scenario)
        self.canvas_view.redraw_dynamic()
        # Run scenario through AEB system logic
        self._apply_weather()
        self._apply_degradation()
        result = self.aeb_system.process_scenario(scenario)
        self.display_log(result)    # Show results in log
        self.display_status(result) # Update colored status indicators
        self._update_metrics(result, new_scenario=True)

    def clear_canvas(self):
        # Clear the canvas and log, reset status indicators
        if self.sim_running:
            self.stop_animation()
        self.canvas_view.set_objects([])
        self.canvas_view.redraw_dynamic()
        self.log_text.config(state="normal")
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state="disabled")
        self.display_status(None)
        # TTC label removed – no reset needed

    def display_log(self, result):
        # Show the results of the scenario in the log panel
        self.log_text.config(state="normal")
        self.log_text.delete(1.0, tk.END)
        if not result:
            self.log_text.config(state="disabled")
            return
        self.log_text.insert(tk.END, f"Detected: {len(result['detected_objects'])}\n")
        # Show threat status and TTC information. Display both trigger TTC (used for decisions)
        # and absolute min TTC (situational awareness) when applicable.
        ttc_trigger = result.get('min_ttc')
        ttc_all = result.get('min_ttc_all')
        finite_trigger = (ttc_trigger is not None and ttc_trigger != float('inf'))
        finite_all = (ttc_all is not None and ttc_all != float('inf'))
        if result['threat_detected']:
            if finite_trigger and finite_all and abs(ttc_trigger - ttc_all) > 1e-3:
                self.log_text.insert(tk.END, f"Threat: YES (Trigger TTC: {ttc_trigger:.2f}s | Min TTC: {ttc_all:.2f}s)\n")
            elif finite_trigger:
                self.log_text.insert(tk.END, f"Threat: YES (TTC: {ttc_trigger:.2f}s)\n")
            elif finite_all:
                self.log_text.insert(tk.END, f"Threat: YES (Min TTC: {ttc_all:.2f}s)\n")
            else:
                self.log_text.insert(tk.END, "Threat: YES\n")
        else:
            if finite_all:
                self.log_text.insert(tk.END, f"Threat: NO (Min TTC: {ttc_all:.2f}s)\n")
            else:
                self.log_text.insert(tk.END, "Threat: NO\n")
        self.log_text.insert(tk.END, f"System State: {result['system_state']}\n")
        self.log_text.insert(tk.END, f"Decision: {result['decision']['action']}\n")
        self.log_text.insert(tk.END, f"Warning: {result['decision']['warning']}\n")
        self.log_text.insert(tk.END, f"Braking: {result['decision']['braking']}\n")
        self.log_text.insert(tk.END, f"Message: {result['decision']['message']}\n")
        self.log_text.config(state="disabled")

    def display_status(self, result):
        # Delegate to StatusPanel for UI updates
        self.status_panel.update_status(result)
        # (Removed TTC label updates)

    # ------------------------------------------------------------------
    # Animated Simulation Mode
    # ------------------------------------------------------------------
    def run_animated_scenario(self):
        """Generate and start an animated time‑stepped scenario.

        Objects have longitudinal distance (m) updated each tick using
        relative closure speed: ego_speed - object_longitudinal_velocity.

        Stops when:
            * Emergency braking triggers
            * A collision threshold is reached
            * Max simulation time elapses
            * User presses Stop Animation
        """
        if self.sim_running:
            return  # Ignore if already running
        # Build a fresh random scenario (slightly constrained for clarity)
        count = RNG.randint(1, 3)
        self.animated_objects = []
        for _ in range(count):
            obj_type = RNG.choice(list(ObjectType))
            dist = RNG.uniform(10, SafetyConstants.MAX_DETECTION_RANGE)
            lat = RNG.uniform(-1.5, 1.5)
            self.animated_objects.append({
                'type': obj_type.value,
                'position': [dist, lat],
                'velocity': [RNG.uniform(-2, 2), 0],  # small longitudinal variation
                'size': [0.6, 1.8]
            })
        self.sim_running = True
        self.sim_elapsed = 0.0
        self._anim_threat_recorded = False
        self._anim_brake_recorded = False
        # Initial draw of static background once (already present) and first frame objects
        self.canvas_view.set_objects(self.animated_objects)
        self.canvas_view.redraw_dynamic()
        # Record scenario & metrics
        self._record_history(self.animated_objects)
        self._animation_step()

    def _animation_step(self):
        """Single animation tick: advance objects, re-evaluate system, redraw."""
        if not self.sim_running:
            return
        dt = SIM_TICK_MS / 1000.0
        self.sim_elapsed += dt
        # Advance each object toward ego (closing distance)
        for obj in self.animated_objects:
            closure = EGO_SPEED_MPS - obj['velocity'][0]
            obj['position'][0] -= closure * dt
        # Evaluate scenario with updated positions
        # Ensure current weather & degradation settings apply during animation
        self._apply_weather()
        self._apply_degradation()
        result = self.aeb_system.process_scenario(self.animated_objects)
        # Redraw scene
        # Delete only dynamic items (performance optimization)
        # Choose ego vehicle color based on current system state for better feedback
        vehicle_color = COLOR_PRIMARY
        if result['decision']['braking']:
            vehicle_color = COLOR_ERR
        elif result['decision']['warning']:
            vehicle_color = COLOR_WARN
        # Redraw dynamic layer via CanvasView
        self.canvas_view.redraw_dynamic(ego_color=vehicle_color)
        # Refresh textual/log + status
        self.display_log(result)
        self.display_status(result)
        self._update_metrics(result, new_scenario=False)
        # Determine stop conditions
        stop_reason = None
        if result['decision']['braking']:
            stop_reason = "Emergency braking triggered"
        else:
            for obj in self.animated_objects:
                if obj['position'][0] <= COLLISION_DISTANCE_M:
                    stop_reason = "Collision threshold reached"
                    break
        if self.sim_elapsed >= MAX_SIM_TIME_S and stop_reason is None:
            stop_reason = "Max simulation time reached"
        if stop_reason:
            self._finalize_animation(stop_reason)
            return
        # Schedule next tick if window still exists
        if self.winfo_exists():
            self._after_id = self.after(SIM_TICK_MS, self._animation_step)

    def _finalize_animation(self, reason):
        """Stop animation loop and append reason to log."""
        self.sim_running = False
        if self._after_id:
            try:
                self.after_cancel(self._after_id)
            except Exception:
                pass
            self._after_id = None
        self.log_text.config(state="normal")
        self.log_text.insert(tk.END, f"\n[Animation stopped] {reason}\n")
        self.log_text.config(state="disabled")
        # Ensure final metrics capture any late braking state
        # (Already updated each tick, so no action needed here.)

    def stop_animation(self):
        """User-triggered termination of the animated scenario."""
        if not self.sim_running:
            return
        self._finalize_animation("Stopped by user")

    # ------------------------------------------------------------------
    # Weather / Degradation Helpers
    # ------------------------------------------------------------------
    def _apply_weather(self):
        try:
            sel = self.weather_var.get()
            wc = WeatherCondition(sel)
            self.aeb_system.sensor_system.set_weather_condition(wc)
        except Exception:
            pass

    def _apply_degradation(self):
        active = bool(self.degrade_var.get())
        # Use a fixed default probability; could be adjusted per weather later
        prob = float(self.degrade_prob_var.get()) if active else 0.0
        # Enable/disable scale visual feedback
        state = "normal" if active else "disabled"
        try:
            self.degrade_scale.state([state])  # ttk widget state toggle
        except Exception:
            pass
        self.aeb_system.sensor_system.set_detection_degradation(active, probability=prob)

    # ------------------------------------------------------------------
    # History / Metrics Helpers
    # ------------------------------------------------------------------
    def _record_history(self, scenario):
        try:
            # Store a shallow copy (positions mutated in animation; copy lists)
            stored = []
            for o in scenario:
                stored.append({
                    'type': o['type'],
                    'position': list(o['position']),
                    'velocity': list(o['velocity']),
                    'size': list(o['size'])
                })
            self.scenario_history.append(stored)
            if len(self.scenario_history) > self.max_history:
                self.scenario_history.pop(0)
            self._refresh_history_list()
        except Exception:
            pass

    def _refresh_history_list(self):
        # delegate to history_panel
        self.history_panel.refresh(self.scenario_history)

    def replay_selected_history(self):
        try:
            sel = self.history_list.curselection()
            if not sel:
                return
            scenario = self.scenario_history[sel[0]]
            # Use deep-ish copy to avoid mutating stored scenario
            replay = []
            for o in scenario:
                replay.append({
                    'type': o['type'],
                    'position': list(o['position']),
                    'velocity': list(o['velocity']),
                    'size': list(o['size'])
                })
            self.visualize_scenario(replay)
        except Exception:
            pass

    def _replay_index(self, idx):
        if idx is None:
            return
        try:
            scenario = self.scenario_history[idx]
            replay = []
            for o in scenario:
                replay.append({
                    'type': o['type'],
                    'position': list(o['position']),
                    'velocity': list(o['velocity']),
                    'size': list(o['size'])
                })
            self.visualize_scenario(replay)
        except Exception:
            pass

    def clear_history(self):
        self.scenario_history.clear()
        self._refresh_history_list()

    def _update_metrics(self, result, new_scenario: bool):
        if new_scenario:
            self.metric_total_scenarios += 1
        if not result:
            self._refresh_metrics_labels()
            return
        self._maybe_count_threat(result, new_scenario)
        self._maybe_count_brake(result, new_scenario)
        self._refresh_metrics_labels()

    def _maybe_count_threat(self, result, new_scenario: bool):
        if not result.get('threat_detected'):
            return
        if new_scenario or not self._anim_threat_recorded:
            self.metric_threat_scenarios += 1
            if not new_scenario:
                self._anim_threat_recorded = True

    def _maybe_count_brake(self, result, new_scenario: bool):
        if not result.get('decision', {}).get('braking'):
            return
        if new_scenario or not self._anim_brake_recorded:
            self.metric_brake_events += 1
            if not new_scenario:
                self._anim_brake_recorded = True

    def _refresh_metrics_labels(self):
        self.metrics_panel.update_values(self.metric_total_scenarios,
                                         self.metric_threat_scenarios,
                                         self.metric_brake_events)

if __name__ == "__main__":
    app = AEBGuiApp()
    app.mainloop()

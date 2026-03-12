"""
INS Antenna Analyser — Scientific Dark GUI
Inputs: Frequency (with unit selector), Diameter, T_sec
Output: Beamwidth, allowable INS error, MC results per sensor type
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
import threading

from backend import run_analysis ,check_diameter

# ── Palette ──────────────────────────────────────────────────────
BG       = "#0a0e14"
PANEL    = "#0f1923"
CARD     = "#131c27"
BORDER   = "#223d5a"
ACCENT   = "#00b4d8"
GREEN    = "#39d353"
RED      = "#f85149"
YELLOW   = "#e3b341"
TEXT     = "#cdd9e5"
DIM      = "#C7E6F4"
MONO     = "Helvetica"
FREQ_UNITS = {"Hz": 1, "kHz": 1e3, "MHz": 1e6, "GHz": 1e9}


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("INS Antenna Analyser")
        self.configure(bg=BG)
        self.minsize(860, 680)
        self.resizable(True, True)

        self._build()
        self.update_idletasks()
        w, h = 960, 760
        self.geometry(f"{w}x{h}+{(self.winfo_screenwidth()-w)//2}+{(self.winfo_screenheight()-h)//2}")

    # ─────────────────────────────────────────
    def _build(self):
        self._header()
        self._inputs()
        self._divider("  ANALYSIS OUTPUT  ")
        self._output_panel()
        self._statusbar()

    # ── Header ───────────────────────────────
    def _header(self):
        f = tk.Frame(self, bg=PANEL, height=60)
        f.pack(fill="x")
        f.pack_propagate(False)
        tk.Label(f, text="◈  INS ANTENNA ANALYSER",
                 bg=PANEL, fg=ACCENT,
                 font=(MONO, 15, "bold"), padx=20).pack(side="left", pady=14)
        tk.Label(f, text="Monte-Carlo  ·  Error Budget  ·  Sensor Selection",
                 bg=PANEL, fg=DIM, font=(MONO, 8)).pack(side="left", pady=22)
        tk.Frame(self, bg=ACCENT, height=1).pack(fill="x")

    # ── Input section ────────────────────────
    def _inputs(self):
        outer = tk.Frame(self, bg=BG)
        outer.pack(fill="x", padx=24, pady=(18, 4))

        # ── row 0: section label
        tk.Label(outer, text="PARAMETERS", bg=BG, fg=DIM,
                 font=(MONO, 8, "bold")).grid(row=0, column=0, sticky="w", pady=(0, 6))

        card = tk.Frame(outer, bg=CARD, padx=20, pady=18,
                        highlightthickness=1, highlightbackground=BORDER)
        card.grid(row=1, column=0, sticky="ew")
        outer.columnconfigure(0, weight=1)

        # helper: labelled entry
        def row(parent, label, r, unit_widget=None):
            tk.Label(parent, text=label, bg=CARD, fg=DIM,
                     font=(MONO, 9), width=22, anchor="w").grid(
                row=r, column=0, padx=(0, 10), pady=6, sticky="w")
            ent = tk.Entry(parent, bg=PANEL, fg=TEXT,
                           font=(MONO, 10), relief="flat",
                           insertbackground=ACCENT,
                           highlightthickness=1,
                           highlightbackground=BORDER,
                           highlightcolor=ACCENT,
                           width=18)
            ent.grid(row=r, column=1, pady=6, sticky="w")
            if unit_widget:
                unit_widget(parent, r)
            return ent

        # Frequency entry + unit dropdown
        self.freq_unit = tk.StringVar(value="GHz")

        def freq_unit_widget(parent, r):
            combo = ttk.Combobox(parent, textvariable=self.freq_unit,
                                 values=list(FREQ_UNITS.keys()),
                                 width=6, state="readonly",
                                 font=(MONO, 9))
            combo.grid(row=r, column=2, padx=(8, 0), pady=6, sticky="w")
            _style_combo(combo)

        self.freq_entry = row(card, "Frequency", 0, freq_unit_widget)
        self.freq_entry.insert(0, "14")

        self.D_entry    = row(card, "Diameter  D  (m)", 1)
        self.D_entry.insert(0, "1.0")

        self.T_entry    = row(card, "Mission time  T  (s)", 2)
        self.T_entry.insert(0, "380")

        # Run button
        self.run_btn = tk.Button(
            card, text="▶  RUN ANALYSIS",
            bg=ACCENT, fg="#000000",
            font=(MONO, 10, "bold"),
            relief="flat", cursor="hand2",
            padx=24, pady=8,
            activebackground="#48cae4",
            command=self._run)
        self.run_btn.grid(row=3, column=0, columnspan=3,
                          pady=(16, 4), sticky="w")

    # ── Divider label ─────────────────────────
    def _divider(self, label):
        f = tk.Frame(self, bg=BG)
        f.pack(fill="x", padx=24, pady=(14, 0))
        tk.Frame(f, bg=BORDER, height=1).pack(fill="x")
        tk.Label(f, text=label, bg=BG, fg=DIM,
                 font=(MONO, 8)).place(relx=0.5, rely=0, anchor="n", y=-1)

    # ── Output panel ─────────────────────────
    def _output_panel(self):
        outer = tk.Frame(self, bg=BG)
        outer.pack(fill="both", expand=True, padx=24, pady=(10, 4))
        outer.columnconfigure(0, weight=1)
        outer.rowconfigure(0, weight=1)

        card = tk.Frame(outer, bg=CARD,
                        highlightthickness=1, highlightbackground=BORDER)
        card.grid(row=0, column=0, sticky="nsew")
        card.columnconfigure(0, weight=1)
        card.rowconfigure(0, weight=1)

        self.out_box = scrolledtext.ScrolledText(
            card, bg=CARD, fg=TEXT,
            font=(MONO, 10),
            relief="flat", bd=0,
            state="disabled",
            wrap="none",
            padx=18, pady=14,
            insertbackground=ACCENT,
            selectbackground=BORDER)
        self.out_box.pack(fill="both", expand=True)

        # configure text tags
        self.out_box.tag_config("title",        foreground=ACCENT,  font=(MONO, 13, "bold"))
        self.out_box.tag_config("heading",      foreground=ACCENT,  font=(MONO, 10, "bold"))
        self.out_box.tag_config("label",        foreground=DIM,     font=(MONO, 10))
        self.out_box.tag_config("value",        foreground=TEXT,    font=(MONO, 10))
        self.out_box.tag_config("pass",         foreground=GREEN,   font=(MONO, 12, "bold"))
        self.out_box.tag_config("fail",         foreground=RED,     font=(MONO, 12, "bold"))
        self.out_box.tag_config("warn",         foreground=YELLOW,  font=(MONO, 10))
        self.out_box.tag_config("dim",          foreground=DIM,     font=(MONO, 9))
        self.out_box.tag_config("sep",          foreground=BORDER,  font=(MONO, 10))
        self.out_box.tag_config("pref_label",   foreground=DIM,     font=(MONO, 11, "bold"))
        self.out_box.tag_config("pref_pass",    foreground=GREEN,   font=(MONO, 20, "bold"))
        self.out_box.tag_config("pref_none",    foreground=RED,     font=(MONO, 20, "bold"))
        self.out_box.tag_config("recommend_label", foreground=YELLOW, font=(MONO, 10, "bold"))
        self.out_box.tag_config("recommend_val",   foreground=YELLOW, font=(MONO, 14, "bold"))

        # ── Clear output button (sits below the text box)
        btn_bar = tk.Frame(outer, bg=BG)
        btn_bar.grid(row=1, column=0, sticky="e", pady=(4, 0))
        tk.Button(
            btn_bar, text="✕  CLEAR OUTPUT",
            bg=BORDER, fg=DIM,
            font=(MONO, 8), relief="flat",
            cursor="hand2", padx=12, pady=4,
            activebackground=PANEL, activeforeground=TEXT,
            command=self._clear_output
        ).pack()

    # ── Status bar ───────────────────────────
    def _statusbar(self):
        tk.Frame(self, bg=BORDER, height=1).pack(fill="x")
        bar = tk.Frame(self, bg=PANEL, height=26)
        bar.pack(fill="x")
        bar.pack_propagate(False)
        self.status_var = tk.StringVar(value="Ready.")
        self.spin_var   = tk.StringVar(value="")
        tk.Label(bar, textvariable=self.status_var,
                 bg=PANEL, fg=DIM, font=(MONO, 8),
                 anchor="w", padx=16).pack(side="left", fill="y")
        tk.Label(bar, textvariable=self.spin_var,
                 bg=PANEL, fg=ACCENT, font=(MONO, 8),
                 anchor="e", padx=16).pack(side="right", fill="y")

    # ── Run logic ────────────────────────────
    def _run(self):
        try:
            unit_mult = FREQ_UNITS[self.freq_unit.get()]
            f_hz = float(self.freq_entry.get()) * unit_mult
            D    = float(self.D_entry.get())
            T    = float(self.T_entry.get())
        except ValueError:
            self._write_error("Invalid input — please enter numeric values.")
            return

        if f_hz <= 0 or D <= 0 or T <= 0:
            self._write_error("All values must be positive.")
            return

        self.run_btn.config(state="disabled", bg=BORDER, fg=DIM, text="⏳  RUNNING…")
        self.status_var.set("Running Monte-Carlo simulation…")
        self._spinning = True
        self._spin(0)

        def worker():
            result = run_analysis(f_hz, D, T)
            self.after(0, lambda: self._display(result))
            self.after(0, self._done)

        threading.Thread(target=worker, daemon=True).start()

    def _done(self):
        self._spinning = False
        self.spin_var.set("")
        self.run_btn.config(state="normal", bg=ACCENT, fg="#000000", text="▶  RUN ANALYSIS")
        self.status_var.set("Analysis complete.")

    def _spin(self, n):
        if not self._spinning:
            return
        frames = ["⠋","⠙","⠹","⠸","⠼","⠴","⠦","⠧","⠇","⠏"]
        self.spin_var.set(f"{frames[n % len(frames)]}  computing")
        self.after(100, lambda: self._spin(n + 1))

    # ── Output renderer ──────────────────────
    def _display(self, r):
        box = self.out_box
        box.config(state="normal")
        box.delete("1.0", "end")

        def w(text, tag="value"):
            box.insert("end", text, tag)

        if r.get('error'):
            w(f"ERROR\n{r['error']}\n", "fail")
            box.config(state="disabled")
            return

        freq_str = _fmt_freq(r['f_hz'])
        sep = "─" * 52

        # ── Preferred INS — opening line (big, bold, coloured)
        w("\n  Preferred INS :  ", "pref_label")
        if r['passing']:
            w("  /  ".join(r['passing']) + "\n\n", "pref_pass")
        else:
            w("NONE\n\n", "pref_none")

        # ── Title block
        w(f"  ANTENNA / INS ANALYSIS REPORT\n", "title")
        w(f"  {sep}\n", "sep")

        # ── Input summary
        w("  INPUTS\n", "heading")
        w(f"  {'Frequency':<26}", "label");  w(f"{freq_str}\n")
        w(f"  {'Diameter D':<26}", "label"); w(f"{r['D']:.3f} m\n")
        w(f"  {'Mission time T':<26}", "label"); w(f"{r['T_sec']:.1f} s  ({r['T_sec']/3600:.4f} hr)\n")
        w(f"\n  {sep}\n", "sep")

        # ── Antenna
        w("  ANTENNA\n", "heading")
        w(f"  {'Beamwidth (HPBW)':<26}", "label")
        w(f"{r['beamwidth']:.4f} deg\n")
        dc = r['diam_check']
        if not dc['ok']:
            w(f"\n  ✘  DESIGN NOT OK\n", "fail")
            w(f"  ➤  Recommended Diameter :  ", "recommend_label")
            w(f"{dc['D_req']:.4f} m\n", "recommend_val") #accuracy .4 decimal places
        else:
            w(f"\n  ✔  Design OK\n", "pass")
        w(f"\n  {sep}\n", "sep")

        # ── MC results — each sensor gets a prominent block
        w("   RESULTS  \n\n", "heading")

        for name, vals in r['results'].items():
            rms    = vals['rms']
            passed = vals['pass']
            badge  = "  ✔  PASS" if passed else "  ✘  FAIL"
            tag    = "pass"      if passed else "fail"

            # Large sensor type name
            w(f"  ┌─ ", "sep")
            w(f"{name}", "title")          # LARGE font via "title" tag
            w(f"\n  │  RMS Attitude Error  ", "label")
            w(f"{rms:.6f} deg\n")
            w(f"  │  vs allowable        ", "label")
            w(f"{r['theta_INS_allow']:.6f} deg\n")
            w(f"  └", "sep")
            w(f"{badge}\n\n", tag)

        w(f"  {sep}\n", "sep")

        # ── Summary
        w("  OBJECTIVE A — PASSING INS OPTIONS\n", "heading")
        if r['passing']:
            for name in r['passing']:
                w(f"  ✔  {name}\n", "pass")
        else:
            w("  ✘  No INS type satisfies Objective A.\n", "fail")

        w(f"\n  {sep}\n\n", "sep")
        box.config(state="disabled")

    def _clear_output(self):
        box = self.out_box
        box.config(state="normal")
        box.delete("1.0", "end")
        box.config(state="disabled")
        self.status_var.set("Output cleared.")

    def _write_error(self, msg):
        box = self.out_box
        box.config(state="normal")
        box.delete("1.0", "end")
        box.insert("end", f"\n  ⚠  {msg}\n", "warn")
        box.config(state="disabled")
        self.status_var.set(f"Error: {msg}")


# ── Helpers ──────────────────────────────────────────────────────
def _fmt_freq(hz):
    if hz >= 1e9:
        return f"{hz/1e9:.4g} GHz"
    if hz >= 1e6:
        return f"{hz/1e6:.4g} MHz"
    if hz >= 1e3:
        return f"{hz/1e3:.4g} kHz"
    return f"{hz:.4g} Hz"


def _style_combo(combo):
    style = ttk.Style()
    style.theme_use("default")
    style.configure("TCombobox",
                    fieldbackground="#0f1923",
                    background="#0f1923",
                    foreground="#cdd9e5",
                    selectbackground="#1e2d3d",
                    selectforeground="#cdd9e5",
                    arrowcolor="#00b4d8")


if __name__ == "__main__":
    app = App()
    app.mainloop()
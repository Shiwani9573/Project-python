
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from models import PRESETS, make_appliance
from logic import calculate_bill, total_units, heavy_appliances, top_consumer
import analytics as an
import charts

DATA_FILE = "data/usage.csv"
BG = "#f4f6fb"
PRIMARY = "#1f4e9c"


class BijliBuddyApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("BijliBuddy: Electricity Bill Predictor")
        self.geometry("1020x700")
        self.minsize(900, 620)
        self.configure(bg=BG)

        self.appliances = []
        self.past_bills = []

        self.setup_style()
        self.build_menu()
        self.build_header()      # place()
        self.build_status()      # pack()
        self.build_tabs()        # pack() + grid()
        self.refresh_all()

    def setup_style(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TFrame", background=BG)
        style.configure("TLabelframe", background=BG)
        style.configure("TLabelframe.Label", background=BG,
                        foreground=PRIMARY, font=("Segoe UI", 10, "bold"))
        style.configure("TLabel", background=BG, font=("Segoe UI", 10))
        style.configure("TButton", font=("Segoe UI", 10), padding=6)
        style.configure("Accent.TButton", background=PRIMARY,
                        foreground="white", font=("Segoe UI", 10, "bold"))
        style.map("Accent.TButton", background=[("active", "#163a73")])
        style.configure("TNotebook.Tab", padding=(16, 8),
                        font=("Segoe UI", 10, "bold"))
        style.configure("Treeview", rowheight=26, font=("Segoe UI", 10))
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))
        style.configure("Big.TLabel", font=("Segoe UI", 12, "bold"),
                        foreground=PRIMARY)

    def build_menu(self):
        menubar = tk.Menu(self)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Save Data", command=self.save_data)
        file_menu.add_command(label="Load Data", command=self.load_data)
        file_menu.add_command(label="Export Report (CSV)", command=self.export_report)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.destroy)
        menubar.add_cascade(label="File", menu=file_menu)

        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="About", command=self.show_about)
        menubar.add_cascade(label="Help", menu=help_menu)
        self.config(menu=menubar)

    def build_header(self):
        header = tk.Frame(self, bg=PRIMARY, height=64)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(header, text="BijliBuddy", bg=PRIMARY, fg="white",
                 font=("Segoe UI", 22, "bold")).place(relx=0.02, rely=0.5, anchor="w")
        tk.Label(header, text="Bijli ka bill aane se pehle hi pata karo.",
                 bg=PRIMARY, fg="#dbe6ff",
                 font=("Segoe UI", 11, "italic")).place(relx=0.98, rely=0.5, anchor="e")

    def build_status(self):
        self.status = tk.StringVar(value="Ready")
        bar = tk.Label(self, textvariable=self.status, anchor="w",
                       bg="#e3e8f2", padx=10, font=("Segoe UI", 9))
        bar.pack(side="bottom", fill="x")

    def build_tabs(self):
        self.nb = ttk.Notebook(self)
        self.nb.pack(fill="both", expand=True, padx=10, pady=10)
        self.build_appliance_tab()
        self.build_bill_tab()
        self.build_predict_tab()
        self.build_graph_tab()

    def build_appliance_tab(self):
        tab = ttk.Frame(self.nb, padding=10)
        self.nb.add(tab, text="  Appliances  ")

        form = ttk.LabelFrame(tab, text="Add Appliance", padding=12)
        form.pack(side="left", fill="y", padx=(0, 12))

        ttk.Label(form, text="Appliance").grid(row=0, column=0, sticky="w", pady=6)
        self.name_var = tk.StringVar(value="AC")
        cb = ttk.Combobox(form, textvariable=self.name_var, width=18,
                          values=list(PRESETS) + ["Other"])
        cb.grid(row=0, column=1, pady=6)
        cb.bind("<<ComboboxSelected>>", self.autofill_watts)

        ttk.Label(form, text="Watts").grid(row=1, column=0, sticky="w", pady=6)
        self.watts_var = tk.StringVar(value=str(PRESETS["AC"]))
        ttk.Entry(form, textvariable=self.watts_var, width=20).grid(row=1, column=1, pady=6)

        ttk.Label(form, text="Hours / day").grid(row=2, column=0, sticky="w", pady=6)
        self.hours_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.hours_var, width=20).grid(row=2, column=1, pady=6)

        ttk.Button(form, text="Add Appliance", style="Accent.TButton",
                   command=self.add_appliance).grid(row=3, column=0, columnspan=2,
                                                    sticky="ew", pady=(14, 4))
        ttk.Button(form, text="Delete Selected",
                   command=self.delete_selected).grid(row=4, column=0, columnspan=2,
                                                      sticky="ew", pady=4)
        ttk.Button(form, text="Clear All",
                   command=self.clear_all).grid(row=5, column=0, columnspan=2,
                                                sticky="ew", pady=4)
        ttk.Button(form, text="Save to CSV",
                   command=self.save_data).grid(row=6, column=0, columnspan=2,
                                                sticky="ew", pady=4)
        ttk.Button(form, text="Load from CSV",
                   command=self.load_data).grid(row=7, column=0, columnspan=2,
                                                sticky="ew", pady=4)

        right = ttk.Frame(tab)
        right.pack(side="left", fill="both", expand=True)
        cols = ("name", "watts", "hours", "units")
        self.tree = ttk.Treeview(right, columns=cols, show="headings")
        for c, t, w in [("name", "Appliance", 160), ("watts", "Watts", 90),
                        ("hours", "Hours/day", 100), ("units", "Units/month", 120)]:
            self.tree.heading(c, text=t)
            self.tree.column(c, width=w, anchor="center")
        sb = ttk.Scrollbar(right, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

    def autofill_watts(self, _event=None):
        name = self.name_var.get()
        if name in PRESETS:
            self.watts_var.set(str(PRESETS[name]))
        else:
            self.watts_var.set("")

    def add_appliance(self):
        name = self.name_var.get().strip()
        try:
            watts = float(self.watts_var.get())
            hours = float(self.hours_var.get())
        except ValueError:
            messagebox.showerror("Error", "Watts aur Hours number mein daalo.")
            return
        if not name or name == "Other":
            messagebox.showerror("Error", "Appliance ka naam likho.")
            return
        if watts <= 0 or not (0 <= hours <= 24):
            messagebox.showerror("Error", "Watts > 0 aur Hours 0 se 24 ke beech hone chahiye.")
            return
        self.appliances.append(make_appliance(name, watts, hours))
        self.hours_var.set("")
        self.refresh_all()
        self.status.set(f"{name} add ho gaya.")

    def delete_selected(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Info", "Pehle table se ek row chuno.")
            return
        idx = self.tree.index(sel[0])
        removed = self.appliances.pop(idx)
        self.refresh_all()
        self.status.set(f"{removed.name} delete ho gaya.")

    def clear_all(self):
        if self.appliances and messagebox.askyesno("Confirm", "Sab appliances hata dein?"):
            self.appliances.clear()
            self.refresh_all()

    
    def build_bill_tab(self):
        tab = ttk.Frame(self.nb, padding=10)
        self.nb.add(tab, text="  Bill & Simulator  ")

        summary = ttk.LabelFrame(tab, text="Bill Summary", padding=14)
        summary.pack(fill="x")
        self.lbl_units = ttk.Label(summary, text="", style="Big.TLabel")
        self.lbl_bill = ttk.Label(summary, text="", style="Big.TLabel")
        self.lbl_top = ttk.Label(summary, text="")
        self.lbl_heavy = ttk.Label(summary, text="")
        self.lbl_units.grid(row=0, column=0, sticky="w", padx=6, pady=4)
        self.lbl_bill.grid(row=0, column=1, sticky="w", padx=40, pady=4)
        self.lbl_top.grid(row=1, column=0, columnspan=2, sticky="w", padx=6, pady=4)
        self.lbl_heavy.grid(row=2, column=0, columnspan=2, sticky="w", padx=6, pady=4)
        ttk.Button(summary, text="Calculate Bill", style="Accent.TButton",
                   command=self.show_bill_popup).grid(row=0, column=2, padx=30)

        sim = ttk.LabelFrame(tab, text="Saving Simulator", padding=14)
        sim.pack(fill="x", pady=14)
        ttk.Label(sim, text="Appliance chuno:").grid(row=0, column=0, sticky="w")
        self.sim_var = tk.StringVar()
        self.sim_cb = ttk.Combobox(sim, textvariable=self.sim_var, width=20,
                                   state="readonly")
        self.sim_cb.grid(row=0, column=1, padx=10, pady=4, sticky="w")
        self.sim_cb.bind("<<ComboboxSelected>>", self.on_sim_select)

        ttk.Label(sim, text="Naye ghante / din:").grid(row=1, column=0, sticky="w", pady=10)
        self.sim_hours = tk.DoubleVar(value=0)
        self.sim_scale = tk.Scale(sim, from_=0, to=24, resolution=0.5,
                                  orient="horizontal", length=420,
                                  variable=self.sim_hours, bg=BG,
                                  highlightthickness=0, command=self.update_simulator)
        self.sim_scale.grid(row=1, column=1, padx=10)
        self.sim_result = ttk.Label(sim, text="Appliance add karke yahan try karo.",
                                    font=("Segoe UI", 11))
        self.sim_result.grid(row=2, column=0, columnspan=2, sticky="w", pady=8)

        tk.Label(tab, text="Note: Slab rates logic.py ki SLABS list mein hain. "
                           "Apne bijli bill ke hisaab se badal lena.",
                 bg=BG, fg="#666", font=("Segoe UI", 9, "italic")).pack(anchor="w")

    def show_bill_popup(self):
        if not self.appliances:
            messagebox.showinfo("Info", "Pehle appliances add karo.")
            return
        u = total_units(self.appliances)
        messagebox.showinfo("Bill", f"Total units: {u:.1f}\nEstimated bill: Rs {calculate_bill(u):,.2f}")

    def on_sim_select(self, _event=None):
        name = self.sim_var.get()
        target = next((a for a in self.appliances if a.name == name), None)
        if target:
            self.sim_hours.set(target.hours)
            self.update_simulator()

    def update_simulator(self, _value=None):
        name = self.sim_var.get()
        target = next((a for a in self.appliances if a.name == name), None)
        if not target:
            self.sim_result.config(text="Appliance add karke yahan try karo.")
            return
        new_h = self.sim_hours.get()
        base = total_units(self.appliances)
        new_units = base - target.monthly_units() + target.watts * new_h * 30 / 1000
        old_bill, new_bill = calculate_bill(base), calculate_bill(new_units)
        diff = old_bill - new_bill
        if diff >= 0:
            msg = f"Units: {base:.0f} -> {new_units:.0f}   |   Bill: Rs {old_bill:,.0f} -> Rs {new_bill:,.0f}\nBachat: Rs {diff:,.0f} / mahina"
        else:
            msg = f"Units: {base:.0f} -> {new_units:.0f}   |   Bill: Rs {old_bill:,.0f} -> Rs {new_bill:,.0f}\nExtra kharcha: Rs {-diff:,.0f} / mahina"
        self.sim_result.config(text=msg)

   
    def build_predict_tab(self):
        tab = ttk.Frame(self.nb, padding=10)
        self.nb.add(tab, text="  Bill Predictor  ")

        top = ttk.LabelFrame(tab, text="Pichle mahino ke bill (comma se alag karo)", padding=12)
        top.pack(fill="x")
        self.bills_var = tk.StringVar(value="2100, 2300, 2600, 2900, 3000, 3200")
        ttk.Entry(top, textvariable=self.bills_var, width=60).grid(row=0, column=0, padx=6)
        ttk.Button(top, text="Predict Next Bill", style="Accent.TButton",
                   command=self.predict).grid(row=0, column=1, padx=10)
        self.pred_label = ttk.Label(top, text="", style="Big.TLabel")
        self.pred_label.grid(row=1, column=0, columnspan=2, sticky="w", pady=(10, 0))

        self.pred_area = ttk.Frame(tab)
        self.pred_area.pack(fill="both", expand=True, pady=10)

    def parse_bills(self):
        try:
            bills = [float(x) for x in self.bills_var.get().split(",") if x.strip()]
        except ValueError:
            messagebox.showerror("Error", "Bills sirf numbers mein, comma se alag karke likho.")
            return None
        if len(bills) < 2:
            messagebox.showerror("Error", "Kam se kam 2 mahine ke bill chahiye.")
            return None
        return bills

    def predict(self):
        bills = self.parse_bills()
        if not bills:
            return
        self.past_bills = bills
        nxt = an.predict_next_bill(bills)
        self.pred_label.config(text=f"Agle mahine ka predicted bill: Rs {nxt:,.2f}")
        self.show_figure(charts.line_fig(bills, nxt), self.pred_area)
        self.status.set("Prediction ho gayi.")

    # ---------------- Tab 4: Graphs ----------------
    def build_graph_tab(self):
        tab = ttk.Frame(self.nb, padding=10)
        self.nb.add(tab, text="  Graphs  ")
        bar = ttk.Frame(tab)
        bar.pack(fill="x")
        buttons = [("Pie: Appliance Share", self.g_pie),
                   ("Bar: Monthly Bill", self.g_bar),
                   ("Heatmap (Seaborn)", self.g_heat),
                   ("Interactive (Plotly)", self.g_plotly)]
        for i, (t, cmd) in enumerate(buttons):
            ttk.Button(bar, text=t, command=cmd).grid(row=0, column=i, padx=5, pady=4)
        self.graph_area = ttk.Frame(tab)
        self.graph_area.pack(fill="both", expand=True, pady=8)

    def need_appliances(self):
        if not self.appliances:
            messagebox.showinfo("Info", "Pehle appliances add karo.")
            return False
        return True

    def need_bills(self):
        bills = self.parse_bills()
        if bills:
            self.past_bills = bills
        return bills

    def g_pie(self):
        if self.need_appliances():
            self.show_figure(charts.pie_fig(self.appliances), self.graph_area)

    def g_bar(self):
        bills = self.need_bills()
        if bills:
            self.show_figure(charts.bar_fig(bills), self.graph_area)

    def g_heat(self):
        if self.need_appliances():
            self.show_figure(charts.heatmap_fig(self.appliances), self.graph_area)

    def g_plotly(self):
        bills = self.need_bills()
        if bills:
            charts.plotly_trend(bills, an.predict_next_bill(bills))
            self.status.set("Plotly chart browser mein khul gaya.")

    def show_figure(self, fig, parent):
        for w in parent.winfo_children():
            w.destroy()
        fig.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

   
    def refresh_all(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for a in self.appliances:
            self.tree.insert("", "end", values=(a.name, f"{a.watts:g}",
                                                f"{a.hours:g}", f"{a.monthly_units():.1f}"))
        units = total_units(self.appliances)
        self.lbl_units.config(text=f"Total Units: {units:.1f}")
        self.lbl_bill.config(text=f"Estimated Bill: Rs {calculate_bill(units):,.2f}")
        top = top_consumer(self.appliances)
        self.lbl_top.config(text=f"Sabse zyada bijli: {top.name} ({top.monthly_units():.0f} units)"
                            if top else "Sabse zyada bijli: -")
        heavy = [a.name for a in heavy_appliances(self.appliances)]
        self.lbl_heavy.config(text="Heavy appliances (100+ units): " + (", ".join(heavy) or "-"))
        names = [a.name for a in self.appliances]
        self.sim_cb["values"] = names
        if names and self.sim_var.get() not in names:
            self.sim_var.set(names[0])
            self.on_sim_select()
        elif not names:
            self.sim_var.set("")
            self.update_simulator()
        else:
            self.update_simulator()

    def save_data(self):
        if not self.appliances:
            messagebox.showinfo("Info", "Save karne ke liye kuch nahi hai.")
            return
        an.save_appliances(self.appliances, DATA_FILE)
        self.status.set(f"Saved: {DATA_FILE}")
        messagebox.showinfo("Saved", f"Data {DATA_FILE} mein save ho gaya.")

    def load_data(self):
        try:
            df = an.load_appliances(DATA_FILE)
        except FileNotFoundError:
            messagebox.showerror("Error", "Pehle data save karo, CSV nahi mili.")
            return
        self.appliances = [make_appliance(r["name"], r["watts"], r["hours"])
                           for _, r in df.iterrows()]
        self.refresh_all()
        self.status.set("Data load ho gaya.")

    def export_report(self):
        if not self.appliances:
            messagebox.showinfo("Info", "Pehle appliances add karo.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".csv",
                                            filetypes=[("CSV", "*.csv")],
                                            initialfile="bijli_report.csv")
        if not path:
            return
        import pandas as pd
        rows = [{"Appliance": a.name, "Watts": a.watts, "Hours/day": a.hours,
                 "Units/month": round(a.monthly_units(), 1)} for a in self.appliances]
        u = total_units(self.appliances)
        rows.append({"Appliance": "TOTAL", "Watts": "", "Hours/day": "",
                     "Units/month": round(u, 1)})
        rows.append({"Appliance": "ESTIMATED BILL (Rs)", "Watts": "", "Hours/day": "",
                     "Units/month": calculate_bill(u)})
        pd.DataFrame(rows).to_csv(path, index=False)
        self.status.set(f"Report saved: {path}")

    def show_about(self):
        messagebox.showinfo("About", "BijliBuddy: Electricity Bill Predictor\n"
                                     "Python | Tkinter | Pandas | NumPy | Matplotlib | Seaborn | Plotly")


if __name__ == "__main__":
    BijliBuddyApp().mainloop()
import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import numpy as np
from pathlib import Path
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from model import compute_profit  # imports from src/model.py

BASE = Path(__file__).resolve().parents[1]
DATA_DIR = BASE / "data"

class ProfitSimulatorUI:
    def __init__(self, master):
        self.master = master
        self.master.title("✈️ Airline Route Profitability Simulator")
        self.master.geometry("1000x600")
        self.master.configure(bg="#1e1e1e")

        self.aircrafts = self.load_aircraft_profiles()
        self.routes = self.load_routes()

        self.create_widgets()

    def load_aircraft_profiles(self):
        path = DATA_DIR / "aircraft_profiles.csv"
        return pd.read_csv(path).to_dict(orient="records")

    def load_routes(self):
        path = DATA_DIR / "sample_routes.csv"
        return pd.read_csv(path).to_dict(orient="records")

    def get_aircraft(self, name):
        for a in self.aircrafts:
            if a["aircraft_type"] == name:
                return a
        return self.aircrafts[0]

    def create_widgets(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TLabel", background="#1e1e1e", foreground="white")
        style.configure("TFrame", background="#1e1e1e")
        style.configure("TButton", background="#0078d4", foreground="white", font=("Segoe UI", 10, "bold"))

        left = ttk.Frame(self.master)
        left.pack(side="left", fill="y", padx=10, pady=10)

        ttk.Label(left, text="Aircraft Type").grid(row=0, column=0, sticky="w", pady=2)
        self.aircraft_var = tk.StringVar(value=self.aircrafts[0]["aircraft_type"])
        ttk.Combobox(left, textvariable=self.aircraft_var, values=[a["aircraft_type"] for a in self.aircrafts]).grid(row=0, column=1, pady=2)

        ttk.Label(left, text="Route").grid(row=1, column=0, sticky="w", pady=2)
        self.route_var = tk.StringVar(value=self.routes[0]["route_name"])
        ttk.Combobox(left, textvariable=self.route_var, values=[r["route_name"] for r in self.routes]).grid(row=1, column=1, pady=2)

        self.inputs = {
            "Avg Fare (USD)": tk.DoubleVar(value=200.0),
            "Load Factor (0-1)": tk.DoubleVar(value=0.85),
            "Fuel Price (USD/kg)": tk.DoubleVar(value=0.9),
            "Ancillaries per Pax (USD)": tk.DoubleVar(value=20.0),
            "Crew Cost per Flight": tk.DoubleVar(value=2000.0),
            "Maintenance per BlockHr": tk.DoubleVar(value=500.0),
            "Airport Fees": tk.DoubleVar(value=1000.0),
        }

        for i, (label, var) in enumerate(self.inputs.items(), start=2):
            ttk.Label(left, text=label).grid(row=i, column=0, sticky="w", pady=2)
            ttk.Entry(left, textvariable=var, width=10).grid(row=i, column=1, pady=2)

        ttk.Button(left, text="Compute Profit", command=self.compute_profit).grid(row=10, column=0, columnspan=2, pady=8)
        ttk.Button(left, text="Generate Grid", command=self.generate_grid).grid(row=11, column=0, columnspan=2, pady=4)

        self.output = tk.Text(left, height=10, width=40, bg="#252526", fg="#d4d4d4", font=("Consolas", 9))
        self.output.grid(row=12, column=0, columnspan=2, pady=10)

        right = ttk.Frame(self.master)
        right.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        self.fig = Figure(figsize=(6, 4))
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, right)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

    def compute_profit(self):
        try:
            aircraft = self.get_aircraft(self.aircraft_var.get())
            route = next(r for r in self.routes if r["route_name"] == self.route_var.get())
            distance = float(route["distance_nm"])

            vals = {k: v.get() for k, v in self.inputs.items()}
            result = compute_profit(
                distance_nm=distance,
                aircraft_profile=aircraft,
                avg_fare=vals["Avg Fare (USD)"],
                load_factor=vals["Load Factor (0-1)"],
                fuel_price_per_kg=vals["Fuel Price (USD/kg)"],
                ancillaries_per_passenger=vals["Ancillaries per Pax (USD)"],
                crew_cost_per_flight=vals["Crew Cost per Flight"],
                maintenance_per_blockhour=vals["Maintenance per BlockHr"],
                airport_fees=vals["Airport Fees"],
            )
            self.output.delete("1.0", tk.END)
            for k, v in result.items():
                self.output.insert(tk.END, f"{k:<22}: {v}\n")

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def generate_grid(self):
        try:
            aircraft = self.get_aircraft(self.aircraft_var.get())
            route = next(r for r in self.routes if r["route_name"] == self.route_var.get())
            distance = float(route["distance_nm"])
            vals = {k: v.get() for k, v in self.inputs.items()}

            fares = np.arange(50, 501, 20)
            lfs = np.arange(0.5, 1.0, 0.05)
            rows = []
            for f in fares:
                for lf in lfs:
                    res = compute_profit(distance, aircraft, f, lf, vals["Fuel Price (USD/kg)"])
                    res.update({"avg_fare": f, "load_factor": lf})
                    rows.append(res)

            df = pd.DataFrame(rows)
            out_path = DATA_DIR / f"profit_grid_{aircraft['aircraft_type']}_{route['route_name']}.csv"
            df.to_csv(out_path, index=False)

            pivot = df.pivot_table(index="load_factor", columns="avg_fare", values="profit")
            self.ax.clear()
            im = self.ax.imshow(pivot.values, origin="lower", aspect="auto")
            self.ax.set_xticks(np.arange(len(pivot.columns)))
            self.ax.set_xticklabels(pivot.columns, rotation=90, fontsize=6)
            self.ax.set_yticks(np.arange(len(pivot.index)))
            self.ax.set_yticklabels([f"{x:.2f}" for x in pivot.index], fontsize=6)
            self.ax.set_xlabel("Average Fare (USD)")
            self.ax.set_ylabel("Load Factor")
            self.ax.set_title(f"Profit Surface: {aircraft['aircraft_type']} ({route['route_name']})")
            self.fig.colorbar(im, ax=self.ax, label="Profit ($)")
            self.canvas.draw()

            messagebox.showinfo("Success", f"Grid saved as: {out_path}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    app = ProfitSimulatorUI(root)
    root.mainloop()

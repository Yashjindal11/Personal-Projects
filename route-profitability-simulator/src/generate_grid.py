import numpy as np
import pandas as pd
from model import compute_profit

def generate_grid(distance_nm, aircraft_profile, fuel_price_per_kg, fare_range, lf_range, out_csv):
    rows = []
    for fare in np.arange(*fare_range):
        for lf in np.arange(*lf_range):
            result = compute_profit(distance_nm, aircraft_profile, avg_fare=fare, load_factor=lf,
                                    fuel_price_per_kg=fuel_price_per_kg)
            result.update({"avg_fare": fare, "load_factor": lf, "aircraft_type": aircraft_profile["aircraft_type"]})
            rows.append(result)
    df = pd.DataFrame(rows)
    df.to_csv(out_csv, index=False)
    print(f"Grid saved to {out_csv}")
    return df

if __name__ == "__main__":
    A320 = {"aircraft_type":"A320","seats":180,"cruise_speed_kts":450,"fuel_burn_kgph":2500,"fixed_costs_per_flight":500}
    generate_grid(1000, A320, 0.9, (50, 501, 25), (0.5, 0.96, 0.05), "../data/profit_grid_A320.csv")

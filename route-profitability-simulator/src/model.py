import math
import pandas as pd

def compute_block_time(distance_nm, cruise_speed_kts, taxi_minutes=30, contingency_minutes=15):
    flight_time_h = distance_nm / cruise_speed_kts
    taxi_h = taxi_minutes / 60.0
    contingency_h = contingency_minutes / 60.0
    return flight_time_h + taxi_h + contingency_h

def compute_profit(distance_nm, aircraft_profile, avg_fare, load_factor, fuel_price_per_kg,
                   ancillaries_per_passenger=20.0, crew_cost_per_flight=2000.0,
                   maintenance_per_blockhour=500.0, airport_fees=1000.0):
    seats = aircraft_profile["seats"]
    cruise_speed_kts = aircraft_profile["cruise_speed_kts"]
    fuel_burn_kgph = aircraft_profile["fuel_burn_kgph"]
    fixed_costs = aircraft_profile.get("fixed_costs_per_flight", 0.0)
    block_time_h = compute_block_time(distance_nm, cruise_speed_kts)
    passengers = seats * load_factor
    ticket_revenue = passengers * avg_fare
    ancillary_revenue = passengers * ancillaries_per_passenger
    revenue = ticket_revenue + ancillary_revenue
    fuel_quantity_kg = fuel_burn_kgph * block_time_h
    fuel_cost = fuel_quantity_kg * fuel_price_per_kg
    maintenance_cost = maintenance_per_blockhour * block_time_h
    crew_cost = crew_cost_per_flight
    total_cost = fuel_cost + maintenance_cost + crew_cost + airport_fees + fixed_costs
    profit = revenue - total_cost
    profit_per_passenger = profit / passengers if passengers > 0 else 0
    profit_margin = profit / revenue if revenue > 0 else 0
    return {
        "distance_nm": distance_nm,
        "block_time_h": round(block_time_h, 3),
        "revenue": round(revenue, 2),
        "total_cost": round(total_cost, 2),
        "profit": round(profit, 2),
        "profit_margin": round(profit_margin, 4),
        "profit_per_passenger": round(profit_per_passenger, 2)
    }

import numpy as np
import pandas as pd
from datetime import datetime, timedelta

def generate_inventory_data(days=180, random_seed=42):
    """
    Génère un dataset synthétique de ventes et de niveaux de stock pour des produits de grande consommation au Mali.
    """
    np.random.seed(random_seed)
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=days)
    dates = pd.date_range(start=start_date, end=end_date, freq='D')
    
    products = [
        {"id": "PROD-001", "name": "Riz Brisé 50kg (Sac)", "category": "Céréales", "price_xof": 22500, "base_daily_sales": 15, "initial_stock": 180, "reorder_point": 100, "lead_time_days": 5},
        {"id": "PROD-002", "name": "Huile de Palme 5L (Bidon)", "category": "Huiles", "price_xof": 6500, "base_daily_sales": 25, "initial_stock": 120, "reorder_point": 150, "lead_time_days": 4},
        {"id": "PROD-003", "name": "Sucre Roux 1kg (Paquet)", "category": "Épicerie", "price_xof": 750, "base_daily_sales": 60, "initial_stock": 450, "reorder_point": 300, "lead_time_days": 3},
        {"id": "PROD-004", "name": "Lait en Poudre 400g (Boîte)", "category": "Produits Laitiers", "price_xof": 2800, "base_daily_sales": 18, "initial_stock": 90, "reorder_point": 110, "lead_time_days": 4},
        {"id": "PROD-005", "name": "Farine de Blé 25kg (Sac)", "category": "Céréales", "price_xof": 14500, "base_daily_sales": 10, "initial_stock": 140, "reorder_point": 80, "lead_time_days": 6},
        {"id": "PROD-006", "name": "Savon de Lave (Carton)", "category": "Hygiène", "price_xof": 4500, "base_daily_sales": 12, "initial_stock": 35, "reorder_point": 60, "lead_time_days": 3}
    ]
    
    records = []
    
    for prod in products:
        current_stock = prod["initial_stock"]
        
        for dt in dates:
            day_of_week = dt.weekday()
            is_weekend = day_of_week >= 5
            
            # Effet de saisonnalité / week-end (ventes plus élevées le vendredi/samedi)
            weekend_mult = 1.35 if is_weekend else 0.95
            monthly_trend = 1.0 + 0.15 * np.sin(dt.day * np.pi / 15)
            
            # Calcul des ventes quotidiennes avec de la variabilité
            sales_units = max(0, int(np.random.poisson(prod["base_daily_sales"] * weekend_mult * monthly_trend)))
            
            # Mise à jour du stock
            current_stock -= sales_units
            
            # Réapprovisionnement automatique si stock trop bas pour continuer la simulation
            if current_stock <= 10:
                current_stock += prod["initial_stock"] * 2
                
            records.append({
                "date": dt.strftime("%Y-%m-%d"),
                "product_id": prod["id"],
                "product_name": prod["name"],
                "category": prod["category"],
                "unit_price_xof": prod["price_xof"],
                "units_sold": sales_units,
                "revenue_xof": sales_units * prod["price_xof"],
                "stock_level": current_stock,
                "reorder_point": prod["reorder_point"],
                "lead_time_days": prod["lead_time_days"]
            })
            
    df = pd.DataFrame(records)
    return df

if __name__ == "__main__":
    df = generate_inventory_data()
    df.to_csv("/home/ibrahim-tomota/Documents/code/mali-smart-inventory-forecast/data/sales_inventory_sample.csv", index=False)
    print(f"Dataset de ventes & stock généré avec succès ({len(df)} lignes).")

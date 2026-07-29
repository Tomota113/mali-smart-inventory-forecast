import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestRegressor

class InventoryForecastingEngine:
    """
    Moteur de prédiction des ventes et de gestion intelligente du réapprovisionnement de stock.
    Utilise le Machine Learning pour anticiper la demande future sur N jours.
    """
    
    def __init__(self, forecast_days=30):
        self.forecast_days = forecast_days
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        
    def _create_features(self, df_product):
        """
        Génère les descripteurs temporels et retards (lags) pour la régression ML.
        """
        data = df_product.copy()
        data['date'] = pd.to_datetime(data['date'])
        data = data.sort_values('date')
        
        data['day_of_week'] = data['date'].dt.dayofweek
        data['day_of_month'] = data['date'].dt.day
        data['month'] = data['date'].dt.month
        
        # Retards (lags) des ventes
        for lag in [1, 2, 3, 7, 14]:
            data[f'sales_lag_{lag}'] = data['units_sold'].shift(lag)
            
        # Moyennes mobiles
        data['rolling_mean_7'] = data['units_sold'].shift(1).rolling(7).mean()
        data['rolling_mean_14'] = data['units_sold'].shift(1).rolling(14).mean()
        
        return data.dropna()

    def train_and_predict_product(self, df_product):
        """
        Entraîne le modèle sur l'historique d'un produit et prédit les ventes sur `forecast_days` futurs.
        """
        df_feat = self._create_features(df_product)
        if len(df_feat) < 20:
            # Sécurité en cas d'historique court : prédiction basée sur la moyenne
            mean_sales = df_product['units_sold'].tail(14).mean()
            predicted_sales = [max(0, int(mean_sales))] * self.forecast_days
        else:
            feature_cols = [c for c in df_feat.columns if 'lag' in c or 'rolling' in c or c in ['day_of_week', 'day_of_month', 'month']]
            X = df_feat[feature_cols]
            y = df_feat['units_sold']
            
            self.model.fit(X, y)
            
            # Simulation itérative pour les N prochains jours
            last_date = df_product['date'].max()
            if isinstance(last_date, str):
                last_date = pd.to_datetime(last_date)
                
            future_dates = [last_date + timedelta(days=i) for i in range(1, self.forecast_days + 1)]
            predicted_sales = []
            
            recent_sales = list(df_product['units_sold'].values)
            
            for f_date in future_dates:
                feat_dict = {
                    'day_of_week': f_date.dayofweek,
                    'day_of_month': f_date.day,
                    'month': f_date.month,
                    'sales_lag_1': recent_sales[-1],
                    'sales_lag_2': recent_sales[-2] if len(recent_sales) >= 2 else recent_sales[-1],
                    'sales_lag_3': recent_sales[-3] if len(recent_sales) >= 3 else recent_sales[-1],
                    'sales_lag_7': recent_sales[-7] if len(recent_sales) >= 7 else recent_sales[-1],
                    'sales_lag_14': recent_sales[-14] if len(recent_sales) >= 14 else recent_sales[-1],
                    'rolling_mean_7': np.mean(recent_sales[-7:]),
                    'rolling_mean_14': np.mean(recent_sales[-14:])
                }
                X_future = pd.DataFrame([feat_dict])[X.columns]
                pred = int(max(0, self.model.predict(X_future)[0]))
                predicted_sales.append(pred)
                recent_sales.append(pred)
                
        return predicted_sales

    def evaluate_inventory_health(self, df):
        """
        Calcule la santé des stocks et les alertes de réapprovisionnement pour l'ensemble des produits.
        """
        summary = []
        df['date'] = pd.to_datetime(df['date'])
        latest_date = df['date'].max()
        
        for prod_id, group in df.groupby('product_id'):
            latest_record = group[group['date'] == latest_date].iloc[0]
            prod_name = latest_record['product_name']
            current_stock = latest_record['stock_level']
            reorder_point = latest_record['reorder_point']
            lead_time_days = latest_record['lead_time_days']
            unit_price = latest_record['unit_price_xof']
            
            # Prédiction ML des ventes
            future_sales = self.train_and_predict_product(group)
            total_predicted_demand_30d = sum(future_sales)
            avg_daily_demand = total_predicted_demand_30d / self.forecast_days
            
            # Stock de sécurité & jours d'autonomie restants
            safety_stock = int(avg_daily_demand * lead_time_days * 1.2)
            days_of_stock_left = int(current_stock / avg_daily_demand) if avg_daily_demand > 0 else 999
            
            # Évaluation du statut du stock
            if current_stock <= reorder_point or days_of_stock_left <= lead_time_days:
                status = "CRITIQUE"
                status_msg = "🚨 Stock critique - Passer commande immédiatement !"
                recommended_reorder_qty = max(0, int(total_predicted_demand_30d + safety_stock - current_stock))
            elif current_stock <= (reorder_point * 1.4):
                status = "ATTENTION"
                status_msg = "⚠️ Stock faible - Prévoir réapprovisionnement"
                recommended_reorder_qty = max(0, int(total_predicted_demand_30d - current_stock))
            else:
                status = "OK"
                status_msg = "✅ Stock suffisant"
                recommended_reorder_qty = 0
                
            summary.append({
                'product_id': prod_id,
                'product_name': prod_name,
                'category': latest_record['category'],
                'current_stock': current_stock,
                'reorder_point': reorder_point,
                'avg_daily_demand': round(avg_daily_demand, 1),
                'forecasted_demand_30d': total_predicted_demand_30d,
                'days_of_stock_left': days_of_stock_left,
                'recommended_reorder_qty': recommended_reorder_qty,
                'reorder_cost_xof': recommended_reorder_qty * unit_price,
                'status': status,
                'status_msg': status_msg,
                'future_sales_list': future_sales
            })
            
        return pd.DataFrame(summary)

from utils.csv_loader import load_csv
import pandas as pd

def get_dashboard_metrics(timeframe: str = "30d", region: str = None):
    df = load_csv("dashboard_metrics.csv")
    
    # Filter by timeframe
    df = df[df['timeframe'] == timeframe]

    # Filter by region if provided
    if region:
        df = df[df['region'] == region]
    else:
        # Aggregate across regions if no region specified
        df = df.groupby(['metric_name', 'date_recorded'], as_index=False).agg({
            'metric_value': 'sum',
            'growth_percentage': 'mean'
        })
    
    # Get the latest date
    latest_date = df['date_recorded'].max()
    latest_df = df[df['date_recorded'] == latest_date]

    # Convert to dict
    metrics = latest_df.set_index('metric_name')['metric_value'].to_dict()
    growths = latest_df.set_index('metric_name')['growth_percentage'].to_dict()

    response = {
            "total_products": metrics.get("total_products"),
            "success_rate": metrics.get("success_rate"),
            "active_users": metrics.get("active_users"),
            "trending_categories": metrics.get("trending_categories"),
            "growth_metrics": {
                "products_growth": growths.get("total_products"),
                "success_rate_growth": growths.get("success_rate"),
                "users_growth": growths.get("active_users")
            }
    }

    return response
from flask import Flask, request, jsonify
from utils.csv_loader import load_csv
from utils.calculations import generate_market_score
from services.dashboard_service import get_dashboard_metrics
import pandas as pd
from datetime import datetime

app = Flask(__name__)

@app.route("/api/dashboard/metrics", methods=["GET"])
def dashboard_metrics():
    data_in = request.json or {}
    timeframe = data_in.get("timeframe", "30d")
    region = data_in.get("region")
    data = get_dashboard_metrics(timeframe, region)
    return jsonify({"success": True, "data": data})


@app.route("/api/products", methods=["GET"])
def get_products():
    data_in = request.json or {}
    page = int(data_in.get("page", 1))
    limit = int(data_in.get("limit", 10))
    category = data_in.get("category")
    search = data_in.get("search")
    sort_by = data_in.get("sort_by", "name")

    df = load_csv("products.csv")

    if category:
        df = df[df['category'].str.lower() == category.lower()]
    if search:
        df = df[
            df['name'].str.contains(search, case=False, na=False) |
            df['ingredients'].str.contains(search, case=False, na=False) |
            df['flavor_profile'].str.contains(search, case=False, na=False)
        ]
    if sort_by in df.columns:
        df = df.sort_values(by=sort_by, ascending=True)

    total_items = len(df)
    start_idx = (page - 1) * limit
    end_idx = start_idx + limit
    df_page = df.iloc[start_idx:end_idx]

    categories_list = sorted(df['category'].dropna().unique().tolist())

    return {
        "success": True,
        "page": page,
        "limit": limit,
        "total": total_items,
        "available_categories": categories_list,
        "data": df_page.to_dict(orient="records")
    }


@app.route("/api/products", methods=["POST"])
def create_product():
    product_data = request.json or {}
    products_df = load_csv("products.csv")
    trends_df = load_csv("market_trends.csv")
    
    score = generate_market_score(product_data.get("ingredients", []), trends_df)
    product_data["market_score"] = score
    
    product_data["id"] = int(products_df["id"].max()) + 1 if not products_df.empty else 1
    if "created_date" not in product_data:
        product_data["created_date"] = datetime.now().strftime("%m/%d/%Y")

    products_df = pd.concat([products_df, pd.DataFrame([product_data])], ignore_index=True)
    products_df.to_csv("data/products.csv", index=False)

    return jsonify({"success": True, "data": product_data})


@app.route("/api/market-trends", methods=["GET"])
def get_market_trends():
    data_in = request.json or {}
    region = data_in.get("region")
    category = data_in.get("category")
    df = load_csv("market_trends.csv")
    df['region'] = df['region'].fillna("").str.strip()
    df['category'] = df['category'].fillna("").str.strip()
    if region:
        df = df[df['region'].str.lower() == region.strip().lower()]
    if category:
        df = df[df['category'].str.lower() == category.strip().lower()]
    return jsonify({"success": True, "count": len(df), "data": df.to_dict(orient="records")})


@app.route("/api/analyze-product", methods=["POST"])
def analyze_product():
    product_concept = request.json or {}
    trends_df = load_csv("market_trends.csv")
    analysis_df = load_csv("analysis_results.csv")
    score = generate_market_score(product_concept.get("ingredients", []), trends_df)
    return jsonify({
        "success": True,
        "data": {
            "market_score": score,
            "recommendations": analysis_df.sample(1).reset_index(drop=True).iloc[0].to_dict()
        }
    })


@app.route("/api/competitors", methods=["GET"])
def get_competitors():
    data_in = request.json or {}
    category = data_in.get("category")
    df = load_csv("competitors.csv")
    if category:
        df = df[df['primary_category'].str.lower() == category.lower()]
    return jsonify({"success": True, "data": df.to_dict(orient="records")})


if __name__ == "__main__":
    app.run(debug=True)
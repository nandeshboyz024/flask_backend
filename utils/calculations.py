def calculate_growth(current: float, previous: float) -> float:
    if previous == 0:
        return 0
    return round(((current - previous) / previous) * 100, 2)

def generate_market_score(ingredients, trends_df):
    # Ensure ingredients are compared case-insensitively and stripped
    ingredients = [i.strip() for i in ingredients]
    
    scores = []
    for ingredient in ingredients:
        match = trends_df[trends_df['ingredient_name'].str.lower() == ingredient.lower()]
        if not match.empty:
            # Simple scoring: average of popularity_score and growth_rate
            avg_score = (match['popularity_score'].mean() + match['growth_rate'].mean()) / 2
            scores.append(avg_score)
    
    # Return average score if found, else default to 50
    return round(sum(scores) / len(scores), 2) if scores else 50.0
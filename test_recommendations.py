
import pandas as pd
from src.analysis import load_data
from src.recommendations import generate_recommendations

# Load sample dataset
df = load_data("data/sample_sales.csv")

# Generate business recommendations
recommendations = generate_recommendations(df)

print("\n===== RECOMMENDATION TEST =====")

print(recommendations)

# Basic validation
assert recommendations is not None, "Recommendations returned None"
assert len(recommendations) > 0, "No recommendations generated"

print("\nRecommendation test passed!")

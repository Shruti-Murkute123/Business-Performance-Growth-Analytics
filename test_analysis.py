
from src.analysis import (
    load_data,
    get_business_summary,
    get_monthly_performance,
    get_product_performance,
    get_region_performance,
    get_category_performance
)

# Load sample business data
df = load_data("data/sample_sales.csv")

# Display cleaned data
print("\n========== CLEANED DATA ==========")
print(df.head())

# Overall business summary
print("\n========== BUSINESS SUMMARY ==========")
summary = get_business_summary(df)

for key, value in summary.items():
    print(f"{key}: {value:,.2f}")

# Monthly analysis
print("\n========== MONTHLY PERFORMANCE ==========")
print(get_monthly_performance(df).to_string(index=False))

# Product analysis
print("\n========== PRODUCT PERFORMANCE ==========")
print(get_product_performance(df).to_string(index=False))

# Regional analysis
print("\n========== REGIONAL PERFORMANCE ==========")
print(get_region_performance(df).to_string(index=False))

# Category analysis
print("\n========== CATEGORY PERFORMANCE ==========")
print(get_category_performance(df).to_string(index=False))

print("\nANALYSIS COMPLETED SUCCESSFULLY!")

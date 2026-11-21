
import pandas as pd


def generate_recommendations(df):
    """
    Analyse business sales data and generate automatic
    business growth recommendations.
    """

    recommendations = []

    if df.empty:
        return [{
            "title": "No business data available",
            "priority": "High",
            "insight": "There are no valid records to analyse.",
            "action": "Upload a CSV file containing valid sales records."
        }]

    # 1. Product performance
    product_data = (
        df.groupby("Product")
        .agg(
            Revenue=("Revenue", "sum"),
            Profit=("Profit", "sum"),
            Quantity=("Quantity", "sum")
        )
        .sort_values("Revenue", ascending=False)
    )

    if len(product_data) >= 2:
        best_product = product_data.index[0]
        weakest_product = product_data.index[-1]

        recommendations.append({
            "title": "Focus on your best-selling product",
            "priority": "High",
            "insight": (
                f"{best_product} generates the highest revenue "
                f"(₹{product_data.loc[best_product, 'Revenue']:,.0f})."
            ),
            "action": (
                f"Consider increasing the availability and promotion "
                f"of {best_product}."
            )
        })

        recommendations.append({
            "title": "Review your lowest-revenue product",
            "priority": "Medium",
            "insight": (
                f"{weakest_product} generates the lowest revenue "
                f"(₹{product_data.loc[weakest_product, 'Revenue']:,.0f})."
            ),
            "action": (
                f"Review customer demand, pricing and marketing for "
                f"{weakest_product} before deciding whether to improve "
                f"or reduce its stock."
            )
        })

    # 2. Profit margin analysis
    total_revenue = df["Revenue"].sum()
    total_profit = df["Profit"].sum()

    if total_revenue > 0:
        overall_margin = (total_profit / total_revenue) * 100

        product_data["Profit_Margin"] = (
            product_data["Profit"] / product_data["Revenue"].replace(0, pd.NA)
        ) * 100

        low_margin_products = product_data[
            product_data["Profit_Margin"] < overall_margin
        ]

        if not low_margin_products.empty:
            names = ", ".join(
                low_margin_products.index.astype(str).tolist()
            )

            recommendations.append({
                "title": "Improve product profit margins",
                "priority": "High",
                "insight": (
                    f"These products have a profit margin below "
                    f"the overall business margin of {overall_margin:.1f}%: "
                    f"{names}."
                ),
                "action": (
                    "Review supplier costs, discounts and selling prices "
                    "to improve profitability."
                )
            })

    # 3. Regional performance
    region_data = (
        df.groupby("Region")
        .agg(
            Revenue=("Revenue", "sum"),
            Profit=("Profit", "sum")
        )
        .sort_values("Revenue", ascending=False)
    )

    if len(region_data) >= 2:
        best_region = region_data.index[0]
        weakest_region = region_data.index[-1]

        recommendations.append({
            "title": "Expand your strongest region",
            "priority": "Medium",
            "insight": (
                f"{best_region} is your highest-revenue region "
                f"(₹{region_data.loc[best_region, 'Revenue']:,.0f})."
            ),
            "action": (
                f"Study what works in {best_region} and consider "
                "replicating those strategies in other regions."
            )
        })

        recommendations.append({
            "title": "Investigate regional sales performance",
            "priority": "Medium",
            "insight": (
                f"{weakest_region} has the lowest revenue "
                f"(₹{region_data.loc[weakest_region, 'Revenue']:,.0f})."
            ),
            "action": (
                "Check local demand, customer preferences, pricing "
                "and marketing activity in this region."
            )
        })

    # 4. Monthly sales trend
    monthly_data = (
        df.assign(Month=df["Order_Date"].dt.to_period("M"))
        .groupby("Month")["Revenue"]
        .sum()
        .sort_index()
    )

    if len(monthly_data) >= 2:
        previous_month = monthly_data.iloc[-2]
        latest_month = monthly_data.iloc[-1]

        if previous_month > 0:
            change = (
                (latest_month - previous_month) / previous_month
            ) * 100

            if change < 0:
                recommendations.append({
                    "title": "Monthly revenue has declined",
                    "priority": "High",
                    "insight": (
                        f"Revenue decreased by {abs(change):.1f}% "
                        "compared with the previous month."
                    ),
                    "action": (
                        "Investigate the reason for the decline and "
                        "review recent orders, product demand and campaigns."
                    )
                })
            else:
                recommendations.append({
                    "title": "Monthly revenue is growing",
                    "priority": "Low",
                    "insight": (
                        f"Revenue increased by {change:.1f}% "
                        "compared with the previous month."
                    ),
                    "action": (
                        "Continue monitoring the strategies contributing "
                        "to this growth."
                    )
                })

    if not recommendations:
        recommendations.append({
            "title": "Business data analysed",
            "priority": "Low",
            "insight": "No major performance issues were identified.",
            "action": "Continue monitoring revenue, profit and regional performance."
        })

    return recommendations

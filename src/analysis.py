
import pandas as pd


# ==========================================
# 1. LOAD AND VALIDATE BUSINESS DATA
# ==========================================



def load_data(file):
    """Load CSV and Excel business datasets."""

    try:
        file_name = getattr(file, "name", str(file)).lower()

        if file_name.endswith(".csv"):
            df = pd.read_csv(file)

        elif file_name.endswith((".xlsx", ".xls")):
            df = pd.read_excel(file)

        else:
            raise ValueError("Unsupported file format.")

    except Exception as e:
        raise ValueError(f"Unable to read file: {e}")

    if df.empty:
        raise ValueError("The uploaded file is empty.")

    df.columns = df.columns.astype(str).str.strip()

    df = df.dropna(axis=1, how="all")
    df = df.dropna(axis=0, how="all")

    if len(df.columns) == 0:
        raise ValueError("No usable columns found.")

    return df

# ==========================================
# 2. OVERALL BUSINESS PERFORMANCE
# ==========================================

def get_business_summary(df):

    total_revenue = df["Revenue"].sum()

    total_profit = df["Profit"].sum()

    total_orders = df["Order_ID"].nunique()

    total_units = df["Quantity"].sum()

    total_cost = df["Cost"].sum()

    profit_margin = (
        (total_profit / total_revenue) * 100
        if total_revenue != 0 else 0
    )

    return {
        "Total Revenue": total_revenue,
        "Total Profit": total_profit,
        "Total Cost": total_cost,
        "Total Orders": total_orders,
        "Units Sold": total_units,
        "Profit Margin": profit_margin
    }


# ==========================================
# 3. MONTHLY PERFORMANCE
# ==========================================

def get_monthly_performance(df):

    monthly = df.copy()

    monthly["Month"] = (
        monthly["Order_Date"].dt.to_period("M")
    )

    result = monthly.groupby("Month").agg(
        Revenue=("Revenue", "sum"),
        Profit=("Profit", "sum"),
        Cost=("Cost", "sum"),
        Orders=("Order_ID", "nunique"),
        Units_Sold=("Quantity", "sum")
    ).reset_index()

    result = result.sort_values("Month")

    result["Month"] = result["Month"].astype(str)

    # Revenue growth percentage
    result["Revenue_Growth"] = (
        result["Revenue"].pct_change() * 100
    )

    # Profit growth percentage
    result["Profit_Growth"] = (
        result["Profit"].pct_change() * 100
    )

    return result


# ==========================================
# 4. PRODUCT PERFORMANCE
# ==========================================

def get_product_performance(df):

    result = df.groupby("Product").agg(
        Revenue=("Revenue", "sum"),
        Profit=("Profit", "sum"),
        Cost=("Cost", "sum"),
        Units_Sold=("Quantity", "sum"),
        Orders=("Order_ID", "nunique")
    ).reset_index()

    # Calculate product profit margin
    result["Profit_Margin"] = (
        result["Profit"] /
        result["Revenue"].replace(0, float("nan"))
    ) * 100

    return result.sort_values(
        by="Revenue",
        ascending=False
    )


# ==========================================
# 5. REGIONAL PERFORMANCE
# ==========================================

def get_region_performance(df):

    result = df.groupby("Region").agg(
        Revenue=("Revenue", "sum"),
        Profit=("Profit", "sum"),
        Cost=("Cost", "sum"),
        Orders=("Order_ID", "nunique"),
        Units_Sold=("Quantity", "sum")
    ).reset_index()

    result["Profit_Margin"] = (
        result["Profit"] /
        result["Revenue"].replace(0, float("nan"))
    ) * 100

    return result.sort_values(
        by="Revenue",
        ascending=False
    )


# ==========================================
# 6. CATEGORY PERFORMANCE
# ==========================================

def get_category_performance(df):

    result = df.groupby("Category").agg(
        Revenue=("Revenue", "sum"),
        Profit=("Profit", "sum"),
        Cost=("Cost", "sum"),
        Units_Sold=("Quantity", "sum"),
        Orders=("Order_ID", "nunique")
    ).reset_index()

    result["Profit_Margin"] = (
        result["Profit"] /
        result["Revenue"].replace(0, float("nan"))
    ) * 100

    return result.sort_values(
        by="Revenue",
        ascending=False
    )

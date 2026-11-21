
import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
from io import BytesIO
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.table import Table, TableStyleInfo

from src.analysis import load_data
from src.data_profiler import profile_dataset
from src.recommendations import generate_recommendations


# ==========================================
# 1. PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="Business Growth Analytics",
    page_icon="📊",
    layout="wide"
)


# ==========================================
# 2. CUSTOM STYLING
# ==========================================


st.markdown("""
<style>

/* Normal dashboard styling */
.main {
    background-color: #f7f9fc;
}

h1, h2, h3 {
    color: #172554;
}

div[data-testid="stMetric"] {
    background-color: white;
    padding: 18px;
    border-radius: 12px;
    border: 1px solid #e5e7eb;
}

/* PRINT SETTINGS */
@media print {

    @page {
        size: A4 landscape;
        margin: 10mm;
    }

    /* Hide sidebar and unnecessary controls */
    [data-testid="stSidebar"],
    [data-testid="stHeader"],
    [data-testid="stToolbar"],
    .stDownloadButton,
    button {
        display: none !important;
    }

    /* Use full printable width */
    .main,
    .block-container {
        width: 100% !important;
        max-width: 100% !important;
        padding: 0 !important;
        margin: 0 !important;
    }

    /* Keep charts together on one page */
    [data-testid="stPlotlyChart"],
    [data-testid="stMetric"],
    [data-testid="stDataFrame"],
    [data-testid="stTable"] {
        break-inside: avoid !important;
        page-break-inside: avoid !important;
    }

    /* Avoid splitting chart containers */
    .element-container {
        break-inside: avoid !important;
        page-break-inside: avoid !important;
    }

    /* Improve chart sizing */
    [data-testid="stPlotlyChart"] {
        width: 100% !important;
        max-width: 100% !important;
    }

    body {
        background: white !important;
        color: black !important;
    }

    h1, h2, h3 {
        color: #172554 !important;
        break-after: avoid !important;
    }

    /* Hide unnecessary decorative dividers */
    hr {
        border-color: #dddddd !important;
    }
}

</style>
""", unsafe_allow_html=True)

# ==========================================
# 3. DATA LOADING
# ==========================================

st.sidebar.title("📊 Business Analytics")
st.sidebar.markdown("Upload your own business CSV dataset.")

uploaded_file = st.sidebar.file_uploader(
    "Upload your Business Data",
    type=["csv", "xlsx", "xls"],
    help="Upload CSV or Excel workbooks."
)

if uploaded_file is not None:
    try:
        df = load_data(uploaded_file)
        st.sidebar.success("CSV uploaded successfully!")

    except Exception as e:
        st.error(f"Unable to process uploaded CSV: {e}")
        st.stop()

else:
    data_path = Path(__file__).parent / "data" / "sample_sales.csv"

    try:
        df = load_data(data_path)
        st.sidebar.info("Using sample sales dataset.")

    except Exception as e:
        st.error(f"Unable to load sample data: {e}")
        st.stop()

if df.empty:
    st.error("The dataset contains no records.")
    st.stop()


# ==========================================
# 4. DASHBOARD HEADER
# ==========================================

st.title("📈 Business Performance & Growth Dashboard")

st.markdown(
    "Analyze business data, discover patterns and identify growth opportunities."
)

st.caption(
    "Adaptive Business Intelligence Dashboard"
)

st.divider()


# ==========================================
# 5. DATASET INTELLIGENCE
# ==========================================

st.header("🔍 Dataset Intelligence")

profile = profile_dataset(df)

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Rows", profile["rows"])
col2.metric("Total Columns", profile["columns"])
col3.metric("Missing Cells", profile["missing_cells"])
col4.metric("Duplicate Rows", profile["duplicate_rows"])

st.subheader("Column Analysis")

profile_df = pd.DataFrame(profile["column_details"])

st.dataframe(
    profile_df,
    use_container_width=True,
    hide_index=True
)

st.caption(
    f"Dataset memory usage: {profile['memory_usage_kb']} KB"
)

st.divider()


# ==========================================
# 6. AUTOMATIC COLUMN DETECTION
# ==========================================

working_df = df.copy()

# Standardize column names for matching.
def normalize_name(name):
    return (
        str(name)
        .strip()
        .lower()
        .replace("_", "")
        .replace(" ", "")
        .replace("-", "")
    )


column_lookup = {
    normalize_name(column): column
    for column in working_df.columns
}


def find_column(possible_names):
    for name in possible_names:
        key = normalize_name(name)

        if key in column_lookup:
            return column_lookup[key]

    return None


# Recognize common business column names.

date_col = find_column([
    "Order_Date",
    "Transaction_Date",
    "Date",
    "Invoice_Date",
    "Sale_Date",
    "Signup_Date",
    "Created_Date"
])

product_col = find_column([
    "Product",
    "Product_Name",
    "Item_Name",
    "Product_Description"
])

category_col = find_column([
    "Category",
    "Product_Category",
    "Customer_Segment"
])

region_col = find_column([
    "Region",
    "Zone",
    "Location",
    "City",
    "Warehouse"
])

quantity_col = find_column([
    "Quantity",
    "Qty",
    "Qty_Sold",
    "Units_Sold"
])

price_col = find_column([
    "Unit_Price",
    "Selling_Price",
    "Price",
    "Sale_Price"
])

cost_col = find_column([
    "Unit_Cost",
    "Cost_Per_Unit",
    "Purchase_Price"
])

revenue_col = find_column([
    "Revenue",
    "Sales",
    "Total_Sales",
    "Sales_Amount"
])

profit_col = find_column([
    "Profit",
    "Net_Profit"
])

amount_col = find_column([
    "Amount",
    "Total_Amount",
    "Transaction_Amount"
])


# ==========================================
# 7. DATE AND NUMERIC PREPARATION
# ==========================================

if date_col is not None:
    working_df[date_col] = pd.to_datetime(
        working_df[date_col],
        errors="coerce"
    )

numeric_columns = working_df.select_dtypes(
    include="number"
).columns.tolist()

# Convert numeric-looking text columns when appropriate.
for column in working_df.columns:

    if column == date_col:
        continue

    if working_df[column].dtype == "object":

        cleaned = (
            working_df[column]
            .astype(str)
            .str.replace(",", "", regex=False)
            .str.replace("₹", "", regex=False)
            .str.strip()
        )

        converted = pd.to_numeric(
            cleaned,
            errors="coerce"
        )

        valid_ratio = converted.notna().mean()

        if valid_ratio >= 0.8 and valid_ratio > 0:
            working_df[column] = converted

numeric_columns = working_df.select_dtypes(
    include="number"
).columns.tolist()


# ==========================================
# 8. SALES DATA DETECTION
# ==========================================

sales_supported = all([
    date_col is not None,
    product_col is not None,
    category_col is not None,
    region_col is not None,
    quantity_col is not None,
    price_col is not None,
    cost_col is not None
])

if sales_supported:

    working_df["Revenue"] = (
        pd.to_numeric(working_df[quantity_col], errors="coerce") *
        pd.to_numeric(working_df[price_col], errors="coerce")
    )

    working_df["Cost"] = (
        pd.to_numeric(working_df[quantity_col], errors="coerce") *
        pd.to_numeric(working_df[cost_col], errors="coerce")
    )

    working_df["Profit"] = (
        working_df["Revenue"] - working_df["Cost"]
    )

    working_df["Profit_Margin"] = (
        working_df["Profit"]
        .div(working_df["Revenue"].where(working_df["Revenue"] != 0))
        .mul(100)
    )

    st.success(
        "Sales dataset detected. Full sales analytics are available."
    )

else:

    st.info(
        "General business dataset detected. "
        "The dashboard will display analytics supported by its columns."
    )


# ==========================================
# 9. ADAPTIVE FILTERS
# ==========================================

st.sidebar.subheader("Dashboard Filters")

filtered_df = working_df.copy()

# Date filter

if date_col is not None:

    valid_dates = working_df[date_col].dropna()

    if not valid_dates.empty:

        min_date = valid_dates.min().date()
        max_date = valid_dates.max().date()

        start_date = st.sidebar.date_input(
            "Start Date",
            value=min_date,
            min_value=min_date,
            max_value=max_date
        )

        end_date = st.sidebar.date_input(
            "End Date",
            value=max_date,
            min_value=min_date,
            max_value=max_date
        )

        if start_date > end_date:
            st.error("Start date cannot be after end date.")
            st.stop()

        filtered_df = filtered_df[
            filtered_df[date_col].notna() &
            (filtered_df[date_col].dt.date >= start_date) &
            (filtered_df[date_col].dt.date <= end_date)
        ].copy()


# Categorical filters

filter_columns = []

for column in [region_col, category_col, product_col]:

    if (
        column is not None
        and column in filtered_df.columns
        and column not in filter_columns
    ):
        filter_columns.append(column)


for column in filter_columns:

    values = sorted(
        filtered_df[column]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    selected_values = st.sidebar.multiselect(
        f"Select {column}",
        options=values,
        default=values
    )

    filtered_df = filtered_df[
        filtered_df[column].astype(str).isin(selected_values)
    ].copy()


if filtered_df.empty:
    st.warning("No records match the selected filters.")
    st.stop()


# ==========================================
# 10. GENERAL BUSINESS OVERVIEW
# ==========================================

st.header("Business Overview")

overview_columns = st.columns(4)

overview_columns[0].metric(
    "Total Records",
    f"{len(filtered_df):,}"
)

overview_columns[1].metric(
    "Total Columns",
    f"{len(filtered_df.columns):,}"
)

overview_columns[2].metric(
    "Numeric Columns",
    f"{len(numeric_columns):,}"
)

overview_columns[3].metric(
    "Date Column Available",
    "Yes" if date_col is not None else "No"
)

st.divider()


# ==========================================
# 11. SALES ANALYTICS
# ==========================================

if sales_supported:

    st.header("Sales Performance Analysis")

    sales_data = filtered_df.copy()

    total_revenue = sales_data["Revenue"].sum()
    total_cost = sales_data["Cost"].sum()
    total_profit = sales_data["Profit"].sum()
    total_quantity = sales_data[quantity_col].sum()

    total_orders = len(sales_data)

    profit_margin = (
        (total_profit / total_revenue) * 100
        if total_revenue != 0
        else 0
    )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Total Revenue",
        f"₹{total_revenue:,.2f}"
    )

    col2.metric(
        "Total Profit",
        f"₹{total_profit:,.2f}"
    )

    col3.metric(
        "Total Records",
        f"{total_orders:,}"
    )

    col4.metric(
        "Profit Margin",
        f"{profit_margin:.2f}%"
    )

    st.caption(
        f"Total units sold: {total_quantity:,.0f}"
    )

    st.divider()

    # Monthly analysis

    st.subheader("Monthly Performance Analysis")

    monthly_data = sales_data.dropna(subset=[date_col]).copy()

    if not monthly_data.empty:

        monthly_data["Month"] = (
            monthly_data[date_col].dt.to_period("M").astype(str)
        )

        monthly_df = (
            monthly_data.groupby("Month", as_index=False)
            .agg({
                "Revenue": "sum",
                "Profit": "sum"
            })
        )

        col1, col2 = st.columns(2)

        with col1:

            fig = px.line(
                monthly_df,
                x="Month",
                y="Revenue",
                markers=True,
                title="Monthly Revenue Trend"
            )

            fig.update_layout(template="plotly_white")

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        with col2:

            fig = px.bar(
                monthly_df,
                x="Month",
                y="Profit",
                title="Monthly Profit Comparison"
            )

            fig.update_layout(template="plotly_white")

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        st.dataframe(
            monthly_df,
            use_container_width=True,
            hide_index=True
        )

    st.divider()

    # Product performance

    st.subheader("Product Performance")

    product_df = (
        sales_data.groupby(product_col, as_index=False)
        .agg({
            "Revenue": "sum",
            "Profit": "sum"
        })
        .sort_values("Revenue", ascending=False)
    )

    col1, col2 = st.columns(2)

    with col1:

        fig = px.bar(
            product_df,
            x=product_col,
            y="Revenue",
            title="Revenue by Product"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    with col2:

        fig = px.bar(
            product_df,
            x=product_col,
            y="Profit",
            title="Profit by Product"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    st.dataframe(
        product_df,
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    # Regional performance

    st.subheader("Regional Performance")

    region_df = (
        sales_data.groupby(region_col, as_index=False)
        .agg({
            "Revenue": "sum",
            "Profit": "sum"
        })
        .sort_values("Revenue", ascending=False)
    )

    col1, col2 = st.columns(2)

    with col1:

        fig = px.bar(
            region_df,
            x=region_col,
            y="Revenue",
            color=region_col,
            title="Revenue by Region"
        )

        fig.update_layout(showlegend=False)

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    with col2:

        fig = px.bar(
            region_df,
            x=region_col,
            y="Profit",
            title="Profit by Region"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    st.dataframe(
        region_df,
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    # Category performance

    st.subheader("Category Performance")

    category_df = (
        sales_data.groupby(category_col, as_index=False)
        .agg({
            "Revenue": "sum",
            "Profit": "sum"
        })
        .sort_values("Revenue", ascending=False)
    )

    col1, col2 = st.columns(2)

    with col1:

        fig = px.pie(
            category_df,
            names=category_col,
            values="Revenue",
            title="Revenue Distribution by Category",
            hole=0.4
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    with col2:

        fig = px.bar(
            category_df,
            x=category_col,
            y="Profit",
            title="Profit by Category"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    st.divider()

    # Business recommendations

    st.header("💡 Automatic Business Growth Recommendations")

    try:

        recommendations = generate_recommendations(sales_data)

        if recommendations:

            for recommendation in recommendations:

                with st.container(border=True):

                    st.subheader(recommendation["title"])

                    st.caption(
                        f"Priority: {recommendation['priority']}"
                    )

                    st.write("**Business Insight:**")
                    st.write(recommendation["insight"])

                    st.write("**Recommended Action:**")
                    st.write(recommendation["action"])

        else:
            st.info("No recommendations are available for this dataset.")

    except Exception as e:

        st.warning(
            f"Recommendations could not be generated: {e}"
        )


# ==========================================
# 12. GENERAL DATASET ANALYTICS
# ==========================================

else:

    st.header("General Dataset Analytics")

    # Numeric analysis

    if numeric_columns:

        st.subheader("Numeric Data Analysis")

        metric_columns = [
            column for column in numeric_columns
            if column in filtered_df.columns
        ]

        metric_columns = metric_columns[:4]

        metric_layout = st.columns(max(1, len(metric_columns)))

        for index, column in enumerate(metric_columns):

            total = filtered_df[column].sum()

            metric_layout[index].metric(
                f"Total {column}",
                f"{total:,.2f}"
            )

        st.subheader("Numeric Column Statistics")

        numeric_summary = (
            filtered_df[numeric_columns]
            .describe()
            .T
            .reset_index()
            .rename(columns={"index": "Column"})
        )

        st.dataframe(
            numeric_summary,
            use_container_width=True
        )

        st.subheader("Numeric Data Visualizations")

        selected_numeric = st.selectbox(
            "Choose a numeric column",
            numeric_columns
        )

        fig = px.histogram(
            filtered_df,
            x=selected_numeric,
            title=f"Distribution of {selected_numeric}"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        # Compare two numeric columns if available.

        if len(numeric_columns) >= 2:

            col1, col2 = st.columns(2)

            with col1:

                x_column = st.selectbox(
                    "Select X-axis",
                    numeric_columns,
                    key="numeric_x"
                )

            with col2:

                y_options = [
                    column for column in numeric_columns
                    if column != x_column
                ]

                y_column = st.selectbox(
                    "Select Y-axis",
                    y_options,
                    key="numeric_y"
                )

            fig = px.scatter(
                filtered_df,
                x=x_column,
                y=y_column,
                title=f"{y_column} vs {x_column}"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

    else:

        st.info(
            "No numeric columns were detected. "
            "Numeric charts are not available for this dataset."
        )

    st.divider()

    # Date analysis

    if date_col is not None:

        st.subheader("Date-Based Analysis")

        date_data = filtered_df.dropna(subset=[date_col]).copy()

        if not date_data.empty:

            date_data["Month"] = (
                date_data[date_col].dt.to_period("M").astype(str)
            )

            monthly_counts = (
                date_data.groupby("Month")
                .size()
                .reset_index(name="Records")
            )

            fig = px.line(
                monthly_counts,
                x="Month",
                y="Records",
                markers=True,
                title="Records Over Time"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

    # Categorical analysis

    categorical_columns = (
        filtered_df.select_dtypes(
            include=["object", "category"]
        ).columns.tolist()
    )

    if categorical_columns:

        st.subheader("Categorical Analysis")

        selected_category = st.selectbox(
            "Choose a categorical column",
            categorical_columns
        )

        category_counts = (
            filtered_df[selected_category]
            .value_counts()
            .reset_index()
        )

        category_counts.columns = [
            selected_category,
            "Record Count"
        ]

        fig = px.bar(
            category_counts.head(20),
            x=selected_category,
            y="Record Count",
            title=f"Distribution of {selected_category}"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        st.dataframe(
            category_counts,
            use_container_width=True,
            hide_index=True
        )


# ==========================================
# 13. BUSINESS DATA EXPLORER
# ==========================================

st.divider()

st.header("📋 Business Data Explorer")

st.write(
    "Explore the records in your uploaded dataset."
)

st.dataframe(
    filtered_df,
    use_container_width=True,
    hide_index=True
)


# ==========================================
# 14. DOWNLOAD ANALYSED DATA
# ==========================================

# csv_data = filtered_df.to_csv(index=False).encode("utf-8")
# ==========================================
# 14. DOWNLOAD ANALYSED DATA
# ==========================================

download_df = filtered_df.copy()


# ==========================================
# 14. PROFESSIONAL EXCEL DOWNLOAD
# ==========================================

download_df = filtered_df.copy()

# Format date columns
for column in download_df.columns:
    if pd.api.types.is_datetime64_any_dtype(download_df[column]):
        download_df[column] = download_df[column].dt.strftime("%d-%b-%Y")

# Create Excel file in memory
output = BytesIO()

with pd.ExcelWriter(output, engine="openpyxl") as writer:

    download_df.to_excel(
        writer,
        index=False,
        sheet_name="Business Data"
    )

    worksheet = writer.sheets["Business Data"]

    # Professional header styling
    for cell in worksheet[1]:
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = PatternFill(
            start_color="1F4E78",
            end_color="1F4E78",
            fill_type="solid"
        )
        cell.alignment = Alignment(horizontal="center")

    # Automatically adjust column widths
    for column_cells in worksheet.columns:

        max_length = 0
        column_letter = get_column_letter(
            column_cells[0].column
        )

        for cell in column_cells:
            if cell.value is not None:
                max_length = max(
                    max_length,
                    len(str(cell.value))
                )

        worksheet.column_dimensions[column_letter].width = min(
            max(max_length + 4, 12),
            35
        )

    # Freeze header
    worksheet.freeze_panes = "A2"

    # Enable Excel filters
    worksheet.auto_filter.ref = worksheet.dimensions

    # Date formatting
    for column_index, column_name in enumerate(download_df.columns, 1):

        if "date" in column_name.lower():
            for row in range(2, worksheet.max_row + 1):
                worksheet.cell(
                    row=row,
                    column=column_index
                ).number_format = "DD-MMM-YYYY"

excel_data = output.getvalue()

st.download_button(
    label="📥 Download Professional Excel Report",
    data=excel_data,
    file_name="Business_Analytics_Report.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    key="professional_excel_download"
)




# ==========================================
# 15. FOOTER
# ==========================================

st.divider()

st.caption(
    "Business Performance & Growth Analytics Dashboard"
)

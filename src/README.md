# Business Performance & Growth Analytics Dashboard

An interactive business analytics dashboard that transforms raw sales data into meaningful business insights and automated growth recommendations.

## Overview

This project helps businesses monitor performance, understand sales trends, evaluate profitability and identify opportunities for growth through interactive data visualizations and automated recommendations.

## Features

- Business KPI tracking: Revenue, Profit, Cost, Orders and Units Sold.
- Monthly sales and profit analysis.
- Product performance analysis.
- Regional performance comparison.
- Category-wise revenue and profit analysis.
- Interactive dashboard filters.
- CSV upload and dataset validation.
- Automated business growth recommendations.
- Filtered data export as CSV.

## Technologies Used

- Python
- Pandas
- Streamlit
- Plotly
- Git
- GitHub

## Project Structure

```text
Business-Analytics-Dashboard/
├── data/
│   └── sample_sales.csv
├── src/
│   ├── analysis.py
│   └── recommendations.py
├── app.py
├── test_analysis.py
├── test_recommendations.py
├── requirements.txt
├── README.md
└── .gitignore
```

## Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/Shruti-Murkute123/Business-Performance-Growth-Analytics.git
```

### 2. Enter the project folder

```bash
cd Business-Performance-Growth-Analytics
```

### 3. Create a virtual environment

```bash
python -m venv venv
```

### 4. Activate the virtual environment

For Windows:

```bash
source venv/Scripts/activate
```

### 5. Install dependencies

```bash
pip install -r requirements.txt
```

### 6. Run the dashboard

```bash
streamlit run app.py
```

APP URL : https://business-performance-growth-analytics.streamlit.app

## Dataset

The sample dataset includes order details, dates, products, categories, regions, quantities, unit prices and unit costs.

Users can also upload their own compatible CSV datasets.

## Future Enhancements

- Sales forecasting.
- Customer segmentation.
- Predictive analytics.
- Advanced business intelligence.
- AI-powered business recommendations.

## Author

Developed as a portfolio project demonstrating practical skills in Python, data analytics, business intelligence and data-driven decision-making.

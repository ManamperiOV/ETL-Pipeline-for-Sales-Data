import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import create_engine

#Title
st.title("📊 Retail Sales Dashboard")
st.markdown("Filter by date, country, and price range to explore sales insights.")

#Set common Seaborn theme for all plots
sns.set_theme(style="darkgrid")

#Connect to DB
dbURL = "postgresql://postgres:ovmpost@localhost:5432/retail_sales"
engine = create_engine(dbURL)

#Load data
query = """
SELECT "InvoiceDate", "Country", "Description", "Quantity", "UnitPriceUSD",
       ("Quantity" * "UnitPriceUSD") AS "TotalSalesUSD"
FROM sales_data
"""
df = pd.read_sql(query, engine)

#SetInvoiceDate as date time format
df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])

#Sidebar filters
st.sidebar.header("🔍 Filters")

#Filter 1 - Date
min_date = df["InvoiceDate"].min()
max_date = df["InvoiceDate"].max()
start_date = st.sidebar.date_input("Start Date", min_date, min_value=min_date, max_value=max_date)
end_date = st.sidebar.date_input("End Date", max_date, min_value=min_date, max_value=max_date)

#Filter 2 - Country
country_options = ["All"] + sorted(df["Country"].unique().tolist())
selected_country = st.sidebar.selectbox("Select Country", country_options)

#Apply filters
filtered_df = df[(df["InvoiceDate"] >= pd.to_datetime(start_date)) & (df["InvoiceDate"] <= pd.to_datetime(end_date))]

if selected_country != "All":
    filtered_df = filtered_df[filtered_df["Country"] == selected_country]

#Display metrics - total revenue and quantity
col1, col2 = st.columns(2)
total_revenue = filtered_df["TotalSalesUSD"].sum()
total_quantity = filtered_df["Quantity"].sum()

col1.metric(label="💰 Total Revenue (USD)", value=f"${total_revenue:,.2f}")
col2.metric(label="📦 Total Quantity Sold", value=int(total_quantity))

#Display trends
st.write("### 📈 Monthly Sales Trend")
df_monthly = filtered_df.groupby(filtered_df["InvoiceDate"].dt.to_period("M"))["TotalSalesUSD"].sum()
df_monthly.index = df_monthly.index.to_timestamp()  # Convert back to timestamp

fig1, ax1 = plt.subplots()
df_monthly.plot(kind="line", marker="o", ax=ax1, color="blue")
ax1.set_title("Monthly Sales Trend")
ax1.set_ylabel("Total Sales (USD)")
st.pyplot(fig1)

#Display info
st.write("### 🏆 Top 5 Selling Products (by Quantity)")
top_products = filtered_df.groupby("Description")["Quantity"].sum().nlargest(5)

fig2, ax2 = plt.subplots()
top_products.plot(kind="bar", ax=ax2, color="orange")
ax2.set_title("Top 5 Selling Products")
ax2.set_ylabel("Quantity Sold")
st.pyplot(fig2)

#Option to view raw filtered data
with st.expander("📄 View Raw Filtered Data"):
    st.dataframe(filtered_df)
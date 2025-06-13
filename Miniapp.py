import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date

st.set_page_config(page_title="Expense Tracker", layout="wide")

st.title("Personal Expense Tracker")

input_mode = st.radio("Choose Input Mode", ["Upload CSV", "Manual Entry"], horizontal=True)


if "manual_data" not in st.session_state:
    st.session_state.manual_data = []

if input_mode == "Upload CSV":
    uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        st.success("File uploaded successfully!")
    else:
        df = pd.DataFrame()

else:  
    with st.form("manual_entry_form"):
        col1, col2, col3 = st.columns(3)
        with col1:
            category = st.text_input("Category")
        with col2:
            amount = st.number_input("Amount", min_value=0.0)
        with col3:
            entry_date = st.date_input("Date", value=date.today())

        submitted = st.form_submit_button("✏️Add Expense")
        if submitted and category:
            st.session_state.manual_data.append({
                "Category": category,
                "Amount": amount,
                "Date": entry_date
            })
            st.success("Expense added!")

   
    df = pd.DataFrame(st.session_state.manual_data)

    if not df.empty:
        if st.button("Clear All Entries"):
            st.session_state.manual_data = []
            df = pd.DataFrame()
            st.experimental_rerun()


if not df.empty:
    st.subheader("📌 All Expenses")
    st.dataframe(df)

    
    all_categories = df["Category"].unique()
    selected_categories = st.multiselect("Filter by Category", all_categories)

    if selected_categories:
        data_to_use = df[df["Category"].isin(selected_categories)]
    else:
        data_to_use = df.copy()

    
    category_summary = data_to_use.groupby("Category")["Amount"].sum()

    
    total = data_to_use["Amount"].sum()
    st.metric("Total Expense", f"₹{total:,.2f}")

   
    chart_type = st.radio("Choose chart type", ["Pie Chart", "Bar Chart"], horizontal=True)

    if chart_type == "Pie Chart":
        fig = px.pie(
            names=category_summary.index,
            values=category_summary.values,
            title="Expense Distribution",
            template="plotly_dark"
        )
    else:
        fig = px.bar(
            x=category_summary.index,
            y=category_summary.values,
            labels={'x': 'Category', 'y': 'Amount'},
            title="Expenses by Category",
            template="plotly_white",
            color=category_summary.index
        )

    st.plotly_chart(fig, use_container_width=True)

    
    csv = data_to_use.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Filtered Data as CSV",
        data=csv,
        file_name="filtered_expense_data.csv",
        mime="text/csv"
    )

else:
    st.info("Please upload a file or enter data manually to get started.")
data_to_use["Date"] = pd.to_datetime(data_to_use["Date"])
data_to_use["Month"] = data_to_use["Date"].dt.to_period("M").astype(str)
monthly_summary = data_to_use.groupby("Month")["Amount"].sum().reset_index()
monthly_summary = monthly_summary.sort_values("Month")
fig = px.line(
    monthly_summary,
    x="Month",
    y="Amount",
    markers=True,
    title="Monthly Expense Trend",
    labels={"Month": "Month-Year", "Amount": "Total Expense"},
    template="plotly_white"
)
st.plotly_chart(fig, use_container_width=True)





    
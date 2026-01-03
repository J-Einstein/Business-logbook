import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="Business_logbook",
    page_icon="🧾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ================= GLOBAL CSS =================
st.markdown("""
<style>
body {
    background-color: #0f172a;
}
.block-container {
    padding: 2rem 3rem;
}
.card {
    background: rgba(255,255,255,0.05);
    backdrop-filter: blur(12px);
    border-radius: 16px;
    padding: 1.5rem;
    box-shadow: 0 0 40px rgba(0,0,0,0.4);
}
.metric {
    text-align: center;
}
h1, h2, h3 {
    font-weight: 700;
}
button {
    border-radius: 12px !important;
    font-weight: 600 !important;
}
</style>
""", unsafe_allow_html=True)

# ================= DATABASE =================
conn = sqlite3.connect("pos_ledger1.db", check_same_thread=False)
c = conn.cursor()

c.execute("""CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY,
    name TEXT,
    price REAL
)""")

c.execute("""CREATE TABLE IF NOT EXISTS income (
    id INTEGER PRIMARY KEY,
    product_id INTEGER,
    quantity INTEGER,
    date TEXT
)""")

c.execute("""CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY,
    item TEXT,
    amount REAL,
    date TEXT
)""")

conn.commit()

# ================= HELPERS =================
def df_products():
    return pd.read_sql("SELECT * FROM products", conn)

def df_income():
    return pd.read_sql("""
    SELECT i.date, p.name, i.quantity, p.price,
           (i.quantity*p.price) AS total
    FROM income i
    JOIN products p ON p.id = i.product_id
    """, conn)

def df_expenses():
    return pd.read_sql("SELECT * FROM expenses", conn)

def export_excel():
    with pd.ExcelWriter("Business_logbook.xlsx", engine="openpyxl") as writer:
        df_products().to_excel(writer, index=False, sheet_name="Products")
        df_income().to_excel(writer, index=False, sheet_name="Income")
        df_expenses().to_excel(writer, index=False, sheet_name="Expenses")

# ================= SIDEBAR =================
st.sidebar.markdown("## 🧾 Business_logbook")
page = st.sidebar.radio(
    "Navigate",
    ["Dashboard", "Products", "Sales", "Expenses", "Export"]
)

# ================= DASHBOARD =================
if page == "Dashboard":
    st.markdown("## 📊 Business Overview")

    income = df_income()
    expenses = df_expenses()

    total_income = income["total"].sum() if not income.empty else 0
    total_expenses = expenses["amount"].sum() if not expenses.empty else 0
    profit = total_income - total_expenses

    col1, col2, col3 = st.columns(3)
    for col, label, value in zip(
        [col1, col2, col3],
        ["Income", "Expenses", "Profit"],
        [total_income, total_expenses, profit]
    ):
        col.markdown(f"""
        <div class="card metric">
            <h3>{label}</h3>
            <h1>₦{value:,.0f}</h1>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("### 📈 Cashflow Trend")

    if not income.empty or not expenses.empty:
        income["month"] = pd.to_datetime(income["date"]).dt.to_period("M")
        expenses["month"] = pd.to_datetime(expenses["date"]).dt.to_period("M")

        trend = pd.DataFrame({
            "Income": income.groupby("month")["total"].sum(),
            "Expenses": expenses.groupby("month")["amount"].sum()
        }).fillna(0)

        trend["Profit"] = trend["Income"] - trend["Expenses"]

        st.area_chart(trend)

# ================= PRODUCTS =================
elif page == "Products":
    st.markdown("## 🏷 Products & Services")

    col1, col2 = st.columns([1, 2])

    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### ➕ Add Product")

        with st.form("add_product", clear_on_submit=True):
            name = st.text_input("Name")
            price = st.number_input("Price (₦)", min_value=0.0)
            submit = st.form_submit_button("Save")

            if submit and name:
                c.execute("INSERT INTO products VALUES (NULL,?,?)", (name, price))
                conn.commit()
                st.success("Added")
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### 📦 Product List")
        st.dataframe(df_products(), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

# ================= SALES =================
elif page == "Sales":
    st.markdown("## 💰 Quick Sale")

    products = df_products()
    if products.empty:
        st.warning("Add products first")
    else:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        with st.form("sale_form"):
            pid = st.selectbox(
                "Product",
                products["id"],
                format_func=lambda x: products.loc[products.id == x, "name"].values[0]
            )
            qty = st.number_input("Quantity", min_value=1)
            date = st.date_input("Date")

            if st.form_submit_button("Complete Sale"):
                c.execute(
                    "INSERT INTO income VALUES (NULL,?,?,?)",
                    (pid, qty, date.strftime("%Y-%m-%d"))
                )
                conn.commit()
                st.success("Sale recorded")
        st.markdown('</div>', unsafe_allow_html=True)

# ================= EXPENSES =================
elif page == "Expenses":
    st.markdown("## 💸 Expenses")

    col1, col2 = st.columns([1, 2])

    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        with st.form("expense_form", clear_on_submit=True):
            item = st.text_input("Item")
            amount = st.number_input("Amount (₦)", min_value=0.0)
            date = st.date_input("Date")

            if st.form_submit_button("Add Expense") and item:
                c.execute(
                    "INSERT INTO expenses VALUES (NULL,?,?,?)",
                    (item, amount, date.strftime("%Y-%m-%d"))
                )
                conn.commit()
                st.success("Expense saved")
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.dataframe(df_expenses(), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

# ================= EXPORT =================
elif page == "Export":
    st.markdown("## 📤 Export Data")
    export_excel()
    st.success("Business_logbook_Ledger.xlsx updated")

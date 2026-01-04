import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

st.set_page_config(
    page_title="POS Ledger",
    page_icon="🧾",
    layout="wide"
)

# ---------------- DATABASE ----------------
conn = sqlite3.connect("pos_ledger.db", check_same_thread=False)
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

# ---------------- HELPERS ----------------
def df_products():
    return pd.read_sql("SELECT * FROM products", conn)

def df_income():
    return pd.read_sql("""
    SELECT i.id, p.name as product, i.quantity, p.price, (i.quantity*p.price) as total, i.date, i.product_id
    FROM income i
    JOIN products p ON p.id = i.product_id
    """, conn)

def df_expenses():
    return pd.read_sql("SELECT * FROM expenses", conn)

def update_product(row):
    c.execute("UPDATE products SET name=?, price=? WHERE id=?", (row['name'], row['price'], row['id']))
    conn.commit()

def update_income(row):
    c.execute("UPDATE income SET product_id=?, quantity=?, date=? WHERE id=?", (row['product_id'], row['quantity'], row['date'], row['id']))
    conn.commit()

def update_expense(row):
    c.execute("UPDATE expenses SET item=?, amount=?, date=? WHERE id=?", (row['item'], row['amount'], row['date'], row['id']))
    conn.commit()

def export_excel():
    with pd.ExcelWriter("POS_Ledger.xlsx", engine="openpyxl") as writer:
        df_products().to_excel(writer, index=False, sheet_name="Products")
        df_income().to_excel(writer, index=False, sheet_name="Income")
        df_expenses().to_excel(writer, index=False, sheet_name="Expenses")

# ---------------- SIDEBAR ----------------
st.sidebar.title("🧾 POS Ledger")
page = st.sidebar.radio(
    "Navigate",
    ["Dashboard", "Products", "Sales", "Expenses", "Export"]
)

# ================= DASHBOARD =================
if page == "Dashboard":
    st.markdown("## 📊 Business Overview")

    income = df_income()
    expenses = df_expenses()

    # -------- HANDLE EMPTY DATABASE --------
    if income.empty and expenses.empty:
        st.info("No data yet. Start by adding sales or expenses.")
        st.stop()

    # -------- AVAILABLE DATE RANGE --------
    all_dates = []

    if not income.empty:
        all_dates.extend(pd.to_datetime(income["date"]).tolist())

    if not expenses.empty:
        all_dates.extend(pd.to_datetime(expenses["date"]).tolist())

    min_date = min(all_dates).date()
    max_date = max(all_dates).date()

    # -------- DATE FILTER UI --------
    st.markdown("### ⏱ Time Filter")

    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input(
            "From",
            value=min_date,
            min_value=min_date,
            max_value=max_date
        )

    with col2:
        end_date = st.date_input(
            "To",
            value=max_date,
            min_value=min_date,
            max_value=max_date
        )

    # -------- AUTO-CORRECT INVALID RANGE --------
    if start_date > end_date:
        st.warning("Start date was after end date. We adjusted it automatically.")
        start_date = end_date

    # -------- FILTER DATA SAFELY --------
    income["date"] = pd.to_datetime(income["date"])
    expenses["date"] = pd.to_datetime(expenses["date"])

    income_f = income[
        (income["date"].dt.date >= start_date) &
        (income["date"].dt.date <= end_date)
    ]

    expenses_f = expenses[
        (expenses["date"].dt.date >= start_date) &
        (expenses["date"].dt.date <= end_date)
    ]

    # -------- KPIs --------
    total_income = income_f["total"].sum() if not income_f.empty else 0
    total_expenses = expenses_f["amount"].sum() if not expenses_f.empty else 0
    profit = total_income - total_expenses

    col1, col2, col3 = st.columns(3)
    col1.metric("💵 Income", f"₦{total_income:,.0f}")
    col2.metric("🛒 Expenses", f"₦{total_expenses:,.0f}")
    col3.metric("📈 Profit", f"₦{profit:,.0f}")

    # -------- TREND (STOCK-LIKE) --------
    st.markdown("### 📈 Cashflow Trend")

    date_index = pd.period_range(start=start_date, end=end_date, freq="M")

    income_trend = (
        income_f
        .assign(month=lambda x: x["date"].dt.to_period("M"))
        .groupby("month")["total"]
        .sum()
        .reindex(date_index, fill_value=0)
    )

    expense_trend = (
        expenses_f
        .assign(month=lambda x: x["date"].dt.to_period("M"))
        .groupby("month")["amount"]
        .sum()
        .reindex(date_index, fill_value=0)
    )

    trend = pd.DataFrame({
        "Income": income_trend,
        "Expenses": expense_trend,
        "Profit": income_trend - expense_trend
    })

    st.area_chart(trend)

# ================= PRODUCTS =================
elif page == "Products":
    st.markdown("## 🏷 Products & Services")
    with st.form("add_product", clear_on_submit=True):
        name = st.text_input("Name")
        price = st.number_input("Price (₦)", min_value=0.0)
        submit = st.form_submit_button("Add Product")
        if submit and name:
            c.execute("INSERT INTO products VALUES (NULL,?,?)", (name, price))
            conn.commit()
            st.success("✅ Product added")

    st.markdown("### 📝 Edit Products")
    products_df = df_products()
    edited_products = st.data_editor(products_df, num_rows="dynamic")
    if st.button("Save Product Changes"):
        for _, row in edited_products.iterrows():
            update_product(row)
        st.success("✅ Products updated")

# ================= SALES =================
elif page == "Sales":
    st.markdown("## 💰 Quick Sale")
    products = df_products()
    if products.empty:
        st.warning("Add products first")
    else:
        with st.form("sale_form"):
            pid = st.selectbox(
                "Product",
                products["id"],
                format_func=lambda x: products.loc[products.id == x, "name"].values[0]
            )
            qty = st.number_input("Quantity", min_value=1)
            date = st.date_input("Date")
            if st.form_submit_button("Complete Sale"):
                c.execute("INSERT INTO income VALUES (NULL,?,?,?)",
                          (pid, qty, date.strftime("%Y-%m-%d")))
                conn.commit()
                st.success("✅ Sale recorded")

    st.markdown("### 📝 Edit Sales")
    income_df = df_income()
    if not income_df.empty:
        # Make product_id editable but show product name
        income_df_display = income_df.drop(columns="product")
        edited_income = st.data_editor(income_df_display, num_rows="dynamic")
        if st.button("Save Sales Changes"):
            for _, row in edited_income.iterrows():
                update_income(row)
            st.success("✅ Sales updated")

# ================= EXPENSES =================
elif page == "Expenses":
    st.markdown("## 💸 Expenses")
    with st.form("expense_form", clear_on_submit=True):
        item = st.text_input("Item")
        amount = st.number_input("Amount (₦)", min_value=0.0)
        date = st.date_input("Date")
        if st.form_submit_button("Add Expense") and item:
            c.execute("INSERT INTO expenses VALUES (NULL,?,?,?)",
                      (item, amount, date.strftime("%Y-%m-%d")))
            conn.commit()
            st.success("✅ Expense saved")

    st.markdown("### 📝 Edit Expenses")
    expenses_df = df_expenses()
    if not expenses_df.empty:
        edited_expenses = st.data_editor(expenses_df, num_rows="dynamic")
        if st.button("Save Expense Changes"):
            for _, row in edited_expenses.iterrows():
                update_expense(row)
            st.success("✅ Expenses updated")

# ================= EXPORT =================
elif page == "Export":
    st.markdown("## 📤 Export Data")
    export_excel()
    st.success("✅ POS_Ledger.xlsx updated")

# 🧾 POS Ledger – Lightweight Business POS & Ledger

A modern, lightweight **Point of Sale (POS) and business ledger** built with **Streamlit**.  
Designed for small businesses to track **products, sales, expenses, and profit** with a clean dashboard and Excel export.

---

## ✨ Features

- 🏷 Add products & services with pricing  
- 💰 Record sales (income)  
- 💸 Track business expenses  
- 📊 POS-style dashboard with KPIs  
- 📈 Stock-like cashflow trend graph  
- 📤 Export all data to Excel (auto overwrite)  
- 🧾 SQLite database (local & lightweight)  
- 🎨 Modern POS-inspired UI  

---

## 🛠 Tech Stack

- Python  
- Streamlit  
- SQLite  
- Pandas  
- OpenPyXL  

---

## 📁 Project Structure

```text
pos-ledger/
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
```

---

## 🚀 How to Run Locally

### 1️⃣ Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/pos-ledger.git
cd pos-ledger
```

### 2️⃣ Install dependencies
```bash
pip install -r requirements.txt
```

### 3️⃣ Run the application
```bash
streamlit run app.py
```

The application will open automatically in your browser.

---

## 📤 Excel Export

- Exports **Products**, **Income**, and **Expenses**
- File name: `POS_Ledger.xlsx`
- Automatically overwrites the previous file

---

## 🧠 Use Cases

- Small businesses  
- Freelancers  
- Service providers  
- Students learning POS systems  
- Portfolio projects  

---

## 🔒 Notes

- Local-first application  
- No internet connection required  
- Authentication not included (can be added later)

---

## 📌 Future Improvements

- User authentication & roles  
- Receipt printing  
- Barcode scanning  
- Cloud deployment  
- Mobile POS layout  
- Dark / Light mode toggle  

---

## 📄 License

This project is open-source and free to use.

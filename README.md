# 💊 Pharmasync
PharmaSync – Synchronizing medicines between pharmacy and patients.
  Flask + Streamlit app for synchronizing pharmacy inventory and patient prescription subscriptions.

    
---

## 🚀 Features

### 🏥 Pharmacy Access
- View all medicines, patients, subscription periods, and dates  
- See inventory color-coded as:  
  🟢 Green → In stock  
  🟡 Yellow → Low stock  
  🔴 Red → Out of stock  

### 👩‍⚕️ Customer Access
- View registered pharmacies  
- Search medicine by name and see which pharmacies have it in stock  

---

## ⚙️ Setup Instructions

### 1️⃣ Install dependencies
```bash
pip install flask pymongo streamlit
```

### 2️⃣ Run MongoDB locally
Default connection:  
```
mongodb://localhost:27017
```

### 3️⃣ Update Database URL
In both `app.py` and `dashboard.py`, update this line if needed:
```python
MONGO_URL = "mongodb://localhost:27017"
```

### 4️⃣ Populate MongoDB
Run these in your mongo shell:
```js
use pharmasync;

db.pharmacies.insertMany([
  { 
    name: "GreenCare Pharmacy", 
    address: "12 MG Road, Bengaluru", 
    inventory: [
      { medicine: "Paracetamol", stock: 50 },
      { medicine: "Amoxicillin", stock: 5 },
      { medicine: "Cough Syrup", stock: 0 }
    ]
  },
  {
    name: "HealthPlus Store", 
    address: "88 Park Street, Kolkata", 
    inventory: [
      { medicine: "Paracetamol", stock: 20 },
      { medicine: "Vitamin C", stock: 100 }
    ]
  }
]);

db.customers.insertMany([
  { 
    name: "Alice Sharma", 
    age: 30, 
    subscriptions: [
      { medicine: "Paracetamol", pharmacy: "GreenCare Pharmacy", days_remaining: 10, period: "30 days" }
    ]
  },
  {
    name: "Rohan Das", 
    age: 45, 
    subscriptions: [
      { medicine: "Vitamin C", pharmacy: "HealthPlus Store", days_remaining: 5, period: "15 days" }
    ]
  }
]);

db.pharmacies.createIndex({ "inventory.medicine": 1 });
```

### 5️⃣ Run Servers
**Flask Backend**
```bash
python app.py
```

**Streamlit Frontend**
```bash
streamlit run dashboard.py
```

---

✨ Built with Python, Flask, Streamlit, and MongoDB

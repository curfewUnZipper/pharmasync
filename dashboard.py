import streamlit as st
import requests

API_BASE = st.secrets["backend"]["uri"]

st.set_page_config(page_title="Pharmasync", layout="wide")
st.title("💊 Pharmasync Portal")

role = st.sidebar.selectbox("Login as", ["Pharmacy", "Customer"])

# -----------------------
# PHARMACY VIEW
# -----------------------
if role == "Pharmacy":
    st.header("🏥 Pharmacy Dashboard")
    data = requests.get(f"{API_BASE}/pharmacies").json()

    for p in data:
        st.markdown(f"### {p['name']} - {p['address']}")
        cols = st.columns(3)
        for idx, med in enumerate(p["inventory"]):
            stock = med["stock"]
            if stock == 0:
                color = "🔴"
            elif stock < 10:
                color = "🟡"
            else:
                color = "🟢"
            cols[idx % 3].write(f"{color} {med['medicine']} — {stock}")

# -----------------------
# CUSTOMER VIEW
# -----------------------
elif role == "Customer":
    st.header("👩‍⚕️ Customer Dashboard")
    st.subheader("Search Medicine Availability")

    try:
        all_medicines = requests.get(f"{API_BASE}/medicines").json()
    except:
        st.error("❌ Could not load medicines. Check Flask server.")
        all_medicines = []

    medicine = st.selectbox("Select a medicine", all_medicines)

    if st.button("Search"):
        res = requests.post(f"{API_BASE}/search", json={"medicine": medicine}).json()
        if res:
            for r in res:
                st.success(f"🏥 {r['pharmacy']} — Stock: {r['stock']} | 📍 {r['address']}")
        else:
            st.warning("No pharmacies have this medicine in stock.")

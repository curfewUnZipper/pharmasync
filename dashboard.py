import streamlit as st
import requests
import pandas as pd

# -----------------------
# CONFIG
# -----------------------
API_BASE = st.secrets["backend"]["uri"]
st.set_page_config(page_title="💊 Pharmasync", layout="wide")

st.markdown("""
    <h1 style='text-align: center; margin-bottom: 20px;'>💊 Pharmasync</h1>
    <p style='text-align: center; color: gray;'>Synchronizing Medicines between Pharmacy and Patients</p>
""", unsafe_allow_html=True)

# -----------------------
# TAB NAVIGATION
# -----------------------
tab1, tab2, tab3 = st.tabs(["Pharmacy", "Patient", "📊 Overview"])

# ============================================================
# PHARMACY TAB
# ============================================================
with tab1:
    st.header("Pharmacy Dashboard")

    try:
        all_pharmacies = [p["name"] for p in requests.get(f"{API_BASE}/pharmacies").json()]
    except:
        st.error("Could not load pharmacy list.")
        st.stop()

    selected_pharmacy = st.selectbox("Select a Pharmacy", all_pharmacies)

    if selected_pharmacy:
        # Fetch details for the selected pharmacy
        details = requests.get(f"{API_BASE}/pharmacy/{selected_pharmacy}").json()
        st.subheader(f"{details['name']} — {details['address']}")

        # Prepare a combined display + editable table
        med_data = []
        for med in details["inventory"]:
            stock = med["stock"]
            subs = med.get("subscriptions", 0)

            if stock == 0:
                color = "🔴"
                status = "Out of Stock"
            elif stock < subs:
                color = "🟡"
                status = f"Low ({stock} < {subs})"
            else:
                color = "🟢"
                status = "Sufficient"

            med_data.append({
                "Medicine": med["medicine"],
                "Current Stock": stock,
                "Subscriptions": subs,
                "Status": f"{color} {status}",
                "Updated Stock": stock  # editable column
            })

        import pandas as pd
        df = pd.DataFrame(med_data)

        # Editable, color-coded stock table
        st.markdown("### Manage Medicine Stock")
        st.info("Edit the 'Updated Stock' values directly below and click **Save Changes**.", icon="💡")

        edited_df = st.data_editor(
            df,
            hide_index=True,
            num_rows="fixed",
            column_config={
                "Medicine": st.column_config.Column(disabled=True),
                "Current Stock": st.column_config.NumberColumn(disabled=True),
                "Subscriptions": st.column_config.NumberColumn(disabled=True),
                "Status": st.column_config.TextColumn(disabled=True),
                "Updated Stock": st.column_config.NumberColumn(help="Enter new stock quantity"),
            },
            use_container_width=True
        )

        # Centered update button
        st.markdown("<div style='text-align:center; margin-top:1rem;'>", unsafe_allow_html=True)
        update_btn = st.button("Save Changes", type="primary")
        st.markdown("</div>", unsafe_allow_html=True)

        # Handle update logic
        if update_btn:
            updates = []
            for i, row in edited_df.iterrows():
                if row["Updated Stock"] != row["Current Stock"]:
                    updates.append({
                        "pharmacy": selected_pharmacy,
                        "medicine": row["Medicine"],
                        "stock": int(row["Updated Stock"])
                    })

            if updates:
                try:
                    for payload in updates:
                        res = requests.post(f"{API_BASE}/update_stock", json=payload)
                        if res.status_code != 200:
                            st.error(f"❌ Failed to update {payload['medicine']}")
                            break
                    else:
                        st.success(f"✅ Updated stock for {len(updates)} medicines successfully!")
                        st.rerun()
                except Exception as e:
                    st.error(f"⚠️ Error: {e}")
            else:
                st.info("No changes made.")


# ============================================================
# Patient TAB
# ============================================================
with tab2:
    st.header("Patient Dashboard")
    st.subheader("Search Medicine Availability")

    try:
        all_medicines = requests.get(f"{API_BASE}/medicines").json()
    except:
        st.error("Could not load medicines. Check Flask server.")
        all_medicines = []

    medicine = st.selectbox("Select a medicine", all_medicines)

    if st.button("Search"):
        res = requests.post(f"{API_BASE}/search", json={"medicine": medicine}).json()
        if res:
            for r in res:
                st.success(f"{r['pharmacy']} — Stock: {r['stock']} | {r['address']}")
        else:
            st.warning("No pharmacies currently have this medicine in stock.")

# ============================================================
# OVERVIEW TAB
# ============================================================
with tab3:
    st.header("System Overview")
    st.subheader("Global Stock Summary Across All Pharmacies")

    try:
        pharmacies = requests.get(f"{API_BASE}/pharmacies").json()
    except:
        st.error("Could not load pharmacies. Check Flask server.")
        st.stop()

    # --- Build a global medicine-level stock summary ---
    stock_summary = {}
    for p in pharmacies:
        for item in p["inventory"]:
            med = item["medicine"]
            stock_summary.setdefault(med, 0)
            stock_summary[med] += item["stock"]

    df = pd.DataFrame([
        {"Medicine": med, "Total Stock": stock}
        for med, stock in stock_summary.items()
    ]).sort_values("Medicine")

    st.dataframe(df, use_container_width=True)

    st.divider()
    st.subheader("Pharmacy-wise Detailed Stocks")

    for p in pharmacies:
        st.markdown(f"### {p['name']} — {p['address']}")
        cols = st.columns(3)

        for idx, med in enumerate(p["inventory"]):
            stock = med["stock"]
            subs = med.get("subscriptions", 0)

            if stock == 0:
                color = "🔴"
                status = "Out of Stock"
            elif stock < subs:
                color = "🟡"
                status = f"Low ({stock} < {subs} subs)"
            else:
                color = "🟢"
                status = "Sufficient"

            cols[idx % 3].write(f"{color} {med['medicine']} — {stock} | {status}")
        st.divider()

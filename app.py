import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Workshop OS", page_icon="🪚", layout="wide")
st.title("🪚 ets Studio | Workshop OS")

# --- INITIALIZE DATA FILES ---
# This block creates your starting data the first time the app runs
if not os.path.exists("equipment.csv"):
    pd.DataFrame({
        "ID": ["MAC-01", "MAC-02", "HND-01", "SHP-01"],
        "Category": ["Table Saw", "Table Saw", "Hand Plane", "Sharpening"],
        "Name": ["SawStop 3HP", "Makita MLT100", "Soba #62 Low-Angle", "Atoma 400 Diamond"],
        "Role": ["Solid wood joinery", "Laminates & breakdown", "End-grain shooting", "Flattening & grinding"],
    }).to_csv("equipment.csv", index=False)

if not os.path.exists("consumables.csv"):
    pd.DataFrame({
        "Machine_ID": ["MAC-01", "MAC-02", "HND-01", "SHP-01"],
        "Item": ["Dimar 254x3.2 24T Rip", "Makita D-46408 60T", "Hock 2-inch A2 Iron", "Atoma #400 Sheet"],
        "Stock": [1, 1, 1, 0],
        "Threshold": [1, 1, 1, 1],
    }).to_csv("consumables.csv", index=False)

if not os.path.exists("maintenance.csv"):
    pd.DataFrame({
        "Machine_ID": ["MAC-01", "MAC-02", "TRL-01"],
        "Task": ["Wax Cast Iron & Check Belt", "Check Motor Brushes", "Check Nissenboim Trailer Hitch"],
        "Freq_Days": [30, 90, 14],
        "Last_Serviced": ["2026-07-15", "2026-06-01", "2026-07-20"],
    }).to_csv("maintenance.csv", index=False)

# --- LOAD DATA ---
def load_data(file):
    return pd.read_csv(file)

def save_data(df, file):
    df.to_csv(file, index=False)

eq_df = load_data("equipment.csv")
cons_df = load_data("consumables.csv")
maint_df = load_data("maintenance.csv")

# --- TABS NAVIGATION ---
tab1, tab2, tab3, tab4 = st.tabs(["🚨 Dashboard", "🗜️ Equipment Master", "📦 Consumables", "🔧 Maintenance"])

# --- TAB 1: DASHBOARD (ALERTS) ---
with tab1:
    st.header("Action Hub")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("⚠️ Low Stock Alerts")
        low_stock = cons_df[cons_df['Stock'] <= cons_df['Threshold']]
        if low_stock.empty:
            st.success("All consumables are sufficiently stocked.")
        else:
            st.error(f"You have {len(low_stock)} items at or below reorder threshold.")
            st.dataframe(low_stock[['Machine_ID', 'Item', 'Stock', 'Threshold']], hide_index=True, use_container_width=True)

    with col2:
        st.subheader("⏰ Maintenance Overdue")
        # Calculate next due dates
        maint_df['Last_Serviced'] = pd.to_datetime(maint_df['Last_Serviced'], errors='coerce')
        maint_df['Next_Due'] = maint_df['Last_Serviced'] + pd.to_timedelta(maint_df['Freq_Days'], unit='D')
        
        today = pd.to_datetime(datetime.today().date())
        overdue = maint_df[maint_df['Next_Due'] < today].copy()
        
        if overdue.empty:
            st.success("All machinery maintenance is up to date.")
        else:
            st.warning(f"You have {len(overdue)} overdue tasks.")
            overdue['Next_Due'] = overdue['Next_Due'].dt.strftime('%Y-%m-%d')
            st.dataframe(overdue[['Machine_ID', 'Task', 'Next_Due']], hide_index=True, use_container_width=True)

# --- TAB 2: EQUIPMENT MASTER ---
with tab2:
    st.header("Equipment & Machinery")
    st.write("Add, edit, or delete machinery. Changes save automatically.")
    edited_eq = st.data_editor(eq_df, num_rows="dynamic", use_container_width=True, key="eq_edit")
    if not edited_eq.equals(eq_df):
        save_data(edited_eq, "equipment.csv")
        st.rerun()

# --- TAB 3: CONSUMABLES ---
with tab3:
    st.header("Tooling & Consumables")
    st.write("Track blades, abrasives, and irons. Update stock quantities here to trigger dashboard alerts.")
    edited_cons = st.data_editor(cons_df, num_rows="dynamic", use_container_width=True, key="cons_edit")
    if not edited_cons.equals(cons_df):
        save_data(edited_cons, "consumables.csv")
        st.rerun()

# --- TAB 4: MAINTENANCE ---
with tab4:
    st.header("Maintenance Schedule")
    st.write("Update the 'Last Serviced' date (YYYY-MM-DD) when a task is completed.")
    
    # Format dates back to strings for clean editing
    maint_display = maint_df.copy()
    maint_display['Last_Serviced'] = maint_display['Last_Serviced'].dt.strftime('%Y-%m-%d')
    maint_display = maint_display.drop(columns=['Next_Due'], errors='ignore')
    
    edited_maint = st.data_editor(maint_display, num_rows="dynamic", use_container_width=True, key="maint_edit")
    if not edited_maint.equals(maint_display):
        save_data(edited_maint, "maintenance.csv")
        st.rerun()
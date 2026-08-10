import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- PAGE CONFIGURATION & BILINGUAL SETUP ---
st.set_page_config(page_title="Grannies' Garage OS", page_icon="🪚", layout="wide")

# Sidebar Language Toggle
st.sidebar.title("🌐 Language / שפה")
lang_choice = st.sidebar.radio("", ["English", "עברית"])
lang = "en" if lang_choice == "English" else "he"

# Dictionary for bilingual text
t = {
    "en": {
        "title": "🪚 ets Studio | Workshop OS",
        "tabs": ["🚨 Dashboard", "🗜️ Equipment Master", "📐 Jigs & Modes", "📦 Consumables", "🔧 Maintenance"],
        "dash_action": "Action Hub",
        "dash_low_stock": "⚠️ Low Stock Alerts",
        "dash_maint": "⏰ Maintenance Overdue",
        "all_good": "Everything is running smoothly.",
        "jigs_desc": "Track dedicated jigs, sleds, and machine configurations.",
        "equip_desc": "Add, edit, or delete machinery. 'Est Value' is safely hidden from public view.",
        "cons_desc": "Track blades, abrasives, and irons. Update stock quantities to trigger dashboard alerts.",
        "maint_desc": "Update the 'Last Serviced' date (YYYY-MM-DD) when a task is completed.",
    },
    "he": {
        "title": "🪚 סטודיו ets | מערכת ניהול סדנא",
        "tabs": ["🚨 לוח בקרה", "🗜️ מצבת ציוד", "📐 ג'יגים וכיוונים", "📦 מלאי מתכלה", "🔧 תחזוקה"],
        "dash_action": "מרכז פעולות",
        "dash_low_stock": "⚠️ התראות מלאי נמוך",
        "dash_maint": "⏰ תחזוקה בפיגור",
        "all_good": "הכל מתנהל כשורה.",
        "jigs_desc": "מעקב אחר ג'יגים ייעודיים, מזחלות ותצורות מכונה.",
        "equip_desc": "ניהול הציוד. עמודת 'הערכת שווי' מוסתרת מהתצוגה הציבורית.",
        "cons_desc": "מעקב אחר להבים, ניירות לטש ועוד. עדכון הכמות יקפיץ התראה בלוח הבקרה.",
        "maint_desc": "יש לעדכן את תאריך 'טיפול אחרון' (YYYY-MM-DD) עם סיום המשימה.",
    }
}

st.title(t[lang]["title"])

# --- DATA INITIALIZATION & MIGRATION ---
# Equipment
if not os.path.exists("equipment.csv"):
    pd.DataFrame({
        "ID": ["MAC-01", "MAC-02"],
        "Category": ["Table Saw", "Table Saw"],
        "Name": ["SawStop 3HP", "Makita MLT100"],
        "Role": ["Solid wood joinery", "Laminates & breakdown"],
        "Manual_Link": ["", ""],
        "Product_Link": ["", ""],
        "Grade": ["S", "B"],
        "Est_Value": [4500, 1500]
    }).to_csv("equipment.csv", index=False)

# Consumables
if not os.path.exists("consumables.csv"):
    pd.DataFrame({
        "Machine_ID": ["MAC-01", "MAC-02"],
        "Item": ["Dimar 254x3.2 24T Rip", "Makita D-46408 60T"],
        "Stock": [1, 1],
        "Threshold": [1, 1],
        "PPU": [350.0, 490.0],
        "Grade": ["A", "C"]
    }).to_csv("consumables.csv", index=False)

# Jigs
if not os.path.exists("jigs.csv"):
    pd.DataFrame({
        "Machine_ID": ["MAC-01", "MAC-01", "MAC-02"],
        "Jig_Name": ["Crosscut Sled", "Tenoning Jig", "Tapering Jig"],
        "Mode_Config": ["Standard 90 deg", "Vertical lock", "Variable angle"],
        "Storage_Location": ["Wall Rack A", "Shelf 2", "Under MLT100"]
    }).to_csv("jigs.csv", index=False)

# Maintenance
if not os.path.exists("maintenance.csv"):
    pd.DataFrame({
        "Machine_ID": ["MAC-01", "MAC-02"],
        "Task": ["Wax Cast Iron & Check Belt", "Check Motor Brushes"],
        "Freq_Days": [30, 90],
        "Last_Serviced": ["2026-07-15", "2026-06-01"],
    }).to_csv("maintenance.csv", index=False)

# Load data and ensure new columns exist for older CSV files
def load_data(file): return pd.read_csv(file)
def save_data(df, file): df.to_csv(file, index=False)

eq_df = load_data("equipment.csv")
if 'Manual_Link' not in eq_df.columns: eq_df[['Manual_Link', 'Product_Link', 'Grade', 'Est_Value']] = ["", "", "C", 0.0]

cons_df = load_data("consumables.csv")
if 'PPU' not in cons_df.columns: cons_df[['PPU', 'Grade']] = [0.0, "C"]

jigs_df = load_data("jigs.csv")
maint_df = load_data("maintenance.csv")

# --- TABS ---
tabs = st.tabs(t[lang]["tabs"])

# --- TAB 1: VISUAL DASHBOARD ---
with tabs[0]:
    st.header(t[lang]["dash_action"])
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader(t[lang]["dash_low_stock"])
        low_stock = cons_df[cons_df['Stock'] <= cons_df['Threshold']]
        if low_stock.empty:
            st.success(f"✅ {t[lang]['all_good']}")
        else:
            st.metric(label="Items to Order", value=len(low_stock))
            for _, row in low_stock.iterrows():
                st.error(f"**{row['Item']}** — Stock: {row['Stock']} (Min: {row['Threshold']})")

    with col2:
        st.subheader(t[lang]["dash_maint"])
        maint_df['Last_Serviced'] = pd.to_datetime(maint_df['Last_Serviced'], errors='coerce')
        maint_df['Next_Due'] = maint_df['Last_Serviced'] + pd.to_timedelta(maint_df['Freq_Days'], unit='D')
        today = pd.to_datetime(datetime.today().date())
        overdue = maint_df[maint_df['Next_Due'] < today]
        
        if overdue.empty:
            st.success(f"✅ {t[lang]['all_good']}")
        else:
            st.metric(label="Tasks Overdue", value=len(overdue))
            for _, row in overdue.iterrows():
                st.warning(f"🔧 **{row['Task']}** ({row['Machine_ID']}) — Due: {row['Next_Due'].strftime('%Y-%m-%d')}")

# --- TAB 2: EQUIPMENT MASTER ---
with tabs[1]:
    st.write(t[lang]["equip_desc"])
    edited_eq = st.data_editor(
        eq_df,
        num_rows="dynamic",
        use_container_width=True,
        column_config={
            "Manual_Link": st.column_config.LinkColumn("Manual URL"),
            "Product_Link": st.column_config.LinkColumn("Product URL"),
            "Grade": st.column_config.SelectboxColumn("Grade", options=["S", "A", "B", "C", "D", "E", "F"]),
            "Est_Value": None # This HIDES the column completely from the web UI
        },
        key="eq_edit"
    )
    if not edited_eq.equals(eq_df):
        save_data(edited_eq, "equipment.csv")
        st.rerun()

# --- TAB 3: JIGS & MODES ---
with tabs[2]:
    st.write(t[lang]["jigs_desc"])
    edited_jigs = st.data_editor(
        jigs_df,
        num_rows="dynamic",
        use_container_width=True,
        key="jigs_edit"
    )
    if not edited_jigs.equals(jigs_df):
        save_data(edited_jigs, "jigs.csv")
        st.rerun()

# --- TAB 4: CONSUMABLES ---
with tabs[3]:
    st.write(t[lang]["cons_desc"])
    edited_cons = st.data_editor(
        cons_df,
        num_rows="dynamic",
        use_container_width=True,
        column_config={
            "PPU": st.column_config.NumberColumn("Price/Unit (₪)", format="₪%.2f"),
            "Grade": st.column_config.SelectboxColumn("Grade", options=["S", "A", "B", "C", "D", "E", "F"])
        },
        key="cons_edit"
    )
    if not edited_cons.equals(cons_df):
        save_data(edited_cons, "consumables.csv")
        st.rerun()

# --- TAB 5: MAINTENANCE ---
with tabs[4]:
    st.write(t[lang]["maint_desc"])
    maint_display = maint_df.copy()
    maint_display['Last_Serviced'] = maint_display['Last_Serviced'].dt.strftime('%Y-%m-%d')
    maint_display = maint_display.drop(columns=['Next_Due'], errors='ignore')
    
    edited_maint = st.data_editor(
        maint_display,
        num_rows="dynamic",
        use_container_width=True,
        key="maint_edit"
    )
    if not edited_maint.equals(maint_display):
        save_data(edited_maint, "maintenance.csv")
        st.rerun()

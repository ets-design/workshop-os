import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Grannies' Garage OS", page_icon="🪚", layout="wide")

# --- SESSION STATE FOR NAVIGATION ---
if 'current_page' not in st.session_state:
    st.session_state.current_page = "Homepage"

def navigate_to(page_name):
    st.session_state.current_page = page_name

# --- BILINGUAL DICTIONARY (Native Hebrew Context) ---
st.sidebar.title("🌐 שפה / Language")
lang_choice = st.sidebar.radio("", ["עברית", "English"])
lang = "he" if lang_choice == "עברית" else "en"

t = {
    "en": {
        "title": "🪚 ets Studio | Workshop OS",
        "nav_home": "🏠 Homepage",
        "nav_equip": "🗜️ Equipment Master",
        "nav_jigs": "📐 Jigs & Modes",
        "nav_cons": "📦 Consumables",
        "nav_maint": "🔧 Maintenance",
        "dash_low_stock": "⚠️ Low Stock Alerts",
        "dash_maint": "⏰ Overdue Maintenance",
        "all_good_stock": "Stock levels are good.",
        "all_good_maint": "All machinery is up to date.",
        "btn_fix_stock": "Update Stock ➔",
        "btn_mark_done": "Mark Done ✓",
        "col_mach_id": "Machine ID",
        "col_cat": "Category",
        "col_name": "Name & Model",
        "col_grade": "Grade",
        "col_stock": "Current Stock",
        "col_thresh": "Reorder Threshold",
        "col_ppu": "Price/Unit (₪)",
        "col_freq": "Frequency (Days)",
        "col_last_serv": "Last Serviced",
    },
    "he": {
        "title": "🪚 סטודיו ets | מערכת ניהול סדנא",
        "nav_home": "🏠 חפ״ק סדנא (מסך הבית)",
        "nav_equip": "🗜️ מצבת ציוד ומכונות",
        "nav_jigs": "📐 עזרים, ג'יגים ותצורות",
        "nav_cons": "📦 חומרים מתכלים ומלאי",
        "nav_maint": "🔧 שגרת טיפולים ותחזוקה",
        "dash_low_stock": "⚠️ התראות חוסר במלאי",
        "dash_maint": "⏰ טיפולי תחזוקה בפיגור",
        "all_good_stock": "הכל מתקתק. אין חוסרים במלאי.",
        "all_good_maint": "כל המכונות מתוחזקות ומוכנות לעבודה.",
        "btn_fix_stock": "לעדכון המלאי ➔",
        "btn_mark_done": "סומן כבוצע ✓",
        "col_mach_id": "קוד מכונה",
        "col_cat": "קטגוריה",
        "col_name": "שם/דגם",
        "col_grade": "דירוג איכות",
        "col_stock": "כמות במלאי",
        "col_thresh": "סף מינימום להזמנה",
        "col_ppu": "מחיר יחידה (₪)",
        "col_freq": "תדירות טיפול (בימים)",
        "col_last_serv": "תאריך טיפול אחרון",
    }
}

# --- NAVIGATION SIDEBAR ---
st.sidebar.markdown("---")
if st.sidebar.button(t[lang]["nav_home"], use_container_width=True): navigate_to("Homepage")
if st.sidebar.button(t[lang]["nav_equip"], use_container_width=True): navigate_to("Equipment")
if st.sidebar.button(t[lang]["nav_jigs"], use_container_width=True): navigate_to("Jigs")
if st.sidebar.button(t[lang]["nav_cons"], use_container_width=True): navigate_to("Consumables")
if st.sidebar.button(t[lang]["nav_maint"], use_container_width=True): navigate_to("Maintenance")
st.sidebar.markdown("---")

st.title(t[lang]["title"])

# --- DATA INITIALIZATION (Bilingual Support) ---
if not os.path.exists("equipment.csv"):
    pd.DataFrame({
        "ID": ["MAC-01", "MAC-02", "SHP-01"],
        "Category": ["Table Saw", "Table Saw", "Sharpening"],
        "Name": ["SawStop 3HP", "Makita MLT100", "Atoma 400 Diamond"],
        "Role_EN": ["Solid wood joinery", "Laminates & breakdown", "Flattening & grinding"],
        "Role_HE": ["עבודות עץ מלא ומחברים", "פירוק לוחות פורמייקה ואלומיניום", "הורדת חומר ויישור אבנים"],
        "Manual_Link": ["", "", ""],
        "Product_Link": ["", "", ""],
        "Grade": ["S", "B", "S"],
        "Est_Value": [4500, 1500, 120]
    }).to_csv("equipment.csv", index=False)

if not os.path.exists("consumables.csv"):
    pd.DataFrame({
        "Machine_ID": ["MAC-01", "MAC-02", "SHP-01"],
        "Item_EN": ["Dimar 254x3.2 24T Rip", "Makita D-46408 60T", "Atoma #400 Sheet"],
        "Item_HE": ["להב דימר 24T עץ מלא", "להב מקיטה 60T דק", "טופס יהלום אטומה 400"],
        "Stock": [1, 1, 0],
        "Threshold": [1, 1, 1],
        "PPU": [350.0, 490.0, 300.0],
        "Grade": ["A", "C", "S"]
    }).to_csv("consumables.csv", index=False)

if not os.path.exists("jigs.csv"):
    pd.DataFrame({
        "Machine_ID": ["MAC-01", "MAC-02"],
        "Jig_Name_EN": ["Crosscut Sled", "Tapering Jig"],
        "Jig_Name_HE": ["מזחלת חיתוך (קרוסקאט)", "ג'יג חיתוך זוויות"],
        "Mode_Config_EN": ["Standard 90 deg", "Variable angle"],
        "Mode_Config_HE": ["90 מעלות סטנדרטי", "זווית משתנה"],
        "Storage_EN": ["Wall Rack A", "Under MLT100"],
        "Storage_HE": ["קיר תלייה א'", "מתחת למקיטה"]
    }).to_csv("jigs.csv", index=False)

if not os.path.exists("maintenance.csv"):
    pd.DataFrame({
        "Machine_ID": ["MAC-01", "MAC-02"],
        "Task_EN": ["Wax Cast Iron & Check Belt", "Check Motor Brushes"],
        "Task_HE": ["שימון משטח יציקה ובדיקת רצועה", "בדיקת פחמים במנוע"],
        "Freq_Days": [30, 90],
        "Last_Serviced": ["2026-07-15", "2026-06-01"],
    }).to_csv("maintenance.csv", index=False)

def load_data(file): return pd.read_csv(file)
def save_data(df, file): df.to_csv(file, index=False)

eq_df = load_data("equipment.csv")
cons_df = load_data("consumables.csv")
jigs_df = load_data("jigs.csv")
maint_df = load_data("maintenance.csv")

# Identify preferred language column suffix
L = "_HE" if lang == "he" else "_EN"

# --- PAGE: HOMEPAGE (DASHBOARD) ---
if st.session_state.current_page == "Homepage":
    st.header(t[lang]["nav_home"])
    col1, col2 = st.columns(2)
    
    # Low Stock Block
    with col1:
        st.subheader(t[lang]["dash_low_stock"])
        low_stock = cons_df[cons_df['Stock'] <= cons_df['Threshold']]
        if low_stock.empty:
            st.success(f"✅ {t[lang]['all_good_stock']}")
        else:
            for _, row in low_stock.iterrows():
                st.error(f"📦 **{row[f'Item{L}']}** | {t[lang]['col_stock']}: **{row['Stock']}** / {row['Threshold']}")
            if st.button(t[lang]["btn_fix_stock"]):
                navigate_to("Consumables")
                st.rerun()

    # Overdue Maintenance Block
    with col2:
        st.subheader(t[lang]["dash_maint"])
        maint_df['Last_Serviced'] = pd.to_datetime(maint_df['Last_Serviced'], errors='coerce')
        maint_df['Next_Due'] = maint_df['Last_Serviced'] + pd.to_timedelta(maint_df['Freq_Days'], unit='D')
        today = pd.to_datetime(datetime.today().date())
        overdue = maint_df[maint_df['Next_Due'] < today]
        
        if overdue.empty:
            st.success(f"✅ {t[lang]['all_good_maint']}")
        else:
            for idx, row in overdue.iterrows():
                c_text, c_btn = st.columns([3, 1])
                with c_text:
                    st.warning(f"🔧 **{row[f'Task{L}']}** ({row['Machine_ID']})")
                with c_btn:
                    if st.button(t[lang]["btn_mark_done"], key=f"done_{idx}"):
                        maint_df.at[idx, 'Last_Serviced'] = datetime.today().strftime('%Y-%m-%d')
                        save_data(maint_df.drop(columns=['Next_Due']), "maintenance.csv")
                        st.rerun()

# --- PAGE: EQUIPMENT MASTER ---
elif st.session_state.current_page == "Equipment":
    st.header(t[lang]["nav_equip"])
    edited_eq = st.data_editor(
        eq_df, num_rows="dynamic", use_container_width=True,
        column_config={
            "ID": st.column_config.TextColumn(t[lang]["col_mach_id"]),
            "Category": st.column_config.TextColumn(t[lang]["col_cat"]),
            "Name": st.column_config.TextColumn(t[lang]["col_name"]),
            "Role_EN": st.column_config.TextColumn("Role (English)"),
            "Role_HE": st.column_config.TextColumn("ייעוד (עברית)"),
            "Manual_Link": st.column_config.LinkColumn("Manual URL"),
            "Product_Link": st.column_config.LinkColumn("Product URL"),
            "Grade": st.column_config.SelectboxColumn(t[lang]["col_grade"], options=["S", "A", "B", "C", "D", "E", "F"]),
            "Est_Value": None # Hidden
        }
    )
    if not edited_eq.equals(eq_df):
        save_data(edited_eq, "equipment.csv")
        st.rerun()

# --- PAGE: JIGS & MODES ---
elif st.session_state.current_page == "Jigs":
    st.header(t[lang]["nav_jigs"])
    edited_jigs = st.data_editor(
        jigs_df, num_rows="dynamic", use_container_width=True,
        column_config={
            "Machine_ID": st.column_config.TextColumn(t[lang]["col_mach_id"]),
            "Jig_Name_EN": st.column_config.TextColumn("Jig Name (English)"),
            "Jig_Name_HE": st.column_config.TextColumn("שם ג'יג (עברית)"),
            "Mode_Config_EN": st.column_config.TextColumn("Configuration (English)"),
            "Mode_Config_HE": st.column_config.TextColumn("תצורה (עברית)"),
            "Storage_EN": st.column_config.TextColumn("Storage (English)"),
            "Storage_HE": st.column_config.TextColumn("מיקום (עברית)"),
        }
    )
    if not edited_jigs.equals(jigs_df):
        save_data(edited_jigs, "jigs.csv")
        st.rerun()

# --- PAGE: CONSUMABLES ---
elif st.session_state.current_page == "Consumables":
    st.header(t[lang]["nav_cons"])
    edited_cons = st.data_editor(
        cons_df, num_rows="dynamic", use_container_width=True,
        column_config={
            "Machine_ID": st.column_config.TextColumn(t[lang]["col_mach_id"]),
            "Item_EN": st.column_config.TextColumn("Item Name (English)"),
            "Item_HE": st.column_config.TextColumn("שם פריט (עברית)"),
            "Stock": st.column_config.NumberColumn(t[lang]["col_stock"]),
            "Threshold": st.column_config.NumberColumn(t[lang]["col_thresh"]),
            "PPU": st.column_config.NumberColumn(t[lang]["col_ppu"], format="₪%.2f"),
            "Grade": st.column_config.SelectboxColumn(t[lang]["col_grade"], options=["S", "A", "B", "C", "D", "E", "F"])
        }
    )
    if not edited_cons.equals(cons_df):
        save_data(edited_cons, "consumables.csv")
        st.rerun()

# --- PAGE: MAINTENANCE ---
elif st.session_state.current_page == "Maintenance":
    st.header(t[lang]["nav_maint"])
    maint_display = maint_df.copy()
    maint_display['Last_Serviced'] = pd.to_datetime(maint_display['Last_Serviced'], errors='coerce').dt.strftime('%Y-%m-%d')
    
    edited_maint = st.data_editor(
        maint_display, num_rows="dynamic", use_container_width=True,
        column_config={
            "Machine_ID": st.column_config.TextColumn(t[lang]["col_mach_id"]),
            "Task_EN": st.column_config.TextColumn("Task (English)"),
            "Task_HE": st.column_config.TextColumn("תיאור טיפול (עברית)"),
            "Freq_Days": st.column_config.NumberColumn(t[lang]["col_freq"]),
            "Last_Serviced": st.column_config.DateColumn(t[lang]["col_last_serv"], format="YYYY-MM-DD")
        }
    )
    if not edited_maint.equals(maint_display):
        save_data(edited_maint, "maintenance.csv")
        st.rerun()

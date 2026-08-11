import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Garage Workshop OS", page_icon="🪚", layout="wide")

# --- SESSION STATE FOR NAVIGATION ---
if 'current_page' not in st.session_state:
    st.session_state.current_page = "Homepage"

def navigate_to(page_name):
    st.session_state.current_page = page_name

# --- BILINGUAL DICTIONARY & UI TOGGLE ---
st.sidebar.title("🌐 שפה / Language")
lang_choice = st.sidebar.radio("Select Language", ["עברית", "English"], label_visibility="collapsed")
lang = "he" if lang_choice == "עברית" else "en"

# --- AGGRESSIVE RTL CSS INJECTION ---
if lang == "he":
    st.markdown(
        """
        <style>
        /* Force RTL direction and right alignment on the entire app and text elements */
        .stApp, .block-container, .stMarkdown, p, h1, h2, h3, h4, h5, h6, span, label, div {
            direction: rtl !important;
            text-align: right !important;
        }
        /* Ensure tables and data grids respect RTL */
        [data-testid="stDataFrame"], [data-testid="stDataFrame"] > div, .stDataFrame {
            direction: rtl !important;
        }
        /* Fix button text alignment */
        .stButton>button {
            text-align: center !important; 
        }
        /* Correct the sidebar flex ordering */
        section[data-testid="stSidebar"] {
            direction: rtl !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

t = {
    "en": {
        "title": "🪚 Garage Workshop | Workshop OS",
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
        "col_ppu": "Price/Unit (ILS)",
        "col_freq": "Frequency (Days)",
        "col_last_serv": "Last Serviced",
        "add_new_equip": "➕ Add New Machine",
        "add_new_jig": "➕ Add New Jig or Setup",
        "add_new_cons": "➕ Add New Consumable",
        "add_new_maint": "➕ Add Maintenance Task",
        "btn_submit": "Save to Database"
    },
    "he": {
        "title": "🪚 נגריית הגראז׳ | מערכת ניהול סדנא",
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
        "add_new_equip": "➕ הוספת מכונה חדשה",
        "add_new_jig": "➕ הוספת עזר/ג'יג חדש",
        "add_new_cons": "➕ הוספת פריט מלאי חדש",
        "add_new_maint": "➕ הוספת משימת תחזוקה",
        "btn_submit": "שמירה למאגר הנתונים"
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

# --- DATA INITIALIZATION ---
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

# LOAD & FIX DATA TYPES
eq_df = load_data("equipment.csv")
eq_df['Manual_Link'] = eq_df['Manual_Link'].fillna("").astype(str)
eq_df['Product_Link'] = eq_df['Product_Link'].fillna("").astype(str)

cons_df = load_data("consumables.csv")
maint_df = load_data("maintenance.csv")

# AUTO-HEAL JIGS FILE
try:
    jigs_df = load_data("jigs.csv")
    if 'Jig_Name_HE' not in jigs_df.columns:
        raise ValueError("Old Jigs format detected")
except (FileNotFoundError, ValueError):
    jigs_df = pd.DataFrame({
        "Machine_ID": ["MAC-01", "MAC-01", "MAC-02"],
        "Jig_Name_EN": ["Crosscut Sled", "Tenoning Jig", "Tapering Jig"],
        "Jig_Name_HE": ["מזחלת חיתוך (קרוסקאט)", "ג'יג סין וגרע", "ג'יג חיתוך זוויות"],
        "Mode_Config_EN": ["Standard 90 deg", "Vertical lock", "Variable angle"],
        "Mode_Config_HE": ["90 מעלות סטנדרטי", "נעילה אנכית", "זווית משתנה"],
        "Storage_EN": ["Wall Rack A", "Shelf 2", "Under MLT100"],
        "Storage_HE": ["קיר תלייה א'", "מדף 2", "מתחת למקיטה"]
    })
    save_data(jigs_df, "jigs.csv")

L = "_HE" if lang == "he" else "_EN"

# --- PAGE: HOMEPAGE (DASHBOARD) ---
if st.session_state.current_page == "Homepage":
    st.header(t[lang]["nav_home"])
    st.markdown("---")
    
    if lang == "he":
        col2, col1 = st.columns(2)
    else:
        col1, col2 = st.columns(2)
    
    # Low Stock Block
    with col1:
        st.subheader(t[lang]["dash_low_stock"])
        low_stock = cons_df[cons_df['Stock'] <= cons_df['Threshold']]
        if low_stock.empty:
            st.success(f"✅ {t[lang]['all_good_stock']}")
        else:
            for _, row in low_stock.iterrows():
                if lang == "he":
                    st.error(f"📦 **{row[f'Item{L}']}** | {t[lang]['col_stock']}: **{row['Stock']}** מתוך **{row['Threshold']}**")
                else:
                    st.error(f"📦 **{row[f'Item{L}']}** | {t[lang]['col_stock']}: **{row['Stock']}** / **{row['Threshold']}**")
            
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
                if lang == "he":
                    c_btn, c_text = st.columns([1, 3])
                else:
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
    
    # Add Item Form
    with st.expander(t[lang]["add_new_equip"]):
        with st.form("form_equip", clear_on_submit=True):
            f_c1, f_c2, f_c3 = st.columns(3)
            n_id = f_c1.text_input(t[lang]["col_mach_id"])
            n_cat = f_c2.text_input(t[lang]["col_cat"])
            n_name = f_c3.text_input(t[lang]["col_name"])
            
            f_c4, f_c5 = st.columns(2)
            n_role_en = f_c4.text_input("Role (English)")
            n_role_he = f_c5.text_input("ייעוד (עברית)")
            
            f_c6, f_c7, f_c8 = st.columns(3)
            n_man = f_c6.text_input("Manual URL / קישור להוראות יצרן")
            n_prod = f_c7.text_input("Product URL / קישור למוצר")
            n_grade = f_c8.selectbox(t[lang]["col_grade"], ["S", "A", "B", "C", "D", "E", "F"])
            
            if st.form_submit_button(t[lang]["btn_submit"]):
                new_row = pd.DataFrame([{"ID": n_id, "Category": n_cat, "Name": n_name, "Role_EN": n_role_en, "Role_HE": n_role_he, "Manual_Link": n_man, "Product_Link": n_prod, "Grade": n_grade, "Est_Value": 0}])
                eq_df = pd.concat([eq_df, new_row], ignore_index=True)
                save_data(eq_df, "equipment.csv")
                st.rerun()

    if lang == "he":
        cols = ["Grade", "Product_Link", "Manual_Link", "Role_HE", "Name", "Category", "ID"]
    else:
        cols = ["ID", "Category", "Name", "Role_EN", "Manual_Link", "Product_Link", "Grade"]
        
    edited_eq = st.data_editor(
        eq_df, column_order=cols, num_rows="dynamic", use_container_width=True,
        column_config={
            "ID": st.column_config.TextColumn(t[lang]["col_mach_id"]),
            "Category": st.column_config.TextColumn(t[lang]["col_cat"]),
            "Name": st.column_config.TextColumn(t[lang]["col_name"]),
            "Role_EN": st.column_config.TextColumn("Role"),
            "Role_HE": st.column_config.TextColumn("ייעוד"),
            "Manual_Link": st.column_config.LinkColumn("Manual URL" if lang == "en" else "קישור להוראות יצרן"),
            "Product_Link": st.column_config.LinkColumn("Product URL" if lang == "en" else "קישור למוצר"),
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
    
    # Add Item Form
    with st.expander(t[lang]["add_new_jig"]):
        with st.form("form_jig", clear_on_submit=True):
            f_c1, f_c2, f_c3 = st.columns(3)
            n_mid = f_c1.text_input(t[lang]["col_mach_id"])
            n_jig_en = f_c2.text_input("Jig Name (English)")
            n_jig_he = f_c3.text_input("שם עזר/ג'יג (עברית)")
            
            f_c4, f_c5 = st.columns(2)
            n_mod_en = f_c4.text_input("Configuration (English)")
            n_mod_he = f_c5.text_input("תצורה או כיוון (עברית)")
            
            f_c6, f_c7 = st.columns(2)
            n_stor_en = f_c6.text_input("Storage Location (English)")
            n_stor_he = f_c7.text_input("מקום אחסון (עברית)")
            
            if st.form_submit_button(t[lang]["btn_submit"]):
                new_row = pd.DataFrame([{"Machine_ID": n_mid, "Jig_Name_EN": n_jig_en, "Jig_Name_HE": n_jig_he, "Mode_Config_EN": n_mod_en, "Mode_Config_HE": n_mod_he, "Storage_EN": n_stor_en, "Storage_HE": n_stor_he}])
                jigs_df = pd.concat([jigs_df, new_row], ignore_index=True)
                save_data(jigs_df, "jigs.csv")
                st.rerun()
                
    if lang == "he":
        cols = ["Storage_HE", "Mode_Config_HE", "Jig_Name_HE", "Machine_ID"]
    else:
        cols = ["Machine_ID", "Jig_Name_EN", "Mode_Config_EN", "Storage_EN"]
        
    edited_jigs = st.data_editor(
        jigs_df, column_order=cols, num_rows="dynamic", use_container_width=True,
        column_config={
            "Machine_ID": st.column_config.TextColumn(t[lang]["col_mach_id"]),
            "Jig_Name_EN": st.column_config.TextColumn("Jig Name"),
            "Jig_Name_HE": st.column_config.TextColumn("שם עזר/ג'יג"),
            "Mode_Config_EN": st.column_config.TextColumn("Configuration"),
            "Mode_Config_HE": st.column_config.TextColumn("תצורה או כיוון"),
            "Storage_EN": st.column_config.TextColumn("Storage Location"),
            "Storage_HE": st.column_config.TextColumn("מקום אחסון"),
        }
    )
    if not edited_jigs.equals(jigs_df):
        save_data(edited_jigs, "jigs.csv")
        st.rerun()

# --- PAGE: CONSUMABLES ---
elif st.session_state.current_page == "Consumables":
    st.header(t[lang]["nav_cons"])
    
    # Add Item Form
    with st.expander(t[lang]["add_new_cons"]):
        with st.form("form_cons", clear_on_submit=True):
            f_c1, f_c2, f_c3 = st.columns(3)
            n_mid = f_c1.text_input(t[lang]["col_mach_id"])
            n_item_en = f_c2.text_input("Item Name (English)")
            n_item_he = f_c3.text_input("שם פריט (עברית)")
            
            f_c4, f_c5, f_c6, f_c7 = st.columns(4)
            n_stock = f_c4.number_input(t[lang]["col_stock"], min_value=0, value=1)
            n_thresh = f_c5.number_input(t[lang]["col_thresh"], min_value=0, value=1)
            n_ppu = f_c6.number_input(t[lang]["col_ppu"], min_value=0.0, value=0.0)
            n_grade = f_c7.selectbox(t[lang]["col_grade"], ["S", "A", "B", "C", "D", "E", "F"])
            
            if st.form_submit_button(t[lang]["btn_submit"]):
                new_row = pd.DataFrame([{"Machine_ID": n_mid, "Item_EN": n_item_en, "Item_HE": n_item_he, "Stock": n_stock, "Threshold": n_thresh, "PPU": n_ppu, "Grade": n_grade}])
                cons_df = pd.concat([cons_df, new_row], ignore_index=True)
                save_data(cons_df, "consumables.csv")
                st.rerun()
                
    if lang == "he":
        cols = ["Grade", "PPU", "Threshold", "Stock", "Item_HE", "Machine_ID"]
    else:
        cols = ["Machine_ID", "Item_EN", "Stock", "Threshold", "PPU", "Grade"]
        
    edited_cons = st.data_editor(
        cons_df, column_order=cols, num_rows="dynamic", use_container_width=True,
        column_config={
            "Machine_ID": st.column_config.TextColumn(t[lang]["col_mach_id"]),
            "Item_EN": st.column_config.TextColumn("Item Name"),
            "Item_HE": st.column_config.TextColumn("שם פריט"),
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
    
    # Add Item Form
    with st.expander(t[lang]["add_new_maint"]):
        with st.form("form_maint", clear_on_submit=True):
            f_c1, f_c2, f_c3 = st.columns(3)
            n_mid = f_c1.text_input(t[lang]["col_mach_id"])
            n_task_en = f_c2.text_input("Task Description (English)")
            n_task_he = f_c3.text_input("תיאור טיפול (עברית)")
            
            f_c4, f_c5 = st.columns(2)
            n_freq = f_c4.number_input(t[lang]["col_freq"], min_value=1, value=30)
            n_date = f_c5.date_input(t[lang]["col_last_serv"])
            
            if st.form_submit_button(t[lang]["btn_submit"]):
                new_row = pd.DataFrame([{"Machine_ID": n_mid, "Task_EN": n_task_en, "Task_HE": n_task_he, "Freq_Days": n_freq, "Last_Serviced": n_date.strftime('%Y-%m-%d')}])
                maint_df = pd.concat([maint_df, new_row], ignore_index=True)
                save_data(maint_df, "maintenance.csv")
                st.rerun()
                
    maint_display = maint_df.copy()
    maint_display['Last_Serviced'] = pd.to_datetime(maint_display['Last_Serviced'], errors='coerce').dt.date
    
    if lang == "he":
        cols = ["Last_Serviced", "Freq_Days", "Task_HE", "Machine_ID"]
    else:
        cols = ["Machine_ID", "Task_EN", "Freq_Days", "Last_Serviced"]
        
    edited_maint = st.data_editor(
        maint_display, column_order=cols, num_rows="dynamic", use_container_width=True,
        column_config={
            "Machine_ID": st.column_config.TextColumn(t[lang]["col_mach_id"]),
            "Task_EN": st.column_config.TextColumn("Task Description"),
            "Task_HE": st.column_config.TextColumn("תיאור טיפול/בדיקה"),
            "Freq_Days": st.column_config.NumberColumn(t[lang]["col_freq"]),
            "Last_Serviced": st.column_config.DateColumn(t[lang]["col_last_serv"], format="YYYY-MM-DD")
        }
    )
    if not edited_maint.equals(maint_display):
        edited_maint['Last_Serviced'] = pd.to_datetime(edited_maint['Last_Serviced']).dt.strftime('%Y-%m-%d')
        save_data(edited_maint, "maintenance.csv")
        st.rerun()

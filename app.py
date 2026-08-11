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
        .stApp, .block-container, .stMarkdown, p, h1, h2, h3, h4, h5, h6, span, label, div {
            direction: rtl !important;
            text-align: right !important;
        }
        [data-testid="stDataFrame"], [data-testid="stDataFrame"] > div, .stDataFrame {
            direction: rtl !important;
        }
        .stButton>button { text-align: center !important; }
        section[data-testid="stSidebar"] { direction: rtl !important; }
        div[data-testid="stTextInput"] button { display: none !important; } /* Hide password eye */
        </style>
        """,
        unsafe_allow_html=True
    )
else:
    st.markdown(
        """
        <style>
        div[data-testid="stTextInput"] button { display: none !important; } /* Hide password eye */
        </style>
        """,
        unsafe_allow_html=True
    )

t = {
    "en": {
        "title": "🪚 Garage Workshop | Workshop OS",
        "nav_home": "🏠 Homepage",
        "nav_equip": "🗜️ Equipment Master",
        "nav_jigs": "📐 Jigs & Configs",
        "nav_cons": "📦 Consumables",
        "nav_maint": "🔧 Maintenance",
        "dash_low_stock": "⚠️ Low Stock Alerts",
        "dash_maint": "⏰ Maintenance Tracker",
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
        "col_next_serv": "Next Service",
        "col_resp": "Responsible",
        "add_new_equip": "➕ Add New Machine",
        "add_new_jig": "➕ Add New Jig/Config",
        "add_new_cons": "➕ Add New Consumable",
        "add_new_maint": "➕ Add Maintenance Task",
        "btn_submit": "Save to Database",
        "req_safety": "Requires Safety Check",
        "safety_cleared": "Safety Cleared (Admin)",
        "is_private": "Private Collection Tool",
        "err_safety": "⚠️ Cannot complete: Pending Admin Safety Clearance!",
        "err_early": "⚠️ Cannot complete before the scheduled next service date.",
        "due_today": "Due Today",
        "days_left": "Days Left",
        "overdue": "OVERDUE",
        "admin_mode": "🛡️ Admin Mode",
        "user_mode": "👤 User Mode",
        "admin_pin": "Admin Access PIN"
    },
    "he": {
        "title": "🪚 נגריית הגראז׳ | מערכת ניהול המרחב",
        "nav_home": "🏠 חפ״ק המרחב",
        "nav_equip": "🗜️ מצבת ציוד ומכונות",
        "nav_jigs": "📐 עזרים, ג'יגים ותצורות",
        "nav_cons": "📦 מלאי מתכלים",
        "nav_maint": "🔧 טיפולים ותחזוקה",
        "dash_low_stock": "⚠️ התראות חוסר במלאי",
        "dash_maint": "⏰ מעקב טיפולים",
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
        "col_next_serv": "תאריך לטיפול הבא",
        "col_resp": "אחראי",
        "add_new_equip": "➕ הוספת מכונה חדשה",
        "add_new_jig": "➕ הוספת ג'יג/תצורה",
        "add_new_cons": "➕ הוספת פריט מלאי חדש",
        "add_new_maint": "➕ הוספת משימת תחזוקה",
        "btn_submit": "שמירה למאגר הנתונים",
        "req_safety": "דורש אישור בטיחות",
        "safety_cleared": "אושר בטיחותית (מנהל)",
        "is_private": "כלי אוסף פרטי",
        "err_safety": "⚠️ לא ניתן להשלים: ממתין לאישור בטיחות של מנהל!",
        "err_early": "⚠️ לא ניתן לסמן כבוצע לפני תאריך היעד שנקבע.",
        "due_today": "לביצוע היום",
        "days_left": "ימים נותרו",
        "overdue": "בפיגור",
        "admin_mode": "🛡️ מצב מנהל",
        "user_mode": "👤 מצב משתמש",
        "admin_pin": "קוד גישת מנהל"
    }
}

# --- NAVIGATION MENUS (Top of Sidebar) ---
st.sidebar.markdown("---")
if st.sidebar.button(t[lang]["nav_home"], use_container_width=True): navigate_to("Homepage")
if st.sidebar.button(t[lang]["nav_equip"], use_container_width=True): navigate_to("Equipment")
if st.sidebar.button(t[lang]["nav_jigs"], use_container_width=True): navigate_to("Jigs")
if st.sidebar.button(t[lang]["nav_cons"], use_container_width=True): navigate_to("Consumables")
if st.sidebar.button(t[lang]["nav_maint"], use_container_width=True): navigate_to("Maintenance")

# --- ADMIN AUTHENTICATION (Bottom of Sidebar) ---
st.sidebar.markdown("---")
admin_pin = st.sidebar.text_input(t[lang]["admin_pin"], type="password")
is_admin = (admin_pin == "2004")

if is_admin:
    st.sidebar.success(t[lang]["admin_mode"])
else:
    st.sidebar.info(t[lang]["user_mode"])

st.title(t[lang]["title"])

# --- DATA INITIALIZATION & AUTO-HEAL ---
def load_data(file): return pd.read_csv(file)
def save_data(df, file): df.to_csv(file, index=False)

if not os.path.exists("equipment.csv"):
    pd.DataFrame({"ID": [], "Category": [], "Name": [], "Role_EN": [], "Role_HE": [], "Manual_Link": [], "Product_Link": [], "Grade": [], "Est_Value": [], "Is_Private": []}).to_csv("equipment.csv", index=False)
if not os.path.exists("consumables.csv"):
    pd.DataFrame({"Machine_ID": [], "Item_EN": [], "Item_HE": [], "Stock": [], "Threshold": [], "PPU": [], "Grade": []}).to_csv("consumables.csv", index=False)
if not os.path.exists("jigs.csv"):
    pd.DataFrame({"Machine_ID": [], "Name_EN": [], "Name_HE": [], "Purpose_EN": [], "Purpose_HE": [], "Notes_EN": [], "Notes_HE": [], "Storage_EN": [], "Storage_HE": []}).to_csv("jigs.csv", index=False)
if not os.path.exists("maintenance.csv"):
    pd.DataFrame({"Machine_ID": [], "Task_EN": [], "Task_HE": [], "Freq_Days": [], "Last_Serviced": [], "Req_Safety": [], "Safety_Cleared": [], "Responsible": []}).to_csv("maintenance.csv", index=False)

# Safe Load: Equipment
eq_df = load_data("equipment.csv")
eq_df['Is_Private'] = eq_df.get('Is_Private', False).fillna(False).astype(bool)
eq_df['Manual_Link'] = eq_df['Manual_Link'].fillna("").astype(str)
eq_df['Product_Link'] = eq_df['Product_Link'].fillna("").astype(str)

# Safe Load: Maintenance
maint_df = load_data("maintenance.csv")
maint_df['Req_Safety'] = maint_df.get('Req_Safety', False).fillna(False).astype(bool)
maint_df['Safety_Cleared'] = maint_df.get('Safety_Cleared', False).fillna(False).astype(bool)
maint_df['Responsible'] = maint_df.get('Responsible', "").fillna("").astype(str)
maint_df['Freq_Days'] = pd.to_numeric(maint_df['Freq_Days'], errors='coerce').fillna(30).astype(int)

# Safe Load: Consumables
cons_df = load_data("consumables.csv")
cons_df['Stock'] = pd.to_numeric(cons_df['Stock'], errors='coerce').fillna(0).astype(int)
cons_df['Threshold'] = pd.to_numeric(cons_df['Threshold'], errors='coerce').fillna(0).astype(int)
cons_df['PPU'] = pd.to_numeric(cons_df['PPU'], errors='coerce').fillna(0.0).astype(float)

# Safe Load: Jigs
try:
    jigs_df = load_data("jigs.csv")
    if 'Name_HE' not in jigs_df.columns: raise ValueError()
except (FileNotFoundError, ValueError):
    jigs_df = pd.DataFrame({"Machine_ID": ["MAC-01", "MAC-01", "MAC-02"], "Name_EN": ["Crosscut Sled", "Tenoning Jig", "Variable Angle Taper"], "Name_HE": ["מזחלת חיתוך (קרוסקאט)", "ג'יג סין וגרע", "חיתוך זווית משתנה"], "Purpose_EN": ["Crosscutting 90 deg", "Cutting tenons vertically", "Tapered cuts"], "Purpose_HE": ["חיתוך 90 מעלות", "חיתוך סין בצורה אנכית", "חיתוך בזווית משתנה"], "Notes_EN": ["Keep waxed", "Clamp tightly", ""], "Notes_HE": ["לשמן שעווה", "להדק היטב", ""], "Storage_EN": ["Wall Rack A", "Shelf 2", "Under MLT100"], "Storage_HE": ["קיר תלייה א'", "מדף 2", "מתחת למקיטה"]})
    save_data(jigs_df, "jigs.csv")

machine_ids = eq_df['ID'].dropna().unique().tolist()
if not machine_ids: machine_ids = ["NO_MACHINES"]

L = "_HE" if lang == "he" else "_EN"
row_control = "dynamic" if is_admin else "fixed"

# --- PAGE: HOMEPAGE (DASHBOARD) ---
if st.session_state.current_page == "Homepage":
    st.header(t[lang]["nav_home"])
    st.markdown("---")
    
    col1, col2 = st.columns(2) if lang == "en" else reversed(st.columns(2))
    
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

    # Maintenance Block (Overdue & Upcoming)
    with col2:
        st.subheader(t[lang]["dash_maint"])
        
        # Safe Date Calculations
        dash_maint = maint_df.copy()
        dash_maint['Last_Serviced_DT'] = pd.to_datetime(dash_maint['Last_Serviced'], errors='coerce')
        dash_maint['Next_Due_DT'] = dash_maint['Last_Serviced_DT'] + pd.to_timedelta(dash_maint['Freq_Days'], unit='D')
        today_dt = pd.to_datetime(datetime.today().date())
        dash_maint['Days_Until'] = (dash_maint['Next_Due_DT'] - today_dt).dt.days

        overdue = dash_maint[dash_maint['Days_Until'] < 0]
        
        upcoming_long = dash_maint[(dash_maint['Freq_Days'] > 7) & (dash_maint['Days_Until'] >= 0) & (dash_maint['Days_Until'] <= 3)]
        upcoming_short = dash_maint[(dash_maint['Freq_Days'] <= 7) & (dash_maint['Days_Until'] >= 0) & (dash_maint['Days_Until'] <= 1)]
        upcoming = pd.concat([upcoming_long, upcoming_short])
        
        if overdue.empty and upcoming.empty:
            st.success(f"✅ {t[lang]['all_good_maint']}")
        else:
            # Render Overdue (Red)
            for idx, row in overdue.iterrows():
                c_text, c_btn = st.columns([3, 1]) if lang == "en" else reversed(st.columns([1, 3]))
                with c_text:
                    if row['Req_Safety'] and not row['Safety_Cleared']:
                        st.error(f"🚨 **{row[f'Task{L}']}** ({row['Machine_ID']}) - {t[lang]['req_safety']}")
                    else:
                        st.error(f"🚨 **{row[f'Task{L}']}** ({row['Machine_ID']}) - {t[lang]['overdue']}")
                        
                with c_btn:
                    if st.button(t[lang]["btn_mark_done"], key=f"done_ovr_{idx}"):
                        if row['Req_Safety'] and not row['Safety_Cleared']:
                            st.error(t[lang]["err_safety"])
                        else:
                            maint_df.at[idx, 'Last_Serviced'] = datetime.today().strftime('%Y-%m-%d')
                            maint_df.at[idx, 'Safety_Cleared'] = False
                            save_data(maint_df, "maintenance.csv")
                            st.rerun()

            # Render Upcoming (Orange/Warning)
            for idx, row in upcoming.iterrows():
                c_text, c_btn = st.columns([3, 1]) if lang == "en" else reversed(st.columns([1, 3]))
                with c_text:
                    due_text = t[lang]["due_today"] if row['Days_Until'] == 0 else f"{int(row['Days_Until'])} {t[lang]['days_left']}"
                    if row['Req_Safety'] and not row['Safety_Cleared']:
                        st.warning(f"⏳ **{row[f'Task{L}']}** ({row['Machine_ID']}) - {due_text} ({t[lang]['req_safety']})")
                    else:
                        st.warning(f"⏳ **{row[f'Task{L}']}** ({row['Machine_ID']}) - {due_text}")
                        
                with c_btn:
                    if st.button(t[lang]["btn_mark_done"], key=f"done_upc_{idx}"):
                        if row['Days_Until'] > 0:
                            st.error(t[lang]["err_early"])
                        elif row['Req_Safety'] and not row['Safety_Cleared']:
                            st.error(t[lang]["err_safety"])
                        else:
                            maint_df.at[idx, 'Last_Serviced'] = datetime.today().strftime('%Y-%m-%d')
                            maint_df.at[idx, 'Safety_Cleared'] = False
                            save_data(maint_df, "maintenance.csv")
                            st.rerun()

# --- PAGE: EQUIPMENT MASTER ---
elif st.session_state.current_page == "Equipment":
    st.header(t[lang]["nav_equip"])
    
    if is_admin:
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
                
                n_private = st.checkbox(t[lang]["is_private"])
                
                if st.form_submit_button(t[lang]["btn_submit"]):
                    new_row = pd.DataFrame([{"ID": n_id, "Category": n_cat, "Name": n_name, "Role_EN": n_role_en, "Role_HE": n_role_he, "Manual_Link": n_man, "Product_Link": n_prod, "Grade": n_grade, "Est_Value": 0, "Is_Private": n_private}])
                    eq_df = pd.concat([eq_df, new_row], ignore_index=True)
                    save_data(eq_df, "equipment.csv")
                    st.rerun()

    eq_df_view = eq_df if is_admin else eq_df[eq_df['Is_Private'] == False].copy()
    cols = ["Is_Private", "Grade", "Product_Link", "Manual_Link", "Role_HE", "Name", "Category", "ID"] if lang == "he" else ["ID", "Category", "Name", "Role_EN", "Manual_Link", "Product_Link", "Grade", "Is_Private"]
    if not is_admin: cols.remove("Is_Private")
    
    edited_eq = st.data_editor(
        eq_df_view, column_order=cols, num_rows=row_control, use_container_width=True,
        column_config={
            "ID": st.column_config.TextColumn(t[lang]["col_mach_id"]),
            "Category": st.column_config.TextColumn(t[lang]["col_cat"]),
            "Name": st.column_config.TextColumn(t[lang]["col_name"]),
            "Role_EN": st.column_config.TextColumn("Role"),
            "Role_HE": st.column_config.TextColumn("ייעוד"),
            "Manual_Link": st.column_config.LinkColumn("Manual URL" if lang == "en" else "קישור להוראות יצרן"),
            "Product_Link": st.column_config.LinkColumn("Product URL" if lang == "en" else "קישור למוצר"),
            "Grade": st.column_config.SelectboxColumn(t[lang]["col_grade"], options=["S", "A", "B", "C", "D", "E", "F"]),
            "Is_Private": st.column_config.CheckboxColumn(t[lang]["is_private"]),
            "Est_Value": None 
        }
    )
    if not edited_eq.equals(eq_df_view):
        if is_admin: save_data(edited_eq, "equipment.csv")
        else: 
            eq_df.update(edited_eq)
            save_data(eq_df, "equipment.csv")
        st.rerun()

# --- PAGE: JIGS & MODES ---
elif st.session_state.current_page == "Jigs":
    st.header(t[lang]["nav_jigs"])
    
    with st.expander(t[lang]["add_new_jig"]):
        with st.form("form_jig", clear_on_submit=True):
            f_c1, f_c2, f_c3 = st.columns(3)
            n_mid = f_c1.selectbox(t[lang]["col_mach_id"], options=machine_ids)
            n_name_en = f_c2.text_input("Jig/Config. Name (English)")
            n_name_he = f_c3.text_input("שם הג׳יג/התצורה (עברית)")
            
            f_c4, f_c5 = st.columns(2)
            n_purp_en = f_c4.text_input("Purpose (English)")
            n_purp_he = f_c5.text_input("מטרה/ייעוד (עברית)")
            
            f_c6, f_c7 = st.columns(2)
            n_notes_en = f_c6.text_input("Notes (English)")
            n_notes_he = f_c7.text_input("הערות (עברית)")
            
            f_c8, f_c9 = st.columns(2)
            n_stor_en = f_c8.text_input("Storage Location (English)")
            n_stor_he = f_c9.text_input("מקום אחסון (עברית)")
            
            if st.form_submit_button(t[lang]["btn_submit"]):
                new_row = pd.DataFrame([{"Machine_ID": n_mid, "Name_EN": n_name_en, "Name_HE": n_name_he, "Purpose_EN": n_purp_en, "Purpose_HE": n_purp_he, "Notes_EN": n_notes_en, "Notes_HE": n_notes_he, "Storage_EN": n_stor_en, "Storage_HE": n_stor_he}])
                jigs_df = pd.concat([jigs_df, new_row], ignore_index=True)
                save_data(jigs_df, "jigs.csv")
                st.rerun()
                
    cols = ["Notes_HE", "Storage_HE", "Purpose_HE", "Name_HE", "Machine_ID"] if lang == "he" else ["Machine_ID", "Name_EN", "Purpose_EN", "Storage_EN", "Notes_EN"]
    edited_jigs = st.data_editor(
        jigs_df, column_order=cols, num_rows=row_control, use_container_width=True,
        column_config={
            "Machine_ID": st.column_config.SelectboxColumn(t[lang]["col_mach_id"], options=machine_ids),
            "Name_EN": st.column_config.TextColumn("Jig/Config. Name"),
            "Name_HE": st.column_config.TextColumn("שם הג׳יג/התצורה"),
            "Purpose_EN": st.column_config.TextColumn("Purpose"),
            "Purpose_HE": st.column_config.TextColumn("מטרה/ייעוד"),
            "Notes_EN": st.column_config.TextColumn("Notes"),
            "Notes_HE": st.column_config.TextColumn("הערות"),
            "Storage_EN": st.column_config.TextColumn("Storage Location"),
            "Storage_HE": st.column_config.TextColumn("מקום אחסון")
        }
    )
    if not edited_jigs.equals(jigs_df):
        save_data(edited_jigs, "jigs.csv")
        st.rerun()

# --- PAGE: CONSUMABLES ---
elif st.session_state.current_page == "Consumables":
    st.header(t[lang]["nav_cons"])
    
    with st.expander(t[lang]["add_new_cons"]):
        with st.form("form_cons", clear_on_submit=True):
            f_c1, f_c2, f_c3 = st.columns(3)
            n_mid = f_c1.selectbox(t[lang]["col_mach_id"], options=machine_ids)
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
                
    cols = ["Grade", "PPU", "Threshold", "Stock", "Item_HE", "Machine_ID"] if lang == "he" else ["Machine_ID", "Item_EN", "Stock", "Threshold", "PPU", "Grade"]
    edited_cons = st.data_editor(
        cons_df, column_order=cols, num_rows=row_control, use_container_width=True,
        column_config={
            "Machine_ID": st.column_config.SelectboxColumn(t[lang]["col_mach_id"], options=machine_ids),
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
    
    with st.expander(t[lang]["add_new_maint"]):
        with st.form("form_maint", clear_on_submit=True):
            f_c1, f_c2, f_c3 = st.columns(3)
            n_mid = f_c1.selectbox(t[lang]["col_mach_id"], options=machine_ids)
            n_task_en = f_c2.text_input("Task Description (English)")
            n_task_he = f_c3.text_input("תיאור טיפול (עברית)")
            
            f_c4, f_c5, f_c6 = st.columns(3)
            n_freq = f_c4.number_input(t[lang]["col_freq"], min_value=1, value=30)
            n_date = f_c5.date_input(t[lang]["col_last_serv"])
            n_resp = f_c6.text_input(t[lang]["col_resp"])
            
            n_req_safety = st.checkbox(t[lang]["req_safety"])
            
            if st.form_submit_button(t[lang]["btn_submit"]):
                new_row = pd.DataFrame([{"Machine_ID": n_mid, "Task_EN": n_task_en, "Task_HE": n_task_he, "Freq_Days": n_freq, "Last_Serviced": n_date.strftime('%Y-%m-%d'), "Req_Safety": n_req_safety, "Safety_Cleared": False, "Responsible": n_resp}])
                maint_df = pd.concat([maint_df, new_row], ignore_index=True)
                save_data(maint_df, "maintenance.csv")
                st.rerun()
                
    maint_display = maint_df.copy()
    
    # Safely cast objects to native Python date objects to prevent TypeCompatibility crashes
    last_serv_dt = pd.to_datetime(maint_display['Last_Serviced'], errors='coerce')
    next_due_dt = last_serv_dt + pd.to_timedelta(maint_display['Freq_Days'], unit='D')
    
    maint_display['Last_Serviced'] = last_serv_dt.apply(lambda x: x.date() if pd.notnull(x) else None)
    maint_display['Next_Due'] = next_due_dt.apply(lambda x: x.date() if pd.notnull(x) else None)
    
    cols = ["Safety_Cleared", "Req_Safety", "Responsible", "Next_Due", "Last_Serviced", "Freq_Days", "Task_HE", "Machine_ID"] if lang == "he" else ["Machine_ID", "Task_EN", "Freq_Days", "Last_Serviced", "Next_Due", "Responsible", "Req_Safety", "Safety_Cleared"]
    
    disabled_cols = ["Next_Due"] if is_admin else ["Next_Due", "Safety_Cleared", "Req_Safety"]

    edited_maint = st.data_editor(
        maint_display, column_order=cols, num_rows=row_control, use_container_width=True, disabled=disabled_cols,
        column_config={
            "Machine_ID": st.column_config.SelectboxColumn(t[lang]["col_mach_id"], options=machine_ids),
            "Task_EN": st.column_config.TextColumn("Task Description"),
            "Task_HE": st.column_config.TextColumn("תיאור טיפול/בדיקה"),
            "Freq_Days": st.column_config.NumberColumn(t[lang]["col_freq"]),
            "Last_Serviced": st.column_config.DateColumn(t[lang]["col_last_serv"], format="YYYY-MM-DD"),
            "Next_Due": st.column_config.DateColumn(t[lang]["col_next_serv"], format="YYYY-MM-DD"),
            "Responsible": st.column_config.TextColumn(t[lang]["col_resp"]),
            "Req_Safety": st.column_config.CheckboxColumn(t[lang]["req_safety"]),
            "Safety_Cleared": st.column_config.CheckboxColumn(t[lang]["safety_cleared"])
        }
    )
    if not edited_maint.equals(maint_display):
        # Convert the safe date objects back to standardized strings before saving
        save_df = edited_maint.drop(columns=['Next_Due'])
        save_df['Last_Serviced'] = pd.to_datetime(save_df['Last_Serviced'], errors='coerce').dt.strftime('%Y-%m-%d').fillna("")
        save_data(save_df, "maintenance.csv")
        st.rerun()

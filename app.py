import streamlit as st
import pandas as pd
import json
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# --- GOOGLE SHEETS CONFIGURATION ---
SHEET_ID = "1bN8Js3DE1VWFLadAhJPktnST10gk8gSXCQYRfdmU-Qw"

@st.cache_resource
def get_gspread_client():
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    creds_json = json.loads(st.secrets["gcp_service_account"])
    credentials = Credentials.from_service_account_info(creds_json, scopes=scopes)
    return gspread.authorize(credentials)

@st.cache_data(ttl=600, show_spinner=False)
def pull_data(tab_name):
    client = get_gspread_client()
    try:
        ws = client.open_by_key(SHEET_ID).worksheet(tab_name)
        val = ws.get_all_values()
        if not val: return None
        return ws.get_all_records()
    except gspread.exceptions.WorksheetNotFound:
        return "NOT_FOUND"

def load_data(tab_name, default_df):
    data = pull_data(tab_name)
    
    if data == "NOT_FOUND":
        client = get_gspread_client()
        spreadsheet = client.open_by_key(SHEET_ID)
        spreadsheet.add_worksheet(title=tab_name, rows="100", cols="20")
        save_data(default_df, tab_name)
        return default_df.copy()
    elif data is None:
        save_data(default_df, tab_name)
        return default_df.copy()
    elif not data:
        return pd.DataFrame(columns=default_df.columns)
    else:
        return pd.DataFrame(data)

def save_data(df, tab_name):
    client = get_gspread_client()
    ws = client.open_by_key(SHEET_ID).worksheet(tab_name)
    ws.clear()
    df_clean = df.fillna("")
    data_to_save = [df_clean.columns.values.tolist()] + df_clean.astype(str).values.tolist()
    ws.update(values=data_to_save, range_name="A1")
    pull_data.clear()

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

# --- GLOBAL FONT (Rubik) & ICON PROTECTION ---
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Rubik:wght@400;500;600;700&display=swap');
    html, body, .stApp { font-family: 'Rubik', -apple-system, BlinkMacSystemFont, sans-serif; }
    .stMarkdown, p, h1, h2, h3, h4, h5, h6, label, input, select, textarea, .stButton button, [data-testid="stMetricValue"], [data-testid="stMetricLabel"] {
        font-family: 'Rubik', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }
    [data-testid="stIcon"], [class*="material-symbols"], [class*="material-icons"], .material-symbols-rounded {
        font-family: 'Material Symbols Rounded', 'Material Symbols Outlined', 'Material Icons' !important;
    }
    div[data-testid="stTextInput"] button { display: none !important; }
    /* Multiselect chips styling */
    .stMultiSelect [data-baseweb="select"] span { font-family: 'Rubik', sans-serif !important; }
    </style>
    """,
    unsafe_allow_html=True
)

# --- RESPONSIVE RTL CSS INJECTION ---
if lang == "he":
    st.markdown(
        """
        <style>
        .block-container, [data-testid="stSidebarUserContent"] { direction: rtl !important; }
        .stMarkdown, .stMarkdown p, h1, h2, h3, h4, h5, h6, label { text-align: right !important; }
        input, select, textarea { text-align: right !important; direction: rtl !important; }
        [data-testid="stDataFrame"], [data-testid="stDataFrame"] > div { direction: rtl !important; }
        .stButton>button { text-align: center !important; }
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
        "btn_approve": "Approve ✓",
        "btn_wait": "Waiting...",
        "col_mach_id": "Tool ID",
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
        "add_new_equip": "➕ Add New Tool",
        "add_new_jig": "➕ Add New Jig/Config",
        "add_new_cons": "➕ Add New Consumable",
        "add_new_maint": "➕ Add Maintenance Task",
        "btn_submit": "Save to Database",
        "req_safety": "Requires Safety Check",
        "safety_cleared": "Safety Cleared (Admin)",
        "is_private": "Private Collection Tool",
        "pending_admin": "⏳ Awaiting Admin Safety Check",
        "err_safety": "⚠️ Cannot complete: Pending Admin Safety Clearance!",
        "err_early": "⚠️ Cannot complete before the scheduled next service date.",
        "due_today": "Due Today",
        "days_left": "Days Left",
        "overdue": "OVERDUE",
        "admin_mode": "🛡️ Admin Mode",
        "user_mode": "👤 User Mode",
        "admin_pin": "Admin Access PIN",
        "filter_tasks": "🔍 Find Tools by Task",
        "filter_tasks_prompt": "Select tasks to filter equipment..."
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
        "btn_approve": "אישור מנהל ✓",
        "btn_wait": "ממתין...",
        "col_mach_id": "קוד כלי",
        "col_cat": "קטגוריה",
        "col_name": "שם/דגם",
        "col_grade": "דירוג איכות",
        "col_stock": "כמות במלאי",
        "col_thresh": "סף מינימום להזמנה",
        "col_ppu": "מחיר יחידה (₪)\u200f",
        "col_freq": "תדירות טיפול (בימים)\u200f",
        "col_last_serv": "תאריך טיפול אחרון",
        "col_next_serv": "תאריך לטיפול הבא",
        "col_resp": "אחראי",
        "add_new_equip": "➕ הוספת כלי חדש",
        "add_new_jig": "➕ הוספת ג'יג/תצורה",
        "add_new_cons": "➕ הוספת פריט מלאי חדש",
        "add_new_maint": "➕ הוספת משימת תחזוקה",
        "btn_submit": "שמירה למאגר הנתונים",
        "req_safety": "דורש אישור בטיחות",
        "safety_cleared": "אושר בטיחותית (מנהל)\u200f",
        "is_private": "כלי אוסף פרטי",
        "pending_admin": "⏳ ממתין לאישור בטיחות של מנהל",
        "err_safety": "⚠️ לא ניתן להשלים: ממתין לאישור בטיחות של מנהל!",
        "err_early": "⚠️ לא ניתן לסמן כבוצע לפני תאריך היעד שנקבע.",
        "due_today": "לביצוע היום",
        "days_left": "ימים נותרו",
        "overdue": "בפיגור",
        "admin_mode": "🛡️ מצב מנהל",
        "user_mode": "👤 מצב משתמש",
        "admin_pin": "קוד גישת מנהל",
        "filter_tasks": "🔍 חיפוש כלים לפי ייעוד",
        "filter_tasks_prompt": "בחירת משימות לסינון הכלים..."
    }
}

# --- NAVIGATION MENUS ---
st.sidebar.markdown("---")
if st.sidebar.button(t[lang]["nav_home"], use_container_width=True): navigate_to("Homepage")
if st.sidebar.button(t[lang]["nav_equip"], use_container_width=True): navigate_to("Equipment")
if st.sidebar.button(t[lang]["nav_jigs"], use_container_width=True): navigate_to("Jigs")
if st.sidebar.button(t[lang]["nav_cons"], use_container_width=True): navigate_to("Consumables")
if st.sidebar.button(t[lang]["nav_maint"], use_container_width=True): navigate_to("Maintenance")

# --- ADMIN AUTHENTICATION ---
st.sidebar.markdown("---")
admin_pin = st.sidebar.text_input(t[lang]["admin_pin"], type="password")
is_admin = (admin_pin == "2004")

if is_admin:
    st.sidebar.success(t[lang]["admin_mode"])
else:
    st.sidebar.info(t[lang]["user_mode"])

st.title(t[lang]["title"])

# --- SAFE LOAD & TYPING (GOOGLE SHEETS) ---
def parse_bool(val):
    if isinstance(val, bool): return val
    if pd.isna(val) or val == "": return False
    return str(val).strip().lower() in ['true', '1', 't', 'y', 'yes']

# CAPABILITIES DATABASE (Comprehensive Woodworking List)
default_cap = pd.DataFrame({
    "Category_EN": ["Sawing & Primary Sizing", "Sawing & Primary Sizing", "Sawing & Primary Sizing", "Sawing & Primary Sizing", "Sawing & Primary Sizing", "Sawing & Primary Sizing", "Sawing & Primary Sizing", "Milling & Surfacing", "Milling & Surfacing", "Milling & Surfacing", "Milling & Surfacing", "Joinery & Precision Shaping", "Joinery & Precision Shaping", "Joinery & Precision Shaping", "Joinery & Precision Shaping", "Joinery & Precision Shaping", "Joinery & Precision Shaping", "Joinery & Precision Shaping", "Joinery & Precision Shaping", "Joinery & Precision Shaping", "Joinery & Precision Shaping", "Joinery & Precision Shaping", "Joinery & Precision Shaping", "Drilling, Boring & Fastening", "Drilling, Boring & Fastening", "Drilling, Boring & Fastening", "Drilling, Boring & Fastening", "Drilling, Boring & Fastening", "Sanding & Surface Prep", "Sanding & Surface Prep", "Sanding & Surface Prep", "Sanding & Surface Prep", "Sanding & Surface Prep", "Sanding & Surface Prep", "Sharpening & Tool Care", "Sharpening & Tool Care", "Sharpening & Tool Care", "Sharpening & Tool Care", "Pressing & Veneering", "Pressing & Veneering", "Pressing & Veneering", "Dust Extraction & Shop Utilities", "Dust Extraction & Shop Utilities", "Dust Extraction & Shop Utilities", "Dust Extraction & Shop Utilities"],
    "Category_HE": ["ניסור וחלוקת חומר", "ניסור וחלוקת חומר", "ניסור וחלוקת חומר", "ניסור וחלוקת חומר", "ניסור וחלוקת חומר", "ניסור וחלוקת חומר", "ניסור וחלוקת חומר", "הקצעה ויישור", "הקצעה ויישור", "הקצעה ויישור", "הקצעה ויישור", "מחברים ועיבוד צורני", "מחברים ועיבוד צורני", "מחברים ועיבוד צורני", "מחברים ועיבוד צורני", "מחברים ועיבוד צורני", "מחברים ועיבוד צורני", "מחברים ועיבוד צורני", "מחברים ועיבוד צורני", "מחברים ועיבוד צורני", "מחברים ועיבוד צורני", "מחברים ועיבוד צורני", "מחברים ועיבוד צורני", "קידוח, שיקוע והברגה", "קידוח, שיקוע והברגה", "קידוח, שיקוע והברגה", "קידוח, שיקוע והברגה", "קידוח, שיקוע והברגה", "ליטוש ועיבוד שטח", "ליטוש ועיבוד שטח", "ליטוש ועיבוד שטח", "ליטוש ועיבוד שטח", "ליטוש ועיבוד שטח", "ליטוש ועיבוד שטח", "השחזה, יישור ותחזוקת כלים", "השחזה, יישור ותחזוקת כלים", "השחזה, יישור ותחזוקת כלים", "השחזה, יישור ותחזוקת כלים", "כבישה, הדבקה ופורניר", "כבישה, הדבקה ופורניר", "כבישה, הדבקה ופורניר", "שאיבה, סינון ותשתיות", "שאיבה, סינון ותשתיות", "שאיבה, סינון ותשתיות", "שאיבה, סינון ותשתיות"],
    "Role_EN": ["Rip-Cutting", "Cross-Cutting", "Sheet Breakdown", "Re-Sawing", "Curved & Contour Cutting", "Intricate & Scroll Cutting", "Mitre & Compound Cutting", "Face Flattening (Jointing)", "Edge Jointing (Squaring)", "Thickness Planing", "Rough Stock Sizing", "Grooving & Dadoing", "Rabbeting (Rebating)", "Mortising", "Tenoning", "Loose Tenon Joinery", "Plate & Biscuit Joinery", "Pocket Hole Joinery", "Dovetail & Box Joinery", "Edge Profiling & Chamfering", "Pattern & Flush Trimming", "Wood Turning", "Curved Bending & Forming", "Perpendicular Drilling", "Angle & Compound Drilling", "Large Diameter Boring", "Countersinking & Counterboring", "Thread Fastening & Driving", "Edge & End-Grain Sanding", "Stationary Sanding", "Internal Curve Sanding", "Wide-Surface Finish Sanding", "Aggressive Surface Leveling", "Hand Scraping & Shaving", "Wet Precision Grinding", "Dry Bench Grinding", "Honing & Stropping", "Stone Flattening", "Vacuum Pressing", "Panel Gluing & Clamping", "Veneer Prep & Jointing", "High-Volume Dust Collection", "Point-of-Source Vacuum", "Ambient Air Filtration", "Compressed Air Supply"],
    "Role_HE": ["חיתוך אורך", "חיתוך רוחב", "פריסת לוחות", "פריסה (Re-saw)", "חיתוך עקומות וצורני", "חיתוך עדין ודקורטיבי", "חיתוך זוויות וגרונג", "יישור פנים", "הקצעת דופן ויישור 90°", "הקצעת עובי", "עיבוד גס", "חריצה (חריץ / דאדו)", "פלייץ (מדרגה)", "חפירת נקבים (גרע / מורטיס)", "ייצור פינים (סין / טנון)", "מחברי סין צף (דומינו)", "מחברי למלו (ביסקוויט)", "קדיחת חורי כיס", "מחברי זנב יונים ואצבע", "כרסום פרופיל ופאזות", "כרסום לפי שבלונה והעתקה", "חריטה בעץ", "כיפוף והדבקת שכבות", "קידוח ניצב מדויק", "קידוח בזוויות", "קידוח קוטר רחב (פורסטנר/צירים)", "שיקוע ברגים ופקקים", "הברגה והידוק", "ליטוש דפנות וגדע", "ליטוש שולחני (סרט/דיסק)", "ליטוש עקומות פנימיות (ספינדל)", "ליטוש גימור שטח", "ליטוש גס ויישור משטחים", "הקצעה ידנית וציקלינה", "השחזה רטובה מדויקת", "השחזה יבשה גסה", "ליטוש עדין והברקה", "יישור אבני השחזה", "כבישה בוואקום", "הדבקת לוחות וכליבה", "חיתוך והתאמת פורניר", "איסוף שבבים בנפח גבוה", "שאיבה נקודתית", "סינון אוויר בחלל", "אספקת לחץ אוויר וניפוח"]
})
cap_df = load_data("capabilities", default_cap)
# Generate dual-language dropdown list
cap_options = [f"{en} | {he}" for en, he in zip(cap_df['Role_EN'].fillna(""), cap_df['Role_HE'].fillna("")) if en or he]

# Equipment
default_eq = pd.DataFrame({"ID": [], "Category": [], "Name": [], "Role_EN": [], "Role_HE": [], "Manual_Link": [], "Product_Link": [], "Grade": [], "Est_Value": [], "Is_Private": []})
eq_df = load_data("equipment", default_eq)
for col in ["ID", "Category", "Name", "Role_EN", "Role_HE", "Manual_Link", "Product_Link", "Grade"]:
    eq_df[col] = eq_df.get(col, "").fillna("").astype(str)
eq_df["Is_Private"] = eq_df.get("Is_Private", False).apply(parse_bool)

# Consumables
default_cons = pd.DataFrame({"Machine_ID": [], "Item_EN": [], "Item_HE": [], "Stock": [], "Threshold": [], "PPU": [], "Grade": []})
cons_df = load_data("consumables", default_cons)
for col in ["Machine_ID", "Item_EN", "Item_HE", "Grade"]:
    cons_df[col] = cons_df.get(col, "").fillna("").astype(str)
cons_df["Stock"] = pd.to_numeric(cons_df.get("Stock", 0), errors='coerce').fillna(0).astype(int)
cons_df["Threshold"] = pd.to_numeric(cons_df.get("Threshold", 0), errors='coerce').fillna(0).astype(int)
cons_df["PPU"] = pd.to_numeric(cons_df.get("PPU", 0.0), errors='coerce').fillna(0.0).astype(float)

# Jigs
default_jigs = pd.DataFrame({"Machine_ID": [], "Name_EN": [], "Name_HE": [], "Purpose_EN": [], "Purpose_HE": [], "Notes_EN": [], "Notes_HE": [], "Storage_EN": [], "Storage_HE": []})
jigs_df = load_data("jigs", default_jigs)
for col in ["Machine_ID", "Name_EN", "Name_HE", "Purpose_EN", "Purpose_HE", "Notes_EN", "Notes_HE", "Storage_EN", "Storage_HE"]:
    jigs_df[col] = jigs_df.get(col, "").fillna("").astype(str)

# Maintenance
default_maint = pd.DataFrame({"Machine_ID": [], "Task_EN": [], "Task_HE": [], "Freq_Days": [], "Last_Serviced": [], "Req_Safety": [], "Safety_Cleared": [], "Responsible": [], "Pending_Approval": []})
maint_df = load_data("maintenance", default_maint)
for col in ["Machine_ID", "Task_EN", "Task_HE", "Responsible"]:
    maint_df[col] = maint_df.get(col, "").fillna("").astype(str)
for col in ["Req_Safety", "Safety_Cleared", "Pending_Approval"]:
    maint_df[col] = maint_df.get(col, False).apply(parse_bool)
maint_df["Freq_Days"] = pd.to_numeric(maint_df.get("Freq_Days", 30), errors='coerce').fillna(30).astype(int)

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
            # Overdue loop
            for idx, row in overdue.iterrows():
                c_text, c_btn = st.columns([3, 1]) if lang == "en" else reversed(st.columns([1, 3]))
                with c_text:
                    if row['Pending_Approval']:
                        st.info(f"🛡️ **{row[f'Task{L}']}** ({row['Machine_ID']}) - {t[lang]['pending_admin']}")
                    elif row['Req_Safety']:
                        st.error(f"🚨 **{row[f'Task{L}']}** ({row['Machine_ID']}) - {t[lang]['req_safety']}")
                    else:
                        st.error(f"🚨 **{row[f'Task{L}']}** ({row['Machine_ID']}) - {t[lang]['overdue']}")
                        
                with c_btn:
                    if row['Pending_Approval']:
                        if is_admin:
                            if st.button(t[lang]["btn_approve"], key=f"app_ovr_{idx}"):
                                maint_df.at[idx, 'Last_Serviced'] = datetime.today().strftime('%Y-%m-%d')
                                maint_df.at[idx, 'Pending_Approval'] = False
                                maint_df.at[idx, 'Safety_Cleared'] = False
                                save_data(maint_df.drop(columns=['Last_Serviced_DT', 'Next_Due_DT', 'Days_Until'], errors='ignore'), "maintenance")
                                st.rerun()
                        else:
                            st.button(t[lang]["btn_wait"], key=f"wait_ovr_{idx}", disabled=True)
                    else:
                        if st.button(t[lang]["btn_mark_done"], key=f"done_ovr_{idx}"):
                            if row['Req_Safety']:
                                if is_admin:
                                    maint_df.at[idx, 'Last_Serviced'] = datetime.today().strftime('%Y-%m-%d')
                                else:
                                    maint_df.at[idx, 'Pending_Approval'] = True
                            else:
                                maint_df.at[idx, 'Last_Serviced'] = datetime.today().strftime('%Y-%m-%d')
                            save_data(maint_df.drop(columns=['Last_Serviced_DT', 'Next_Due_DT', 'Days_Until'], errors='ignore'), "maintenance")
                            st.rerun()

            # Upcoming loop
            for idx, row in upcoming.iterrows():
                c_text, c_btn = st.columns([3, 1]) if lang == "en" else reversed(st.columns([1, 3]))
                with c_text:
                    due_text = t[lang]["due_today"] if row['Days_Until'] == 0 else f"{int(row['Days_Until'])} {t[lang]['days_left']}"
                    
                    if row['Pending_Approval']:
                        st.info(f"🛡️ **{row[f'Task{L}']}** ({row['Machine_ID']}) - {t[lang]['pending_admin']}")
                    elif row['Req_Safety']:
                        st.warning(f"⏳ **{row[f'Task{L}']}** ({row['Machine_ID']}) - {due_text} ({t[lang]['req_safety']})")
                    else:
                        st.warning(f"⏳ **{row[f'Task{L}']}** ({row['Machine_ID']}) - {due_text}")
                        
                with c_btn:
                    if row['Pending_Approval']:
                        if is_admin:
                            if st.button(t[lang]["btn_approve"], key=f"app_upc_{idx}"):
                                maint_df.at[idx, 'Last_Serviced'] = datetime.today().strftime('%Y-%m-%d')
                                maint_df.at[idx, 'Pending_Approval'] = False
                                maint_df.at[idx, 'Safety_Cleared'] = False
                                save_data(maint_df.drop(columns=['Last_Serviced_DT', 'Next_Due_DT', 'Days_Until'], errors='ignore'), "maintenance")
                                st.rerun()
                        else:
                            st.button(t[lang]["btn_wait"], key=f"wait_upc_{idx}", disabled=True)
                    else:
                        if st.button(t[lang]["btn_mark_done"], key=f"done_upc_{idx}"):
                            if row['Days_Until'] > 0:
                                st.error(t[lang]["err_early"])
                            elif row['Req_Safety']:
                                if is_admin:
                                    maint_df.at[idx, 'Last_Serviced'] = datetime.today().strftime('%Y-%m-%d')
                                else:
                                    maint_df.at[idx, 'Pending_Approval'] = True
                                save_data(maint_df.drop(columns=['Last_Serviced_DT', 'Next_Due_DT', 'Days_Until'], errors='ignore'), "maintenance")
                                st.rerun()
                            else:
                                maint_df.at[idx, 'Last_Serviced'] = datetime.today().strftime('%Y-%m-%d')
                                save_data(maint_df.drop(columns=['Last_Serviced_DT', 'Next_Due_DT', 'Days_Until'], errors='ignore'), "maintenance")
                                st.rerun()

# --- PAGE: EQUIPMENT MASTER ---
elif st.session_state.current_page == "Equipment":
    st.header(t[lang]["nav_equip"])
    
    # Task Finder UI
    with st.container():
        st.subheader(t[lang]["filter_tasks"])
        filter_tasks = st.multiselect(t[lang]["filter_tasks_prompt"], options=cap_options)
    
    if is_admin:
        with st.expander(t[lang]["add_new_equip"]):
            with st.form("form_equip", clear_on_submit=True):
                f_c1, f_c2, f_c3 = st.columns(3)
                n_id = f_c1.text_input(t[lang]["col_mach_id"])
                n_cat = f_c2.text_input(t[lang]["col_cat"])
                n_name = f_c3.text_input(t[lang]["col_name"])
                
                # New Dropdown for Capabilities instead of plain text
                n_roles = st.multiselect("Capabilities & Roles / משימות וייעוד", options=cap_options)
                
                f_c6, f_c7, f_c8 = st.columns(3)
                n_man = f_c6.text_input("Manual URL / קישור להוראות יצרן")
                n_prod = f_c7.text_input("Product URL / קישור למוצר")
                n_grade = f_c8.selectbox(t[lang]["col_grade"], ["S", "A", "B", "C", "D", "E", "F"])
                
                n_private = st.checkbox(t[lang]["is_private"]) if is_admin else False
                
                if st.form_submit_button(t[lang]["btn_submit"]):
                    # Parse the multi-select output to save clean comma-separated strings
                    n_role_en = ", ".join([r.split(" | ")[0] for r in n_roles])
                    n_role_he = ", ".join([r.split(" | ")[1] for r in n_roles])
                    
                    new_row = pd.DataFrame([{"ID": n_id, "Category": n_cat, "Name": n_name, "Role_EN": n_role_en, "Role_HE": n_role_he, "Manual_Link": n_man, "Product_Link": n_prod, "Grade": n_grade, "Est_Value": 0, "Is_Private": n_private}])
                    eq_df = pd.concat([eq_df, new_row], ignore_index=True)
                    save_data(eq_df, "equipment")
                    st.rerun()

    # Filter Logic
    eq_df_view = eq_df if is_admin else eq_df[eq_df['Is_Private'] == False].copy()
    
    if filter_tasks:
        selected_en_tasks = [t.split(" | ")[0] for t in filter_tasks]
        def has_capability(role_str):
            # Show the machine if it possesses ANY of the selected capabilities
            return any(task in str(role_str) for task in selected_en_tasks)
        eq_df_view = eq_df_view[eq_df_view['Role_EN'].apply(has_capability)]

    cols = ["Is_Private", "Grade", "Product_Link", "Manual_Link", "Role_HE", "Name", "Category", "ID"] if lang == "he" else ["ID", "Category", "Name", "Role_EN", "Manual_Link", "Product_Link", "Grade", "Is_Private"]
    if not is_admin: 
        if "Is_Private" in cols: cols.remove("Is_Private")
    
    disabled_cols_eq = [] if is_admin else cols
    
    edited_eq = st.data_editor(
        eq_df_view, column_order=cols, num_rows=row_control, use_container_width=True, hide_index=True, disabled=disabled_cols_eq,
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
        if is_admin: 
            save_data(edited_eq, "equipment")
        else: 
            eq_df.update(edited_eq)
            save_data(eq_df, "equipment")
        st.rerun()

# --- PAGE: JIGS & MODES ---
elif st.session_state.current_page == "Jigs":
    st.header(t[lang]["nav_jigs"])
    
    with st.expander(t[lang]["add_new_jig"]):
        with st.form("form_jig", clear_on_submit=True):
            f_c1, f_c2, f_c3 = st.columns(3)
            n_mid = f_c1.selectbox(t[lang]["col_mach_id"], options=machine_ids)
            n_name_en = f_c2.text_input("Jig/Config. Name (English)")
            n_name_he = f_c3.text_input("שם הג׳יג/התצורה (עברית)\u200f")
            
            f_c4, f_c5 = st.columns(2)
            n_purp_en = f_c4.text_input("Purpose (English)")
            n_purp_he = f_c5.text_input("מטרה/ייעוד (עברית)\u200f")
            
            f_c6, f_c7 = st.columns(2)
            n_notes_en = f_c6.text_input("Notes (English)")
            n_notes_he = f_c7.text_input("הערות (עברית)\u200f")
            
            f_c8, f_c9 = st.columns(2)
            n_stor_en = f_c8.text_input("Storage Location (English)")
            n_stor_he = f_c9.text_input("מקום אחסון (עברית)\u200f")
            
            if st.form_submit_button(t[lang]["btn_submit"]):
                new_row = pd.DataFrame([{"Machine_ID": n_mid, "Name_EN": n_name_en, "Name_HE": n_name_he, "Purpose_EN": n_purp_en, "Purpose_HE": n_purp_he, "Notes_EN": n_notes_en, "Notes_HE": n_notes_he, "Storage_EN": n_stor_en, "Storage_HE": n_stor_he}])
                jigs_df = pd.concat([jigs_df, new_row], ignore_index=True)
                save_data(jigs_df, "jigs")
                st.rerun()
                
    cols = ["Notes_HE", "Storage_HE", "Purpose_HE", "Name_HE", "Machine_ID"] if lang == "he" else ["Machine_ID", "Name_EN", "Purpose_EN", "Storage_EN", "Notes_EN"]
    disabled_cols_jigs = [] if is_admin else cols
    
    edited_jigs = st.data_editor(
        jigs_df, column_order=cols, num_rows=row_control, use_container_width=True, hide_index=True, disabled=disabled_cols_jigs,
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
        save_data(edited_jigs, "jigs")
        st.rerun()

# --- PAGE: CONSUMABLES ---
elif st.session_state.current_page == "Consumables":
    st.header(t[lang]["nav_cons"])
    
    with st.expander(t[lang]["add_new_cons"]):
        with st.form("form_cons", clear_on_submit=True):
            f_c1, f_c2, f_c3 = st.columns(3)
            n_mid = f_c1.selectbox(t[lang]["col_mach_id"], options=machine_ids)
            n_item_en = f_c2.text_input("Item Name (English)")
            n_item_he = f_c3.text_input("שם פריט (עברית)\u200f")
            
            f_c4, f_c5, f_c6, f_c7 = st.columns(4)
            n_stock = f_c4.number_input(t[lang]["col_stock"], min_value=0, value=1)
            n_thresh = f_c5.number_input(t[lang]["col_thresh"], min_value=0, value=1)
            n_ppu = f_c6.number_input(t[lang]["col_ppu"], min_value=0.0, value=0.0)
            n_grade = f_c7.selectbox(t[lang]["col_grade"], ["S", "A", "B", "C", "D", "E", "F"])
            
            if st.form_submit_button(t[lang]["btn_submit"]):
                new_row = pd.DataFrame([{"Machine_ID": n_mid, "Item_EN": n_item_en, "Item_HE": n_item_he, "Stock": n_stock, "Threshold": n_thresh, "PPU": n_ppu, "Grade": n_grade}])
                cons_df = pd.concat([cons_df, new_row], ignore_index=True)
                save_data(cons_df, "consumables")
                st.rerun()
                
    cols = ["Grade", "PPU", "Threshold", "Stock", "Item_HE", "Machine_ID"] if lang == "he" else ["Machine_ID", "Item_EN", "Stock", "Threshold", "PPU", "Grade"]
    disabled_cols_cons = [] if is_admin else [c for c in cols if c != "Stock"]
    
    edited_cons = st.data_editor(
        cons_df, column_order=cols, num_rows=row_control, use_container_width=True, hide_index=True, disabled=disabled_cols_cons,
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
        save_data(edited_cons, "consumables")
        st.rerun()

# --- PAGE: MAINTENANCE ---
elif st.session_state.current_page == "Maintenance":
    st.header(t[lang]["nav_maint"])
    
    with st.expander(t[lang]["add_new_maint"]):
        with st.form("form_maint", clear_on_submit=True):
            f_c1, f_c2, f_c3 = st.columns(3)
            n_mid = f_c1.selectbox(t[lang]["col_mach_id"], options=machine_ids)
            n_task_en = f_c2.text_input("Task Description (English)")
            n_task_he = f_c3.text_input("תיאור טיפול (עברית)\u200f")
            
            f_c4, f_c5, f_c6 = st.columns(3)
            n_freq = f_c4.number_input(t[lang]["col_freq"], min_value=1, value=30)
            n_date = f_c5.date_input(t[lang]["col_last_serv"])
            n_resp = f_c6.text_input(t[lang]["col_resp"])
            
            n_req_safety = st.checkbox(t[lang]["req_safety"])
            
            if st.form_submit_button(t[lang]["btn_submit"]):
                new_row = pd.DataFrame([{"Machine_ID": n_mid, "Task_EN": n_task_en, "Task_HE": n_task_he, "Freq_Days": n_freq, "Last_Serviced": n_date.strftime('%Y-%m-%d'), "Req_Safety": n_req_safety, "Safety_Cleared": False, "Responsible": n_resp, "Pending_Approval": False}])
                maint_df = pd.concat([maint_df, new_row], ignore_index=True)
                save_data(maint_df, "maintenance")
                st.rerun()
                
    maint_display = maint_df.copy()
    
    def parse_date(val):
        try:
            if pd.isna(val) or str(val).strip() == "": return None
            return pd.to_datetime(val).date()
        except:
            return None
            
    maint_display['Last_Serviced'] = maint_display['Last_Serviced'].apply(parse_date)
    maint_display['Next_Due'] = (pd.to_datetime(maint_display['Last_Serviced']) + pd.to_timedelta(maint_display['Freq_Days'], unit='D')).apply(lambda x: x.date() if pd.notnull(x) else None)
    
    cols = ["Safety_Cleared", "Req_Safety", "Responsible", "Next_Due", "Last_Serviced", "Freq_Days", "Task_HE", "Machine_ID"] if lang == "he" else ["Machine_ID", "Task_EN", "Freq_Days", "Last_Serviced", "Next_Due", "Responsible", "Req_Safety", "Safety_Cleared"]
    
    # Strictly disable the date column for non-admins to force use of the Dashboard button
    disabled_cols = ["Next_Due"] if is_admin else ["Next_Due", "Safety_Cleared", "Req_Safety", "Last_Serviced"]

    edited_maint = st.data_editor(
        maint_display, column_order=cols, num_rows=row_control, use_container_width=True, disabled=disabled_cols, hide_index=True,
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
        for idx in edited_maint.index:
            is_cleared = edited_maint.at[idx, 'Safety_Cleared'] == True
            is_pending = edited_maint.at[idx, 'Pending_Approval'] == True
            if is_cleared and is_pending:
                edited_maint.at[idx, 'Last_Serviced'] = datetime.today().date()
                edited_maint.at[idx, 'Safety_Cleared'] = False
                edited_maint.at[idx, 'Pending_Approval'] = False
                
        save_df = edited_maint.drop(columns=['Next_Due'])
        save_df['Last_Serviced'] = save_df['Last_Serviced'].apply(lambda x: x.strftime('%Y-%m-%d') if pd.notnull(x) else "")
        save_data(save_df, "maintenance")
        st.rerun()

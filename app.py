import os
import warnings
import streamlit as st
import streamlit.components.v1 as components
from google import genai
from pypdf import PdfReader

warnings.filterwarnings("ignore")

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="BIS Standard Compliance Portal",
    page_icon="🇮🇳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. SECRETS & API KEY MANAGEMENT ---
try:
    GOOGLE_API_KEY = st.secrets["GEMINI_API_KEY"]
    MODEL_NAME = st.secrets.get("GEMINI_MODEL", "gemini-3.6-flash")
except Exception:
    st.error("⚠️ API Key नहीं मिली! कृपया Streamlit Secrets सेट करें।")
    st.stop()

client = genai.Client(api_key=GOOGLE_API_KEY)

# --- 3. LANGUAGE TRANSLATION DICTIONARY ---
TRANSLATIONS = {
    "English": {
        "title": "Bureau of Indian Standards",
        "subtitle": "National Standards Body of India",
        "portal_name": "BIS Multi-Document AI Verification Portal",
        "portal_desc": "Integrated AI Engine for Industry Compliance, Regulatory Analysis & Multi-Document Search",
        "repo_title": "📁 Central Document Repository",
        "repo_desc": "Upload multiple BIS Standards PDFs at once:",
        "upload_label": "Upload BIS Documents (PDFs)",
        "upload_success": "files saved to repository!",
        "db_files_title": "🗄️ Available Documents in Database:",
        "no_files": "No documents uploaded yet.",
        "tab1": "🔍 Global Search",
        "tab2": "📑 Executive Summary",
        "tab3": "⚠️ Penalties & Rules",
        "tab4": "📊 Consumer Quiz",
        "search_heading": "Ask Questions Across Entire Database",
        "search_sub": "Your query will be searched across all uploaded documents simultaneously.",
        "input_label": "Enter Query / Specific Clause Search:",
        "input_placeholder": "e.g., toy safety limits, IS 9873 rules, packaged water testing",
        "btn_search": "Run Verification Query",
        "sum_heading": "Database Executive Summary",
        "sum_sub": "Generate a structured overview of all stored regulatory files.",
        "btn_sum": "Generate Executive Summary",
        "pen_heading": "Penalties, Fines & Legal Inspector",
        "pen_sub": "Extract legal provisions, penalties, and mandatory manufacturer obligations.",
        "btn_pen": "Inspect Legal Penalties & Obligations",
        "quiz_heading": "Public Awareness Quiz Generator",
        "quiz_sub": "Generate evaluation MCQs based on compliance documents.",
        "btn_quiz": "Generate Awareness Quiz",
        "warning_upload": "👈 Please upload BIS Documents (PDFs) from the sidebar to begin.",
        "warning_empty_query": "Please enter a valid search query.",
        "official_response": "Official Verification Response",
    },
    "Hindi": {
        "title": "भारतीय मानक ब्यूरो",
        "subtitle": "भारत का राष्ट्रीय मानक निकाय",
        "portal_name": "भारतीय मानक ब्यूरो - बहु-दस्तावेज़ एआई सत्यापन पोर्टल",
        "portal_desc": "उद्योग अनुपालन, नियामक विश्लेषण और बहु-दस्तावेज़ खोज के लिए एकीकृत एआई इंजन",
        "repo_title": "📁 केंद्रीय दस्तावेज़ रिपोजिटरी",
        "repo_desc": "एक से अधिक BIS मानक PDFs एक साथ अपलोड करें:",
        "upload_label": "BIS दस्तावेज़ (PDFs) अपलोड करें",
        "upload_success": "फाइलें डेटाबेस में सफलतापूर्वक सहेजी गईं!",
        "db_files_title": "🗄️ डेटाबेस में उपलब्ध दस्तावेज़:",
        "no_files": "अभी कोई दस्तावेज़ अपलोड नहीं है।",
        "tab1": "🔍 वैश्विक खोज",
        "tab2": "📑 कार्यकारी सारांश",
        "tab3": "⚠️ कानूनी दंड व नियम",
        "tab4": "📊 जागरूकता क्विज",
        "search_heading": "पूरे डेटाबेस में सवाल पूछें",
        "search_sub": "आपका प्रश्न सभी अपलोड किए गए दस्तावेज़ों में एक साथ खोजा जाएगा।",
        "input_label": "अपना प्रश्न दर्ज करें:",
        "input_placeholder": "उदा. खिलौना सुरक्षा नियम, आईएस 9873 मानक, पैकेज्ड पानी परीक्षण",
        "btn_search": "सत्यापन प्रश्न चलाएं",
        "sum_heading": "डेटाबेस का कार्यकारी सारांश",
        "sum_sub": "सभी संग्रहीत नियामक फाइलों का संक्षिप्त विवरण जनरेट करें।",
        "btn_sum": "कार्यकारी सारांश जनरेट करें",
        "pen_heading": "दंड, जुर्माना और अनुपालन निरीक्षक",
        "pen_sub": "कानूनी प्रावधानों, जुर्माने और निर्माताओं के अनिवार्य दायित्वों को निकालें।",
        "btn_pen": "कानूनी दंड और नियमों का निरीक्षण करें",
        "quiz_heading": "सार्वजनिक और औद्योगिक जागरूकता क्विज",
        "quiz_sub": "अनुपालन दस्तावेज़ों के आधार पर MCQs जनरेट करें।",
        "btn_quiz": "जागरूकता क्विज बनाएं",
        "warning_upload": "👈 शुरुआत करने के लिए कृपया साइडबार से BIS दस्तावेज़ (PDFs) अपलोड करें।",
        "warning_empty_query": "कृपया कोई मान्य प्रश्न लिखें।",
        "official_response": "आधिकारिक सत्यापन उत्तर",
    }
}

# --- 4. CSS OVERRIDES & CLEAN UI ---
st.markdown("""
    <style>
    /* 1. Transparent Header & Hide Fork/GitHub/Deploy Toolbar */
    header[data-testid="stHeader"] {
        background: transparent !important;
    }
    [data-testid="stAppViewToolbar"] { display: none !important; }
    #MainMenu { visibility: hidden !important; }
    footer { visibility: hidden !important; }
    .stAppDeployButton { display: none !important; }
    div[class*="viewerBadge_container"] { display: none !important; }

    /* 2. Sidebar Toggle Button Styling */
    button[data-testid="stHeaderSidebarToggle"] {
        color: #0B2545 !important;
        background-color: #F1F5F9 !important;
        border: 1px solid #CBD5E1 !important;
        border-radius: 6px;
        margin-top: 6px;
        margin-left: 6px;
    }

    .block-container { padding-top: 1.5rem !important; }

    /* 3. Sidebar UI Elements */
    .sidebar-flag-box { width: 100%; margin-bottom: 12px; }
    .sidebar-flag-box img {
        width: 105px;
        height: auto;
        border-radius: 4px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.12);
        display: block;
    }

    /* 4. Modern & Clean Tab Navigation (Fixed Ugly Blue Box Issue) */
    .stTabs [data-baseweb="tab-list"] {
        background-color: #F8FAFC !important;
        padding: 6px 8px;
        border-radius: 10px;
        border: 1px solid #E2E8F0;
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: transparent !important;
        border-radius: 8px !important;
        padding: 8px 18px !important;
        border: none !important;
        color: #475569 !important;
        font-weight: 600 !important;
        transition: all 0.2s ease-in-out;
    }
    .stTabs [data-baseweb="tab"]:hover {
        background-color: #E2E8F0 !important;
        color: #0F172A !important;
    }
    .stTabs [aria-selected="true"] {
        background-color: #0B2545 !important;
        color: #FFFFFF !important;
        box-shadow: 0 2px 4px rgba(11, 37, 69, 0.15);
    }
    .stTabs [aria-selected="true"] p, .stTabs [aria-selected="true"] span {
        color: #FFFFFF !important;
        font-weight: 700 !important;
    }
    .stTabs [data-baseweb="tab-highlight"] {
        display: none !important; /* Disables default awkward bar */
    }

    /* 5. Clean Card Output Box */
    .output-card {
        background-color: #FFFFFF !important;
        border-left: 4px solid #0B2545;
        border-radius: 8px;
        padding: 22px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        border-top: 1px solid #F1F5F9;
        border-right: 1px solid #F1F5F9;
        border-bottom: 1px solid #F1F5F9;
        margin-top: 15px;
    }
    .output-card * { color: #0F172A !important; }
    </style>
""", unsafe_allow_html=True)

# --- 5. STORAGE SETUP ---
DB_FOLDER = "stored_documents"
if not os.path.exists(DB_FOLDER):
    os.makedirs(DB_FOLDER)

# --- 6. HELPER FUNCTIONS ---
def save_uploaded_files(uploaded_files):
    for file in uploaded_files:
        file_path = os.path.join(DB_FOLDER, file.name)
        with open(file_path, "wb") as f:
            f.write(file.getbuffer())

def load_all_documents_text():
    combined_text = ""
    files = [f for f in os.listdir(DB_FOLDER) if f.endswith('.pdf')]
    max_chars_per_doc = 30000
    
    for file_name in sorted(files):
        file_path = os.path.join(DB_FOLDER, file_name)
        try:
            reader = PdfReader(file_path)
            doc_text = ""
            for i, page in enumerate(reader.pages):
                page_text = page.extract_text()
                if page_text:
                    doc_text += f"\n--- [Doc: {file_name} | Page {i+1}] ---\n" + page_text
            
            combined_text += f"\n\n=== START OF DOCUMENT: {file_name} ===\n"
            combined_text += doc_text[:max_chars_per_doc]
            combined_text += f"\n=== END OF DOCUMENT: {file_name} ===\n"
        except Exception:
            continue
        
    return combined_text, files

def run_gemini(prompt):
    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt
        )
        return response.text
    except Exception as e:
        return f"Error connecting to AI service: {e}"

# --- 7. TOP NAVIGATION ---
col_space, col_lang = st.columns([4, 1])
with col_lang:
    lang_choice = st.selectbox("🌐 Language / भाषा", options=["English", "Hindi"], index=0)

t = TRANSLATIONS[lang_choice]

# --- 8. SIDEBAR ---
with st.sidebar:
    st.markdown("""
        <div class="sidebar-flag-box">
            <img src="https://upload.wikimedia.org/wikipedia/commons/4/41/Flag_of_India.svg" alt="India Flag" />
        </div>
    """, unsafe_allow_html=True)

    st.markdown(f"### **{t['title']}**")
    st.caption(t['subtitle'])
    st.markdown("---")
    
    st.markdown(f"#### {t['repo_title']}")
    st.caption(t['repo_desc'])
    
    uploaded_files = st.file_uploader(t['upload_label'], type=["pdf"], accept_multiple_files=True)
    
    if uploaded_files:
        save_uploaded_files(uploaded_files)
        st.success(f"✅ {len(uploaded_files)} {t['upload_success']}")

    st.markdown("---")
    st.markdown(f"#### {t['db_files_title']}")
    
    saved_files = [f for f in os.listdir(DB_FOLDER) if f.endswith('.pdf')]
    if saved_files:
        for file in sorted(saved_files):
            st.text(f"📄 {file}")
    else:
        st.info(t['no_files'])

# --- 9. MAIN INTERFACE ---
banner_html = f"""
<!DOCTYPE html>
<html>
<head>
<style>
body {{ margin: 0; padding: 0; font-family: system-ui; }}
.tricolor-band {{
    height: 4px;
    background: linear-gradient(to right, #FF9933 0%, #FFFFFF 50%, #128807 100%);
    border-radius: 2px;
    margin-bottom: 12px;
}}
.banner-container {{
    background-color: #0B2545;
    padding: 20px 24px;
    border-radius: 8px;
    border-bottom: 4px solid #D4AF37;
}}
.banner-title {{ color: #FFFFFF !important; font-size: 22px; font-weight: 700; margin-bottom: 6px; }}
.banner-desc {{ color: #E2E8F0 !important; font-size: 13.5px; margin: 0; }}
</style>
</head>
<body>
    <div class="tricolor-band"></div>
    <div class="banner-container">
        <div class="banner-title">{t['portal_name']}</div>
        <div class="banner-desc">{t['portal_desc']}</div>
    </div>
</body>
</html>
"""

components.html(banner_html, height=115)

all_text, file_list = load_all_documents_text()

if not file_list:
    st.warning(t['warning_upload'])
else:
    tab1, tab2, tab3, tab4 = st.tabs([t['tab1'], t['tab2'], t['tab3'], t['tab4']])

    with tab1:
        st.subheader(t['search_heading'])
        st.caption(f"{t['search_sub']} (Total Loaded: {len(file_list)} PDFs)")
        user_query = st.text_input(t['input_label'], placeholder=t['input_placeholder'])
        if st.button(t['btn_search']):
            if user_query:
                with st.spinner("Processing..."):
                    prompt = f"You are a BIS compliance assistant. Search across ALL documents and answer in {lang_choice}.\n\nDocs:\n{all_text}\n\nQuery:\n{user_query}"
                    ans = run_gemini(prompt)
                    st.markdown('<div class="output-card">', unsafe_allow_html=True)
                    st.markdown(f"### **{t['official_response']}**")
                    st.write(ans)
                    st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.warning(t['warning_empty_query'])

    with tab2:
        st.subheader(t['sum_heading'])
        if st.button(t['btn_sum']):
            with st.spinner("Analyzing..."):
                summary = run_gemini(f"Provide executive summary in {lang_choice}:\n\n{all_text}")
                st.markdown('<div class="output-card">', unsafe_allow_html=True)
                st.write(summary)
                st.markdown('</div>', unsafe_allow_html=True)

    with tab3:
        st.subheader(t['pen_heading'])
        if st.button(t['btn_pen']):
            with st.spinner("Extracting Legal Clauses..."):
                penalties = run_gemini(f"List penalties & obligations in {lang_choice}:\n\n{all_text}")
                st.markdown('<div class="output-card">', unsafe_allow_html=True)
                st.write(penalties)
                st.markdown('</div>', unsafe_allow_html=True)

    with tab4:
        st.subheader(t['quiz_heading'])
        if st.button(t['btn_quiz']):
            with st.spinner("Generating Quiz..."):
                quiz = run_gemini(f"Generate 4 MCQs in {lang_choice}:\n\n{all_text}")
                st.markdown('<div class="output-card">', unsafe_allow_html=True)
                st.write(quiz)
                st.markdown('</div>', unsafe_allow_html=True)
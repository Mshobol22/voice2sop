import streamlit as st
import google.generativeai as genai
from fpdf import FPDF
import time

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Voice2SOP | AI Process Documentation",
    page_icon="🎙️",
    layout="centered"
)

# --- HELPER FUNCTION: PDF GENERATION ---
def create_pdf(text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    # Title
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="Standard Operating Procedure", ln=True, align='C')
    pdf.ln(10)
    
    # Content
    pdf.set_font("Arial", size=12)
    # Handle basic encoding for PDF
    pdf.multi_cell(0, 10, txt=text.encode('latin-1', 'replace').decode('latin-1'))
    
    return pdf.output(dest='S').encode('latin-1')

# --- UI STYLING (PRO DASHBOARD LOOK) ---
def apply_pro_style():
    st.markdown("""
        <style>
        /* Base fonts */
        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
        }
        
        /* Hide default streamlit chrome */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}

        /* MAIN TITLE styling */
        .main-title {
            font-size: 3rem;
            font-weight: 800;
            text-align: center;
            background: -webkit-linear-gradient(45deg, #2563eb, #9333ea);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0px;
        }
        
        /* SUBTITLE styling */
        .subtitle {
            text-align: center;
            font-size: 1.2rem;
            opacity: 0.8;
            margin-bottom: 30px;
        }

        /* CARD styling (SaaS Box Shadow) */
        div.stContainer {
            background-color: transparent; 
        }
        
        /* Metric Cards */
        div[data-testid="stMetric"] {
            background-color: rgba(150, 150, 150, 0.1);
            border-radius: 10px;
            padding: 15px;
            text-align: center;
        }

        /* Button Styling - Gradient Action */
        div.stButton > button {
            width: 100%;
            border-radius: 8px;
            font-weight: 600;
            border: none;
            padding: 0.6rem;
            transition: all 0.3s ease;
        }
        
        div.stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }
        </style>
    """, unsafe_allow_html=True)

apply_pro_style()

# --- SIDEBAR ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/9373/9373977.png", width=60)
    st.markdown("### **Voice2SOP** `Pro`")
    st.caption("AI-Powered Process Documentation")
    st.divider()

    # SECRET MANAGEMENT
    if "GEMINI_API_KEY" in st.secrets:
        st.success("✅ Connected to Enterprise AI")
        api_key = st.secrets["GEMINI_API_KEY"]
    else:
        # Fallback for local testing or if secret is missing
        api_key = st.text_input("🔑 Enter API Key", type="password")
        if not api_key:
            st.warning("Please enter key to start.")

    st.divider()
    
    # UPSELL CARD (LINKED TO YOUR STRIPE)
    with st.container(border=True):
        st.markdown("#### 🚀 **Unlock Teams**")
        st.markdown("- Unlimited History\n- Custom Branding\n- Slack Integration")
        st.link_button("Upgrade Plan - $19/mo", "https://buy.stripe.com/00w6oGdlF5bN4Pl8gj9Zm00")

# --- MAIN DASHBOARD ---

# 1. HEADER SECTION
st.markdown('<h1 class="main-title">Voice2SOP</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Turn your voice notes into professional documentation.</p>', unsafe_allow_html=True)

# 2. DASHBOARD METRICS (Visual "Fluff" to make it look active)
col_m1, col_m2, col_m3 = st.columns(3)
col_m1.metric("Time Saved", "2.5 hrs", "+15%")
col_m2.metric("SOPs Generated", "12", "+2")
col_m3.metric("Words Processed", "4.2k", "High")

st.divider()

# 3. WORKFLOW CONTAINER
with st.container(border=True):
    st.markdown("### 🛠️ New Documentation Project")
    
    # A visual "Stepper"
    st.markdown("`1️⃣ Setup Context` &nbsp; → &nbsp; `2️⃣ Record Audio` &nbsp; → &nbsp; `3️⃣ Generate Docs`")
    st.write("") # Spacer

    col1, col2 = st.columns(2)
    with col1:
        sop_type = st.selectbox(
            "Document Type",
            ["Standard Operating Procedure (SOP)", "Safety Protocol", "Employee Onboarding", "Technical Tutorial"],
            index=0
        )
    with col2:
        tone = st.selectbox(
            "Tone of Voice",
            ["Professional & Direct", "Friendly & Encouraging", "Strict & Compliance-Focused"],
            index=0
        )

    st.write("") # Spacer
    st.markdown("##### 🎙️ Record Process")
    st.caption("Explain the task naturally. We will structure it for you.")
    
    # AUDIO INPUT
    audio_value = st.audio_input("Tap to record")

# --- PROCESSING LOGIC ---
if audio_value and api_key:
    st.divider()
    
    with st.spinner("🤖 AI is analyzing your voice... formatting structure..."):
        try:
            genai.configure(api_key=api_key)
            
            # MODEL SETUP
            model = genai.GenerativeModel("gemini-2.5-flash") 
            
            # PREPARE DATA
            audio_bytes = audio_value.read()
            audio_part = {"mime_type": audio_value.type, "data": audio_bytes}
            
            # PROMPT
            prompt = f"""
            You are an expert technical writer. 
            I will provide an audio transcript. 
            Your goal is to convert this transcript into a professional {sop_type}.
            The tone should be {tone}.
            
            Please generate THREE distinct outputs separated by specific markers:
            
            [SECTION 1: CHECKLIST]
            A strictly action-oriented checklist (bullet points) of the steps.
            
            [SECTION 2: DOCUMENT]
            The full, formal document with Introduction, Prerequisites, Steps, and Troubleshooting.
            
            [SECTION 3: EMAIL]
            A short, professional email to the team announcing this new process.
            """
            
            # GENERATE
            response = model.generate_content([prompt, audio_part])
            full_text = response.text
            
            # PARSE
            try:
                parts = full_text.split("[SECTION")
                checklist_content = parts[1].replace(" 1: CHECKLIST]", "").strip()
                doc_content = parts[2].replace(" 2: DOCUMENT]", "").strip()
                email_content = parts[3].replace(" 3: EMAIL]", "").strip()
            except:
                checklist_content = full_text
                doc_content = full_text
                email_content = "Could not generate email draft."

            st.success("✨ Documentation Ready!")

            # TABS INTERFACE
            tab1, tab2, tab3 = st.tabs(["✅ Checklist", "📄 Full SOP", "✉️ Email Draft"])
            
            with tab1:
                st.markdown(checklist_content)
                
            with tab2:
                with st.container(border=True):
                    st.markdown(doc_content)
                
            with tab3:
                st.info("Copy this draft to send to your team.")
                st.code(email_content, language="text")

            # EXPORT SECTION
            st.markdown("### 📥 Export")
            col_ex1, col_ex2 = st.columns(2)
            
            with col_ex1:
                st.download_button(
                    label="📄 Download .TXT",
                    data=doc_content,
                    file_name="sop_draft.txt",
                    mime="text/plain"
                )
            
            with col_ex2:
                pdf_data = create_pdf(doc_content)
                st.download_button(
                    label="📕 Download PDF (Pro)",
                    data=pdf_data,
                    file_name="SOP_Document.pdf",
                    mime="application/pdf",
                    help="Professional PDF Export"
                )
                st.caption("[Unlock Custom Branding](https://buy.stripe.com/00w6oGdlF5bN4Pl8gj9Zm00)")

        except Exception as e:
            st.error(f"An error occurred: {e}")

# --- EMPTY STATE / HELP (When nothing is recorded yet) ---
elif not audio_value:
    st.divider()
    st.info("💡 **Pro Tip:** For best results, mention the 'Why' (Goal) and the 'Who' (Responsible Person) at the start of your recording.")
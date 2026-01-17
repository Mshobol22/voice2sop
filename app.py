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

# --- UI STYLING (ADAPTIVE) ---
def apply_saas_style():
    st.markdown("""
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        /* Custom Font - Applied to everything */
        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
        }

        /* Centered Title - Color automatically adjusts */
        h1 {
            font-weight: 700;
            font-size: 2.5rem;
            text-align: center;
            margin-bottom: 10px;
        }
        
        /* Subtitle Styling */
        .subtitle {
            text-align: center;
            font-size: 1.1rem;
            opacity: 0.7; /* Makes it slightly gray in both modes */
            margin-bottom: 30px;
        }
        
        /* Bigger, bolder buttons */
        div.stButton > button {
            width: 100%;
            border-radius: 8px;
            font-weight: 600;
            padding-top: 0.5rem;
            padding-bottom: 0.5rem;
        }
        </style>
    """, unsafe_allow_html=True)

apply_saas_style()

# --- SIDEBAR ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/9373/9373977.png", width=50)
    st.markdown("### **Voice2SOP** `v2.0`")
    st.caption("Turn rambles into rigid documentation.")
    st.divider()
    api_key = st.text_input("🔑 Enter Gemini API Key", type="password")
    st.divider()
    st.markdown("### 🚀 **Upgrade to PRO**")
    st.info("Unlock PDF Exports, Team Sharing, and Unlimited History.")
    st.button("Get PRO - $19/mo")

# --- MAIN APP LAYOUT ---
st.markdown("<h1>Voice2SOP</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Speak your process. We'll write the manual.</p>", unsafe_allow_html=True)

with st.container(border=True):
    st.markdown("### 1. Set Context")
    col1, col2 = st.columns(2)
    with col1:
        sop_type = st.selectbox(
            "What type of doc is this?",
            ["Standard Operating Procedure (SOP)", "Safety Protocol", "Employee Onboarding", "Technical Tutorial"]
        )
    with col2:
        tone = st.selectbox(
            "Tone of voice?",
            ["Professional & Direct", "Friendly & Encouraging", "Strict & Compliance-Focused"]
        )

    st.markdown("### 2. Record Process")
    # Using st.audio_input
    audio_value = st.audio_input("Record your voice note")

# --- LOGIC ---
if audio_value and api_key:
    st.divider()
    
    with st.spinner("🎧 Transcribing audio and formatting document..."):
        try:
            genai.configure(api_key=api_key)
            
            # 1. SETUP MODEL
            model = genai.GenerativeModel("gemini-2.5-flash") 
            
            # 2. PREPARE AUDIO DATA
            audio_bytes = audio_value.read()
            
            # Package it correctly for Gemini
            audio_part = {
                "mime_type": audio_value.type, 
                "data": audio_bytes
            }
            
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
            
            # 3. GENERATE CONTENT
            response = model.generate_content([prompt, audio_part])
            full_text = response.text
            
            # 4. PARSE OUTPUT
            try:
                parts = full_text.split("[SECTION")
                checklist_content = parts[1].replace(" 1: CHECKLIST]", "").strip()
                doc_content = parts[2].replace(" 2: DOCUMENT]", "").strip()
                email_content = parts[3].replace(" 3: EMAIL]", "").strip()
            except:
                checklist_content = full_text
                doc_content = full_text
                email_content = "Could not generate email draft."

            st.success("✨ Documentation Generated!")

            # 5. DISPLAY TABS
            tab1, tab2, tab3 = st.tabs(["📋 Action Checklist", "📄 Official SOP", "✉️ Team Email"])
            
            with tab1:
                st.markdown("#### Quick Steps")
                st.markdown(checklist_content)
                
            with tab2:
                st.markdown("#### Full Documentation")
                st.markdown(doc_content)
                
            with tab3:
                st.code(email_content, language="text")
                st.caption("Copy and paste this into Outlook/Slack.")

            # 6. EXPORT BUTTONS
            st.divider()
            col_ex1, col_ex2 = st.columns(2)
            
            with col_ex1:
                st.download_button(
                    label="Download as .TXT (Free)",
                    data=doc_content,
                    file_name="sop_draft.txt",
                    mime="text/plain"
                )
            
            with col_ex2:
                pdf_data = create_pdf(doc_content)
                st.download_button(
                    label="Download PDF (Pro)",
                    data=pdf_data,
                    file_name="SOP_Document.pdf",
                    mime="application/pdf",
                    help="Export your SOP as a professional PDF"
                )

        except Exception as e:
            st.error(f"An error occurred: {e}")

elif audio_value and not api_key:
    st.warning("⚠️ Please enter your API Key in the sidebar to process the audio.")
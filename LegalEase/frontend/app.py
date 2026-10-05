import os
import requests
import streamlit as st
from ai_core.generator import format_docx, format_pdf, format_html_preview, sanitize_text

st.set_page_config(page_title="LegalEase", page_icon="⚖️", layout="centered")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WEB_LOGO_PATH = os.path.join(BASE_DIR, "Image", "Logo.png")

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if os.path.exists(WEB_LOGO_PATH):
        st.image(WEB_LOGO_PATH, use_container_width=True)
    else:
        st.title("⚖️ LegalEase")

st.markdown("<h2 style='text-align: center;'>AI Legal Document Generator</h2>", unsafe_allow_html=True)

document_type = st.text_input("Document Type (Ex: Agreement, Contract, NDA)", placeholder="Freelance Work Contract")
parties = st.text_area("Parties Involved", placeholder="Jane Doe (Service Provider), TechNova Inc. (Client)")
terms = st.text_area("Terms & Conditions (Use semicolons for bullet points)", placeholder="Work must be delivered by May 15; Payment within 7 days of invoice")
dates = st.text_input("Effective Date", placeholder="April 15, 2025")

API_URL = "http://localhost:8000/generate"

if st.button("Generate Document", type="primary"):
    if not (document_type and parties and terms and dates):
        st.warning("Please fill in all fields before generating.")
    else:
        with st.spinner("Generating legal document via Gemini AI..."):
            try:
                payload = {
                    "document_type": document_type,
                    "parties": parties,
                    "terms": terms,
                    "dates": dates
                }
                res = requests.post(API_URL, json=payload)
                if res.status_code == 200:
                    generated_text = res.json().get("document", "")
                    st.session_state["generated_text"] = sanitize_text(generated_text)
                    st.session_state["doc_type"] = document_type
                    st.session_state["show_edit"] = False
                    st.success("Document Generated Successfully!")
                else:
                    st.error(f"Error from API: {res.json().get('detail')}")
            except Exception as e:
                st.error(f"Could not connect to FastAPI backend: {e}")

if "generated_text" in st.session_state:
    st.markdown("---")
    
    styled_preview = format_html_preview(st.session_state["generated_text"])
    st.markdown(
        f"<div style='background-color: #1e1e1e; padding: 20px; border-radius: 8px; border: 1px solid #333;'>{styled_preview}</div>", 
        unsafe_allow_html=True
    )
    
    st.write("")
    if st.button("✏️ Click to Edit Document"):
        st.session_state["show_edit"] = not st.session_state.get("show_edit", False)

    if st.session_state.get("show_edit"):
        edited_text = st.text_area("Edit Document Below:", st.session_state["generated_text"], height=300)
        st.session_state["generated_text"] = edited_text

    st.markdown("### Export & Download Options")
    
    col_txt, col_docx, col_pdf = st.columns(3)
    clean_filename = st.session_state["doc_type"].replace(" ", "_").lower()
    
    col_txt.download_button(
        label="📄 Download as .TXT",
        data=st.session_state["generated_text"],
        file_name=f"{clean_filename}.txt",
        mime="text/plain"
    )
    
    docx_file = format_docx(st.session_state["generated_text"], st.session_state["doc_type"], WEB_LOGO_PATH)
    col_docx.download_button(
        label="📝 Download as .DOCX",
        data=docx_file,
        file_name=f"{clean_filename}.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
    
    pdf_bytes = format_pdf(st.session_state["generated_text"], st.session_state["doc_type"], WEB_LOGO_PATH)
    col_pdf.download_button(
        label="📕 Download as .PDF",
        data=pdf_bytes,
        file_name=f"{clean_filename}.pdf",
        mime="application/pdf"
    )
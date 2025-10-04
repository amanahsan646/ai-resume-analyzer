# app.py
# 🚀 AI Resume Analyzer + PDF Summary Generator (Private Dashboard)

import streamlit as st
import PyPDF2
from docx import Document
import openai
import pandas as pd
import re
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# ------------------- SETTINGS -------------------
PASSWORD = "MySecret123"  # Change this
openai.api_key = "YOUR_OPENAI_API_KEY"  # Replace with your OpenAI key

st.set_page_config(page_title="AI Resume Analyzer", layout="wide")
st.title("🤖 AI Resume Analyzer & Report Generator (Private)")

# ------------------- PASSWORD -------------------
password_input = st.text_input("Enter password to continue:", type="password")
if password_input != PASSWORD:
    st.warning("❌ Incorrect password. Access denied.")
    st.stop()

# ------------------- FUNCTIONS -------------------
def extract_text(file):
    """Extract text from PDF or DOCX"""
    if file.name.endswith(".pdf"):
        reader = PyPDF2.PdfReader(file)
        return "".join([page.extract_text() for page in reader.pages if page.extract_text()])
    elif file.name.endswith(".docx"):
        doc = Document(file)
        return "\n".join([p.text for p in doc.paragraphs])
    return ""

def analyze_resume(resume_text, job_description):
    """Analyze resume with AI"""
    prompt = f"""
You are an HR AI.
Compare this resume to the job description.

Job Description:
{job_description}

Resume:
{resume_text}

1. Key skills and experience summary
2. Strengths
3. Missing or weak points
4. Match score from 1–10
"""
    response = openai.ChatCompletion.create(
        model="gpt-5-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=600
    )
    return response["choices"][0]["message"]["content"]

def generate_pdf(candidate_name, feedback):
    """Create a simple PDF summary for each candidate"""
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, 750, f"AI Resume Summary - {candidate_name}")
    c.setFont("Helvetica", 11)

    y = 720
    for line in feedback.split("\n"):
        if y < 60:
            c.showPage()
            c.setFont("Helvetica", 11)
            y = 750
        c.drawString(50, y, line[:100])  # truncate long lines
        y -= 15

    c.save()
    buffer.seek(0)
    return buffer

# ------------------- APP -------------------
job_description = st.text_area("📄 Enter Job Description", height=150)
uploaded_files = st.file_uploader("📁 Upload Resumes (PDF or DOCX)", accept_multiple_files=True)

if st.button("🚀 Analyze Resumes"):
    if not job_description:
        st.warning("Please enter a job description.")
    elif not uploaded_files:
        st.warning("Please upload at least one resume.")
    else:
        results = []
        for file in uploaded_files:
            resume_text = extract_text(file)
            if resume_text.strip():
                feedback = analyze_resume(resume_text, job_description)

                # extract numeric score
                score_match = re.search(r"\b([1-9]|10)\b", feedback)
                score = int(score_match.group(1)) if score_match else 0

                results.append({
                    "Candidate": file.name,
                    "Score": score,
                    "Feedback": feedback
                })
            else:
                results.append({
                    "Candidate": file.name,
                    "Score": 0,
                    "Feedback": "⚠️ Could not extract text."
                })

        df = pd.DataFrame(results).sort_values(by="Score", ascending=False)

        st.subheader("📊 Results")
        st.dataframe(df[["Candidate", "Score"]], use_container_width=True)

        for _, row in df.iterrows():
            with st.expander(f"🧾 {row['Candidate']} — Score: {row['Score']}"):
                st.markdown(row["Feedback"])

                pdf_buffer = generate_pdf(row["Candidate"], row["Feedback"])
                st.download_button(
                    label="⬇️ Download PDF Summary",
                    data=pdf_buffer,
                    file_name=f"{row['Candidate']}_summary.pdf",
                    mime="application/pdf"
                )

# app.py
# 🚀 Upgraded AI Resume Analyzer (with password, sorting, and CSV export)

import streamlit as st
import PyPDF2
from docx import Document
import openai
import pandas as pd
import re
from io import StringIO

# ------------------- SETTINGS -------------------
PASSWORD = "MySecret123"  # Change to your own password
openai.api_key = "YOUR_OPENAI_API_KEY"  # Replace with your OpenAI key

st.set_page_config(page_title="AI Resume Analyzer", layout="wide")
st.title("🤖 AI Resume Analyzer & Job Matcher (Private Dashboard)")

# ------------------- PASSWORD PROTECTION -------------------
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
    """Analyze resume and return AI feedback"""
    prompt = f"""
You are an HR expert AI.
Compare the following candidate's resume with this job description.

Job Description:
{job_description}

Resume:
{resume_text}

1. Summarize candidate’s key skills, experience, and education.
2. Give a match score from 1-10 (1=poor fit, 10=perfect fit).
3. List the strengths.
4. List what’s missing or can be improved.
Format the response neatly.
"""
    response = openai.ChatCompletion.create(
        model="gpt-5-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=600
    )
    return response["choices"][0]["message"]["content"]

# ------------------- APP INTERFACE -------------------
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
                analysis = analyze_resume(resume_text, job_description)

                # Extract score (find first number between 1–10)
                score_match = re.search(r"\b([1-9]|10)\b", analysis)
                score = int(score_match.group(1)) if score_match else 0

                results.append({
                    "Candidate": file.name,
                    "Score (1–10)": score,
                    "AI Feedback": analysis
                })
            else:
                results.append({
                    "Candidate": file.name,
                    "Score (1–10)": 0,
                    "AI Feedback": "⚠️ Could not read text from file."
                })

        # Sort by score (highest first)
        df = pd.DataFrame(results).sort_values(by="Score (1–10)", ascending=False)

        st.subheader("📊 Resume Analysis Results")
        st.dataframe(df[["Candidate", "Score (1–10)"]], use_container_width=True)

        # CSV Export
        csv = df.to_csv(index=False)
        st.download_button("⬇️ Download Results as CSV", data=csv, file_name="resume_analysis.csv", mime="text/csv")

        # Detailed Feedback
        for _, row in df.iterrows():
            with st.expander(f"🔍 {row['Candidate']} — Score: {row['Score (1–10)']}"):
                st.markdown(row["AI Feedback"])

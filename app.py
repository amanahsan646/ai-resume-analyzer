# app.py
# AI Resume Analyzer with password protection
# pip install streamlit openai PyPDF2 python-docx pandas

import streamlit as st
import PyPDF2
from docx import Document
import openai
import pandas as pd
import re

# ------------------- PASSWORD PROTECTION -------------------
PASSWORD = "MySecret123"  # Change this to your own strong password

st.set_page_config(page_title="Private AI Resume Analyzer", layout="wide")
st.title("🔒 Private AI Resume Analyzer & Job Matcher Dashboard")

password_input = st.text_input("Enter password to continue:", type="password")
if password_input != PASSWORD:
    st.warning("❌ Incorrect password. Access denied.")
    st.stop()

# ------------------- OPENAI SETUP -------------------
openai.api_key = "YOUR_OPENAI_API_KEY"  # Replace with your OpenAI API key

# ------------------- FUNCTIONS -------------------
def extract_text(file):
    """Extract text from PDF or DOCX"""
    if file.name.endswith(".pdf"):
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        return text
    elif file.name.endswith(".docx"):
        doc = Document(file)
        return "\n".join([para.text for para in doc.paragraphs])
    else:
        return ""

def analyze_resume(resume_text, job_description):
    """Send resume + job description to OpenAI and get summary + score"""
    prompt = f"""
You are an HR AI assistant.
Job Description: {job_description}

Candidate Resume: {resume_text}

1. Extract key points: skills, experience, education, achievements.
2. Give a ranking score from 1-10 based on how well the resume matches the job description.
3. List recommendations for improvement or missing points.
"""
    response = openai.ChatCompletion.create(
        model="gpt-5-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=500
    )
    return response['choices'][0]['message']['content']

# ------------------- STREAMLIT UI -------------------
job_description = st.text_area("Enter Job Description", height=150)

uploaded_files = st.file_uploader("Upload Resumes (PDF or DOCX)", accept_multiple_files=True)

if st.button("Analyze Resumes"):
    if not job_description:
        st.warning("Please enter a job description!")
    elif not uploaded_files:
        st.warning("Please upload at least one resume!")
    else:
        results = []
        for file in uploaded_files:
            resume_text = extract_text(file)
            if resume_text.strip():
                analysis = analyze_resume(resume_text, job_description)

                # Extract score from AI output (fallback to 0 if not found)
                score = 0
                match = re.search(r'(\d{1,2})', analysis)
                if match:
                    score = int(match.group(1))
                    if score > 10: score = 10

                results.append({
                    "Candidate": file.name,
                    "Score (1-10)": score,
                    "Analysis": analysis
                })
            else:
                results.append({
                    "Candidate": file.name,
                    "Score (1-10)": "N/A",
                    "Analysis": "Could not extract text from this file."
                })

        # Display dashboard
        df = pd.DataFrame(results)
        st.subheader("📊 Resume Analysis Dashboard")
        st.dataframe(df)

        # Show detailed analysis
        for i, row in df.iterrows():
            with st.expander(f"🔍 Details for {row['Candidate']}"):
                st.text_area("AI Analysis", row['Analysis'], height=300)

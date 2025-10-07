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

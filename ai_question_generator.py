import os
import google.generativeai as genai

genai.configure(
    api_key=os.getenv("GEMINI_API_KEY")
)

def generate_ai_questions(resume_text):

    prompt = f"""
    You are a senior technical interviewer.

    Resume:

    {resume_text}

    Generate:

    5 Technical Questions
    3 HR Questions
    2 Project Questions

    Return only questions.
    """

    model = genai.GenerativeModel("gemini-2.5-flash")

    response = model.generate_content(prompt)

    return response.text
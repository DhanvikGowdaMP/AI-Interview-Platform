import os
import google.generativeai as genai

genai.configure(
    api_key=os.getenv("GEMINI_API_KEY")
)

def evaluate_answers(questions, answers):

    prompt = f"""
    You are an expert technical interviewer.

    Interview Questions:

    {questions}

    Candidate Answers:

    {answers}

    Evaluate the answers.

    Give:

    1. Overall Score out of 10
    2. Strengths
    3. Weaknesses
    4. Suggestions for Improvement

    Return in a professional format.
    """

    model = genai.GenerativeModel("gemini-2.5-flash")

    response = model.generate_content(prompt)

    return response.text
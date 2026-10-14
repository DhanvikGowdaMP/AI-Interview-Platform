
import os
from groq import Groq


def generate_ai_questions(resume_text):

    api_key = os.environ.get("GROQ_API_KEY")

    if not api_key:
        raise ValueError("GROQ_API_KEY environment variable is not set.")

    client = Groq(api_key=api_key)

    prompt = f"""
    You are a senior technical interviewer.

    Analyze the following resume:

    {resume_text}

    Generate exactly:
    2 less complicated Technical Questions
    1 HR Question
    2 medium level short Project Questions

    Requirements:
    - Make technical questions relevant to the candidate's skills.
    - Make project questions relevant to projects in the resume.
    - Make HR questions professional and realistic.
    - Number all 5 questions clearly.
    - Return only the questions, without answers or explanations.
    """

    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.7,
    )

    return response.choices[0].message.content

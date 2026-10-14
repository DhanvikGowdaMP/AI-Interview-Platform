
import os
from groq import Groq


def evaluate_answers(questions, answers):

    api_key = os.environ.get("GROQ_API_KEY")

    if not api_key:
        raise ValueError("GROQ_API_KEY environment variable is not set.")

    client = Groq(api_key=api_key)

    prompt = f"""
    You are an expert technical interviewer.

    Interview Questions:
    {questions}

    Candidate Answers:
    {answers}

    Evaluate the candidate's answers fairly and professionally.

    Provide the following:

    1. Overall Score out of 10
    2. Strengths
    3. Weaknesses
    4. Suggestions for Improvement

    Consider technical accuracy, relevance, clarity,
    and completeness of the answers.

    Use this exact score format: Score: X/10

    Return the evaluation in a professional, well-structured format.
    """

    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.5,
    )

    return response.choices[0].message.content

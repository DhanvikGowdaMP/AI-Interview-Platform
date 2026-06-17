def generate_questions(skills):

    questions = {

        "Python": [
            "What is a list in Python?",
            "Explain OOP in Python."
        ],

        "SQL": [
            "What is a primary key?",
            "Difference between DELETE and TRUNCATE?"
        ],

        "C": [
            "What is a pointer?",
            "What is the difference between malloc and calloc?"
        ],

        "Data Structures": [
            "What is a stack?",
            "Difference between stack and queue?"
        ],

        "Git": [
            "What is Git?",
            "Difference between Git and GitHub?"
        ]
    }

    generated = {}

    for skill in skills:
        if skill in questions:
            generated[skill] = questions[skill]

    return generated
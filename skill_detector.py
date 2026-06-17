def detect_skills(text):

    skills = [
        "Python",
        "Java",
        "C",
        "C++",
        "SQL",
        "Flask",
        "HTML",
        "CSS",
        "JavaScript",
        "Machine Learning",
        "Data Structures",
        "Git"
    ]

    found_skills = []

    for skill in skills:

        if skill.lower() in text.lower():
            found_skills.append(skill)

    return found_skills
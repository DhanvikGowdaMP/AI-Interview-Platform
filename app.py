from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename
import os
from flask import Flask, render_template, request, session
from flask import redirect, url_for
import sqlite3
import pdfplumber
from skill_detector import detect_skills
#from question_generator import generate_questions
from ai_question_generator import generate_ai_questions
from datetime import datetime,timedelta
#from zoneinfo import ZoneInfo
from flask import redirect
from ai_answer_evaluator import evaluate_answers
import re
from dotenv import load_dotenv

from database import create_database
import os

if os.path.exists("users.db"):
    os.remove("users.db")
    
create_database()

load_dotenv()

app = Flask(__name__)
app.secret_key = "mysecretkey123"

UPLOAD_FOLDER = "uploads"

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Home Page
#@app.route('/')
#def home():
    #return render_template('index.html')


# Registration Page
@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        phone = request.form['phone']
        linkedin = request.form['linkedin']

        hashed_password = generate_password_hash(password)

        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE email=?",
            (email,)
        )

        existing_user = cursor.fetchone()

        if existing_user:
            conn.close()

            return render_template(
                'register.html',
                error="Email already registered. If new User try again with your email id."
            )

        cursor.execute(
            """
            INSERT INTO users
            (name,email,password,phone,linkedin)
            VALUES(?,?,?,?,?)
            """,
            (
                name,
                email,
                hashed_password,
                phone,
                linkedin
            )
        )

        

        conn.commit()
        conn.close()

        return redirect(url_for('login'))

    return render_template('register.html')


# Login Page
@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        email = request.form['email']
        password = request.form['password']

        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE email=?",
            (email,)
        )

        user = cursor.fetchone()

        conn.close()

        if user and check_password_hash(user[3], password):

             session['email'] = user[2]
             session['name'] = user[1]

             cursor = sqlite3.connect('users.db').cursor()

             cursor.execute(
                "SELECT is_admin FROM users WHERE email=?",
                (user[2],)
            )

             admin = cursor.fetchone()

             return render_template(
                'dashboard.html',
                name=user[1],
                is_admin=admin[0]
            )

        else:
            return render_template(
               'login.html',
                error="Invalid Email or Password"
            )

    return render_template('login.html')


@app.route('/upload_resume', methods=['GET', 'POST'])
def upload_resume():

    if request.method == 'POST':

        file = request.files['resume']

        if file:

            filename = secure_filename(file.filename)

            upload_folder = os.path.join(os.getcwd(), "uploads")

            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)

            filepath = os.path.join(
                upload_folder,
                filename
            )
            file.save(filepath)

            text = ""

            with pdfplumber.open(filepath) as pdf:

                for page in pdf.pages:
                    text += page.extract_text() or ""

            skills = detect_skills(text)

            # Resume Strength (1 to 5 stars)
            strength = min(5, max(1, len(skills) // 2))

            ist_time = (
                datetime.utcnow() + timedelta(hours=5, minutes=30)
            ).strftime("%Y-%m-%d %H:%M:%S")

            conn = sqlite3.connect('users.db')
            cursor = conn.cursor()

            cursor.execute(
               """
               INSERT INTO resume_analysis
               (user_email, filename, skills, upload_date, strength)
               VALUES (?, ?, ?, ?, ?)
               """,
               (
                   session['email'],
                   filename,
                   ", ".join(skills),
                   ist_time,
                   strength
                )
            )
            conn.commit()
            conn.close()
            
            questions = generate_ai_questions(text)

            session['questions'] = questions
            return render_template(
               'questions.html',
                questions=questions
)
            

    return render_template('upload_resume.html')
@app.route('/profile')
def profile():

    if 'email' not in session:
        return "Please Login First"

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
        name,
        email,
        phone,
        linkedin
        FROM users
        WHERE email=?
        """,
        (session['email'],)
    )

    user = cursor.fetchone()

    conn.close()

    return render_template(
        'profile.html',
        user=user
    )
@app.route('/history')
def history():

    if 'email' not in session:
        return "Please Login First"

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id,filename, skills, upload_date,strength
        FROM resume_analysis
        WHERE user_email = ?
        ORDER BY upload_date DESC
        """,
        (session['email'],)
    )

    records = cursor.fetchall()

    conn.close()

    return render_template(
        'history.html',
        records=records
    )
@app.route('/logout')
def logout():

    session.clear()

    return render_template('logout.html')
@app.route('/dashboard')
def dashboard():

    if 'email' not in session:
        return redirect('/login')

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    cursor.execute(
        "SELECT is_admin FROM users WHERE email=?",
        (session['email'],)
    )

    admin = cursor.fetchone()

    conn.close()

    is_admin = admin[0] if admin else 0

    return render_template(
        'dashboard.html',
        name=session['name'],
        is_admin=is_admin
    )
@app.route('/admin/analysis')
def admin_analysis():

    if 'email' not in session:
        return "Please Login First"

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    cursor.execute(
        "SELECT is_admin FROM users WHERE email=?",
        (session['email'],)
    )

    admin = cursor.fetchone()

    if not admin or admin[0] != 1:
        conn.close()
        return "Access Denied"

    cursor.execute("""
        SELECT id,
               user_email,
               filename,
               skills,
               strength,
               DATE(upload_date),
                   upload_date
        FROM resume_analysis
        ORDER BY upload_date DESC
    """)

    records = cursor.fetchall()

    conn.close()

    return render_template(
        'admin_analysis.html',
        records=records
    )
@app.route('/admin/users')
def admin_users():

    if 'email' not in session:
        return "Please Login First"

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    cursor.execute(
        "SELECT is_admin FROM users WHERE email=?",
        (session['email'],)
    )

    admin = cursor.fetchone()

    if not admin or admin[0] != 1:
        conn.close()
        return "Access Denied"

    cursor.execute("""
        SELECT id,
               name,
               email,
               Date(created_at),
               is_admin
        FROM users
    """)

    users = cursor.fetchall()

    conn.close()

    return render_template(
        'admin_users.html',
        users=users
    )
@app.route('/admins')
def admins():

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    cursor.execute("""
    SELECT name, email
    FROM users
    WHERE is_admin = 1
    """)

    admins = cursor.fetchall()

    conn.close()

    return render_template(
        'admins.html',
        admins=admins
    )
@app.route('/admin/dashboard')
def admin_dashboard():

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    # Total Users
    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]

    # Total Resume Uploads
    cursor.execute("SELECT COUNT(*) FROM resume_analysis")
    total_uploads = cursor.fetchone()[0]

    # Total Admins
    cursor.execute(
        "SELECT COUNT(*) FROM users WHERE is_admin = 1"
    )
    total_admins = cursor.fetchone()[0]

    conn.close()

    return render_template(
        'admin_dashboard.html',
        total_users=total_users,
        total_uploads=total_uploads,
        total_admins=total_admins
    )

@app.route('/admin/delete_user/<int:user_id>')
def admin_delete_user(user_id):

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    cursor.execute(
        "SELECT email, is_admin FROM users WHERE id=?",
        (user_id,)
    )

    user = cursor.fetchone()

    if not user:
        conn.close()
        return "User not found"

    # Prevent deleting yourself
    if user[0] == session['email']:
        conn.close()
        return "You cannot delete your own account."

    cursor.execute(
        "DELETE FROM users WHERE id=?",
        (user_id,)
    )

    conn.commit()
    conn.close()

    return redirect('/admin/users')
@app.route('/admin/make_admin')
def make_admin_page():

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    cursor.execute("""
    SELECT id,name,email
    FROM users
    WHERE is_admin = 0
    """)

    users = cursor.fetchall()

    conn.close()

    return render_template(
        'make_admin.html',
        users=users
    )
@app.route('/admin/promote/<int:user_id>')
def promote_user(user_id):

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE users SET is_admin=1 WHERE id=?",
        (user_id,)
    )

    conn.commit()
    conn.close()

    return redirect('/admin/make_admin')
@app.route('/admin/remove_admin')
def remove_admin_page():

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    cursor.execute("""
    SELECT id,name,email
    FROM users
    WHERE is_admin = 1
    """)

    admins = cursor.fetchall()

    conn.close()

    return render_template(
        'remove_admin.html',
        admins=admins
    )
@app.route('/admin/demote/<int:user_id>')
def demote_user(user_id):

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE users SET is_admin=0 WHERE id=?",
        (user_id,)
    )

    user = cursor.fetchone()

    if user and user[0] == session['email']:
        conn.close()
        return "You cannot remove your own admin access."

    cursor.execute(
        "UPDATE users SET is_admin=0 WHERE id=?",
        (user_id,)
    )


    conn.commit()
    conn.close()

    return redirect('/admin/remove_admin')
@app.route('/admin/edit_user/<int:user_id>',
           methods=['GET', 'POST'])
def edit_user(user_id):

    if 'email' not in session:
        return "Please Login First"

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    # Admin Check
    cursor.execute(
        "SELECT is_admin FROM users WHERE email=?",
        (session['email'],)
    )

    admin = cursor.fetchone()

    if not admin or admin[0] != 1:
        conn.close()
        return "Access Denied"

    # Update User
    if request.method == 'POST':

        phone = request.form['phone']
        linkedin = request.form['linkedin']

        cursor.execute(
            """
            UPDATE users
            SET phone=?,
                linkedin=?
            WHERE id=?
            """,
            (
                phone,
                linkedin,
                user_id
            )
        )

        conn.commit()
        conn.close()

        return redirect('/admin/users')

    # Load User Data
    cursor.execute(
        """
        SELECT
            id,
            name,
            email,
            phone,
            linkedin
        FROM users
        WHERE id=?
        """,
        (user_id,)
    )

    user = cursor.fetchone()

    conn.close()

    return render_template(
        'edit_user.html',
        user=user
    )
@app.route('/admin/user_profile/<int:user_id>')
def admin_user_profile(user_id):

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            name,
            email,
            phone,
            linkedin,
            is_admin,
            created_at
        FROM users
        WHERE id=?
        """,
        (user_id,)
    )

    user = cursor.fetchone()

    conn.close()

    return render_template(
        'admin_user_profile.html',
        user=user
    )
@app.route('/')
def home():
    return render_template('home.html')
@app.route('/admin/add_user',
           methods=['GET', 'POST'])
def admin_add_user():

    if 'email' not in session:
        return "Please Login First"

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    cursor.execute(
        "SELECT is_admin FROM users WHERE email=?",
        (session['email'],)
    )

    admin = cursor.fetchone()

    if not admin or admin[0] != 1:
        conn.close()
        return "Access Denied"

    if request.method == 'POST':

        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        phone = request.form['phone']
        linkedin = request.form['linkedin']

        cursor.execute(
            "SELECT * FROM users WHERE email=?",
            (email,)
        )

        existing_user = cursor.fetchone()

        if existing_user:
            conn.close()

            return render_template(
                'admin_add_user.html',
                error="Email already exists."
            )

        hashed_password = generate_password_hash(password)

        cursor.execute(
            """
            INSERT INTO users
            (name,email,password,phone,linkedin)
            VALUES(?,?,?,?,?)
            """,
            (
                name,
                email,
                hashed_password,
                phone,
                linkedin
            )
        )

        conn.commit()
        conn.close()

        return redirect('/admin/users')

    conn.close()

    return render_template(
        'admin_add_user.html'
    )
@app.route('/delete_analysis/<int:analysis_id>')
def delete_analysis(analysis_id):

    if 'email' not in session:
        return "Please Login First"

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT user_email
        FROM resume_analysis
        WHERE id=?
        """,
        (analysis_id,)
    )

    record = cursor.fetchone()

    if not record:
        conn.close()
        return "Record Not Found"

    if record[0] != session['email']:
        conn.close()
        return "Access Denied"

    cursor.execute(
        """
        DELETE FROM resume_analysis
        WHERE id=?
        """,
        (analysis_id,)
    )

    conn.commit()
    conn.close()

    return redirect('/history')
@app.route('/admin/confirm_delete_analysis')
def confirm_delete_analysis():

    if 'email' not in session:
        return "Please Login First"

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    cursor.execute(
        "SELECT is_admin FROM users WHERE email=?",
        (session['email'],)
    )

    admin = cursor.fetchone()

    conn.close()

    if not admin or admin[0] != 1:
        return "Access Denied"

    return render_template(
        'confirm_delete_analysis.html'
    )
@app.route('/admin/delete_all_analysis')
def delete_all_analysis():

    if 'email' not in session:
        return "Please Login First"

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    cursor.execute(
        "SELECT is_admin FROM users WHERE email=?",
        (session['email'],)
    )

    admin = cursor.fetchone()

    if not admin or admin[0] != 1:
        conn.close()
        return "Access Denied"

    cursor.execute(
        "DELETE FROM resume_analysis"
    )

    conn.commit()
    conn.close()

    return redirect('/admin/analysis')
@app.route('/admin/delete_analysis/<int:analysis_id>')
def admin_delete_analysis(analysis_id):

    if 'email' not in session:
        return "Please Login First"

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    cursor.execute(
        "SELECT is_admin FROM users WHERE email=?",
        (session['email'],)
    )

    admin = cursor.fetchone()

    if not admin or admin[0] != 1:
        conn.close()
        return "Access Denied"

    cursor.execute(
        "DELETE FROM resume_analysis WHERE id=?",
        (analysis_id,)
    )

    conn.commit()
    conn.close()

    return redirect('/admin/analysis')
@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():

    if request.method == 'POST':

        email = request.form['email']

        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE email=?",
            (email,)
        )

        user = cursor.fetchone()

        conn.close()

        if user:
            return render_template(
                'password_reset_request.html'
            )
            

        return render_template(
            'forgot_password.html',
            error="Email not found"
        )

    return render_template('forgot_password.html')
@app.route('/admin/reset_password/<int:user_id>',
           methods=['GET', 'POST'])
def reset_password(user_id):

    if 'email' not in session:
        return "Please Login First"

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    cursor.execute(
        "SELECT is_admin FROM users WHERE email=?",
        (session['email'],)
    )

    admin = cursor.fetchone()

    if not admin or admin[0] != 1:
        conn.close()
        return "Access Denied"

    if request.method == 'POST':

        new_password = request.form['password']

        hashed_password = generate_password_hash(
            new_password
        )

        cursor.execute(
            """
            UPDATE users
            SET password=?
            WHERE id=?
            """,
            (
                hashed_password,
                user_id
            )
        )

        conn.commit()
        conn.close()

        return redirect('/admin/users')

    conn.close()

    return render_template(
        'reset_password.html',
        user_id=user_id
    )
@app.route('/submit_answers', methods=['POST'])
def submit_answers():

    if 'email' not in session:
        return "Please Login First"

    answers = request.form['answers']

    questions = session.get(
        'questions',
        'Questions not found'
    )

    # AI Evaluation
    evaluation = evaluate_answers(
        questions,
        answers
    )

    # Extract Score
    import re

    match = re.search(
        r'(\d+)/10',
        evaluation
    )

    if match:
        score = match.group(1) + "/10"
    else:
        score = "N/A"

    # Current IST Time
    ist_time = (
        datetime.utcnow() +
        timedelta(hours=5, minutes=30)
    ).strftime("%Y-%m-%d %H:%M:%S")

    # Save Interview Result
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO interview_results
        (
            user_email,
            score,
            evaluation,
            interview_date
        )
        VALUES (?, ?, ?, ?)
        """,
        (
            session['email'],
            score,
            evaluation,
            ist_time
        )
    )

    conn.commit()
    conn.close()

    return render_template(
        'evaluation.html',
        evaluation=evaluation
    )
@app.route('/interview_history')
def interview_history():

    if 'email' not in session:
        return "Please Login First"

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    cursor.execute(
        "SELECT is_admin FROM users WHERE email=?",
        (session['email'],)
    )

    admin = cursor.fetchone()
    is_admin = admin[0] if admin else 0

    cursor.execute(
        """
        SELECT
            id,
            score,
            interview_date
        FROM interview_results
        WHERE user_email=?
        ORDER BY interview_date DESC
        """,
        (session['email'],)
    )

    records = cursor.fetchall()

    conn.close()

    return render_template(
        'interview_history.html',
        records=records,
        is_admin=is_admin
    )
@app.route('/view_interview/<int:report_id>')
def view_interview(report_id):

    if 'email' not in session:
        return "Please Login First"

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            user_email,
            evaluation
        FROM interview_results
        WHERE id=?
        """,
        (report_id,)
    )

    report = cursor.fetchone()

    conn.close()

    if not report:
        return "Report Not Found"

    if report[0] != session['email']:
        return "Access Denied"

    return render_template(
        'view_interview.html',
        evaluation=report[1]
    )
@app.route('/admin/interview_reports')
def admin_interview_reports():

    if 'email' not in session:
        return "Please Login First"

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    cursor.execute(
        "SELECT is_admin FROM users WHERE email=?",
        (session['email'],)
    )

    admin = cursor.fetchone()

    if not admin or admin[0] != 1:
        conn.close()
        return "Access Denied"

    cursor.execute("""
        SELECT
            id,
            user_email,
            score,
            interview_date
        FROM interview_results
        ORDER BY interview_date DESC
    """)

    records = cursor.fetchall()

    conn.close()

    return render_template(
        'admin_interview_reports.html',
        records=records
    )
@app.route('/admin/view_interview/<int:report_id>')
def admin_view_interview(report_id):

    if 'email' not in session:
        return "Please Login First"

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    cursor.execute(
        "SELECT is_admin FROM users WHERE email=?",
        (session['email'],)
    )

    admin = cursor.fetchone()

    if not admin or admin[0] != 1:
        conn.close()
        return "Access Denied"

    cursor.execute(
        """
        SELECT evaluation
        FROM interview_results
        WHERE id=?
        """,
        (report_id,)
    )

    report = cursor.fetchone()

    conn.close()

    if not report:
        return "Report Not Found"

    return render_template(
        'view_interview.html',
        evaluation=report[0]
    )

@app.route('/interview_analytics')
def interview_analytics():

    if 'email' not in session:
        return "Please Login First"

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT score
        FROM interview_results
        WHERE user_email=?
        """,
        (session['email'],)
    )

    scores = cursor.fetchall()

    conn.close()

    score_list = []

    for s in scores:
        try:
            score_list.append(
                int(s[0].replace('/10', ''))
            )
        except:
            pass

    total = len(score_list)

    best = max(score_list) if score_list else 0

    average = (
        round(sum(score_list) / total, 2)
        if total > 0 else 0
    )

    latest = score_list[0] if score_list else 0

    return render_template(
        'interview_analytics.html',
        total=total,
        best=best,
        average=average,
        latest=latest
    )
@app.route('/delete_interview/<int:report_id>')
def delete_interview(report_id):

    if 'email' not in session:
        return "Please Login First"

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT user_email
        FROM interview_results
        WHERE id=?
        """,
        (report_id,)
    )

    report = cursor.fetchone()

    if not report:
        conn.close()
        return "Report Not Found"

    if report[0] != session['email']:
        conn.close()
        return "Access Denied"

    cursor.execute(
        """
        DELETE FROM interview_results
        WHERE id=?
        """,
        (report_id,)
    )

    conn.commit()
    conn.close()

    return redirect('/interview_history')

@app.route('/admin/interview_analytics')
def admin_interview_analytics():

    if 'email' not in session:
        return "Please Login First"

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    cursor.execute(
        "SELECT is_admin FROM users WHERE email=?",
        (session['email'],)
    )

    admin = cursor.fetchone()

    if not admin or admin[0] != 1:
        conn.close()
        return "Access Denied"

    cursor.execute(
        "SELECT COUNT(*) FROM users"
    )

    total_users = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM interview_results"
    )

    total_interviews = cursor.fetchone()[0]

    cursor.execute(
        "SELECT score FROM interview_results"
    )

    scores = cursor.fetchall()

    conn.close()

    values = []

    for s in scores:
        try:
            values.append(
                int(s[0].replace('/10', ''))
            )
        except:
            pass

    avg_score = (
        round(sum(values)/len(values),2)
        if values else 0
    )

    best_score = max(values) if values else 0

    return render_template(
        'admin_interview_analytics.html',
        total_users=total_users,
        total_interviews=total_interviews,
        avg_score=avg_score,
        best_score=best_score
    )
@app.route('/admin/delete_interview/<int:report_id>')
def admin_delete_interview(report_id):

    if 'email' not in session:
        return "Please Login First"

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    cursor.execute(
        "SELECT is_admin FROM users WHERE email=?",
        (session['email'],)
    )

    admin = cursor.fetchone()

    if not admin or admin[0] != 1:
        conn.close()
        return "Access Denied"

    cursor.execute(
        """
        DELETE FROM interview_results
        WHERE id=?
        """,
        (report_id,)
    )

    conn.commit()
    conn.close()

    return redirect('/admin/interview_reports')
# Run Flask Application
if __name__ == '__main__':
    app.run(debug=True)
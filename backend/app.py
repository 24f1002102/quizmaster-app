from flask import Flask, request, jsonify, session
from flask_cors import CORS
import sqlite3
from datetime import datetime
from celery import Celery
from flask import Flask
import sqlite3
import smtplib
from email.mime.text import MIMEText
from datetime import datetime, date
import pytz
import redis
import json




app = Flask(__name__)
celery = Celery(__name__, broker='redis://localhost:6379/0')
r = redis.Redis(host='localhost', port=6379, db=1)  # Use db=1 for caching
app.secret_key = 'your_secret_key_here'
CORS(app, supports_credentials=True)

def get_db_connection():
    conn = sqlite3.connect('quiz_master.db')
    conn.row_factory = sqlite3.Row
    return conn


def get_cached_or_query(key, expiry, query_function):
    cached = r.get(key)
    if cached:
        return json.loads(cached)

    result = query_function()
    r.setex(key, expiry, json.dumps(result))
    return result


@app.route('/api/login', methods=['POST']) 
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'success': False, 'message': 'Username and password are required'}), 400

    try:
        with get_db_connection() as conn:
            # Check admin table
            admin = conn.execute(
                'SELECT * FROM admin WHERE username = ? AND password = ?',
                (username, password)
            ).fetchone()
            if admin:
                session['user'] = {
                    'id': admin['id'],
                    'username': username,
                    'role': 'admin'
                }
                return jsonify({'success': True, 'role': 'admin'})

            # Check user table
            user = conn.execute(
                'SELECT * FROM user WHERE username = ? AND password = ?',
                (username, password)
            ).fetchone()
            if user:
                session['user'] = {
                    'id': user['id'],
                    'username': username,
                    'role': 'user'
                }

                # ✅ Get current time in IST (Asia/Kolkata)
                ist = pytz.timezone('Asia/Kolkata')
                current_ist_time = datetime.now(ist).strftime('%Y-%m-%d %H:%M:%S')

                # ✅ Update last_login with IST time
                conn.execute(
                    'UPDATE user SET last_login = ? WHERE id = ?',
                    (current_ist_time, user['id'])
                )
                conn.commit()

                return jsonify({'success': True, 'role': 'user'})

        return jsonify({'success': False, 'message': 'Invalid credentials'}), 401
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500



@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    fullname = data.get('fullname')
    qualification = data.get('qualification')
    dob = data.get('dob')

    if not username or not password or not fullname:
        return jsonify({'success': False, 'message': 'Username, password, and full name are required.'}), 400

    conn = get_db_connection()
    existing_user = conn.execute('SELECT id FROM user WHERE username = ?', (username,)).fetchone()
    if existing_user:
        conn.close()
        return jsonify({'success': False, 'message': 'User with this email already exists.'}), 409

    # Store password as plain text (NOT SECURE)
    conn.execute(
        'INSERT INTO user (username, password, full_name, qualification, dob) VALUES (?, ?, ?, ?, ?)',
        (username, password, fullname, qualification, dob)
    )
    conn.commit()
    conn.close()

    return jsonify({'success': True, 'message': 'Registration successful.'}), 201


@app.route('/api/subjects', methods=['GET'])
def get_subjects():
    # Ensure user is logged in and is an admin
    if 'user' not in session or session['user']['role'] != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401

    try:
        def query():
            conn = get_db_connection()
            subjects = conn.execute('SELECT * FROM subject').fetchall()
            conn.close()
            return [dict(subject) for subject in subjects]

        subjects_list = get_cached_or_query('subjects_list', 20, query)
        return jsonify(subjects_list), 200

    except Exception as e:
        print("Error fetching subjects:", e)
        return jsonify({'error': 'Internal Server Error'}), 500


@app.route('/api/subjects', methods=['POST'])
def create_subject():
    data = request.get_json()

    name = data.get('name')
    description = data.get('description', '')

    if not name or len(name.strip()) < 3:
        return jsonify({'error': 'Subject name must be at least 3 characters'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO subject (name, description) VALUES (?, ?)',
        (name.strip(), description.strip())
    )
    conn.commit()
    conn.close()

    return jsonify({'message': 'Subject created successfully'}), 201

@app.route('/api/chapters')
def get_chapters():
    try:
        def query_chapters():
            conn = get_db_connection()
            chapters = conn.execute('''
                SELECT chapter.id, chapter.name, chapter.subject_id, subject.name AS subject_name
                FROM chapter
                JOIN subject ON chapter.subject_id = subject.id
            ''').fetchall()
            conn.close()

            chapters_list = []
            for ch in chapters:
                chapters_list.append({
                    'id': ch['id'],
                    'name': ch['name'],
                    'subject_id': ch['subject_id'],
                    'subject_name': ch['subject_name'],
                    'num_questions': 0,
                    'first_quiz_id': None
                })
            return chapters_list

        cached_chapters = get_cached_or_query('api_chapters', 20, query_chapters)
        return jsonify(cached_chapters)

    except Exception as e:
        print("Error fetching chapters:", e)
        return jsonify({'error': 'Internal Server Error'}), 500

@app.route('/api/new-chapter', methods=['POST'])
def add_chapter():
    data = request.get_json()
    chapter_id = data.get('chapter_id')
    subject_id = data.get('subject_id')
    name = data.get('chapter_name')
    description = data.get('chapter_description')

    if not (chapter_id and subject_id and name):
        return jsonify({'error': 'Missing required fields'}), 400

    try:
        conn = get_db_connection()
        conn.execute(
            'INSERT INTO chapter (id, subject_id, name, description) VALUES (?, ?, ?, ?)',
            (chapter_id, subject_id, name, description)
        )
        conn.commit()
        conn.close()
        return jsonify({'message': 'Chapter added successfully'}), 201
    except Exception as e:
        print("Error adding chapter:", e)
        return jsonify({'error': 'Failed to add chapter'}), 500

@app.route('/api/delete-subject/<int:subject_id>', methods=['DELETE'])
def delete_subject(subject_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # First, delete chapters related to the subject
        cursor.execute('DELETE FROM chapter WHERE subject_id = ?', (subject_id,))

        # Then, delete the subject itself
        cursor.execute('DELETE FROM subject WHERE id = ?', (subject_id,))

        conn.commit()
        conn.close()

        return jsonify({'message': 'Subject and its chapters deleted'}), 200

    except Exception as e:
        print("Error deleting subject:", e)
        return jsonify({'error': 'Failed to delete subject'}), 500

@app.route('/api/delete-chapter/<int:chapter_id>', methods=['DELETE'])
def delete_chapter(chapter_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # First, delete quizzes related to the chapter (if applicable)
        cursor.execute('DELETE FROM quiz WHERE chapter_id = ?', (chapter_id,))

        # Then, delete the chapter itself
        cursor.execute('DELETE FROM chapter WHERE id = ?', (chapter_id,))

        conn.commit()
        conn.close()

        return jsonify({'message': 'Chapter and its quizzes deleted'}), 200

    except Exception as e:
        print("Error deleting chapter:", e)
        return jsonify({'error': 'Failed to delete chapter'}), 500

@app.route('/api/chapter/<int:chapter_id>', methods=['GET'])
def get_chapter(chapter_id):
    try:
        def query_chapter():
            conn = get_db_connection()
            chapter = conn.execute(
                'SELECT id, subject_id, name, description FROM chapter WHERE id = ?',
                (chapter_id,)
            ).fetchone()
            conn.close()

            if chapter is None:
                return None

            return {
                'chapter_id': chapter['id'],
                'subject_id': chapter['subject_id'],
                'chapter_name': chapter['name'],
                'chapter_description': chapter['description']
            }

        key = f'api_chapter_{chapter_id}'
        result = get_cached_or_query(key, 20, query_chapter)

        if result is None:
            return jsonify({'error': 'Chapter not found'}), 404

        return jsonify(result)

    except Exception as e:
        print("Error fetching chapter:", e)
        return jsonify({'error': 'Internal Server Error'}), 500

app.route('/api/edit-chapter/<int:chapter_id>', methods=['PUT'])
def edit_chapter(chapter_id):
    data = request.get_json()
    subject_id = data.get('subject_id')
    name = data.get('chapter_name')
    description = data.get('chapter_description')

    if not (subject_id and name):
        return jsonify({'error': 'Missing required fields'}), 400

    try:
        conn = get_db_connection()
        conn.execute(
            'UPDATE chapter SET subject_id = ?, name = ?, description = ? WHERE id = ?',
            (subject_id, name, description, chapter_id)
        )
        conn.commit()
        conn.close()
        return jsonify({'message': 'Chapter updated successfully'}), 200
    except Exception as e:
        print("Error updating chapter:", e)
        return jsonify({'error': 'Failed to update chapter'}), 500

@app.route('/api/delete-quiz/<int:quiz_id>', methods=['DELETE'])
def delete_quiz(quiz_id):
    conn = get_db_connection()
    try:
        # Delete associated questions first
        conn.execute('DELETE FROM question WHERE quiz_id = ?', (quiz_id,))
        # Then delete the quiz itself
        conn.execute('DELETE FROM quiz WHERE id = ?', (quiz_id,))
        conn.commit()
        return jsonify({'message': 'Quiz and associated questions deleted successfully'}), 200
    except Exception as e:
        print('Error deleting quiz:', e)
        return jsonify({'error': 'Failed to delete quiz'}), 500
    finally:
        conn.close()

@app.route('/api/delete_question/<int:question_id>', methods=['DELETE'])
def delete_question(question_id):
    if 'user' not in session or session['user']['role'] != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401

    conn = get_db_connection()
    cur = conn.execute('SELECT * FROM question WHERE id = ?', (question_id,))
    question = cur.fetchone()
    if not question:
        conn.close()
        return jsonify({'error': 'Question not found'}), 404

    conn.execute('DELETE FROM question WHERE id = ?', (question_id,))
    conn.commit()
    conn.close()
    return jsonify({'status': f'Question {question_id} deleted successfully'}), 200


@app.route('/api/chapters-with-questions')
def chapters_with_questions():
    try:
        def query_chapters_with_questions():
            conn = get_db_connection()
            chapters = conn.execute('''
                SELECT 
                    c.*, 
                    COUNT(q.id) as question_count,
                    CASE WHEN EXISTS (
                        SELECT 1 FROM quiz WHERE chapter_id = c.id
                    ) THEN 1 ELSE 0 END as has_quiz
                FROM chapter c
                LEFT JOIN quiz ON c.id = quiz.chapter_id
                LEFT JOIN question q ON quiz.id = q.quiz_id
                GROUP BY c.id
            ''').fetchall()
            conn.close()
            return [dict(chapter) for chapter in chapters]

        key = 'api_chapters_with_questions'
        result = get_cached_or_query(key, 20, query_chapters_with_questions)
        return jsonify(result)

    except Exception as e:
        print("Error fetching chapters with questions:", e)
        return jsonify({'error': 'Internal Server Error'}), 500

@app.route('/api/quizzes')
def api_quizzes():
    if 'user' not in session or session['user']['role'] != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401

    search_query = request.args.get('query', '').strip()

    try:
        def query_quizzes():
            conn = get_db_connection()
            if search_query:
                quizzes = conn.execute(
                    'SELECT id, quiz_name, chapter_id, date_of_quiz, time_duration FROM quiz WHERE quiz_name LIKE ? ORDER BY date_of_quiz DESC',
                    (f'%{search_query}%',)
                ).fetchall()
            else:
                quizzes = conn.execute(
                    'SELECT id, quiz_name, chapter_id, date_of_quiz, time_duration FROM quiz ORDER BY date_of_quiz DESC'
                ).fetchall()
            conn.close()
            return [dict(q) for q in quizzes]

        if search_query:
            return jsonify(query_quizzes())
        else:
            key = 'api_quizzes_all'
            result = get_cached_or_query(key, 20, query_quizzes)
            return jsonify(result)

    except Exception as e:
        print("Error fetching quizzes:", e)
        return jsonify({'error': 'Internal Server Error'}), 500

@app.route('/api/questions')
def get_questions():
    try:
        def query_questions():
            conn = get_db_connection()
            questions = conn.execute('''
                SELECT id, chapter_id, title, question_statement, option1, option2, option3, option4, correct_option, quiz_id
                FROM question
                ORDER BY id
            ''').fetchall()
            conn.close()

            questions_list = []
            for q in questions:
                questions_list.append({
                    'id': q['id'],
                    'chapter_id': q['chapter_id'],
                    'title': q['title'],
                    'question_statement': q['question_statement'],
                    'option1': q['option1'],
                    'option2': q['option2'],
                    'option3': q['option3'],
                    'option4': q['option4'],
                    'correct_option': q['correct_option'],
                    'quiz_id': q['quiz_id']
                })
            return questions_list

        key = 'api_questions_all'
        result = get_cached_or_query(key, 20, query_questions)
        return jsonify(result)

    except Exception as e:
        print("Error fetching questions:", e)
        return jsonify({'error': 'Internal Server Error'}), 500


@app.route('/api/newquiz', methods=['POST'])
def create_quiz():
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['quiz_name', 'chapter_id', 'date_of_quiz', 'time_duration']
    if not all(field in data and data[field] for field in required_fields):
        return jsonify({"message": "Missing required fields"}), 400
    
    try:
        quiz_name = data['quiz_name'].strip()
        chapter_id = int(data['chapter_id'])
        date_of_quiz = data['date_of_quiz'].strip()  # Expecting YYYY-MM-DD string
        time_duration = int(data['time_duration'])
        
        conn = get_db_connection()
        conn.execute(
            'INSERT INTO quiz (quiz_name, chapter_id, date_of_quiz, time_duration) VALUES (?, ?, ?, ?)',
            (quiz_name, chapter_id, date_of_quiz, time_duration)
        )
        conn.commit()
        conn.close()
        
        return jsonify({"message": "Quiz created successfully"}), 201

    except Exception as e:
        print("Error creating quiz:", e)
        return jsonify({"message": "Failed to create quiz"}), 404



@app.route('/api/newquestion/<int:quiz_id>', methods=['GET', 'POST'])
def handle_new_question(quiz_id):
    if request.method == 'GET':
        try:
            conn = get_db_connection()
            quiz = conn.execute(
                'SELECT chapter_id FROM quiz WHERE id = ?',
                (quiz_id,)
            ).fetchone()
            conn.close()

            if quiz:
                return jsonify({'chapter_id': quiz['chapter_id']}), 200
            else:
                return jsonify({'error': 'Quiz not found'}), 404
        except Exception as e:
            print("Error fetching quiz:", e)
            return jsonify({'error': 'Server error'}), 500

    if request.method == 'POST':
        data = request.get_json()
        question_title = data.get('question_title')
        question_statement = data.get('question_statement')
        option1 = data.get('option1')
        option2 = data.get('option2')
        option3 = data.get('option3')
        option4 = data.get('option4')
        correct_answer = data.get('correct_answer')
        chapter_id = data.get('chapter_id')

        # Basic validation
        if not all([question_title, question_statement, option1, option2, option3, option4, correct_answer, chapter_id]):
            return jsonify({'error': 'Missing required fields'}), 400

        try:
            conn = get_db_connection()
            conn.execute(
    '''
    INSERT INTO question (
        quiz_id, chapter_id, title, question_statement,
        option1, option2, option3, option4, correct_option
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''',
    (
        quiz_id, chapter_id, question_title, question_statement,
        option1, option2, option3, option4, correct_answer
    )
)

            conn.commit()
            conn.close()
            return jsonify({'message': 'Question added successfully'}), 201
        except Exception as e:
            print("Error adding question:", e)
            return jsonify({'error': 'Failed to add question'}), 500


            
# Route to get the details of a question
@app.route('/api/question/<int:question_id>', methods=['GET'])
def get_question(question_id):
    conn = get_db_connection()
    question = conn.execute('SELECT * FROM question WHERE id = ?', (question_id,)).fetchone()
    conn.close()

    if question is None:
        return jsonify({'error': 'Question not found'}), 404

    return jsonify({
        'id': question['id'],
        'quiz_id': question['quiz_id'],
        'chapter_id': question['chapter_id'],
        'question_title': question['title'],
        'question_statement': question['question_statement'],
        'option1': question['option1'],
        'option2': question['option2'],
        'option3': question['option3'],
        'option4': question['option4'],
        'correct_option': question['correct_option']
    })

# Route to update an existing question
@app.route('/api/question/<int:question_id>', methods=['POST'])
def update_question(question_id):
    data = request.get_json()

    try:
        conn = get_db_connection()
        conn.execute('''
            UPDATE question SET
                title = ?, question_statement = ?, option1 = ?, option2 = ?, 
                option3 = ?, option4 = ?, correct_option = ?
            WHERE id = ?
        ''', (
            data['question_title'], data['question_statement'], data['option1'],
            data['option2'], data['option3'], data['option4'], data['correct_option'],
            question_id
        ))
        conn.commit()
        conn.close()
        return jsonify({'message': 'Question updated successfully'}), 200
    except Exception as e:
        print("Error updating question:", e)
        return jsonify({'error': 'Failed to update question'}), 500



@app.route('/api/summary')
def api_summary():
    if 'user' not in session or session['user']['role'] != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401

    try:
        def query_summary():
            conn = get_db_connection()

            top_scores_data = conn.execute('''
                SELECT subject.name AS subject_name, MAX(score.total_scored) AS top_score
                FROM score
                JOIN chapter ON score.chapter_id = chapter.id
                JOIN subject ON chapter.subject_id = subject.id
                GROUP BY subject.id
            ''').fetchall()

            user_attempts_data = conn.execute('''
                SELECT subject.name AS subject_name, COUNT(score.quiz_id) AS attempts
                FROM score
                JOIN chapter ON score.chapter_id = chapter.id
                JOIN subject ON chapter.subject_id = subject.id
                GROUP BY subject.id
            ''').fetchall()

            conn.close()

            subjects = [row['subject_name'] for row in top_scores_data]
            top_scores = [row['top_score'] for row in top_scores_data]
            user_attempts = [row['attempts'] for row in user_attempts_data]

            return {
                'subjects': subjects,
                'top_scores': top_scores,
                'user_attempts': user_attempts
            }

        key = 'api_summary_data'
        result = get_cached_or_query(key, 20, query_summary)
        return jsonify(result), 200

    except Exception as e:
        print("Error fetching summary:", e)
        return jsonify({'error': 'Internal Server Error'}), 500

@app.route('/api/users', methods=['GET'])
def get_all_users():
    try:
        def query_users():
            conn = get_db_connection()
            users = conn.execute('''
                SELECT id, username, full_name, qualification, dob
                FROM user
                ORDER BY id
            ''').fetchall()
            conn.close()
            return [dict(user) for user in users]

        key = 'api_all_users'
        result = get_cached_or_query(key, 20, query_users)
        return jsonify(result), 200

    except Exception as e:
        print("Error fetching users:", e)
        return jsonify({'error': 'Failed to fetch users'}), 500

@app.route('/api/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if user exists
        user = cursor.execute('SELECT * FROM user WHERE id = ?', (user_id,)).fetchone()
        if not user:
            conn.close()
            return jsonify({"error": "User not found"}), 404

        # Delete the user
        cursor.execute('DELETE FROM user WHERE id = ?', (user_id,))
        conn.commit()
        conn.close()

        return jsonify({"message": "User deleted"}), 200

    except Exception as e:
        print("Error deleting user:", e)
        return jsonify({"error": "Failed to delete user"}), 500


@app.route('/api/logout', methods=['POST'])
def logout():
    session.clear()  # Clear session if you're using Flask sessions
    return jsonify({"message": "Logged out"}), 200

# Admin is Done here!






@app.route('/api/quizzess')
def get_quizzes():
    if 'user' not in session or session['user']['role'] != 'user':
        return jsonify({'error': 'Unauthorized'}), 401

    user_id = session['user']['id']

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Fetch quizzes NOT attempted by this user
        cursor.execute('''
            SELECT q.id, q.quiz_name, q.date_of_quiz, q.time_duration,
                   COUNT(ques.id) AS num_questions
            FROM quiz q
            LEFT JOIN question ques ON q.id = ques.quiz_id
            WHERE q.id NOT IN (
                SELECT quiz_id FROM score WHERE user_id = ?
            )
            GROUP BY q.id
            HAVING COUNT(ques.id) > 0
            ORDER BY q.date_of_quiz ASC
        ''', (user_id,))
        quizzes = cursor.fetchall()
        conn.close()

        result = [
            {
                'id': row[0],
                'quiz_name': row[1],
                'date_of_quiz': row[2],
                'time_duration': row[3],
                'num_questions': row[4]
            }
            for row in quizzes
        ]

        return jsonify(result), 200

    except Exception as e:
        print("Error fetching quizzes:", e)
        return jsonify({'error': 'Internal Server Error'}), 500


@app.route('/api/quiz/<int:quiz_id>')
def get_quiz_details(quiz_id):
    # Check if user is logged in and is of role 'user'
    if 'user' not in session or session['user']['role'] != 'user':
        return jsonify({'error': 'Unauthorized'}), 401

    user_id = session['user']['id']

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Optional: Check if user has already attempted the quiz
        cursor.execute('SELECT 1 FROM score WHERE user_id = ? AND quiz_id = ?', (user_id, quiz_id))
        if cursor.fetchone():
            conn.close()
            return jsonify({'error': 'You have already attempted this quiz'}), 403

        # Fetch quiz details if not attempted
        cursor.execute('''
            SELECT q.id, q.quiz_name, q.date_of_quiz, q.time_duration,
                   s.name AS subject_name,
                   c.name AS chapter_name,
                   (SELECT COUNT(*) FROM question WHERE quiz_id = q.id) AS num_questions
            FROM quiz q
            JOIN chapter c ON q.chapter_id = c.id
            JOIN subject s ON c.subject_id = s.id
            WHERE q.id = ?
        ''', (quiz_id,))
        
        row = cursor.fetchone()
        conn.close()

        if row is None:
            return jsonify({'error': 'Quiz not found'}), 404

        quiz_details = {
            'id': row[0],
            'quiz_name': row[1],
            'date_of_quiz': row[2],
            'time_duration': row[3],
            'subject': row[4],
            'chapter_name': row[5],
            'num_questions': row[6]
        }

        return jsonify(quiz_details), 200

    except Exception as e:
        print("Error fetching quiz details:", e)
        return jsonify({'error': 'Internal server error'}), 500






@app.route('/api/scores', methods=['GET'])
def get_scores():
    if 'user' not in session or session['user']['role'] != 'user':
        return jsonify({'error': 'Unauthorized'}), 401

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        query = request.args.get('query', '').lower()
        user_id = session['user']['id']  # ✅ Use logged-in user ID

        cursor.execute('''
            SELECT 
                q.quiz_name,
                q.time_duration,
                s.total_scored,
                s.time_stamp,
                sub.name AS subject_name,
                ch.name AS chapter_name,
                q.id AS quiz_id,
                (
                    SELECT COUNT(*) 
                    FROM question 
                    WHERE question.quiz_id = q.id
                ) AS num_questions
            FROM score s
            JOIN quiz q ON s.quiz_id = q.id
            JOIN chapter ch ON q.chapter_id = ch.id
            JOIN subject sub ON ch.subject_id = sub.id
            WHERE s.user_id = ?
        ''', (user_id,))

        all_scores = cursor.fetchall()
        conn.close()

        result = []
        for row in all_scores:
            score_data = {
                'quiz_name': row['quiz_name'],
                'time_duration': row['time_duration'],
                'total_scored': row['total_scored'],
                'date_attempted': row['time_stamp'],
                'subject_name': row['subject_name'],
                'chapter_name': row['chapter_name'],
                'id': row['quiz_id'],
                'num_questions': row['num_questions']
            }

            if query:
                if query in row['quiz_name'].lower() or \
                   query in row['subject_name'].lower() or \
                   query in row['chapter_name'].lower():
                    result.append(score_data)
            else:
                result.append(score_data)

        return jsonify(result), 200

    except Exception as e:
        print("Error fetching scores:", e)
        return jsonify({'error': 'Internal Server Error'}), 500

@app.route('/api/current_user', methods=['GET'])
def get_current_user():
    if 'user' in session and session['user'].get('role') == 'user':
        conn = get_db_connection()
        user = conn.execute(
            'SELECT id, username FROM user WHERE username = ?',
            (session['user']['username'],)
        ).fetchone()
        conn.close()
        if user:
            return jsonify({
                'user_id': user['id'],
                'username': user['username'],
                'email': user['username']  # because you're using email as username
            }), 200
    return jsonify({'error': 'Unauthorized'}), 401



@app.route('/api/user-summary')
def user_summary():
    if 'user' not in session or session['user']['role'] != 'user':
        return jsonify({'error': 'Unauthorized'}), 401

    user_id = session['user']['id']
    
    try:
        conn = get_db_connection()
        
        # 1. Subject-wise quizzes attended
        subject_data = conn.execute('''
            SELECT s.name AS subject, COUNT(DISTINCT q.id) AS quiz_count
            FROM score sc
            JOIN quiz q ON sc.quiz_id = q.id
            JOIN chapter c ON q.chapter_id = c.id
            JOIN subject s ON c.subject_id = s.id
            WHERE sc.user_id = ?
            GROUP BY s.id
        ''', (user_id,)).fetchall()

        # 2. Month-wise quizzes attempted (last 6 months)
        month_data = conn.execute('''
            SELECT 
                strftime('%Y-%m', sc.time_stamp) AS month,
                COUNT(DISTINCT sc.quiz_id) AS quiz_count
            FROM score sc
            WHERE sc.user_id = ?
            AND sc.time_stamp >= date('now', '-6 months')
            GROUP BY strftime('%Y-%m', sc.time_stamp)
            ORDER BY month DESC
            LIMIT 6
        ''', (user_id,)).fetchall()

        conn.close()

        # Format data for charts
        subjects = [row['subject'] for row in subject_data]
        quizzes_attended = [row['quiz_count'] for row in subject_data]
        
        months = [row['month'] for row in month_data]
        quizzes_attempted = [row['quiz_count'] for row in month_data]

        return jsonify({
            'subjects': subjects,
            'quizzes_attended': quizzes_attended,
            'months': months,
            'quizzes_attempted': quizzes_attempted
        })

    except Exception as e:
        print("Error fetching summary data:", e)
        return jsonify({'error': 'Failed to load summary data'}), 500



@app.route('/api/startquiz/<int:quiz_id>', methods=['GET'])
def start_quiz(quiz_id):
    user = session.get('user')
    if not user or user['role'] != 'user':
        return jsonify({'error': 'Unauthorized'}), 401

    user_id = user['id']

    try:
        conn = get_db_connection()

        # Fetch quiz metadata
        quiz = conn.execute('''
            SELECT 
                q.id, q.quiz_name, q.time_duration, q.date_of_quiz,
                c.name AS chapter_name, s.name AS subject,
                (SELECT COUNT(*) FROM question WHERE quiz_id = q.id) AS num_questions
            FROM quiz q
            JOIN chapter c ON q.chapter_id = c.id
            JOIN subject s ON c.subject_id = s.id
            WHERE q.id = ?
        ''', (quiz_id,)).fetchone()

        if quiz is None:
            return jsonify({'error': 'Quiz not found'}), 404

        # Fetch quiz questions
        questions = conn.execute('''
            SELECT id, question_statement, option1, option2, option3, option4, correct_option
            FROM question
            WHERE quiz_id = ?
        ''', (quiz_id,)).fetchall()

        quiz_data = {
            "quiz": dict(quiz),
            "questions": [dict(q) for q in questions]
        }

        return jsonify(quiz_data)

    except Exception as e:
        return jsonify({'error': str(e)}), 500









@app.route('/api/save-answer', methods=['POST'])
def save_answer():
    data = request.get_json()
    quiz_id = data.get('quiz_id')
    question_id = data.get('question_id')
    answer = data.get('answer')
    remaining_time = data.get('remaining_time')

    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401

    conn = get_db_connection()
    conn.execute('''
        INSERT INTO temp_answers (user_id, quiz_id, question_id, selected_option, remaining_time)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(user_id, quiz_id, question_id)
        DO UPDATE SET selected_option = excluded.selected_option, remaining_time = excluded.remaining_time
    ''', (user_id, quiz_id, question_id, answer, remaining_time))
    conn.commit()
    conn.close()

    return jsonify({'success': True})


@app.route('/api/submit-quiz', methods=['POST'])
def submit_quiz():
    if 'user' not in session or session['user']['role'] != 'user':
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.get_json()
    quiz_id = data.get('quiz_id')
    score = data.get('score')
    answers = data.get('answers')

    if not quiz_id or score is None or not answers:
        return jsonify({'error': 'Invalid data'}), 400

    user_id = session['user']['id']

    conn = get_db_connection()
    cursor = conn.cursor()

    quiz_info = cursor.execute(
        'SELECT chapter_id FROM quiz WHERE id = ?', (quiz_id,)
    ).fetchone()

    if not quiz_info:
        return jsonify({'error': 'Quiz not found'}), 404

    chapter_id = quiz_info['chapter_id']

    cursor.execute('''
        INSERT INTO score (quiz_id, chapter_id, user_id, time_stamp, total_scored)
        VALUES (?, ?, ?, datetime('now'), ?)
    ''', (quiz_id, chapter_id, user_id, score))

    conn.commit()
    conn.close()

    return jsonify({'success': True})




@app.route('/api/clear-quiz-session/<int:quiz_id>', methods=['POST'])
def clear_quiz_session(quiz_id):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401

    conn = get_db_connection()
    conn.execute('DELETE FROM temp_answers WHERE user_id = ? AND quiz_id = ?', (user_id, quiz_id))
    conn.commit()
    conn.close()

    return jsonify({'success': True})


# Backend Jobs A
from flask import Flask, request, jsonify, g
from celery import Celery
from celery.schedules import crontab
import sqlite3
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from datetime import datetime, date
import pytz
import ssl
from flask import current_app
import csv
from flask import send_from_directory



# === Flask-Mail (SMTP) Configuration ===
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = '24f1002102@ds.study.iitm.ac.in'  # ✅ IITM DS Gmail
app.config['MAIL_PASSWORD'] = 'xaqo tjhb baao auda'             # 🔐 Gmail App Password
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

# === Celery Configuration ===
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.timezone = 'Asia/Kolkata'
celery.conf.update(app.config)

class ContextTask(celery.Task):
    def __call__(self, *args, **kwargs):
        with app.app_context():
            return self.run(*args, **kwargs)

celery.Task = ContextTask



def send_email(to_email, subject, body):
    print("📥 ENTERED send_email function")
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = app.config['MAIL_USERNAME']
    msg['To'] = to_email
    msg['Reply-To'] = app.config['MAIL_USERNAME']
    msg.add_header('X-Mailer', 'Flask-Mail')
    msg.add_header('X-Priority', '3')

    try:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(app.config['MAIL_SERVER'], app.config['MAIL_PORT'], context=context) as server:
            server.set_debuglevel(1)  # 👈 SHOW SMTP conversation
            server.login(app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
            server.sendmail(msg['From'], [msg['To']], msg.as_string())
        print(f"✅ Email sent to {to_email}")
    except Exception as e:
        print(f"❌ Failed to send email to {to_email}: {e}")


# === Daily Reminder Task with Minute Matching ===
@celery.task(name='send_daily_reminders')
def send_daily_reminders():
    print("⏰ [Celery Task] Triggered send_daily_reminders at:", datetime.now())
    now = datetime.now()
    today_str = date.today().isoformat()
    current_hour = now.hour
    current_minute = now.minute

    conn = get_db_connection()

    # Get users who have set reminders for this exact time
    users = conn.execute('''
        SELECT * FROM user
        WHERE reminder_hour = ? AND reminder_minute = ?
    ''', (current_hour, current_minute)).fetchall()

    for user in users:
        user_id = user['id']
        email = user['username']
        full_name = user['full_name']
        last_login = user['last_login'] or "2000-01-01"  # fallback for NULLs

        # 🆕 Case 1: New quizzes created after last login and not attempted
        new_quizzes = conn.execute('''
            SELECT q.quiz_name, q.date_of_creation, q.time_duration
            FROM quiz q
            WHERE datetime(q.date_of_creation) > datetime(?)
              AND date(q.date_of_quiz) >= date('now')
              AND NOT EXISTS (
                  SELECT 1 FROM score s
                  WHERE s.quiz_id = q.id AND s.user_id = ?
              )
        ''', (last_login, user_id)).fetchall()

        if new_quizzes:
            for quiz in new_quizzes:
                subject = quiz['quiz_name']
                quiz_date = quiz['date_of_creation']
                duration = quiz['time_duration']

                body = f"""
👋 Hey {full_name},

📝 Quiz Name - **{subject}**  
📢 A new quiz has just been published and it looks important!  
📅 **Date**: {quiz_date}  
⏳ **Duration**: {duration} minutes

Since your last visit, new quizzes have been added.  
Don't miss out — log in now and check them out! 🚀

🔗 [Login to Quiz Master](http://localhost:5173/login)

Cheers,  
– Quiz Master 🧠
"""
                send_email(email, f"🚨 New Quiz Alert: {subject}", body)

            continue  # ⛔ Skip other reminders if new quizzes were sent

        # 📋 Case 2: Upcoming quizzes that are unattempted
        unattempted_quizzes = conn.execute('''
            SELECT quiz.quiz_name
            FROM quiz
            WHERE quiz.id NOT IN (
                SELECT quiz_id FROM score WHERE user_id = ?
            )
            AND date(quiz.date_of_quiz) >= date('now')
        ''', (user_id,)).fetchall()

        if unattempted_quizzes:
            quiz_list = "\n".join([f"• {q['quiz_name']}" for q in unattempted_quizzes])
            body = f"""
👋 Hello {full_name},

📌 You have some **pending quizzes** waiting for you!

{quiz_list}

Take a few minutes and give them a try — your progress matters! 🌟  
🎯 [Login and start attempting](http://localhost:5173/login)

All the best,  
– Quiz Master 📚
"""
            send_email(email, "📌 Reminder: Quizzes Awaiting Your Attempt!", body)

        else:
            # 🧭 Case 3: General nudge (no new quizzes, no pending)
            body = f"""
👋 Hi {full_name},

Just a quick reminder to drop by and check if there’s anything new for you on Quiz Master!  
Even a few minutes today can keep you ahead. 🚀

🔍 Stay curious. Stay consistent.

🔗 [Visit Quiz Master](http://localhost:5173/login)

Have a great day!  
– Quiz Master 🌟
"""
            send_email(email, "⏰ Daily Check-in – Quiz Master", body)

    conn.close()

@app.route('/api/user/reminder', methods=['PUT'])
def update_reminder_time():
    if 'user' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    user_id = session['user']['id']
    data = request.get_json()
    reminder_hour = data.get('reminder_hour')
    reminder_minute = data.get('reminder_minute', 0)

    conn = get_db_connection()
    conn.execute('''
        UPDATE user
        SET reminder_hour = ?, reminder_minute = ?
        WHERE id = ?
    ''', (reminder_hour, reminder_minute, user_id))
    print("Updating reminder time:", reminder_hour, reminder_minute)

    conn.commit()
    conn.close()

    return jsonify({'status': 'Reminder time updated'})

@app.route('/api/user/reminder', methods=['GET'])
def get_reminder_time():
    if 'user' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    user_id = session['user']['id']
    conn = get_db_connection()
    user = conn.execute(
        'SELECT reminder_hour, reminder_minute FROM user WHERE id = ?',
        (user_id,)
    ).fetchone()
    conn.close()

    if user:
        return jsonify({
            'reminder_hour': user['reminder_hour'],
            'reminder_minute': user['reminder_minute'] if user['reminder_minute'] is not None else 0
        })
    return jsonify({'error': 'User not found'}), 404





# BACKEND B 

from datetime import datetime
from premailer import transform
import sqlite3
from celery import Celery
from celery.schedules import crontab

@celery.task(name='send_monthly_reports') 
def send_monthly_reports():
    from datetime import datetime
    import calendar

    now = datetime.now()
    month = now.month - 1
    year = now.year
    if month == 0:  # January → last December
        month = 12
        year -= 1

    conn = get_db_connection()
    users = conn.execute('SELECT id, username FROM user').fetchall()

    for user in users:
        user_id = user['id']
        email = user['username']  # assuming username = email

        try:
            html, email, subject= generate_monthly_report(user_id, month, year, conn)
            emailsend(email, subject, html)

            subject = f"[Quiz Master] Monthly Report - {calendar.month_name[month]} {year}"
            print(f"✅ Sent report to {email}")
        except Exception as e:
            print(f"❌ Failed to send report to {email}: {e}")


def generate_monthly_report(user_id, month, year, conn):
    conn.row_factory = sqlite3.Row
    
    # Get user details
    user = conn.execute('SELECT * FROM user WHERE id = ?', (user_id,)).fetchone()
    if not user:
        return None, None, None

    # Get quiz attempts for the month
    scores = conn.execute('''
        SELECT q.quiz_name, s.total_scored, s.time_stamp,
               c.name AS chapter_name, subj.name AS subject_name, q.id AS quiz_id,
               (SELECT COUNT(*) FROM question WHERE quiz_id = q.id) AS total_questions
        FROM score s
        JOIN quiz q ON s.quiz_id = q.id
        JOIN chapter c ON q.chapter_id = c.id
        JOIN subject subj ON c.subject_id = subj.id
        WHERE s.user_id = ?
          AND strftime('%m', s.time_stamp) = ?
          AND strftime('%Y', s.time_stamp) = ?
        ORDER BY s.time_stamp
    ''', (user_id, f"{month:02d}", str(year))).fetchall()

    # Calculate statistics
    total_quizzes = len(scores)
    total_score = sum(row['total_scored'] for row in scores)
    total_possible = sum(row['total_questions'] for row in scores) if scores else 1
    avg_score = total_score / total_quizzes if total_quizzes else 0
    avg_percentage = (total_score / total_possible * 100) if total_quizzes else 0

    # Calculate rankings
    quiz_rankings = []
    quiz_avg_scores = []
    for row in scores:
        all_scores = conn.execute(
            'SELECT user_id, total_scored FROM score WHERE quiz_id = ? ORDER BY total_scored DESC',
            (row['quiz_id'],)
        ).fetchall()
        ranks = {r['user_id']: idx+1 for idx, r in enumerate(all_scores)}
        quiz_rankings.append(ranks.get(user_id, 0))
        
        # Calculate average score for this quiz
        avg = conn.execute(
            'SELECT AVG(total_scored) FROM score WHERE quiz_id = ?',
            (row['quiz_id'],)
        ).fetchone()[0] or 0
        quiz_avg_scores.append(avg)

    # Calculate overall ranking
    cursor = conn.execute('''
        SELECT user_id, SUM(total_scored) as total
        FROM score
        WHERE strftime('%m', time_stamp) = ? AND strftime('%Y', time_stamp) = ?
        GROUP BY user_id
        ORDER BY total DESC
    ''', (f"{month:02d}", str(year)))
    
    ranked_users = cursor.fetchall()
    rankings = {user[0]: idx+1 for idx, user in enumerate(ranked_users)}
    user_rank = rankings.get(user_id, 0)
    total_users = len(ranked_users)

    # Generate chapter-wise analysis
    chapter_stats = {}
    for row in scores:
        chapter = row['chapter_name']
        if chapter not in chapter_stats:
            chapter_stats[chapter] = {
                'count': 0,
                'total_score': 0,
                'total_possible': 0,
                'subject': row['subject_name']
            }
        chapter_stats[chapter]['count'] += 1
        chapter_stats[chapter]['total_score'] += row['total_scored']
        chapter_stats[chapter]['total_possible'] += row['total_questions']

    # Get class averages for chapters
    chapter_class_avgs = {}
    for chapter in chapter_stats.keys():
        avg = conn.execute('''
    SELECT AVG(s.total_scored), AVG(q_stats.total_questions)
    FROM score s
    JOIN (
        SELECT q.id AS quiz_id, COUNT(ques.id) AS total_questions
        FROM quiz q
        JOIN question ques ON q.id = ques.quiz_id
        GROUP BY q.id
    ) AS q_stats ON s.quiz_id = q_stats.quiz_id
    JOIN quiz q ON s.quiz_id = q.id
    JOIN chapter c ON q.chapter_id = c.id
    WHERE c.name = ?
      AND strftime('%m', s.time_stamp) = ?
      AND strftime('%Y', s.time_stamp) = ?
''', (chapter, f"{month:02d}", str(year))).fetchone()

        chapter_class_avgs[chapter] = avg or (0, 1)  # Handle division by zero

    month_name = datetime(int(year), int(month), 1).strftime('%B %Y')
    current_year = datetime.now().year

    # Email-friendly HTML with inline styles
    html = f"""
    <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
    <html xmlns="http://www.w3.org/1999/xhtml">
    <head>
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <title>Monthly Quiz Report - {month_name}</title>
        <style type="text/css">
            /* Client-specific styles */
            body, table, td, a {{ -webkit-text-size-adjust: 100%; -ms-text-size-adjust: 100%; }}
            table, td {{ mso-table-lspace: 0pt; mso-table-rspace: 0pt; }}
            img {{ -ms-interpolation-mode: bicubic; border: 0; height: auto; line-height: 100%; outline: none; text-decoration: none; }}
        </style>
    </head>
    <body style="margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; color: #333333; background-color: #f8f9fa;">
        <!-- Main container -->
        <table border="0" cellpadding="0" cellspacing="0" width="100%" style="background-color: #f8f9fa;">
            <tr>
                <td align="center" valign="top">
                    <table border="0" cellpadding="0" cellspacing="0" width="900" style="background-color: #ffffff; margin: 20px 0; box-shadow: 0 4px 6px rgba(0,0,0,0.1); border-radius: 8px; overflow: hidden;">
                        <!-- Header -->
                        <tr>
                            <td align="center" style="background-color: #4361ee; color: #ffffff; padding: 20px; text-align: center;">
                                <h1 style="margin: 0; font-size: 24px; font-weight: 600;">Monthly Quiz Activity Report</h1>
                                <h2 style="margin: 10px 0 0 0; font-size: 18px; font-weight: 400;">{month_name}</h2>
                            </td>
                        </tr>
                        
                        <!-- Greeting -->
                        <tr>
                            <td style="padding: 20px;">
                                <h3 style="margin: 0 0 8px 0; font-size: 18px;">Hello, <span style="color: #4361ee;">{user['full_name']}</span></h3>
                                <p style="margin: 0; color: #6c757d;">Here's your performance summary for <strong>{month_name}</strong></p>
                            </td>
                        </tr>
                        
                        <!-- Stats Grid -->
                        <tr>
                            <td style="padding: 0 20px;">
                                <table border="0" cellpadding="0" cellspacing="0" width="90%" style="margin-bottom: 20px;">
                                    <tr>
                                        <td width="25%" valign="top" style="padding: 10px; text-align: center; background-color: #e6f0ff; border-radius: 8px; margin-right: 10px;">
    <div style="font-size: 14px; color: #6c757d;">Quizzes Taken</div>
    <div style="font-size: 28px; font-weight: 700; color: #4361ee;">{total_quizzes}</div>
</td>

<td width="25%" valign="top" style="padding: 10px; text-align: center; background-color: #e6f0ff; border-radius: 8px; margin-right: 10px;">
    <div style="font-size: 14px; color: #6c757d;">Average Score</div>
    <div style="font-size: 28px; font-weight: 700; color: #4361ee;">{avg_score:.1f}</div>
</td>

<td width="25%" valign="top" style="padding: 10px; text-align: center; background-color: #e6f0ff; border-radius: 8px; margin-right: 10px;">
    <div style="font-size: 14px; color: #6c757d;">Average Percentage</div>
    <div style="font-size: 28px; font-weight: 700; color: #4361ee;">{avg_percentage:.1f}<span style="font-size: 16px;">%</span></div>
</td>

<td width="25%" valign="top" style="padding: 10px; text-align: center; background-color: #e6f0ff; border-radius: 8px;">
    <div style="font-size: 14px; color: #6c757d;">Overall Rank</div>
    <div style="font-size: 28px; font-weight: 700; color: #4361ee;">
        <span style="display: inline-block; width: 28px; height: 28px; line-height: 28px; border-radius: 50%; background-color: #4361ee; color: white; font-weight: 600; font-size: 14px;">{user_rank}</span>
        <span style="font-size: 14px;">/{total_users}</span>
    </div>
</td>

                                            </div>
                                        </td>
                                    </tr>
                                </table>
                            </td>
                        </tr>
                        
                        <!-- Divider -->
                        <tr>
                            <td style="padding: 0 20px;">
                                <table border="0" cellpadding="0" cellspacing="0" width="100%">
                                    <tr>
                                        <td style="border-bottom: 1px solid #eeeeee; height: 1px; width: 100%; margin: 20px 0;"></td>
                                    </tr>
                                </table>
                            </td>
                        </tr>
                        
                        <!-- Quiz Performance -->
                        <tr>
                            <td style="padding: 0 20px;">
                                <h3 style="font-size: 18px; font-weight: 600; color: #4361ee; margin: 20px 0 10px 0;">Quiz Performance Details</h3>
                                {"""
                                <table border="0" cellpadding="0" cellspacing="0" width="100%" style="margin-bottom: 20px; border-collapse: collapse;">
                                    <tr style="background-color: #e6f0ff; color: #4361ee; font-weight: 600; text-transform: uppercase; font-size: 13px;">
                                        <th style="padding: 12px 15px; text-align: left;">Quiz Name</th>
                                        <th style="padding: 12px 15px; text-align: left;">Subject</th>
                                        <th style="padding: 12px 15px; text-align: left;">Chapter</th>
                                        <th style="padding: 12px 15px; text-align: left;">Date</th>
                                        <th style="padding: 12px 15px; text-align: left;">Your Score</th>
                                        <th style="padding: 12px 15px; text-align: left;">Rank</th>
                                    </tr>
                                    """ + "".join([
                                        f"""
                                        <tr style="border-bottom: 1px solid #eeeeee;">
                                            <td style="padding: 12px 15px;">{row['quiz_name']}</td>
                                            <td style="padding: 12px 15px;">{row['subject_name']}</td>
                                            <td style="padding: 12px 15px;">{row['chapter_name']}</td>
                                            <td style="padding: 12px 15px;">{row['time_stamp'].split(' ')[0]}</td>
                                            <td style="padding: 12px 15px; font-weight: 600;">{row['total_scored']}/{row['total_questions']}</td>
                                            <td style="padding: 12px 15px;">
                                                <span style="display: inline-block; width: 25px; height: 25px; line-height: 25px; text-align: center; border-radius: 50%; background-color: #4361ee; color: white; font-weight: bold;">{quiz_rankings[idx]}</span>
                                            </td>
                                        </tr>
                                        """ for idx, row in enumerate(scores)
                                    ]) + """
                                </table>
                                """ if scores else """
                                <div style="text-align: center; padding: 30px; color: #6c757d; font-style: italic;">
                                    You didn't attempt any quizzes this month. Keep learning!
                                </div>
                                """}
                            </td>
                        </tr>
                        
                        <!-- Chapter-wise Analysis -->
                        {f"""
                        <tr>
                            <td style="padding: 0 20px;">
                                <table border="0" cellpadding="0" cellspacing="0" width="100%">
                                    <tr>
                                        <td style="border-bottom: 1px solid #eeeeee; height: 1px; width: 100%; margin: 20px 0;"></td>
                                    </tr>
                                </table>
                            </td>
                        </tr>
                        <tr>
                            <td style="padding: 0 20px 20px 20px;">
                                <h3 style="font-size: 18px; font-weight: 600; color: #4361ee; margin: 20px 0 10px 0;">Chapter-wise Analysis</h3>
                                <table border="0" cellpadding="0" cellspacing="0" width="100%" style="margin-bottom: 20px; border-collapse: collapse;">
                                    <tr style="background-color: #e6f0ff; color: #4361ee; font-weight: 600; text-transform: uppercase; font-size: 13px;">
                                        <th style="padding: 12px 15px; text-align: left;">Chapter</th>
                                        <th style="padding: 12px 15px; text-align: left;">Subject</th>
                                        <th style="padding: 12px 15px; text-align: left;">Quizzes</th>
                                        <th style="padding: 12px 15px; text-align: left;">Your Avg</th>
                                        
                                    </tr>
                                    """ + "".join([
                                        f"""
                                        <tr style="border-bottom: 1px solid #eeeeee;">
                                            <td style="padding: 12px 15px;">{chapter}</td>
                                            <td style="padding: 12px 15px;">{stats['subject']}</td>
                                            <td style="padding: 12px 15px;">{stats['count']}</td>
                                            <td style="padding: 12px 15px;">{(stats['total_score']/stats['total_possible']*100):.1f}%</td>
                                        

                                        </tr>
                                        """ for chapter, stats in chapter_stats.items()
                                    ]) + """
                                </table>
                            </td>
                        </tr>
                        """ if scores else ""}
                        
                        <!-- Footer -->
                        <tr>
                            <td style="padding: 20px; text-align: center; color: #6c757d; font-size: 14px; border-top: 1px solid #eeeeee;">
                                <p style="margin: 0;">This is an automated report. For any questions, please contact 24f1002102@ds.study.iitm.ac.in</p>
                                <p style="margin: 10px 0 0 0;">© {current_year} Quiz Application. All rights reserved. | <a href="#" style="color: #4361ee; text-decoration: none;">Unsubscribe</a></p>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """

    
    # Use premailer to inline all CSS styles
    inlined_html = transform(html)
    subject = f"Monthly Quiz Report – {month_name}"
    return inlined_html, user['email'] if 'email' in user else user['username'], subject

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def emailsend(to_email, subject, html_content):
    # Create the email message
    msg = MIMEMultipart()
    msg['From'] = '24f1002102@ds.study.iitm.ac.in'
    msg['To'] = to_email
    msg['Subject'] = subject

    # Attach the HTML content
    msg.attach(MIMEText(html_content, 'html'))

    try:
        # Connect to SMTP server
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login('24f1002102@ds.study.iitm.ac.in', 'xaqo tjhb baao auda')  # App Password
            server.send_message(msg)
            print(f"✅ Email sent to {to_email}")
    except Exception as e:
        print(f"❌ Error sending email to {to_email}: {e}")

@app.route('/test-monthly')
def test_monthly():
    send_monthly_reports.delay()
    return "Triggered monthly report"

import os

app.config['EXPORT_FOLDER'] = os.path.join(os.getcwd(), 'exports')
os.makedirs(app.config['EXPORT_FOLDER'], exist_ok=True)


# Backedn C
# === Celery Task to Generate CSV and Email ===
@celery.task(name='export_csv_job')
def export_csv_job(user_id, email):
    conn = get_db_connection()
    rows = conn.execute('''
        SELECT q.id AS quiz_id, q.quiz_name, c.id AS chapter_id, c.name AS chapter_name,
               s.name AS subject_name, q.date_of_quiz, sc.total_scored,
               (SELECT COUNT(*) FROM question WHERE quiz_id = q.id) AS total_questions
        FROM score sc
        JOIN quiz q ON sc.quiz_id = q.id
        JOIN chapter c ON q.chapter_id = c.id
        JOIN subject s ON c.subject_id = s.id
        WHERE sc.user_id = ?
    ''', (user_id,)).fetchall()

    now = datetime.now().strftime('%Y%m%d%H%M%S')
    filename = f'user_{user_id}_quiz_export_{now}.csv'
    filepath = os.path.join(current_app.config['EXPORT_FOLDER'], filename)
    os.makedirs(current_app.config['EXPORT_FOLDER'], exist_ok=True)

    with open(filepath, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            "quiz_id", "quiz_name", "chapter_id", "chapter_name", "subject_name",
            "date_of_quiz", "score_obtained", "remarks"
        ])
        for r in rows:
            total_questions = r['total_questions']
            scored = r['total_scored']
            score_display = f"{scored}/{total_questions}" if total_questions > 0 else f"{scored}/0"
            pct = (scored / total_questions) * 100 if total_questions > 0 else 0.0
            remark = (
                'Excellent' if pct >= 90 else
                'Good' if pct >= 70 else
                'Needs Improvement' if pct >= 50 else
                'Poor'
            )
            writer.writerow([
                r['quiz_id'], r['quiz_name'], r['chapter_id'], r['chapter_name'], r['subject_name'],
                r['date_of_quiz'], score_display, remark
            ])

    link = f"http://localhost:5000/exports/{filename}"
    body = f"Hi,\n\nYour quiz export is ready.\nDownload it here:\n{link}"
    emailsender(email, "✅ Your Quiz CSV Export is Ready", body)

# === API Endpoint to Trigger CSV Export ===
@app.route('/api/export_csv', methods=['POST'])
def trigger_csv_export():
    data = request.get_json()
    user_id = data.get('user_id')
    user_email = data.get('email')

    if not user_id or not user_email:
        return jsonify({'status': 'error', 'message': 'User ID and Email required'}), 400

    export_csv_job.delay(user_id, user_email)
    return jsonify({'status': 'processing', 'message': 'CSV export started. You will be notified once done.'})

# === Serve Exported CSV Files ===
@app.route('/exports/<filename>')
def download_export(filename):
    return send_from_directory(app.config['EXPORT_FOLDER'], filename, as_attachment=True)


# === Email Utility ===
def emailsender(to_email, subject, body):
    msg = MIMEMultipart()
    msg['From'] = app.config['MAIL_USERNAME']
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
        server.send_message(msg)


from celery.schedules import crontab

celery.conf.beat_schedule = {
    'send-daily-reminders-every-minute': {
        'task': 'send_daily_reminders',
        'schedule': crontab(),  # every minute
    },
    'send-monthly-reports': {
        'task': 'send_monthly_reports',
        'schedule': crontab(minute=0, hour=9, day_of_month=1),  # 7:00 AM, 1st of each month
    }
}

if __name__ == "__main__":
    # Optional: run your Flask app if needed
    app.run(debug=True)


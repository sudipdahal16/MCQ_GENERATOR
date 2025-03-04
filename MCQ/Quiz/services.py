import sqlite3
import google.generativeai as genai
import time
from django.http import JsonResponse
import uuid  # Add this import at the top
import MySQLdb
# Configure generative AI
genai.configure(api_key='AIzaSyAWm9frf4gsvLD61IPxqDu7w_vOLoc2A40')


def initialize_database():
    """Initializes the MySQL database and creates the questions table if it does not exist."""
    conn = MySQLdb.connect(
        host="127.0.0.1",
        user="root",
        passwd="",
        db="mcq_db"
    )
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS questions (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        `key` VARCHAR(255) UNIQUE,
                        `value` TEXT,
                        correct_answer TEXT
                      )''')
    conn.commit()
    conn.close()

def extract_correct_answer(question):
    """Extracts the correct answer from the formatted question."""
    lines = question.split("\n")
    for line in lines:
        if line.startswith("Correct Answer:"):
            return line.split(":", 1)[1].strip()
    return None

def generate_question(text, num_questions):
    """Generates multiple-choice questions and stores them in MySQL database."""
    initialize_database()

    # Connect to MySQL instead of SQLite
    conn = MySQLdb.connect(
        host="127.0.0.1",
        user="root",
        passwd="",
        db="mcq_db"
    )
    cursor = conn.cursor()

    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(f"""Create a practice test with {num_questions} multiple choice questions on the following text: {text}.
              Each question should have:
              - A clear question.
              - Four answer options
              - The correct answer clearly indicated.
              - Questions should be generated in the same language of provided text.
              - Answer for each MCQ should be random.
              Format:
              ## MCQ
              [question]
              A) [option A]
              B) [option B]  
              C) [option C]
              D) [option D]  
              Correct Answer: [correct option]""")

    questions = response.candidates[0].content.parts[0].text
    mcqs_with_ids = []  

    for question in questions.split("## MCQ"):
        if question.strip():
            correct_answer = extract_correct_answer(question)
            question_without_answer = "\n".join(
                line for line in question.split("\n") if not line.startswith("Correct Answer:")
            )

            key = str(uuid.uuid4())

            try:
                cursor.execute(
                    "INSERT INTO questions (`key`, `value`, correct_answer) VALUES (%s, %s, %s)",
                    (key, question_without_answer, correct_answer),
                )
                conn.commit()
                question_id = cursor.lastrowid  

                mcqs_with_ids.append({'id': question_id, 'question': question_without_answer})
            except MySQLdb.IntegrityError as e:
                print(f"IntegrityError: {e}. Skipping duplicate question.")

    cursor.close()
    conn.close()
    return mcqs_with_ids



def get_answer(request, question_id):
    """Fetches the correct answer for a given question ID from MySQL."""
    conn = MySQLdb.connect(
        host="127.0.0.1",
        user="root",
        passwd="",
        db="mcq_db"
    )
    cursor = conn.cursor()
    cursor.execute("SELECT correct_answer FROM questions WHERE id = %s", (question_id,))
    result = cursor.fetchone()
    conn.close()

    if result:
        return JsonResponse({'correct_answer': result[0]})
    else:
        return JsonResponse({'error': 'Answer not found'}, status=404)

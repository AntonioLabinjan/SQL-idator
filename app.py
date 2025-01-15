from flask import Flask, render_template, request, redirect, url_for, flash, session
import mysql.connector
import random
import threading
import time

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # For flash messages

# MySQL connection details
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',
    'database': 'app_test_db'
}

# Function to get a database connection
def get_db_connection():
    return mysql.connector.connect(**db_config)

# Function to fetch table information
def get_tables_info():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Get the list of tables
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()

    # Get column details for each table
    table_info = {}
    for table in tables:
        table_name = table[0]
        cursor.execute(f"DESCRIBE {table_name}")
        columns = cursor.fetchall()
        table_info[table_name] = columns

    conn.close()
    return tables, table_info

# Route to set a timer
@app.route('/set_timer', methods=['POST'])
def set_timer():
    # Extract duration from form
    duration = 40
    
    if duration is not None:
        duration = int(duration)
    else:
        # Handle the case where the duration is missing
        return "Duration not provided", 400

    # Start the timer task
    def timer_task():
        time.sleep(duration)
        flash(f"Time's up! The timer set for {duration} seconds has expired.", 'warning')

    threading.Thread(target=timer_task).start()

    flash(f"Timer started for {duration} seconds.", 'info')
    
    return redirect(url_for('index'))

# Route to validate a query and track correct answers
@app.route('/validate_query', methods=['POST'])
def validate_query():
    query = request.form['query']
    expected_result = request.form['expected_result'].split(',')  # Convert back to list

    # Initialize correct answers in session if not present
    if 'correct_answers' not in session:
        session['correct_answers'] = 0

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(query)
        result = cursor.fetchall()
        conn.close()

        # Extract the first element from each row (assuming a single column in the result)
        result_cleaned = [str(row[0]) for row in result]

        if sorted(result_cleaned) == sorted(expected_result):
            flash("Correct!", 'success')
            session['correct_answers'] += 1  # Increment correct answers
        else:
            flash(f"Incorrect. Expected: {expected_result}, Got: {result_cleaned}", 'danger')

        return redirect(url_for('index'))

    except Exception as e:
        conn.close()
        flash(f"Error executing query: {e}", 'danger')
        return redirect(url_for('index'))

@app.route('/')
def index():
    tables, table_info = get_tables_info()

    # Predefined tasks/questions for the exam
    tasks = [
        {
            "task": "Write a query to get all book names.",
            "expected_result": [
                "Harry Potter and the Sorcerer's Stone",
                '1984',
                'The Hobbit',
                'Pride and Prejudice'
            ]
        },
        {
            "task": "Write a query to get all authors born after 1950.",
            "expected_result": ['J.K. Rowling']
        },
        {
            "task": "Write a query to find all genres in the books table.",
            "expected_result": ['Fantasy', 'Dystopian', 'Romance']
        },
        {
            "task": "Write a query to find books published before 1950.",
            "expected_result": ['1984', 'The Hobbit', 'Pride and Prejudice']
        },
        {
            "task": "Write a query to get the total number of books.",
            "expected_result": [4]
        }
    ]

    # Select a random task
    selected_task = random.choice(tasks)

    return render_template('index.html', tables=tables, table_info=table_info, tasks=[selected_task], correct_answers=session.get('correct_answers', 0))

if __name__ == '__main__':
    app.run(debug=True)

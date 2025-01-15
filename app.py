from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector
import random

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

  #  return render_template('index.html', tables=tables, table_info=table_info, task=selected_task)
    return render_template('index.html', tables=tables, table_info=table_info, tasks=[selected_task])


@app.route('/query', methods=['POST'])
def query():
    query = request.form['query']
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(query)
        result = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        conn.close()
        return render_template('index.html', result=result, columns=columns, query=query)
    except Exception as e:
        conn.close()
        flash(f"Error executing query: {e}", 'danger')
        return redirect(url_for('index'))

@app.route('/validate_query', methods=['POST'])
def validate_query():
    query = request.form['query']
    expected_result = request.form['expected_result'].split(',')  # Convert back to list

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
        else:
            flash(f"Incorrect. Expected: {expected_result}, Got: {result_cleaned}", 'danger')

        return redirect(url_for('index'))

    except Exception as e:
        conn.close()
        flash(f"Error executing query: {e}", 'danger')
        return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)

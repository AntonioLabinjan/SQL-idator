from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector

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
                ("Harry Potter and the Sorcerer's Stone", 1, 'Fantasy', 1997),
                ('1984', 2, 'Dystopian', 1949),
                ('The Hobbit', 3, 'Fantasy', 1937),
                ('Pride and Prejudice', 4, 'Romance', 1813)
            ]
        }
    ]

    return render_template('index.html', tables=tables, table_info=table_info, tasks=tasks)


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

    # Hardcoded expected result
    expected_result = [
        "Harry Potter and the Sorcerer's Stone",
        '1984',
        'The Hobbit',
        'Pride and Prejudice'
    ]

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(query)
        result = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        conn.close()

        # Extract the first element from each row (assuming a single column in the result)
        result_cleaned = [row[0] for row in result]

        # Debugging print statements
        print(f"Expected Result: {expected_result}")
        print(f"Actual Result: {result_cleaned}")

        if sorted(result_cleaned) == sorted(expected_result):
            flash("Correct!", 'success')
        else:
            flash(f"Incorrect. Expected: {expected_result}, Got: {result_cleaned}", 'danger')

        return render_template('index.html', result=result, columns=columns, query=query)

    except Exception as e:
        conn.close()
        flash(f"Error executing query: {e}", 'danger')
        return render_template('index.html', query=query)


if __name__ == '__main__':
    app.run(debug=True)

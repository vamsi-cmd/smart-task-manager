from flask import Flask, render_template, request, redirect, session
from flask_bcrypt import Bcrypt
import sqlite3

app = Flask(__name__)

app.secret_key = "secret123"

bcrypt = Bcrypt(app)


def get_db_connection():

    conn = sqlite3.connect('database.db')

    conn.row_factory = sqlite3.Row

    return conn


@app.route('/')
def home():
    if 'user' not in session:
        return redirect('/login')

    search = request.args.get('search', '')

    priority = request.args.get('priority', '')

    status = request.args.get('status', '')

    conn = get_db_connection()

    query = "SELECT * FROM tasks WHERE 1=1"

    params = []

    if search:

        query += " AND title LIKE ?"

        params.append(f"%{search}%")

    if priority:

        query += " AND priority=?"

        params.append(priority)

    if status:

        query += " AND status=?"

        params.append(status)

    tasks = conn.execute(query, params).fetchall()

    total_tasks = conn.execute(
        "SELECT COUNT(*) FROM tasks"
    ).fetchone()[0]

    completed_tasks = conn.execute(
        "SELECT COUNT(*) FROM tasks WHERE status='Completed'"
    ).fetchone()[0]

    pending_tasks = conn.execute(
        "SELECT COUNT(*) FROM tasks WHERE status='Pending'"
    ).fetchone()[0]

    high_priority_tasks = conn.execute(
        "SELECT COUNT(*) FROM tasks WHERE priority='High'"
    ).fetchone()[0]

    conn.close()

    return render_template(
        'index.html',
        tasks=tasks,
        total_tasks=total_tasks,
        completed_tasks=completed_tasks,
        pending_tasks=pending_tasks,
        high_priority_tasks=high_priority_tasks
    )


@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        username = request.form['username']

        password = bcrypt.generate_password_hash(
            request.form['password']
        ).decode('utf-8')

        conn = get_db_connection()

        conn.execute(
            'INSERT INTO users (username, password) VALUES (?, ?)',
            (username, password)
        )

        conn.commit()
        conn.close()

        return redirect('/login')

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()

        user = conn.execute(
            'SELECT * FROM users WHERE username=?',
            (username,)
        ).fetchone()

        conn.close()

        if user and bcrypt.check_password_hash(
            user['password'],
            password
        ):

            session['user'] = username

            return redirect('/')

    return render_template('login.html')


@app.route('/logout')
def logout():

    session.pop('user', None)

    return redirect('/login')


@app.route('/add', methods=['POST'])
def add_task():

    title = request.form['title']

    conn = get_db_connection()

    conn.execute(
        'INSERT INTO tasks (title, status) VALUES (?, ?)',
        (title, 'Pending')
    )

    conn.commit()
    conn.close()

    return redirect('/')


@app.route('/delete/<int:id>')
def delete_task(id):

    conn = get_db_connection()

    conn.execute(
        'DELETE FROM tasks WHERE id=?',
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect('/')


@app.route('/complete/<int:id>')
def complete_task(id):

    conn = get_db_connection()

    conn.execute(
        'UPDATE tasks SET status=? WHERE id=?',
        ('Completed', id)
    )

    conn.commit()
    conn.close()

    return redirect('/')


if __name__ == '__main__':
    app.run(debug=True)
import requests
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import check_password_hash
import database as db
import click

app = Flask(__name__)
app.secret_key = 'supersecretkey'

API_URL = "http://marcconrad.com/uob/heart/api.php"

# Command to initialize the database
@app.cli.command("init-db")
def init_db_command():
    """Clears the existing data and creates new tables."""
    db.init_db()
    click.echo("Initialized the database.")

@app.route('/')
def index():
    # Fetch the user's score from the database to ensure it's up-to-date
    if 'username' in session:
        user = db.get_user_by_username(session['username'])
        if user:
            session['score'] = user[3]
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'username' in session:
        return redirect(url_for('play'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if not username or not password:
            flash('Username and password are required.', 'error')
            return redirect(url_for('register'))
        
        if db.create_user(username, password):
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Username already exists.', 'error')
            return redirect(url_for('register'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'username' in session:
        return redirect(url_for('play'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = db.get_user_by_username(username)
        
        if user and check_password_hash(user[2], password):
            session['username'] = user[1]
            session['score'] = user[3]
            flash('Logged in successfully!', 'success')
            return redirect(url_for('play'))
        else:
            flash('Invalid username or password.', 'error')
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/play')
def play():
    if 'username' not in session:
        flash('Please log in to play.', 'error')
        return redirect(url_for('login'))

    try:
        response = requests.get(API_URL)
        response.raise_for_status()
        data = response.json()
        session['solution'] = data['solution']
        
        image_url = data['question']

    except requests.exceptions.RequestException as e:
        flash(f"Error fetching question from API: {e}", 'error')
        return redirect(url_for('leaderboard'))

    return render_template('game.html', image_url=image_url, score=session['score'])

@app.route('/submit', methods=['POST'])
def submit():
    if 'username' not in session:
        return redirect(url_for('login'))

    try:
        guess = int(request.form['guess'])
        solution = int(session.get('solution'))

        if guess == solution:
            session['score'] += 1
            db.update_score(session['username'], session['score'])
            flash('Correct!', 'success')
        else:
            flash(f"Wrong! The correct answer was {solution}.", 'danger')

    except (ValueError, TypeError):
        flash('Invalid answer submitted.', 'error')

    return redirect(url_for('play'))


@app.route('/leaderboard')
def leaderboard():
    leaders = db.get_leaderboard()
    return render_template('leaderboard.html', leaderboard=leaders)

@app.route('/game_over')
def game_over():
    final_score = session.get('score', 0)
    return render_template('game_over.html', score=final_score)

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('score', None)
    session.pop('solution', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)

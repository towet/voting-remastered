from flask import Flask, render_template, request, url_for, redirect, Blueprint, send_from_directory, flash, session, jsonify
from flask_wtf import FlaskForm
from wtforms.fields import StringField, SubmitField
from wtforms.validators import DataRequired
import os
import json
from login import login_check as lc
from register import register_on_submit as rs

main = Blueprint('main', __name__)

secret_key = str(os.urandom(24))

app = Flask(__name__)
app.config['TESTING'] = False
app.config['DEBUG'] = True
app.config['FLASK_ENV'] = 'deployment'
app.config['SECRET_KEY'] = secret_key

app.register_blueprint(main)

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    url = StringField('DataURL', validators=[])
    submit = SubmitField('LOGIN')

class VoteForm(FlaskForm):
    votes = StringField('Votes')
    submit = SubmitField('Submit Votes')

# File to store votes
VOTES_FILE = 'votes.json'

def load_votes():
    try:
        with open(VOTES_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_votes(votes):
    with open(VOTES_FILE, 'w') as f:
        json.dump(votes, f)

def get_results():
    votes = load_votes()
    results = {}
    
    # Initialize results structure
    positions = ['kubsa_chair', 'secretary', 'treasurer', 'non_resident']
    for position in positions:
        results[position] = {}
    
    # Count votes for each position and candidate
    for user_votes in votes.values():
        for position, candidate in user_votes.items():
            if position not in results:
                results[position] = {}
            if candidate not in results[position]:
                results[position][candidate] = 0
            results[position][candidate] += 1
    
    return results

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('is_admin'):
        return redirect(url_for('admin_dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        url = form.url.data
        status = lc(email, url)
        if status == "Successfully Logged in!":
            session['user_email'] = email
            return redirect(url_for('vote'))
        else:
            flash(status)
            return render_template('fail.html', msg=status)
    return render_template('index.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if session.get('is_admin'):
        return redirect(url_for('admin_dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        url = form.url.data
        status = rs(email, url)
        if status == "Registration Successful!":
            flash("Registration successful! Please login.")
            return redirect(url_for('login'))
        else:
            flash(status)
            return render_template('fail.html', msg=status)
    return render_template('register.html', form=form)

@app.route('/vote', methods=['GET', 'POST'])
def vote():
    if session.get('is_admin'):
        return redirect(url_for('admin_dashboard'))
    if 'user_email' not in session:
        flash('Please login first')
        return redirect(url_for('login'))
    
    form = VoteForm()
    if request.method == 'POST' and form.validate_on_submit():
        votes_data = request.form.get('votes')
        if votes_data:
            votes = load_votes()
            votes[session['user_email']] = json.loads(votes_data)
            save_votes(votes)
            flash('Thank you for voting!')
            return redirect(url_for('home'))
    
    return render_template('vote.html', form=form)

@app.route('/results')
def results():
    if 'user_email' not in session:
        flash('Please login first')
        return redirect(url_for('login'))
    
    if not session.get('is_admin'):
        flash('Only administrators can view results')
        return redirect(url_for('home'))
    
    results = get_results()
    return render_template('results.html', results=results)

@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if session.get('is_admin'):
        return redirect(url_for('admin_dashboard'))
    
    if request.method == 'POST':
        # In a real application, use secure credentials
        if request.form.get('username') == 'admin' and request.form.get('password') == 'admin123':
            session['is_admin'] = True
            session['user_email'] = 'admin'  # Set admin email for session
            flash('Welcome, Administrator!')
            return redirect(url_for('admin_dashboard'))
        flash('Invalid credentials')
    return render_template('admin_login.html')

@app.route('/admin-dashboard')
def admin_dashboard():
    if not session.get('is_admin'):
        flash('Please login as admin')
        return redirect(url_for('admin_login'))
    
    # Get voting results
    results = get_results()
    
    # Format the results for display
    formatted_results = {}
    for position in ['kubsa_chair', 'secretary', 'treasurer', 'non_resident']:
        formatted_results[position] = {}
    
    votes = load_votes()
    for user_votes in votes.values():
        for position, candidate in user_votes.items():
            if position in formatted_results:
                formatted_results[position][candidate] = formatted_results[position].get(candidate, 0) + 1
    
    return render_template('admin_dashboard.html', results=formatted_results)

@app.route('/logout')
def logout():
    session.pop('user_email', None)
    session.pop('is_admin', None)
    flash('You have been logged out')
    return redirect(url_for('home'))

@app.route('/favicon.ico') 
def favicon(): 
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

if __name__ == "__main__":
    app.run(debug=True)
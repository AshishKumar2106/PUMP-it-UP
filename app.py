import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mail import Mail, Message
import mysql.connector
import bcrypt
import random
from datetime import date

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'supersecretkey')  # Use env var or fallback

# MySQL Configuration (from environment variables)
db_config = {
    "host": os.getenv('MYSQL_HOST', 'localhost'),
    "user": os.getenv('MYSQL_USER', 'root'),
    "password": os.getenv('MYSQL_PASSWORD', 'Ashish@123'),
    "database": os.getenv('MYSQL_DATABASE', 'pump_it_up')
}

# Mail Configuration (from environment variables)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME', 'ashish.kumar.789566@gmail.com')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD', 'qboq vaku kvhl tiit')

mail = Mail(app)

# ... (rest of app.py remains unchanged) ...

# --- Database Functions ---
def get_db_connection():
    return mysql.connector.connect(**db_config)

# --- Calculator Functions ---
def calculate_bmi(weight_kg, height_m):
    try:
        bmi = weight_kg / (height_m ** 2)
        return round(bmi, 2)
    except:
        return "Invalid"

def calculate_bmr(weight_kg, height_cm, age, gender):
    try:
        if gender.lower() == "male":
            bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age + 5
        else:
            bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age - 161
        return round(bmr, 2)
    except:
        return "Invalid"

def calculate_protein(weight_kg):
    try:
        protein = weight_kg * 1.2
        return round(protein, 2)
    except:
        return "Invalid"

def calculate_calories(weight_kg, activity_level):
    try:
        bmr = calculate_bmr(weight_kg, weight_kg * 100, 30, "male")  # Use height in cm (assumed 170cm for simplicity)
        if bmr == "Invalid":
            return "Invalid"
        levels = {"sedentary": 1.2, "light": 1.375, "moderate": 1.55, "active": 1.725}
        return round(float(bmr) * levels[activity_level], 2)
    except:
        return "Invalid"

def calculate_creatine(weight_kg):
    try:
        creatine = weight_kg * 0.03
        return round(creatine, 2)
    except:
        return "Invalid"

def calculate_nutrition(weight_kg, goal):
    try:
        base_calories = calculate_calories(weight_kg, "moderate")
        if base_calories == "Invalid":
            return {"calories": "Invalid", "protein": "Invalid"}
        
        base_calories = float(base_calories)
        if goal == "gain":
            calories = base_calories + 500
        elif goal == "loss":
            calories = base_calories - 500
        else:  # maintain
            calories = base_calories

        if goal == "gain":
            protein = weight_kg * 2.0
        elif goal == "loss":
            protein = weight_kg * 1.6
        else:  # maintain
            protein = weight_kg * 1.2

        return {"calories": round(calories, 2), "protein": round(protein, 2)}
    except:
        return {"calories": "Invalid", "protein": "Invalid"}

# --- Routes ---
@app.route('/')
def home():
    quotes = ["Push harder!", "Strength is earned.", "You’re stronger than you think."]
    return render_template('home.html', quote=random.choice(quotes))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT password, is_premium FROM users WHERE username = %s", (username,))
        result = cursor.fetchone()
        conn.close()
        if result and bcrypt.checkpw(password.encode(), result[0].encode()):
            session['username'] = username
            session['is_premium'] = result[1]
            flash("Logged in successfully!", "success")
            return redirect(url_for('home'))
        flash("Invalid credentials!", "error")
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (username, password, email, is_premium) VALUES (%s, %s, %s, %s)", 
                           (username, hashed_pw, email, False))
            conn.commit()
            flash("Registered successfully! Please log in.", "success")
            return redirect(url_for('login'))
        except mysql.connector.IntegrityError:
            flash("Username already exists!", "error")
        conn.close()
    return render_template('register.html')

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT username FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        if user:
            reset_token = str(random.randint(100000, 999999))
            msg = Message("Password Reset - PUMP it UP", sender=app.config['MAIL_USERNAME'], recipients=[email])
            msg.body = f"Use this code to reset your password: {reset_token}\nReset here: http://127.0.0.1:5000/reset/{reset_token}"
            mail.send(msg)
            session['reset_email'] = email
            session['reset_token'] = reset_token
            flash("Reset code sent to your email!", "success")
            return redirect(url_for('reset_password', token=reset_token))
        flash("Email not found!", "error")
        conn.close()
    return render_template('forgot_password.html')

@app.route('/reset/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if request.method == 'POST':
        if session.get('reset_token') == token and session.get('reset_email'):
            new_password = request.form['password']
            hashed_pw = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt())
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET password = %s WHERE email = %s", (hashed_pw, session['reset_email']))
            conn.commit()
            conn.close()
            session.pop('reset_email', None)
            session.pop('reset_token', None)
            flash("Password reset successfully! Please log in.", "success")
            return redirect(url_for('login'))
        flash("Invalid or expired token!", "error")
    return render_template('forgot_password.html', reset=True, token=token)

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('is_premium', None)
    flash("Logged out successfully!", "success")
    return redirect(url_for('home'))

@app.route('/calculators', methods=['GET', 'POST'])
def calculators():
    if 'username' not in session:
        flash("Please log in first!", "error")
        return redirect(url_for('login'))
    
    results = {"bmi": "", "bmr": "", "protein": "", "calories": "", "creatine": "", "nutrition": {"calories": "", "protein": ""}}
    if request.method == 'POST':
        # Determine which tab submitted the form (Basic or Premium)
        if 'height' in request.form:  # Basic tab
            weight = float(request.form.get('weight', 0))
            height = float(request.form.get('height', 0))
            height_cm = float(request.form.get('height_cm', 0))
            age = int(request.form.get('age', 0))
            gender = request.form.get('gender', 'male')
            activity = request.form.get('activity', 'moderate')

            if weight <= 0 or height <= 0 or height_cm <= 0 or age <= 0:
                flash("Please enter valid positive numbers for weight, height, and age!", "error")
                return render_template('calculators.html', results=results, is_premium=session.get('is_premium', False))

            results["bmi"] = calculate_bmi(weight, height)
            results["bmr"] = calculate_bmr(weight, height_cm, age, gender)
            results["protein"] = calculate_protein(weight)
            results["calories"] = calculate_calories(weight, activity)
        elif 'goal' in request.form:  # Premium tab
            weight = float(request.form.get('weight', 0))
            goal = request.form.get('goal', 'maintain')

            if weight <= 0:
                flash("Please enter a valid positive weight!", "error")
                return render_template('calculators.html', results=results, is_premium=session.get('is_premium', False))

            if session.get('is_premium'):
                results["creatine"] = calculate_creatine(weight)
                results["nutrition"] = calculate_nutrition(weight, goal)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        if 'height' in request.form:  # Only update if Basic tab is used
            cursor.execute("UPDATE users SET weight=%s, height=%s, age=%s, gender=%s WHERE username=%s",
                           (weight, height, age, gender, session['username']))
        cursor.execute("INSERT INTO progress (username, date, weight) VALUES (%s, %s, %s)",
                       (session['username'], date.today(), weight))
        conn.commit()
        conn.close()
    
    return render_template('calculators.html', results=results, is_premium=session.get('is_premium', False))

@app.route('/nutrition')
def nutrition():
    if 'username' not in session:
        flash("Please log in first!", "error")
        return redirect(url_for('login'))
    return render_template('nutrition.html', is_premium=session.get('is_premium', False))

@app.route('/workouts')
def workouts():
    if 'username' not in session:
        flash("Please log in first!", "error")
        return redirect(url_for('login'))
    if not session.get('is_premium', False):
        flash("Upgrade to premium to access workouts!", "error")
        return redirect(url_for('home'))
    return render_template('workouts.html')

@app.route('/profile')
def profile():
    if 'username' not in session:
        flash("Please log in first!", "error")
        return redirect(url_for('login'))
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT username, email, is_premium, weight, height, age, gender FROM users WHERE username=%s",
                   (session['username'],))
    user = cursor.fetchone()
    cursor.execute("SELECT date, weight FROM progress WHERE username=%s ORDER BY date", (session['username'],))
    progress = cursor.fetchall()
    conn.close()
    return render_template('profile.html', user=user, progress=progress)

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']
        flash(f"Thanks, {name}! Your message has been received.", "success")
    return render_template('contact.html')

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
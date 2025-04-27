from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import os

from models import db, User

# Load environment variables from .env
load_dotenv()

# App setup
app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['DEBUG'] = os.getenv('DEBUG', 'False') == 'True'  # Optional, control debug from .env

# Initialize database
db.init_app(app)

# Initialize Login Manager
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Home Route
@app.route('/')
def index():
    return render_template('index.html')

# Register Route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.form
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        confirm_password = data.get('confirm_password')
        phone_number = data.get('phone_number')
        gender = data.get('gender')

        # Password validation
        if password != confirm_password:
            flash('⚠️ Passwords do not match.', 'danger')
            return redirect(url_for('register'))

        # Check if user exists
        existing_user = User.query.filter(
            (User.username == username) | (User.email == email)
        ).first()

        if existing_user:
            flash('⚠️ Username or email already exists.', 'danger')
            return redirect(url_for('register'))

        # Create new user
        new_user = User(
            first_name=first_name,
            last_name=last_name,
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            phone_number=phone_number,
            gender=gender
        )

        db.session.add(new_user)
        db.session.commit()

        flash('✅ Account created successfully. Please login.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

# Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username_or_email = request.form.get('username_or_email')
        password = request.form.get('password')

        user = User.query.filter(
            (User.username == username_or_email) | (User.email == username_or_email)
        ).first()

        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            flash('✅ Logged in successfully.', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('❌ Invalid credentials.', 'danger')
            return redirect(url_for('login'))

    return render_template('login.html')

# Dashboard Route
@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == 'admin':
        return render_template('admin_dashboard.html', user=current_user)
    return render_template('user_dashboard.html', user=current_user)

# Logout Route
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('👋 Logged out successfully.', 'info')
    return redirect(url_for('login'))

# Auto-create Admin (Bonus enhancement)
def create_admin_user():
    admin_email = os.getenv('ADMIN_EMAIL', 'admin@example.com')
    admin_username = os.getenv('ADMIN_USERNAME', 'admin')
    admin_password = os.getenv('ADMIN_PASSWORD', 'admin123')

    admin = User.query.filter_by(role='admin').first()
    if not admin:
        new_admin = User(
            first_name='Admin',
            last_name='User',
            username=admin_username,
            email=admin_email,
            password_hash=generate_password_hash(admin_password),
            phone_number='0000000000',
            gender='Other',
            role='admin',
            two_factor_enabled=False
        )
        db.session.add(new_admin)
        db.session.commit()
        print('✅ Default admin user created.')

# Main entry
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        create_admin_user()  # Auto-create admin if none exists
    app.run(host="0.0.0.0", port=int(os.getenv('PORT', 5000)), debug=app.config['DEBUG'])

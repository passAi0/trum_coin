from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import os
import re
from sqlalchemy.exc import SQLAlchemyError

from models import db, User

# Load environment variables
load_dotenv()

# App setup
app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['DEBUG'] = os.getenv('DEBUG', 'True') == 'True'

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


# Auto-create default Admin user if none exists
def create_default_admin():
    admin_email = os.getenv('ADMIN_EMAIL', 'admin@yourapp.com')
    admin_username = os.getenv('ADMIN_USERNAME', 'admin')
    admin_password = os.getenv('ADMIN_PASSWORD', 'admin123')

    admin = User.query.filter_by(role='admin').first()
    if not admin:
        new_admin = User(
            first_name='Admin',
            last_name='User',
            username=admin_username.lower(),
            email=admin_email.lower(),
            password_hash=generate_password_hash(admin_password),
            phone_number='0000000000',
            gender='Other',
            role='admin',
            two_factor_enabled=False
        )
        db.session.add(new_admin)
        db.session.commit()
        print('✅ Default admin created successfully.')
    else:
        print('ℹ️ Admin already exists.')


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
        username = data.get('username').lower()
        email = data.get('email').lower()
        password = data.get('password')
        confirm_password = data.get('confirm_password')
        phone_number = data.get('phone_number')
        gender = data.get('gender')

        # Basic Validations
        if password != confirm_password:
            flash('⚠️ Passwords do not match.', 'danger')
            return redirect(url_for('register'))

        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            flash('⚠️ Invalid email format.', 'danger')
            return redirect(url_for('register'))

        if len(password) < 6:
            flash('⚠️ Password must be at least 6 characters.', 'danger')
            return redirect(url_for('register'))

        existing_user = User.query.filter(
            (User.username == username) | (User.email == email)
        ).first()
        if existing_user:
            flash('⚠️ Username or email already exists.', 'danger')
            return redirect(url_for('register'))

        try:
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
        except SQLAlchemyError:
            db.session.rollback()
            flash('❌ An error occurred. Please try again.', 'danger')
            return redirect(url_for('register'))

    return render_template('register.html')


# Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username_or_email = request.form.get('username_or_email', '').lower()
        password = request.form.get('password', '')

        if not username_or_email or not password:
            flash('⚠️ Both username/email and password are required.', 'danger')
            return redirect(url_for('login'))


        user = User.query.filter(
            (User.username == username_or_email) | (User.email == username_or_email)
        ).first()

        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            flash('✅ Logged in successfully.', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('❌ Invalid credentials. Please try again.', 'danger')
            return redirect(url_for('login'))

    return render_template('login.html')


# Dashboard Route
@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == 'admin':
        return redirect(url_for('admin_dashboard'))
    return render_template('user_dashboard.html', user=current_user)


# Admin Dashboard Route (Only Admins can access)
@app.route('/admin_dashboard')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        flash('🚫 Access Denied. Admins only.', 'danger')
        return redirect(url_for('dashboard'))
    return render_template('admin_dashboard.html', user=current_user)


# Admin View Users Route
@app.route('/admin/users')
@login_required
def admin_view_users():
    if current_user.role != 'admin':
        flash('🚫 Access Denied. Admins only.', 'danger')
        return redirect(url_for('dashboard'))

    users = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin_users.html', users=users)


# Logout Route
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('👋 Logged out successfully.', 'info')
    return redirect(url_for('login'))


# Main entry
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        create_default_admin()
    print(f"🚀 Server running | Debug Mode: {app.config['DEBUG']} | Database: {os.getenv('DATABASE_URL')}")
    app.run(host="0.0.0.0", port=int(os.getenv('PORT', 5000)), debug=app.config['DEBUG'])

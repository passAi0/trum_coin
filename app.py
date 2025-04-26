from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_mail import Mail, Message
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
from config import Config
from models import db, User, Admin, KYCRequest, Wallet, Transaction, Trade, Asset

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

mail = Mail(app)

UPLOAD_FOLDER = os.path.join('static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = generate_password_hash(request.form['password'])
        user = User(email=email, password_hash=password)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful. Please login.')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials')
    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == 'admin':
        return redirect(url_for('admin_dashboard'))
    return render_template('dashboard.html')

@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        flash('Access Denied')
        return redirect(url_for('dashboard'))
    users = User.query.all()
    return render_template('admin_dashboard.html', users=users)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/kyc-upload', methods=['GET', 'POST'])
@login_required
def kyc_upload():
    if request.method == 'POST':
        doc_type = request.form['document_type']
        doc_number = request.form['document_number']
        file = request.files['document_photo']
        filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)

        kyc = KYCRequest(
            user_id=current_user.id,
            document_type=doc_type,
            document_number=doc_number,
            document_photo_url=file_path
        )
        db.session.add(kyc)
        db.session.commit()

        # Email user
        msg = Message('KYC Submission Received', recipients=[current_user.email])
        msg.body = "Your KYC submission is received and pending verification."
        mail.send(msg)

        flash('KYC uploaded successfully. Please wait for verification.')
        return redirect(url_for('dashboard'))
    return render_template('kyc_upload.html')

if __name__ == '__main__':
    app.run(debug=True)

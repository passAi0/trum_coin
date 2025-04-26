from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.Text, nullable=False)
    two_factor_enabled = db.Column(db.Boolean, default=False)
    phone_number = db.Column(db.String(20))
    role = db.Column(db.String(10), default='user')  # user or admin
    balance = db.Column(db.Numeric(18, 8), default=0.0)
    kyc_status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)

class Admin(db.Model):
    __tablename__ = 'admins'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True)
    permissions = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class KYCRequest(db.Model):
    __tablename__ = 'kyc_requests'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    document_type = db.Column(db.String(50))
    document_number = db.Column(db.String(100))
    document_photo_url = db.Column(db.Text)
    status = db.Column(db.String(20), default='pending')
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    verified_at = db.Column(db.DateTime)

class Wallet(db.Model):
    __tablename__ = 'wallets'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    asset_symbol = db.Column(db.String(10))
    balance = db.Column(db.Numeric(30, 8), default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Transaction(db.Model):
    __tablename__ = 'transactions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    type = db.Column(db.String(20))
    asset_symbol = db.Column(db.String(10))
    amount = db.Column(db.Numeric(30, 8))
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Trade(db.Model):
    __tablename__ = 'trades'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    asset_symbol = db.Column(db.String(10))
    trade_type = db.Column(db.String(10))
    price = db.Column(db.Numeric(30, 8))
    quantity = db.Column(db.Numeric(30, 8))
    total = db.Column(db.Numeric(30, 8))
    status = db.Column(db.String(20), default='open')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Asset(db.Model):
    __tablename__ = 'assets'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    symbol = db.Column(db.String(10), unique=True)
    price = db.Column(db.Numeric(30, 8))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class KYCUpload(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    document_type = db.Column(db.String(100), nullable=False)
    document_number = db.Column(db.String(100), nullable=False)
    document_photo = db.Column(db.String(255), nullable=False)

    user = db.relationship('User', backref='kyc_uploads')

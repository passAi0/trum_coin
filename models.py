from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from sqlalchemy import Enum
import enum

db = SQLAlchemy()

# Gender Enum
class GenderEnum(enum.Enum):
    male = "male"
    female = "female"
    others = "others"

# Role Enum
class RoleEnum(enum.Enum):
    user = "user"
    admin = "admin"

# KYC Status Enum
class KYCStatusEnum(enum.Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"

# Transaction Type Enum
class TransactionTypeEnum(enum.Enum):
    deposit = "deposit"
    withdrawal = "withdrawal"
    transfer = "transfer"

# Trade Type Enum
class TradeTypeEnum(enum.Enum):
    buy = "buy"
    sell = "sell"

# -------------------- MODELS -----------------------

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.Text, nullable=False)
    phone_number = db.Column(db.String(20))
    gender = db.Column(Enum(GenderEnum))
    two_factor_enabled = db.Column(db.Boolean, default=False)
    role = db.Column(Enum(RoleEnum), default=RoleEnum.user)
    balance = db.Column(db.Numeric(18, 8), default=0.0)
    kyc_status = db.Column(Enum(KYCStatusEnum), default=KYCStatusEnum.pending)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    admin_profile = db.relationship('Admin', backref='user', uselist=False, cascade="all, delete")
    kyc_requests = db.relationship('KYCRequest', backref='user', cascade="all, delete")
    wallets = db.relationship('Wallet', backref='user', cascade="all, delete")
    transactions = db.relationship('Transaction', backref='user', cascade="all, delete")
    trades = db.relationship('Trade', backref='user', cascade="all, delete")


class Admin(db.Model):
    __tablename__ = 'admins'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    permissions = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class KYCRequest(db.Model):
    __tablename__ = 'kyc_requests'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    document_type = db.Column(db.String(50), nullable=False)
    document_number = db.Column(db.String(100), nullable=False)
    document_photo_url = db.Column(db.Text, nullable=False)
    status = db.Column(Enum(KYCStatusEnum), default=KYCStatusEnum.pending)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    verified_at = db.Column(db.DateTime, nullable=True)


class Wallet(db.Model):
    __tablename__ = 'wallets'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    asset_symbol = db.Column(db.String(10), nullable=False)
    balance = db.Column(db.Numeric(30, 8), default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Transaction(db.Model):
    __tablename__ = 'transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    type = db.Column(Enum(TransactionTypeEnum), nullable=False)
    asset_symbol = db.Column(db.String(10), nullable=False)
    amount = db.Column(db.Numeric(30, 8), nullable=False)
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Trade(db.Model):
    __tablename__ = 'trades'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    asset_symbol = db.Column(db.String(10), nullable=False)
    trade_type = db.Column(Enum(TradeTypeEnum), nullable=False)
    price = db.Column(db.Numeric(30, 8), nullable=False)
    quantity = db.Column(db.Numeric(30, 8), nullable=False)
    total = db.Column(db.Numeric(30, 8), nullable=False)
    status = db.Column(db.String(20), default='open')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Asset(db.Model):
    __tablename__ = 'assets'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    symbol = db.Column(db.String(10), unique=True, nullable=False)
    price = db.Column(db.Numeric(30, 8), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

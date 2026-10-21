from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from app.db.base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(255), index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(255), default="student")
    is_active = Column(Boolean, default=True)
    emailVerified = Column("email_verified", Boolean, default=False)
    verificationOTP = Column("verification_otp", String(255), nullable=True)
    otpExpiry = Column("otp_expiry", DateTime(timezone=True), nullable=True)
    password_reset_otp = Column(String(255), nullable=True)
    password_reset_expiry = Column(DateTime(timezone=True), nullable=True)
    
    # Settings
    theme = Column(String(255), default="dark")
    notifications_enabled = Column(Boolean, default=True)
    language = Column(String(255), default="en")
    profile_picture_url = Column(String(255), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

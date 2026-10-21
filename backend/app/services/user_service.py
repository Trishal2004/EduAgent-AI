import random
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.security.security import get_password_hash, verify_password, create_access_token, create_refresh_token, create_password_reset_token, verify_password_reset_token
from app.crud.crud_user import user_crud
from app.DTOs.user import UserCreate, UserLogin, ForgotPassword, ResetPassword, VerifyEmailRequest, ResendOTPRequest
from app.services.email import sendVerificationEmail, send_password_reset_email

import logging
logger = logging.getLogger(__name__)

class UserService:
    def register_user(self, db: Session, user_in: UserCreate):
        print(f"[Step 2] Backend received registration request for {user_in.email}")
        # 1. Validation: Unique Email
        existing_user = user_crud.get_by_email(db, email=user_in.email)
        if existing_user:
            if existing_user.emailVerified:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )
            else:
                # User exists but not verified, resend OTP
                code = str(random.randint(100000, 999999))
                print(f"[Step 4] Generated new 6-digit OTP for unverified user: {code}")
                existing_user.verificationOTP = code
                existing_user.otpExpiry = datetime.now(timezone.utc) + timedelta(minutes=10)
                
                # Update password in case they chose a new one on second try
                existing_user.password_hash = get_password_hash(user_in.password)
                
                db.add(existing_user)
                db.commit()
                db.refresh(existing_user)
                
                sendVerificationEmail(existing_user.email, code)
                
                return {
                    "success": True,
                    "message": "Verification code resent to your email."
                }
        
        # 2. Hash Password
        hashed_password = get_password_hash(user_in.password)
        
        # 3. Save User
        user_dict = {
            "email": user_in.email,
            "full_name": user_in.full_name,
            "password_hash": hashed_password
        }
        created_user = user_crud.create(db, user_dict=user_dict)
        print(f"[Step 3] User {user_in.email} saved in the database with ID {created_user.id}")
        
        # Generate 2FA code and expiry
        code = str(random.randint(100000, 999999))
        print(f"[Step 4] Generated 6-digit OTP: {code}")
        created_user.verificationOTP = code
        created_user.otpExpiry = datetime.now(timezone.utc) + timedelta(minutes=10)
        db.add(created_user)
        db.commit()
        db.refresh(created_user)
        print("[Step 5] OTP stored in the database.")
        
        sendVerificationEmail(created_user.email, code)
        
        return {
            "success": True,
            "message": "Verification code sent to your email."
        }

    def login_user(self, db: Session, user_credentials: UserLogin):
        logger.info(f"Received login request for {user_credentials.email}")
        # 1. Find user by email
        user = user_crud.get_by_email(db, email=user_credentials.email)
        
        # 2. Validate user exists and password is correct
        if not user or not verify_password(user_credentials.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        # 3. Check Verification
        if not user.emailVerified:
            print(f"[Step 11] Login blocked for unverified user {user.email}")
            # Generate new OTP and send email
            code = str(random.randint(100000, 999999))
            user.verificationOTP = code
            user.otpExpiry = datetime.now(timezone.utc) + timedelta(minutes=10)
            db.add(user)
            db.commit()
            
            sendVerificationEmail(user.email, code)
            
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Please verify your email first."
            )
            
        print(f"[Step 12] Login succeeded for verified user {user.email}")
        # 4. Generate Tokens
        access_token = create_access_token(data={"sub": str(user.id)})
        refresh_token = create_refresh_token(data={"sub": str(user.id)})
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": user
        }

    def login_request(self, db: Session, user_credentials: UserLogin):
        logger.info(f"Received login request for {user_credentials.email}")
        user = user_crud.get_by_email(db, email=user_credentials.email)
        
        if not user or not verify_password(user_credentials.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
            )
            
        if not user.emailVerified:
            # Generate new OTP and send email for verification
            code = str(random.randint(100000, 999999))
            user.verificationOTP = code
            user.otpExpiry = datetime.now(timezone.utc) + timedelta(minutes=10)
            db.add(user)
            db.commit()
            
            sendVerificationEmail(user.email, code)
            
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Please verify your email first."
            )
            
        code = str(random.randint(100000, 999999))
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=5)
        
        from app.models.otp import UserLoginOTP
        new_otp = UserLoginOTP(
            user_id=user.id,
            email=user.email,
            otp_code=code,
            expires_at=expires_at
        )
        db.add(new_otp)
        db.commit()

        sendVerificationEmail(user.email, code)
        
        return {"message": "OTP sent"}

    def verify_login_otp(self, db: Session, email: str, otp_code: str):
        user = user_crud.get_by_email(db, email=email)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
            
        from app.models.otp import UserLoginOTP
        
        otp_record = db.query(UserLoginOTP).filter(
            UserLoginOTP.email == email,
            UserLoginOTP.otp_code == otp_code,
            UserLoginOTP.is_used == False
        ).order_by(UserLoginOTP.created_at.desc()).first()
        
        if not otp_record:
            raise HTTPException(status_code=400, detail="Invalid OTP")
            
        if otp_record.expires_at.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
            raise HTTPException(status_code=400, detail="OTP has expired")
            
        otp_record.is_used = True
        db.add(otp_record)
        db.commit()
        
        access_token = create_access_token(data={"sub": str(user.id)})
        refresh_token = create_refresh_token(data={"sub": str(user.id)})
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": user
        }

    def verify_email(self, db: Session, req: VerifyEmailRequest):
        user = user_crud.get_by_email(db, email=req.email)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        print(f"[Step 9] Verifying OTP for {req.email}")
        if not user.verificationOTP or user.verificationOTP != req.otp:
            logger.warning(f"[Step 9] Incorrect OTP provided for {req.email}")
            raise HTTPException(status_code=400, detail="Invalid verification code")
            
        if user.otpExpiry and user.otpExpiry.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
            raise HTTPException(status_code=400, detail="Verification code has expired")
            
        user.emailVerified = True
        print(f"[Step 10] User emailVerified field changed to True for {req.email}")
        user.verificationOTP = None
        user.otpExpiry = None
        db.add(user)
        db.commit()
        
        return {"success": True, "message": "Email verified successfully."}

    def resend_otp(self, db: Session, req: ResendOTPRequest):
        user = user_crud.get_by_email(db, email=req.email)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
            
        if user.emailVerified:
            raise HTTPException(status_code=400, detail="User is already verified")
            
        code = str(random.randint(100000, 999999))
        user.verificationOTP = code
        user.otpExpiry = datetime.now(timezone.utc) + timedelta(minutes=10)
        db.add(user)
        db.commit()
        print(f"\n{'='*40}\n[EMAIL SIMULATION] Verification code for {user.email} is: {code}\n{'='*40}\n")
        sendVerificationEmail(user.email, code)
        
        return {"message": "OTP sent successfully"}

    def forgot_password(self, db: Session, email_data: ForgotPassword):
        user = user_crud.get_by_email(db, email=email_data.email)
        if not user:
            return {"message": "If the email is registered, a password reset OTP has been sent."}
            
        code = str(random.randint(100000, 999999))
        user.password_reset_otp = code
        user.password_reset_expiry = datetime.now(timezone.utc) + timedelta(minutes=10)
        db.add(user)
        db.commit()
        
        send_password_reset_email(user.email, code)
        return {"message": "If the email is registered, a password reset OTP has been sent."}

    def reset_password(self, db: Session, reset_data: ResetPassword):
        user = user_crud.get_by_email(db, email=reset_data.email)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
            
        if not user.password_reset_otp or user.password_reset_otp != reset_data.otp:
            raise HTTPException(status_code=400, detail="Invalid reset code")
            
        if user.password_reset_expiry and user.password_reset_expiry.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
            raise HTTPException(status_code=400, detail="Reset code has expired")
            
        hashed_password = get_password_hash(reset_data.new_password)
        user_crud.update_password(db, user, hashed_password)
        
        # Clear reset tokens
        user.password_reset_otp = None
        user.password_reset_expiry = None
        db.add(user)
        db.commit()
        
        return {"message": "Password has been successfully reset"}

user_service = UserService()

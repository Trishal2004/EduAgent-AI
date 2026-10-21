import random
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.repositories.user import UserRepository
from app.DTOs.user import UserCreate, UserResponse, Token, UserUpdate, VerifyEmailRequest, ResetPassword
from app.security.security import verify_password, get_password_hash, create_access_token
from app.models.user import User
from app.models.otp import UserLoginOTP
from app.services.email import sendVerificationEmail, send_password_reset_email
from app.utils.email import send_otp_email
from sqlalchemy import select
from datetime import datetime, timedelta, timezone

async def generate_and_store_otp(user: User, db: AsyncSession) -> str:
    """
    Generates a random 6-digit OTP, stores it in the user's verificationOTP,
    sets the expiry to 10 minutes from now, and saves the updated user.
    """
    code = str(random.randint(100000, 999999))
    user.verificationOTP = code
    user.otpExpiry = datetime.now(timezone.utc) + timedelta(minutes=10)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return code

class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)

    async def register_user(self, user_in: UserCreate):
        """Registers a new user after verifying the email isn't taken."""
        user = await self.user_repo.get_by_email(email=user_in.email)
        if user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The user with this email already exists in the system.",
            )
        new_user = await self.user_repo.create(user_in)
        
        # Generate and store OTP
        code = await generate_and_store_otp(new_user, self.db)
        print(f"\n{'='*40}\n[EMAIL SIMULATION] Verification code for {new_user.email} is: {code}\n{'='*40}\n")
        sendVerificationEmail(new_user.email, code)
        
        return {
            "success": True,
            "message": "Registration successful."
        }

    async def authenticate_user(self, form_data: OAuth2PasswordRequestForm) -> Token:
        """Authenticates a user and returns a JWT access token."""
        # Note: OAuth2PasswordRequestForm uses 'username' instead of 'email'.
        # We expect the user to send their email in the 'username' field.
        user = await self.user_repo.get_by_email(email=form_data.username)
        if not user or not verify_password(form_data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        elif not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inactive user"
            )
        
        # Authenticate normally
        access_token = create_access_token(subject=str(user.id))
        return Token(access_token=access_token, token_type="bearer")

    async def login_request(self, email: str, password: str):
        """Initiates 2-Step OTP login."""
        user = await self.user_repo.get_by_email(email=email)
        if not user or not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
            )
        elif not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inactive user"
            )

        # Generate OTP
        code = str(random.randint(100000, 999999))
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=5)
        
        new_otp = UserLoginOTP(
            user_id=user.id,
            email=user.email,
            otp_code=code,
            expires_at=expires_at
        )
        self.db.add(new_otp)
        await self.db.commit()

        # Send email
        print(f"\n{'='*40}\n[EMAIL SIMULATION] Login OTP for {user.email} is: {code}\n{'='*40}\n")
        send_otp_email(user.email, code)
        
        return {"message": "OTP sent"}

    async def verify_login_otp(self, email: str, otp_code: str):
        """Verifies the login OTP and issues token."""
        user = await self.user_repo.get_by_email(email=email)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
            
        stmt = select(UserLoginOTP).where(
            UserLoginOTP.email == email,
            UserLoginOTP.otp_code == otp_code,
            UserLoginOTP.is_used == False
        ).order_by(UserLoginOTP.created_at.desc())
        
        result = await self.db.execute(stmt)
        otp_record = result.scalars().first()
        
        if not otp_record:
            raise HTTPException(status_code=400, detail="Invalid OTP")
            
        expiry = otp_record.expires_at.replace(tzinfo=timezone.utc) if otp_record.expires_at.tzinfo is None else otp_record.expires_at
        if expiry < datetime.now(timezone.utc):
            raise HTTPException(status_code=400, detail="OTP has expired")
            
        # Mark as used
        otp_record.is_used = True
        self.db.add(otp_record)
        await self.db.commit()
        
        access_token = create_access_token(subject=str(user.id))
        return {
            "access_token": access_token,
            "refresh_token": "refresh_token_placeholder",
            "token_type": "bearer",
            "user": UserResponse.model_validate(user)
        }

    async def verify_email(self, req: VerifyEmailRequest):
        user = await self.user_repo.get_by_email(email=req.email)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
            
        if user.verificationOTP != req.otp:
            raise HTTPException(status_code=400, detail="Invalid verification code")
            
        if user.otpExpiry:
            expiry = user.otpExpiry.replace(tzinfo=timezone.utc) if user.otpExpiry.tzinfo is None else user.otpExpiry
            if expiry < datetime.now(timezone.utc):
                raise HTTPException(status_code=400, detail="OTP has expired")
        
        user.emailVerified = True
        user.verificationOTP = None
        user.otpExpiry = None
        self.db.add(user)
        await self.db.commit()
        
        return {"success": True, "message": "Email verified successfully."}

    async def update_user(self, user: User, update_data: UserUpdate) -> UserResponse:
        update_dict = update_data.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            setattr(user, key, value)
            
        self.user_repo.db.add(user)
        await self.user_repo.db.commit()
        await self.user_repo.db.refresh(user)
        return UserResponse.model_validate(user)

    async def change_password(self, user: User, current_password: str, new_password: str):
        if not verify_password(current_password, user.hashed_password):
            raise HTTPException(status_code=400, detail="Incorrect password")
        user.hashed_password = get_password_hash(new_password)
        self.user_repo.db.add(user)
        await self.user_repo.db.commit()
        return {"status": "success"}

    async def delete_account(self, user: User):
        await self.user_repo.delete(user.id)
        return {"status": "success"}

    async def resend_otp(self, email: str):
        user = await self.user_repo.get_by_email(email=email)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
            
        code = await generate_and_store_otp(user, self.db)
        
        print(f"\n{'='*40}\n[EMAIL SIMULATION] Verification code for {user.email} is: {code}\n{'='*40}\n")
        sendVerificationEmail(user.email, code)
        return {"status": "success"}

    async def forgot_password(self, email: str):
        user = await self.user_repo.get_by_email(email=email)
        if not user:
            # Return success even if not found to prevent user enumeration
            return {"status": "success"}
            
        code = await generate_and_store_otp(user, self.db)
        
        print(f"\n{'='*40}\n[EMAIL SIMULATION] Password reset code for {user.email} is: {code}\n{'='*40}\n")
        send_password_reset_email(user.email, code)
        return {"status": "success"}

    async def reset_password(self, data: ResetPassword):
        user = await self.user_repo.get_by_email(email=data.email)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
            
        if user.verificationOTP != data.otp:
            raise HTTPException(status_code=400, detail="Invalid verification code")
            
        user.hashed_password = get_password_hash(data.new_password)
        user.verificationOTP = None
        self.db.add(user)
        await self.db.commit()
        return {"status": "success"}

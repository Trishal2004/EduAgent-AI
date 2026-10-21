from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.DTOs.user import UserCreate, UserResponse, UserLogin, TokenResponse, ForgotPassword, ResetPassword, UserUpdate, VerifyEmailRequest, ResendOTPRequest
from fastapi import Body
from app.services.user_service import user_service
from app.security.deps import get_current_user
from app.models.user import User

# Create an API Router for authentication routes
router = APIRouter()

@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user.
    """
    # Delegate the complex logic to the service layer
    user = user_service.register_user(db, user_in)
    return user

@router.post("/verify-email", status_code=status.HTTP_200_OK)
def verify_email(req: VerifyEmailRequest, db: Session = Depends(get_db)):
    """
    Verify email with 2FA code.
    """
    return user_service.verify_email(db, req)

@router.post("/resend-otp", status_code=status.HTTP_200_OK)
def resend_otp(req: ResendOTPRequest, db: Session = Depends(get_db)):
    """
    Resend verification OTP.
    """
    return user_service.resend_otp(db, req)

@router.post("/login", response_model=TokenResponse, status_code=status.HTTP_200_OK)
def login(
    user_credentials: UserLogin = Body(..., example={
        "email": "student@example.com",
        "password": "strongpassword123"
    }), 
    db: Session = Depends(get_db)
):
    """
    Authenticate user and return JWT tokens alongside user profile information.
    """
    return user_service.login_user(db, user_credentials)

@router.post("/login-request", status_code=status.HTTP_200_OK)
def login_request(
    user_credentials: UserLogin = Body(...),
    db: Session = Depends(get_db)
):
    """
    Initiate 2-Step OTP login.
    """
    return user_service.login_request(db, user_credentials)

@router.post("/verify-otp", response_model=TokenResponse, status_code=status.HTTP_200_OK)
def verify_otp(
    data: VerifyEmailRequest,
    db: Session = Depends(get_db)
):
    """
    Verify OTP and return access token.
    """
    return user_service.verify_login_otp(db, data.email, data.otp)

@router.get("/me", response_model=UserResponse)
def read_users_me(current_user: User = Depends(get_current_user)):
    """
    Get current logged in user profile.
    Only accessible if a valid JWT token is provided.
    """
    return current_user

@router.put("/me", response_model=UserResponse)
def update_users_me(
    user_in: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update current logged in user profile.
    """
    if user_in.full_name is not None:
        current_user.full_name = user_in.full_name
    if user_in.theme is not None:
        current_user.theme = user_in.theme
    if user_in.notifications_enabled is not None:
        current_user.notifications_enabled = user_in.notifications_enabled
    if user_in.language is not None:
        current_user.language = user_in.language
    if user_in.profile_picture_url is not None:
        current_user.profile_picture_url = user_in.profile_picture_url

    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    return current_user

@router.post("/forgot-password", status_code=status.HTTP_200_OK)
def forgot_password(email_data: ForgotPassword, db: Session = Depends(get_db)):
    """
    Initiate password reset process by sending an email with a reset token.
    """
    return user_service.forgot_password(db, email_data)

@router.post("/reset-password", status_code=status.HTTP_200_OK)
def reset_password(reset_data: ResetPassword, db: Session = Depends(get_db)):
    """
    Reset a user's password using a valid reset token.
    """
    return user_service.reset_password(db, reset_data)

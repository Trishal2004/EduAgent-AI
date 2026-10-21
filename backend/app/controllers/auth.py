from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordRequestForm
from app.security import deps
from app.db.session import get_db
from app.DTOs.user import UserCreate, UserResponse, Token, UserUpdate, ChangePassword, VerifyEmailRequest, ResendOTPRequest, ForgotPassword, ResetPassword, UserLogin, TokenResponse
from app.services.auth import AuthService
from app.models.user import User

router = APIRouter()

@router.post("/register", status_code=201)
async def register(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    """
    Register a new user.
    """
    auth_service = AuthService(db)
    return await auth_service.register_user(user_in)

@router.post("/verify-email")
async def verify_email(req: VerifyEmailRequest, db: AsyncSession = Depends(get_db)):
    auth_service = AuthService(db)
    return await auth_service.verify_email(req)

@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """
    OAuth2 compatible token login, get an access token for future requests.
    Note: The form expects `username` which we treat as `email`.
    """
    auth_service = AuthService(db)
    return await auth_service.authenticate_user(form_data)

@router.post("/login-request")
async def login_request(
    data: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    """
    Initiate 2-Step OTP login.
    """
    auth_service = AuthService(db)
    return await auth_service.login_request(data.email, data.password)

@router.post("/verify-otp", response_model=TokenResponse)
async def verify_otp(
    data: VerifyEmailRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Verify OTP and return access token.
    """
    auth_service = AuthService(db)
    return await auth_service.verify_login_otp(data.email, data.otp)

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(deps.get_current_user)):
    """
    Get current logged in user details.
    This is a protected route!
    """
    return current_user

@router.put("/me", response_model=UserResponse)
async def update_users_me(
    user_in: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    Update current logged in user details.
    """
    auth_service = AuthService(db)
    return await auth_service.update_user(current_user, user_in)

@router.put("/password")
async def change_password(
    password_data: ChangePassword,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """Change current user password."""
    auth_service = AuthService(db)
    return await auth_service.change_password(current_user, password_data.current_password, password_data.new_password)

@router.delete("/me")
async def delete_account(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """Delete current user account."""
    auth_service = AuthService(db)
    return await auth_service.delete_account(current_user)

@router.post("/resend-otp")
async def resend_otp(req: ResendOTPRequest, db: AsyncSession = Depends(get_db)):
    auth_service = AuthService(db)
    return await auth_service.resend_otp(req.email)

@router.post("/forgot-password")
async def forgot_password(req: ForgotPassword, db: AsyncSession = Depends(get_db)):
    auth_service = AuthService(db)
    return await auth_service.forgot_password(req.email)

@router.post("/reset-password")
async def reset_password(req: ResetPassword, db: AsyncSession = Depends(get_db)):
    auth_service = AuthService(db)
    return await auth_service.reset_password(req)


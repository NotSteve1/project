from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.schemas.user_schema import UserCreate, UserResponse
from app.schemas.auth_schema import BootstrapAdminRequest, LoginRequest, TokenResponse, VerifyEmailRequest, ResendOtpRequest
from app.services.auth_service import verify_email, register_user, login_user, bootstrap_admin, resend_otp
from app.core.security import create_access_token
from app.services.auth_service import resend_otp

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    user = register_user(db, user_data)
    if user is None:
        raise HTTPException(status_code=409, detail="Email already registered")
    return user

@router.post("/verify-email")
def verify_email(data: VerifyEmailRequest, db: Session = Depends(get_db)):
    result = verify_email(db, data)
    if result == "not_found":
        raise HTTPException(status_code=404, detail="No pending verification for this email")
    if result == "expired":
        raise HTTPException(status_code=400, detail="OTP has expired")
    if result == "invalid":
        raise HTTPException(status_code=400, detail="Incorrect OTP")
    return {"message": "Email verified successfully"}

@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    result_status, user = login_user(db, data)
    if result_status in ("not_found", "wrong_password"):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    if result_status == "not_verified":
        raise HTTPException(status_code=403, detail="Please verify your email first")

    token = create_access_token({"sub": str(user.id)})
    return TokenResponse(access_token=token)

@router.post("/resend-otp")
def resend_otp(data: ResendOtpRequest, db: Session = Depends(get_db)):
    result = resend_otp(db, data.email)
    if result == "not_found":
        raise HTTPException(status_code=404, detail="No account found with this email")
    if result == "already_verified":
        raise HTTPException(status_code=400, detail="This email is already verified")
    return {"message": "A new verification code has been sent to your email"}

@router.post("/bootstrap-admin")
def bootstrap_admin(data: BootstrapAdminRequest, db: Session = Depends(get_db)):
    result = bootstrap_admin(db, data.email)
    if result == "admin_exists":
        raise HTTPException(status_code=403, detail="An admin already exists. This endpoint is disabled.")
    if result == "user_not_found":
        raise HTTPException(status_code=404, detail="No account found with this email. Register first.")
    return {"message": f"{data.email} is now a super admin."}
import uuid
from fastapi import APIRouter, Depends, HTTPException, Form, File, UploadFile
from app.utils.dependencies import get_current_user, require_admin
from app.models.user_model import User
from app.database.db import get_db
from sqlalchemy.orm import Session
from app.models.user_model import UserRole
from app.services.user_service import update_user, delete_user, change_password, get_users, update_user_role, get_user_by_id
from app.schemas.user_schema import UserResponse, ChangePasswordRequest, UpdateUserRoleRequest

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/me", response_model=UserResponse)
def get_user(current_user: User = Depends(get_current_user)):
    return current_user

@router.get("/list-all-users", response_model=list[UserResponse])
def list_all_users(db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    return get_users(db)

@router.patch("/update-user-role", response_model=UserResponse)
def update_role(user_id: uuid.UUID, data:UpdateUserRoleRequest, db: Session = Depends(get_db), admin: User = Depends(require_admin)):

    target_user = get_user_by_id(db, user_id)

    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")
    if data.role == UserRole.SUPER_ADMIN and admin.role != UserRole.SUPER_ADMIN:
        raise HTTPException(
            status_code=403,
            detail="Only super admins can grant super admin status",
        )

    if target_user.role == UserRole.SUPER_ADMIN and admin.role != UserRole.SUPER_ADMIN:
        raise HTTPException(
            status_code=403,
            detail="Only super admins can change another super admin's role",
        )
    
    updated = update_user_role(db, user_id, data)

    if not updated:
        raise HTTPException(status_code=404, detail="User not found")
    return updated

@router.patch("/update-user", response_model=UserResponse)
def update_me(
    full_name: str | None = Form(None),
    email: str | None = Form(None),
    image: UploadFile | None = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = update_user(
        db, current_user.id, full_name=full_name, email=email, image=image
    )
    if result is None:
        raise HTTPException(status_code=404, detail="User not found")
    if result == "email_taken":
        raise HTTPException(status_code=409, detail="This email is already in use")
    return result

@router.patch("/me/change-password")
def change_password(
    data: ChangePasswordRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = change_password(
        db, current_user, data.current_password, data.new_password
    )
    if result == "wrong_password":
        raise HTTPException(status_code=401, detail="Current password is incorrect")
    return {"message": "Password updated successfully"}    

@router.delete('/delete-user')
def user_delete(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    del_user = delete_user(db, current_user.id)
    if not del_user:
        raise HTTPException(status_code=404, detail="User not found")

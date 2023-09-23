# IMPORTING MODULES
from fastapi import APIRouter, Depends, HTTPException, status, Path
from database import SessionLocal, Account
from typing import Annotated
from sqlalchemy.orm import Session
from .auth import get_current_user
from pydantic import BaseModel


# DECLARING THE ROUTER APP
router = APIRouter(
    prefix="/admin"
)


# FUNCTION FOR DATABASE CONNECTION AND DEPENDENCY INJECTION
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]


# PYDANTIC CLASSES FOR RESPONSE AND REQUEST DATA
class UserResponseModel(BaseModel):
    id: int
    first_name: str
    last_name: str
    username: str
    email: str
    role: str


# CREATING A USER DEPENDENCY FOR JWT AUTHORIZATION
user_dependency = Annotated[dict, Depends(get_current_user)]


# CREATING ROUTES FOR ADMIN
@router.get('/users', status_code=status.HTTP_200_OK)
async def get_all_users(user: user_dependency, db: db_dependency) -> list[UserResponseModel]:
    if user is None or user.get("user_role") != "admin":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not an Admin to access the data")
    
    users_list = db.query(Account).all()
    users_list_model = [UserResponseModel(id=user.id, first_name=user.first_name, last_name=user.last_name, username=user.username, email=user.email, role= user.role) for user in users_list]
    return users_list_model


@router.get('/users/{user_id}', status_code=status.HTTP_200_OK)
async def get_user(user: user_dependency, db: db_dependency, user_id: int = Path(gt=0)) -> UserResponseModel:
    if user is None or user.get("user_role") != "admin":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not an Admin to access the data")
    
    user_model = db.query(Account).filter(Account.id == user_id).first()

    if user_model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")
    
    user_info = UserResponseModel(
        id=user_model.id,
        first_name=user_model.first_name,
        last_name=user_model.last_name,
        username=user_model.username,
        email=user_model.email,
        role=user_model.role
    )

    return user_info


@router.delete('/users/{user_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user: user_dependency, db: db_dependency, user_id: int = Path(gt=0)):
    if user is None or user.get("user_role") != "admin":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not an Admin to access the data")
    
    user_model = db.query(Account).filter(Account.id == user_id).first()

    if user_model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")
    
    db.query(Account).filter(Account.id == user_id).delete()
    db.commit()

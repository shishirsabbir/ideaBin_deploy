# IMPORTING MODULES
from fastapi import APIRouter, Depends, HTTPException, status, Path
from database import SessionLocal, Account
from typing import Annotated
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime


# DECLARING THE ROUTER APP
router = APIRouter(
    prefix="/validation"
)


# FUNCTION FOR DATABASE CONNECTION AND DEPENDENCY INJECTION
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]


# SETUP APP KEY FOR FRONTEND
APP_KEY = "b6655a6929beb2ad975ac68b8373db51"


# FUNCTION FOR VALIDATING APP KEY
def check_app_key(app_key: str):
    if app_key != APP_KEY:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="App key is not valid")
    
    return True


# PYDANTIC CLASSES FOR CREATE IDEAS OR GET IDEAS
class UserResponse(BaseModel):
    user_id: int
    user_name: str
    user_email: str
    user_since: datetime

    model_config= {
        "json_schema_extra": {
            "examples": [
                {
                    "user_id": 5,
                    "user_name": "shishirsabbir",
                    "user_email": "shishir@aol.com",
                    "user_since": "2023-07-02"
                }
            ]
        }
    }


class IdeaResponse(BaseModel):
    pass


# CREATING ROUTES FOR VALIDATORS
@router.get('/user/{app_key}', status_code=status.HTTP_200_OK)
async def get_username(db: db_dependency, app_key: str = Path(min_length=32)):
    if check_app_key(app_key):
        username_list = db.query(Account).all()
        users_list = [UserResponse(user_id=single_user.id, user_name=single_user.username, user_email=single_user.email, user_since=single_user.created_on) for single_user in username_list]
        return users_list
    



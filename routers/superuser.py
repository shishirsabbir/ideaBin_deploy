# IMPORTING MODULES
from fastapi import APIRouter, Depends, HTTPException, status, Path
from database import SessionLocal, Account
from typing import Annotated
from sqlalchemy.orm import Session
from .auth import bcrypt_context
from pydantic import BaseModel, Field



# DECLARING THE ROUTER APP
router = APIRouter(
    prefix="/superuser"
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
class CreateAdminAccountRequest(BaseModel):
    first_name: str
    last_name: str
    username: str
    email: str
    password: str
    role: str = Field(default="admin") # can not create a admin account

    model_config= {
        "json_schema_extra": {
            "examples": [
                {
                    "first_name": "John",
                    "last_name": "Doe",
                    "username": "john_doe",
                    "email": "johndoe@mail.com",
                    "password": "test123"
                }
            ]
        }
    }


# CREATING ROUTES TO CREATE ADMIN ACCOUNT
@router.get("/", status_code=status.HTTP_200_OK)
async def get_admin_accounts(db: db_dependency):
    return db.query(Account).filter(Account.role == "admin").all()



@router.post('/', status_code=status.HTTP_201_CREATED)
async def create_admin_account(db: db_dependency, create_admin_account_request: CreateAdminAccountRequest):
    account_model = Account(
        first_name = create_admin_account_request.first_name.casefold(),
        last_name = create_admin_account_request.last_name.casefold(),
        username = create_admin_account_request.username,
        email = create_admin_account_request.email,
        hashed_password = bcrypt_context.hash(create_admin_account_request.password),
        role = "admin"
    )

    db.add(account_model)
    db.commit()


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_admin(db: db_dependency, user_id: int = Path(gt=0)):
    admin_model = db.query(Account).filter(Account.id == user_id).filter(Account.role == "admin").first()
    if admin_model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Admin account not found")
    
    db.query(Account).filter(Account.id == user_id).filter(Account.role == "admin").delete()
    db.commit()


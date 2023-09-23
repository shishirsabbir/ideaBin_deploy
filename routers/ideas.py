# IMPORTING MODULES
from fastapi import APIRouter, Depends, HTTPException, status, Path
from database import SessionLocal, Account, Idea, Vote, Comment
from typing import Annotated
from sqlalchemy.orm import Session
from .auth import get_current_user
from pydantic import BaseModel, Field
from datetime import datetime


# DECLARING THE ROUTER APP
router = APIRouter(
    prefix="/idea"
)


# FUNCTION FOR DATABASE CONNECTION AND DEPENDENCY INJECTION
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]


# PYDANTIC CLASSES FOR CREATE IDEAS OR GET IDEAS
class CreateIdeaRequest(BaseModel):
    title: str
    content: str
    # category: Literal["General", "Technology", "Marketing", "Business", "Application", "Tools"]
    subtitle: str

    model_config= {
        "json_schema_extra": {
            "examples": [
                {
                    "title": "LinkedIn Web Crawler",
                    "content": "A LinkedIn scraper in Python is a script or program that extracts data from LinkedIn profiles or pages using web scraping techniques. It typically leverages libraries like BeautifulSoup and requests to access and retrieve information from LinkedIn's public web pages.",
                    "subtitle": "Dedicated web crawler for linkedin"
                }
            ]
        }
    }


class UpdateIdeaRequest(BaseModel):
    title: str
    content: str = Field(min_length=10)
    # category: Literal["General", "Technology", "Marketing", "Business", "Application", "Tools"]
    subtitle: str

    model_config= {
        "json_schema_extra": {
            "examples": [
                {
                    "title": "LinkedIn Web Crawler",
                    "content": "A LinkedIn scraper in Python is a script or program that extracts data from LinkedIn profiles or pages using web scraping techniques. It typically leverages libraries like BeautifulSoup and requests to access and retrieve information from LinkedIn's public web pages.",
                    "subtitle": "Application"
                }
            ]
        }
    }


class AuthorInfo(BaseModel):
    id: int
    first_name: str
    last_name: str
    username: str
    email: str


class IdeaResponseModel(BaseModel):
    id: int
    title: str
    content: str
    subtitle: str
    own_vote: bool
    author_info: Annotated[dict, AuthorInfo]


class IdeaFeedResponse(BaseModel):
    id: int
    title: str
    subtitle: str
    vote_count: int
    own_vote: bool
    comment_count: int
    author_info: Annotated[dict, AuthorInfo]


class CommentResponse(BaseModel):
    id: int
    content: str
    created_on: datetime
    author_info: Annotated[dict, AuthorInfo]


# FUNCTION TO GET AUTHOR NAME
def get_author_info(author_id: int, db):
    author_model = db.query(Account).filter(Account.id == author_id).first()
    author_info_model = AuthorInfo(id=author_model.id, first_name=author_model.first_name, last_name=author_model.last_name, username=author_model.username, email=author_model.email)

    return author_info_model


def get_vote_count(idea_id: int, db):
    vote_model = db.query(Vote).filter(Vote.idea_id == idea_id).all()
    vote_count = len(vote_model)

    return vote_count


def get_comment_count(idea_id: int, db):
    comment_model = db.query(Comment).filter(Comment.idea_id == idea_id).all()
    comment_count = len(comment_model)

    return comment_count


def check_own_vote_status(idea_id: int, author_id: int, db):
    vote_model = db.query(Vote).filter(Vote.idea_id == idea_id).filter(Vote.author_id == author_id).first()
    if not vote_model:
        return False
    
    return True


# CREATING A USER DEPENDENCY FOR JWT AUTHORIZATION
user_dependency = Annotated[dict, Depends(get_current_user)]


# CREATING ROUTES FOR FRONTEND
@router.get('/feed', status_code=status.HTTP_200_OK)
async def get_ideas_feed(user: user_dependency, db: db_dependency) -> list[IdeaFeedResponse]:
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed")
    
    idea_list = db.query(Idea).all()
    idea_model_list = [IdeaFeedResponse(id=idea.id, title=idea.title, subtitle=idea.subtitle, vote_count=get_vote_count(idea.id, db), own_vote=check_own_vote_status(idea_id=idea.id, author_id=user.get("user_id"), db=db), comment_count=get_comment_count(idea.id, db), author_info=get_author_info(idea.author, db)) for idea in idea_list]

    return idea_model_list


@router.get("/comments/{idea_id}", status_code=status.HTTP_200_OK)
async def get_ideas_comments(user: user_dependency, db: db_dependency, idea_id: int = Path(gt=0)) -> list[CommentResponse]:
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed")
    
    comment_list = db.query(Comment).filter(Comment.idea_id == idea_id).all()
    comment_model_list = [CommentResponse(id=comment.id, content=comment.content, created_on=comment.created_on, author_info=get_author_info(comment.author_id, db)) for comment in comment_list]

    return comment_model_list


# CREATING ROUTES FOR IDEA
# @router.get('/', status_code=status.HTTP_200_OK)
# async def get_ideas(user: user_dependency, db: db_dependency) -> list[IdeaResponseModel]:
#     if user is None:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed")
    
#     idea_list = db.query(Idea).all()
#     idea_model_list = [IdeaResponseModel(id=idea.id, title=idea.title, content=idea.content, subtitle=idea.subtitle, author_info=get_author_info(idea.author, db)) for idea in idea_list]
    
#     return idea_model_list


@router.get('/{idea_id}', status_code=status.HTTP_200_OK)
async def get_idea(user: user_dependency, db: db_dependency, idea_id: int = Path(gt=0)) -> IdeaResponseModel:
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed")
    
    idea_model = db.query(Idea).filter(Idea.id == idea_id).first()
    if idea_model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Idea not found")
    
    idea_model_response = IdeaResponseModel(
        id = idea_model.id,
        title = idea_model.title,
        content = idea_model.content,
        subtitle = idea_model.subtitle,
        own_vote=check_own_vote_status(idea_id=idea_model.id, author_id=user.get("user_id"), db=db),
        author_info=get_author_info(idea_model.author, db)
    )
    
    return idea_model_response


@router.post('/', status_code=status.HTTP_201_CREATED)
async def create_idea(user: user_dependency, db: db_dependency, create_idea_request: CreateIdeaRequest):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed")
    
    idea_model = Idea(**create_idea_request.model_dump(), author=user.get("user_id"))

    db.add(idea_model)
    db.commit()


# @router.put('/{content_id}', status_code=status.HTTP_204_NO_CONTENT)
# async def update_idea(user: user_dependency, db: db_dependency, update_idea_request: UpdateIdeaRequest, content_id: int = Path(gt=0)):
#     if user is None:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed")
    
#     idea_model = db.query(Idea).filter(Idea.id == content_id).first()
#     if idea_model is None:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Idea not found")
    
#     idea_model.title = update_idea_request.title
#     idea_model.content = update_idea_request.content
#     idea_model.subtitle = update_idea_request.subtitle

#     db.add(idea_model)
#     db.commit()


@router.delete('/{content_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_idea(user: user_dependency, db: db_dependency, content_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed")
    
    idea_model = db.query(Idea).filter(Idea.id == content_id).first()
    if idea_model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Idea not found")
    
    if idea_model.author == user.get("user_id"):
        db.query(Idea).filter(Idea.id == content_id).delete()
        db.commit()
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can't not delete other users post, unless you are admin")

    
    

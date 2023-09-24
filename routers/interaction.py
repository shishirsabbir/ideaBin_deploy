# IMPORTING MODULES
from fastapi import APIRouter, Depends, HTTPException, status, Path
from database import SessionLocal, Account, Idea, Vote, Comment
from typing import Annotated
from sqlalchemy.orm import Session
from .auth import get_current_user
from pydantic import BaseModel, Field
from .ideas import check_own_vote_status


# DECLARING THE ROUTER APP
router = APIRouter(
    prefix="/interact"
)


# FUNCTION FOR DATABASE CONNECTION AND DEPENDENCY INJECTION
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]


# PYDANTIC CLASSES FOR VOTING AND COMMENTING ON IDEAS
class VoteIdeaRequest(BaseModel):
    idea_id: int

    model_config= {
        "json_schema_extra": {
            "examples": [
                {
                    "idea_id": "1"
                }
            ]
        }
    }


class CommentIdeaRequest(BaseModel):
    idea_id: int
    content: str = Field(min_length=10)

    model_config= {
        "json_schema_extra": {
            "examples": [
                {
                    "idea_id": "1",
                    "content": "This is a nice idea"
                }
            ]
        }
    }


# class CommentDeleteRequest(BaseModel):
#     comment_id: int
#     idea_id: int

#     model_config= {
#         "json_schema_extra": {
#             "examples": [
#                 {
#                     "comment_id": "1",
#                     "idea_id": "1"
#                 }
#             ]
#         }
#     }


# CREATING A USER DEPENDENCY FOR JWT AUTHORIZATION
user_dependency = Annotated[dict, Depends(get_current_user)]


# CREATING ROUTES FOR INTERACTIONS
@router.post("/vote", status_code=status.HTTP_200_OK)
async def vote_on_idea(user: user_dependency, db: db_dependency, vote_idea_request: VoteIdeaRequest):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed")
    
    vote_model = Vote(**vote_idea_request.model_dump(), author_id=user.get("user_id"))
    
    db.add(vote_model)
    db.commit()

    # returning total number of votes
    vote_update_model = db.query(Vote).filter(Vote.idea_id == vote_idea_request.idea_id).all()

    return {
        "status": "voted" if check_own_vote_status(idea_id=vote_idea_request.idea_id, author_id=user.get("user_id"), db=db) else "unvoted",
        "vote_count": len(vote_update_model),
    }




@router.post("/unvote", status_code=status.HTTP_200_OK)
async def unvote_on_idea(user: user_dependency, db: db_dependency, vote_idea_request: VoteIdeaRequest):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed")
    
    vote_model = db.query(Vote).filter(Vote.idea_id == vote_idea_request.idea_id).filter(Vote.author_id == user.get("user_id")).first()

    if not vote_model:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vote not found for this idea by this user")
    
    db.query(Vote).filter(Vote.idea_id == vote_idea_request.idea_id).filter(Vote.author_id == user.get("user_id")).delete()
    db.commit()

    # returning total number of votes
    vote_update_model = db.query(Vote).filter(Vote.idea_id == vote_idea_request.idea_id).all()

    return {
        "status": "voted" if check_own_vote_status(idea_id=vote_idea_request.idea_id, author_id=user.get("user_id"), db=db) else "unvoted",
        "vote_count": len(vote_update_model),
    }


@router.post("/comment", status_code=status.HTTP_201_CREATED)
async def comment_on_idea(user: user_dependency, db: db_dependency, comment_idea_request: CommentIdeaRequest):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed")
    
    comment_model = Comment(**comment_idea_request.model_dump(), author_id=user.get("user_id"))

    db.add(comment_model)
    db.commit()


# @router.delete("/comment", status_code=status.HTTP_201_CREATED)
# async def comment_on_idea(user: user_dependency, db: db_dependency, comment_delete_request: CommentDeleteRequest):
#     if user is None:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed")
    
#     comment_model = db.query(Comment).filter(Comment.id == comment_delete_request.comment_id).filter(Comment.idea_id == comment_delete_request.idea_id).first()

#     if user.get("user") == comment_model.author_id:
#         db.query(Comment).filter(Comment.id == comment_delete_request.comment_id).filter(Comment.idea_id == comment_delete_request.idea_id).delete()
#         db.commit()
#     else:
#         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can't not delete other users comments, unless you are admin")

    
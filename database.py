# IMPORTING MODULES
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, Enum, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from sqlalchemy.sql import func


# SETUP POSTGRESQL AND ADD PASSWORD
# SQL_URL = "postgresql+psycopg2://postgres:<password>@localhost:5432/IdeaBinDB"
# engine = create_engine(SQL_URL)


# SETUP SQLITE
SQL_URL = "sqlite:///IdeaBinDB.db"
engine = create_engine(SQL_URL, connect_args={"check_same_thread": False})


# CREATING DATABASE SESSION AND BASE
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# CREATING CLASSES FOR TABLES
class Account(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum('admin', 'user', name="user_role"), nullable=False)
    created_on = Column(DateTime, server_default=func.now())

    idea_post = relationship("Idea", back_populates="owner")
    vote = relationship("Vote", back_populates="owner")
    comment = relationship("Comment", back_populates="owner")


class Idea(Base):
    __tablename__ = "ideas"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
    subtitle = Column(String, nullable=False)
    # category = Column(Enum("General", "Technology", "Marketing", "Business", "Application", "Tools", name="idea_category"), nullable=False)
    author = Column(Integer, ForeignKey("accounts.id"), nullable=False)

    owner = relationship("Account", back_populates="idea_post")
    comment = relationship("Comment", back_populates="idea_post")
    vote = relationship("Vote", back_populates="idea_post")


Account.idea_post = relationship("Idea", back_populates="owner", cascade="all, delete-orphan")


class Comment(Base):
    __tablename__ = 'comments'

    id = Column(Integer, primary_key=True)
    author_id = Column(Integer, ForeignKey('accounts.id'), nullable=False)
    idea_id = Column(Integer, ForeignKey('ideas.id'), nullable=False)
    content = Column(String, nullable=False)
    created_on = Column(DateTime, server_default=func.now())
    
    owner = relationship("Account", back_populates="comment")
    idea_post = relationship("Idea", back_populates="comment")


class Vote(Base):
    __tablename__ = 'votes'

    id = Column(Integer, primary_key=True)
    author_id = Column(Integer, ForeignKey('accounts.id'), nullable=False)
    idea_id = Column(Integer, ForeignKey('ideas.id'), nullable=False)
    
    owner = relationship('Account', back_populates='vote')
    idea_post = relationship('Idea', back_populates='vote')


Account.comment = relationship('Comment', back_populates="owner", cascade="all, delete-orphan")
Account.vote = relationship('Vote', back_populates='owner', cascade="all, delete-orphan")
Idea.comment = relationship('Comment', back_populates='idea_post', cascade="all, delete-orphan")
Idea.vote = relationship('Vote', back_populates='idea_post', cascade="all, delete-orphan")

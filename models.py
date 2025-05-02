from pydantic import BaseModel, Field, ConfigDict
from typing import Optional,List
from datetime import datetime

from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from db import Base

# POSTS
class Post(BaseModel):
    id: int
    title: str
    url: Optional[str] = None
    text: Optional[str] = None
    author: str
    points: int = 0
    comment_count: int = 0

    class Config:
        from_attributes = True

class PostCreate(BaseModel):
    title: str
    url: Optional[str] = None
    text: Optional[str] = None
    author: str

# USERS
class UserCreate(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    username: Optional[str] = None

# COMMENTS
class CommentBase(BaseModel):
    text: str
    parent_id: Optional[int] = None 

class CommentCreate(CommentBase):
    pass

class CommentUpdate(BaseModel):
    text: str

class Comment(CommentBase):
    id: int
    post_id: int
    author: str
    children: List["Comment"] = []

    class Config:
        from_attributes = True

Comment.model_rebuild()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

class PostDB(Base):
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    url = Column(String)
    text = Column(Text)
    author = Column(String, nullable=False)
    points = Column(Integer, default=0)
    comments = relationship("CommentDB", back_populates="post", cascade="all, delete-orphan")

class CommentDB(Base):
    __tablename__ = "comments"
    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False)
    text = Column(Text, nullable=False)
    parent_id = Column(Integer, ForeignKey("comments.id"), nullable=True)
    author = Column(String, nullable=False)
    post = relationship("PostDB", back_populates="comments")
    children = relationship("CommentDB", cascade="all, delete-orphan")

class Vote(Base):
    __tablename__ = "votes"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, nullable=False)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False)
    value = Column(Integer, nullable=False)
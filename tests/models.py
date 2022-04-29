from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Post(Base):
    __tablename__ = 'posts'

    id = Column(Integer, primary_key=True)
    message = Column(String, nullable=False)

    user_id = Column(Integer, ForeignKey('users.id'))

    def __init__(self, user_id, message):
        self.user_id = user_id
        self.message = message

    def __repr__(self) -> str:
        return (
            f"<Post('{self.id}')>"
        )


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)

    posts = relationship("Post")

    def __init__(self, name):
        self.name = name

    def __repr__(self) -> str:
        return (
            f"<User('{self.id}/{self.name}')>"
        )

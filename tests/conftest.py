import pytest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from .models import User, Post, Base


@pytest.fixture
def session() -> Session:
    engine = create_engine('sqlite:///:memory:')
    session_maker = sessionmaker(bind=engine)
    Base.metadata.create_all(engine)
    return session_maker()


@pytest.fixture
def populate_users(session):
    for i in range(5):
        user = User(f'user{i}')
        session.add(user)
        session.flush()

        for j in range(5):
            post = Post(user.id, f'This is {user.name}\'s post #{i}')
            session.add(post)

    session.flush()

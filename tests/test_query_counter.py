import pytest

from query_counter import QueryCounter, QueryAnalysisConfig, QueryCountError
from .models import User


def test_queries(session, populate_users):
    query_counter = QueryCounter(
        session=session,
        config=QueryAnalysisConfig(alert_threshold=3)
    )
    query_counter.initialize()

    users = session.query(User).all()

    # one query to get users, not above threshold
    assert len(query_counter.queries) == 1
    assert len(query_counter.filtered_queries) == 0
    assert query_counter.sorted_queries[0].count == 1

    # triggers n+1 querying each user (5x) for posts
    for user in users:
        print(len(user.posts))

    # two unique queries, one called 5 times, one above alert threshold
    assert len(query_counter.queries) == 2
    assert len(query_counter.filtered_queries) == 1
    assert query_counter.sorted_queries[0].count == 5


def test_exceptions(session, populate_users):
    query_counter = QueryCounter(
        session=session,
        config=QueryAnalysisConfig(alert_threshold=3, raise_if_exceeds=True)
    )
    query_counter.initialize()

    users = session.query(User).all()

    # triggers n+1 querying each user (5x) for posts
    for user in users:
        print(len(user.posts))

    with pytest.raises(QueryCountError):
        query_counter.analyze()


def test_traceback(session, populate_users):
    query_counter = QueryCounter(
        session=session,
        config=QueryAnalysisConfig(
            alert_threshold=3,
            traceback_enabled=True,
        )
    )
    query_counter.initialize()

    session.query(User).first()

    assert len(query_counter.sorted_queries) == 1
    assert len(query_counter.sorted_queries[0].stack) > 0


def test_heuristics(session, populate_users):
    query_counter = QueryCounter(
        session=session,
        config=QueryAnalysisConfig(
            alert_threshold=3,
            heuristics_enabled=True,
            heuristic_paths=['test_query_counter.py']
        )
    )
    query_counter.initialize()

    users = session.query(User).all()

    # triggers n+1 querying each user (5x) for posts
    for user in users:
        print(len(user.posts))

    assert len(query_counter.filtered_queries) == 1
    assert len(query_counter.filtered_queries[0].heuristics) == 1
    assert query_counter.filtered_queries[0].heuristics[0].caller == 'test_heuristics'

# QueryCounter

[![QueryCounter Publish](https://github.com/tatari-tv/query-counter/actions/workflows/main.yml/badge.svg?branch=main)](https://github.com/tatari-tv/query-counter/actions/workflows/main.yml)
[![PyPI version](https://badge.fury.io/py/query-counter.svg)](https://badge.fury.io/py/query-counter)
[![PyPI pyversions](https://img.shields.io/pypi/pyversions/query-counter.svg)](https://pypi.python.org/pypi/query-counter/)
[![Downloads](https://pepy.tech/badge/query-counter/month)](https://pepy.tech/project/query-counter)
[![Downloads](https://static.pepy.tech/personalized-badge/query-counter?period=total&units=international_system&left_color=grey&right_color=blue&left_text=Downloads)](https://pepy.tech/project/query-counter)
[![PyPI license](https://img.shields.io/pypi/l/query-counter.svg)](https://pypi.python.org/pypi/query-counter/)

SQLAlchemy model N+1 debugger.

NOTE: This is a debugging tool that is not meant to be deployed in production.

## About
This module will help identify N+1 DB calls made through SQLAlchemy. It takes advantage of the SQLAlchemy event listener for `do_orm_execute`.

QueryCounter will provide insights into which model DB calls are made multiple times, with optional tracebacks and heuristics to determine where these calls originate.

By default, QueryCounter will log results with an optional config to raise an Exception.

## Installation
```bash
pip install query-counter
```

## Usage
Usage: Create QueryCounter with a SQLalchemy session, an optional config, and `initialize`
when you would like to start tracking requests:
```python
from query_counter import QueryCounter

query_counter = QueryCounter(session=session)
query_counter.initialize()
```

Run `analyze` to dig into queries that ran since initialization:
```python
query_counter.analyze()
```

This also works as a context manager:

```python
with QueryCounter(
    session=session, config=QueryAnalysisConfig(alert_threshold=0)
) as counter:
    session.query(User).first()
    counter.analyze()
```

Setting a breakpoint in the analyze function will allow you to inspect
all of the queries and their stack traces.

## Configuration
`QueryCounter` accepts an optional `config` kwarg of type `QueryAnalysisConfig`.

`QueryAnalysisConfig` is a dataclass with the following specifications/defaults:
```python
# QueryCounter analyze will not log or raise exceptions if the number
# of duplicated DB calls is less than the alert_threshold
alert_threshold: int = 10

# QueryCounter analyze will raise an exception if True
raise_if_exceeds: bool = False

# QueryCounter analyze will info log if no DB calls
# exceed the threshold
log_no_alert: bool = False

# QueryCounter will store the stacktrace relevant to the DB call
traceback_enabled: bool = False

# QueryInstance will inspect frames and filter the stack down
# to codepaths specified in heuristic_paths
heuristics_enabled: bool = False

# Requires heuristics_enabled=True - filters stack down to
# these codepaths
heuristic_paths: list = field(default_factory=list)
```

## TODO
- [ ] Linting
- [x] Tests
- [x] Pipeline

## License
QueryCounter is distributed under the MIT License.

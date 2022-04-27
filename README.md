# QueryCounter
SQLAlchemy model N+1 debugger.

## About
This module will help identify N+1 DB calls made through SQLAlchemy. It takes advantage of the SQLAlchemy event listener for `do_orm_execute`.

QueryCounter will provide insights into which model DB calls are made multiple times, with optional tracebacks and heuristics to determine where these calls originate.

By default, QueryCounter will log results with an optional config to raise an Exception.

## Installation
TODO

## Configuration
TODO

## Usage
Usage: Create QueryCounter with optional config and `initialize`
when you would like to start tracking requests:
```python
query_counter = QueryCounter(session=session, config=query_counter_config)
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

## TODO
- [ ] Linting
- [ ] Tests
- [ ] Pipeline

## License
QueryCounter is distributed under the MIT License.

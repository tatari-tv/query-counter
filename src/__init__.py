from __future__ import annotations

import logging
import sys
import traceback
import warnings
from dataclasses import dataclass
from dataclasses import field

from sqlalchemy import event
from sqlalchemy.orm import ORMExecuteState
from sqlalchemy.orm import Session
from sqlalchemy.sql.selectable import Select

logger = logging.getLogger(__name__)


class QueryCountMissingSession(Exception):
    '''
    Raised when a QueryCounter attempts to create a listener,
    but there is no sqlalchemy session.
    '''

    def __init__(self):
        super().__init__('Failed to create listener - no session provided')


class QueryCountError(Exception):
    '''
    Raised when a QueryCounter encounters the same query multiple
    times exceeding the QueryAnalysisConfig provided to the QueryCounter
    '''

    def __init__(self, message=None):
        message = f'QueryCounter:\n{message}'
        super().__init__(message)


@dataclass
class QueryAnalysisConfig:
    '''
    Determines the behavior of QueryCounter and QueryInstance
    '''

    alert_threshold: int = 10
    raise_if_exceeds: bool = False
    log_no_alert: bool = False
    traceback_enabled: bool = False
    heuristics_enabled: bool = False
    heuristic_paths: list = field(default_factory=list)


@dataclass
class Heuristics:
    '''
    Filtered stack data containing key info relevant to DB calls
    '''

    filename: str
    caller: str
    line_number: int


@dataclass
class QueryInstance:
    '''
    Stores data related to a db call and its related stack trace
    including the number of times it was called
    '''

    stack: list[str]
    count: int
    statement: Select
    config: QueryAnalysisConfig
    heuristics: list[Heuristics] = field(default_factory=list)

    def __init__(
        self,
        stack: list[str],
        count: int,
        statement: Select,
        config: QueryAnalysisConfig,
    ):
        self.stack = stack
        self.count = count
        self.statement = statement
        self.config = config
        self.heuristics = self._heuristics() if self.config.heuristics_enabled else []

    def __eq__(self, other):
        return (
            isinstance(other, self.__class__)
            and self.stack == other.stack
            and str(self.statement) == str(other.statement)
        )

    def __hash__(self):
        return hash((str(self.statement), ''.join(self.stack)))

    def _heuristics(self):
        filtered_stack = []
        frame = 1

        if not self.config.heuristic_paths:
            return []

        while True:
            try:
                filename = sys._getframe(frame).f_code.co_filename
                caller = sys._getframe(frame).f_code.co_name
                line = sys._getframe(frame).f_lineno

                if any(path in filename for path in self.config.heuristic_paths):
                    filtered_stack.append(
                        Heuristics(filename=filename, caller=caller, line_number=line)
                    )

                frame += 1
            except ValueError:
                return filtered_stack


@dataclass
class QueryCounter:
    '''
    Store unique QueryInstances and aggregate the counts. Includes
    helper functions to format, analyze, and report on frequent
    duplicate calls.

    By default, this will log results with an optional config
    to raise an Exception.

    Usage: Create QueryCounter with optional config and `initialize`
    when you would like to start tracking requests:
    query_counter = QueryCounter(session=session, config=query_counter_config)
    query_counter.initialize()

    Run `analyze` to dig into queries that ran since initialization:
    query_counter.analyze()

    This also works as a context manager:

        with QueryCounter(
            session=session, config=QueryAnalysisConfig(alert_threshold=0)
        ) as counter:
            session.query(User).first()
            counter.analyze()

    Setting a breakpoint in the analyze function will allow you to inspect
    all of the queries and their stack traces.
    '''

    session: Session | None = None
    config: QueryAnalysisConfig = QueryAnalysisConfig()
    queries: dict[int, QueryInstance] = field(default_factory=dict)

    def __enter__(self):
        self._create_listener()
        return self

    def __exit__(self, *args):
        event.remove(self.session, 'do_orm_execute', self._record_query)
        return self

    def _record_query(self, orm_execute_state: ORMExecuteState):
        stack = traceback.format_stack() if self.config.traceback_enabled else []
        qi = QueryInstance(
            stack=stack,
            count=1,
            statement=orm_execute_state.statement,
            config=self.config,
        )
        self.insert(qi)

    def initialize(self):
        self._clear()
        self._create_listener()

    def _create_listener(self):
        if not self.session:
            raise QueryCountMissingSession()

        if not event.contains(self.session, 'do_orm_execute', self._record_query):
            event.listen(self.session, 'do_orm_execute', self._record_query)

    def insert(self, query_instance: QueryInstance):
        key = hash(query_instance)
        if key in self.queries:
            self.queries[key].count += 1
        else:
            self.queries[key] = query_instance

    @property
    def sorted_queries(self):
        '''
        Sort queries by count in descending order
        '''
        return sorted(self.queries.values(), key=lambda x: x.count, reverse=True)

    @property
    def filtered_queries(self):
        '''
        Filter sorted queries where the count is greater than the
        configured threshold
        '''
        return [q for q in self.sorted_queries if q.count > self.config.alert_threshold]

    def format(self):
        '''
        Format filtered queries for logging
        '''
        return '\n'.join(
            [f'Count: {q.count} Query: {q.statement}' for q in self.filtered_queries]
        )

    def analyze(self):
        '''
        Log or raise an exception based on the provided QueryAnalysisConfig
        '''
        if len(self.filtered_queries) > 0:
            if self.config.raise_if_exceeds:
                raise QueryCountError(message=self.format())
            else:
                warnings.warn(
                    UserWarning(
                        'QueryCounter: '
                        'Test triggered DB query exceeding alert threshold\n'
                        f'{self.format()}'
                    )
                )
        elif self.config.log_no_alert:
            logger.info('QueryCounter: No queries exceed threshold')

    def _clear(self):
        '''
        Clear queries for new round of analysis
        '''
        self.queries = {}

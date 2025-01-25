from _typeshed import Incomplete
from sqlalchemy.orm import Session as Session

class SqlAlchemyPostgresqlEngineWrapper:
    engine: Incomplete
    def __init__(self, sql_user: str, sql_password: str, sql_host: str, sql_port: int, sql_database: str, pool_size: int) -> None: ...
    def create_session(self) -> Session: ...

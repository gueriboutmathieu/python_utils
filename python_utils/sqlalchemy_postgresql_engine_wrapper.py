from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import QueuePool


class SqlAlchemyPostgresqlEngineWrapper:
    def __init__(
        self,
        sql_user: str,
        sql_password: str,
        sql_host: str,
        sql_port: int,
        sql_database: str,
        pool_size: int,
    ):
        self.engine = create_engine(
            f"postgresql+psycopg2://{sql_user}:{sql_password}@{sql_host}:{sql_port}/{sql_database}",
            poolclass=QueuePool,
            pool_size=pool_size,
        )

    def create_session(self) -> Session:
        session = sessionmaker(self.engine)()
        return session

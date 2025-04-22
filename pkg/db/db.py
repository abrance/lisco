from contextlib import contextmanager

from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from pkg.util.config.config import config_manager

Base = declarative_base()


class DBManager:
    def __init__(self, db_name, db_host, db_port, db_user, db_password):
        self.db_name = db_name
        self.db_host = db_host
        self.db_port = db_port
        self.db_user = db_user
        self.db_password = db_password

        # 创建数据库连接字符串
        connection_string = (
            f"mysql+pymysql://"
            f"{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"
        )

        # 创建数据库引擎
        self.engine = create_engine(connection_string)

        # 初始化会话工厂
        self.SessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=self.engine
        )

    def init_db(self):
        Base.metadata.create_all(bind=self.engine)

    def connect(self):
        self.engine.connect()

    @contextmanager
    def get_db_session(self):
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()


# 为FastAPI创建一个依赖函数来提供数据库会话
def get_db(
    db_manager: DBManager = Depends(
        lambda: DBManager(
            config_manager.get_config().db.db_name,
            config_manager.get_config().db.host,
            config_manager.get_config().db.port,
            config_manager.get_config().db.user,
            config_manager.get_config().db.password,
        ),
    )
):
    with db_manager.get_db_session() as session:
        yield session

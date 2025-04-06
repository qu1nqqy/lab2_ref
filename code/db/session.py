# MySQLのベースとセッションの定義
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session, declarative_base

# 接続情報
user_name = "user"
password = "password"
host = "db"
database_name = "sample_db"

DATABASE = 'mysql://%s:%s@%s/%s?charset=utf8' % (
    user_name,
    password,
    host,
    database_name
)

# DBとの接続
ENGINE = create_engine(
    DATABASE,
    echo=True
)

# Sessionの作成
session = scoped_session(
    sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=ENGINE
    )
)

# modelで使用する
Base = declarative_base()
# DB接続用のセッションクラス、インスタンスが作成されると起動する
Base.query = session.query_property()

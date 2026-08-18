# 

import os
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.orm import sessionmaker, declarative_base

# ----------------------------------------------------
# 1. MySQL Connection Configuration
# ----------------------------------------------------
DB_USER = os.getenv("DB_USER", "techsasi_2207")
DB_PASSWORD = os.getenv("DB_PASSWORD", "SasiKutty2207@Lovely")  # Put your MySQL password here
DB_HOST = os.getenv("DB_HOST", "65.108.76.42")
DB_PORT = int(os.getenv("DB_PORT", 3306))
DB_NAME = os.getenv("DB_NAME", "techsasi_mentohub")

# URL.create safely encodes passwords containing special characters (like '@' or '#')
DATABASE_URL = URL.create(
    drivername="mysql+pymysql",
    username=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT,
    database=DB_NAME,
    query={"charset": "utf8mb4"}
)

# ----------------------------------------------------
# 2. Engine & Connection Pool Settings
# ----------------------------------------------------
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,      # Tests connection liveness before executing queries
    pool_recycle=3600,       # Recycles idle connections every hour
    pool_size=10,            # Main pool connection limit
    max_overflow=20,         # Extra connections allowed during peak traffic
    connect_args={
        "connect_timeout": 10  # Timeout (in seconds) if remote server is unreachable
    }
)

# ----------------------------------------------------
# 3. Session & Base
# ----------------------------------------------------
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# FastAPI Dependency for handling DB sessions per request
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
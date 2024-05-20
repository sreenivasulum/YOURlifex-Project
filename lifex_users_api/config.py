from functools import cache
import sys
import logging
import time
import contextlib


from loguru import logger
from starlette.config import Config
from sqlalchemy import MetaData, Table, create_engine
from sqlalchemy.engine import URL
from sqlalchemy.orm import sessionmaker


config = Config(".env")


# logging configuration
class InterceptHandler(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:  # pragma: no cover
        logger_opt = logger.opt(depth=7, exception=record.exc_info)
        logger_opt.log(record.levelname, record.getMessage())

DEBUG = config("DEBUG", cast=bool, default=False)
LOGGING_LEVEL = logging.DEBUG if DEBUG else logging.INFO
logging.basicConfig(
    handlers=[InterceptHandler(level=LOGGING_LEVEL)], level=LOGGING_LEVEL
)
logger.configure(handlers=[{"sink": sys.stderr, "level": LOGGING_LEVEL}])

# database engine configuration
url = URL.create(
    drivername="postgresql",
    username=config("APP_DATABASE_USERNAME", default=""),
    host=config("APP_DATABASE_HOST", default=""),
    database=config("APP_DATABASE_NAME", default=""),
    password=config("APP_DATABASE_PASSWORD", default=""),
)

# Connection String (Adjust for your database type)
@cache
def get_engine():
    engine = create_engine(
        url,
        pool_pre_ping=True, 
        pool_recycle=600,
        pool_size=25,
    )
    return engine

# fetch metadata
metadata = MetaData()
metadata.reflect(bind=get_engine())

# provide session and answers table references
Users = Table('users', metadata)
Session = sessionmaker(bind=get_engine())

def get_user_voice_id(user_id):
    with Session() as session:
        user_rows = session.query(Users).filter(Users.c.id == user_id).with_entities(Users.c.voice_id)

        
        voice_id:str
        if user_rows.first():
            voice_id= str(user_rows.first()[0])
            logger.info(user_rows.first()[0])
            logger.info("User voice id found!")
        else:
            logger.info("User not found.")
            voice_id = config("ELEVENLABS_VOICE_ID")
        
        logger.info("User voice id:")
        logger.info(voice_id)
        return voice_id
    
# time code assets
@contextlib.contextmanager
def time_code_section(name):
    """Context manager to time and report the execution time of a code section.

    Args:
        name: Name of the code section to be displayed in the report.
    """
    start_time = time.time()
    yield  # This is where the code we want to time will run
    end_time = time.time()
    elapsed_time = end_time - start_time
    logger.info(f"Code Section '{name}' took {elapsed_time:.4f} seconds to execute.")
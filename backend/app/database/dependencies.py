from sqlalchemy.exc import SQLAlchemyError

from app.database.database import SessionLocal
from app.core.logger import logger


def get_db():
    db = SessionLocal()
    try:
        yield db
    except Exception:
        try:
            db.rollback()
        except SQLAlchemyError:
            logger.warning("Could not roll back a failed database request.", exc_info=True)
        raise
    finally:
        try:
            db.close()
        except SQLAlchemyError:
            logger.warning("Could not cleanly close a database request session.", exc_info=True)
from dotenv import dotenv_values
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import cx_Oracle


config = dotenv_values(".env")
Base = declarative_base()
Session = None

def init_db(test_flag: bool):
    global Base, Session

    cx_Oracle.init_oracle_client(lib_dir=config['TEST_ORACLE_CLIENT'] if test_flag else config['ORACLE_CLIENT'])
    # oracle+cx_oracle://user:pass@hostname:port[/dbname][?service_name=<service>[&key=value&key=value...]]
    dsn = f"oracle+cx_oracle://{config['DAMIDB_USERNAME']}:{config['DAMIDB_PASSWORD']}@{config['TNS_ADMIN']}"
    engine = create_engine(dsn)
    Session = sessionmaker(bind=engine)

    import db.model.Music
    import db.model.Record
    Base.metadata.create_all(engine)


class SessionContext:
    session = None

    def __enter__(self):
        self.session = Session()
        return self.session

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()

from dotenv import dotenv_values
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import cx_Oracle

cx_Oracle.init_oracle_client(lib_dir="db/instantclient_19_24")

config = dotenv_values(".env")

# oracle+cx_oracle://user:pass@hostname:port[/dbname][?service_name=<service>[&key=value&key=value...]]
dsn = f"oracle+cx_oracle://{config['DAMIDB_USERNAME']}:{config['DAMIDB_PASSWORD']}@{config['TNS_ADMIN']}"
engine = create_engine(dsn)
Base = declarative_base()

Session = sessionmaker(bind=engine)

def init_db():
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

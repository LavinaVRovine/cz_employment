from sqlalchemy import create_engine, exc
from config import DATABASE_URL, MY_LOGGER
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


def test_engine(url=DATABASE_URL):
    try:
        eng = create_engine(url)
        eng.connect()
        return eng
    except exc.OperationalError as oe:
        MY_LOGGER.critical(f"Could not connect to db {oe}", exc_info=True)
        raise
    except Exception as e:
        MY_LOGGER.critical(f"Could not connect to db {e}", exc_info=True)
        raise


engine = test_engine()
Session = sessionmaker(bind=engine)


def table_exists(name, engine):
    ret = engine.dialect.has_table(engine, name)
    print('Table "{}" exists: {}'.format(name, ret))
    return ret


def flush_db():
    from sqlalchemy import MetaData
    base = declarative_base()
    metadata = MetaData(engine, reflect=True)
    rly = input("Do you really want to drop all the tables in db? Y/n/Y2A: ")
    if rly == "Y":
        tables = [metadata.tables.get(table_name) for table_name in list(metadata.tables) if
                  table_name != "demographic_statistics"]
        base.metadata.drop_all(engine, tables, checkfirst=True)
    elif rly == "Y2A":
        rly_rly = input("Do you really want to drop all the tables in db including demographics? "
                        "It' takes a while to scrape! Y/n/: ")
        if rly_rly == "Y":
            tables = [metadata.tables.get(table_name) for table_name in list(metadata.tables)]
            base.metadata.drop_all(engine, tables, checkfirst=True)


if __name__ == "__main__":
    flush_db()

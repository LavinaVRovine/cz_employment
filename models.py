from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
Base = declarative_base()


class ProcessedFile(Base):
    __tablename__ = 'processed_files'

    id = Column(Integer, primary_key=True)
    url = Column(String)
    time_created = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<ProcessedFile(id={self.id}, url={self.url}, time_created={self.time_created})>"


def create_all_tables(sa_engine):
    Base.metadata.create_all(sa_engine)
    print("All tables created")


if __name__ == "__main__":

    from db_handle import engine

    create_all_tables(engine)
    Base.metadata.create_all(engine)
    print("Successfully created all tables (and yes, it's a single table)")

import os
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# database file path
DATABASE_FILE = "cv_database.sqlite"

# absolute path of the directory the script is in
project_dir = os.path.dirname(os.path.abspath(__file__))

# Go up one level to the root directory
root_dir = os.path.dirname(project_dir)
DATABASE_PATH = os.path.join(root_dir, DATABASE_FILE)

engine = create_engine(f'sqlite:///{DATABASE_PATH}', echo=False)
db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

Base = declarative_base()
Base.query = db_session.query_property()

# CV table model
class CV(Base):
    __tablename__ = 'cvs'
    id = Column(Integer, primary_key=True)
    filename = Column(String(200), unique=True, nullable=False)
    content = Column(Text, nullable=False)

    def __repr__(self):
        return f'<CV {self.filename}>'

# initializing the database and creating tables
def init_db():
    
    Base.metadata.create_all(bind=engine)
    print("Database initialized and tables created.")


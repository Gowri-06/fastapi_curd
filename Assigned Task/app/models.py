from sqlalchemy import  Column, Integer, String
from config import Base


class Book(Base):
    __tablename__ ="book"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    author = Column(String)
    publication_year = Column(Integer)
from sqlalchemy.orm import Session
from models import Book
from schemas import BookSchema


def get_book(db: Session, skip: int = 0, limit: int = 100):
    book_objects = db.query(Book).offset(skip).limit(limit).all()

    for book_object in book_objects: 
        book_id = book_object.id
        book_title = book_object.title
        book_author = book_object.author
        book_publication_year = book_object.publication_year
        # Format the attributes into a readable format, for example, a string
        formatted_book = f"id: {book_id}, Title: {book_title}, Author: {book_author}, Publication Year: {book_publication_year}"
        print(formatted_book)
    # c  = dict(book_object)
    # print("c",c)
    return db.query(Book).offset(skip).limit(limit).all()


def get_book_by_id(db: Session, book_id: int):
    return db.query(Book).filter(Book.id == book_id).first()




def create_book(db: Session, book: BookSchema):
    _book = Book(title=book.title, author=book.author,publication_year=book.publication_year)
    db.add(_book)
    db.commit()
    db.refresh(_book)
    return _book


def remove_book(db: Session, book_id: int):
    _book = get_book_by_id(db=db, book_id=book_id)
    db.delete(_book)
    db.commit()


def update_book(db: Session, book_id: int, title: str, author: str,publication_year: int):
    
    _book = get_book_by_id(db=db, book_id=book_id)

    _book.title = title
    _book.author = author
    _book.publication_year = publication_year

    db.commit()
    db.refresh(_book)
    return _book

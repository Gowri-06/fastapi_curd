from fastapi import APIRouter, HTTPException, Path
from fastapi import Depends
from config import SessionLocal
from sqlalchemy.orm import Session
from schemas import BookSchema, Request, Response, RequestBook
from fastapi.responses import JSONResponse

import crud

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# @router.post("/create", response_model=Response[BookSchema])
# async def create_book_service(request: RequestBook, db: Session = Depends(get_db)):
#     created_book = crud.create_book(db, book=request.parameter)
#     return Response[BookSchema](code="200", status="Ok", message="Book created successfully",)

@router.post("/create/")
async def create_book_service(request: RequestBook, db: Session = Depends(get_db)):
    created_book = crud.create_book(db, book=request.parameter)
    print(created_book)
    return Response(status="Ok",
                    code="200",
                    message="Book created successfully").dict(exclude_none=True)


@router.get("/")
async def get_books(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    try:
        _books = crud.get_book(db, skip, limit)
        print(_books)
    except:
        response_data = {"error": "record not found"}
        return JSONResponse(status_code=200, content=response_data)
    a  = []
    for book_object in _books: 
        book_id = book_object.id
        book_title = book_object.title
        book_author = book_object.author
        book_publication_year = book_object.publication_year
        b = {
            "id":book_id,
            "title":book_title,
            "author":book_author,
            "publication_year":book_publication_year 
            }
        print(b)
        a.append(b)
    print("all_data",a)
    return JSONResponse(status_code=200, content=a)

    # return Response(status="Ok", code="200", message="Success fetch all data", result=_books)

@router.get("/{book_id}/")  
async def get_book_by_id(book_id: int, db: Session = Depends(get_db)):
        print("check")
        _books = crud.get_book_by_id(db, book_id=book_id)
        print("_books",_books,bool(_books))
        check = bool(_books) 
        if not(bool(_books)):
            response_data = {"error": "Book not found"}
            return JSONResponse(status_code=200, content=response_data)
        book_id = _books.id
        book_title = _books.title
        book_author = _books.author
        book_publication_year = _books.publication_year
        b = {
            "book_id":book_id,
            "book_title":book_title,
            "book_author":book_author,
            "book_publication_year":book_publication_year 
            }
        print(b)   
        return JSONResponse(status_code=200, content=b)
        # for book_object in _books: 
        #     book_id = book_object.id
        #     book_title = book_object.title
        #     book_author = book_object.author
        #     book_publication_year = book_object.publication_year
        #     b = {
        #         "book_id":book_id,
        #         "book_title":book_title,
        #         "book_author":book_author,
        #         "book_publication_year":book_publication_year 
        #         }
        #     b.update(a)
        #     # Format the attributes into a readable format, for example, a string
        #     # formatted_book = f"id: {book_id}, Title: {book_title}, Author: {book_author}, Publication Year: {book_publication_year}"
       

        # return Response(status="Ok", code="200", message="Success fetch one particular data", result=_books)
       


@router.put("/{book_id}/")
async def update_book(book_id: int,request: RequestBook, db: Session = Depends(get_db)):
    try:
        _books = crud.update_book(db, book_id=book_id,
                                title=request.parameter.title, author=request.parameter.author,publication_year=request.parameter.publication_year)
        print("_books",_books)
    except:
        response_data = {"error": "record not found"}
        return JSONResponse(status_code=200, content=response_data)
        # if not(bool(_books)):
        #     response_data = {"error": "record not found"}
        #     return JSONResponse(status_code=200, content=response_data)
    book_id = _books.id
    book_title = _books.title
    book_author = _books.author
    book_publication_year = _books.publication_year
    b = {
        "book_id":book_id,
        "book_title":book_title,
        "book_author":book_author,
        "book_publication_year":book_publication_year 
        }
    print(b)   
    return JSONResponse(status_code=200, content=b)
   
    # return Response(status="Ok", code="200", message="Success update data", result=_book)


@router.delete("/{book_id}/")
async def delete_book(book_id: int,  db: Session = Depends(get_db)):
    crud.remove_book(db, book_id=book_id)
    return Response(status="Ok", code="200", message="Success delete data").dict(exclude_none=True)

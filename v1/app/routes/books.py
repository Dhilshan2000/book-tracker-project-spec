from typing import List
from fastapi import APIRouter, HTTPException, status
from app.models.book import BookCreate, BookUpdate, BookResponse
from app.services import book_service

router = APIRouter(prefix="/books", tags=["Books"])

@router.post(
    "",
    response_model=BookResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add a new book"
)
def add_book(book_in: BookCreate):
    created_book = book_service.create_book(book_in)
    return created_book

@router.get(
    "",
    response_model=List[BookResponse],
    status_code=status.HTTP_200_OK,
    summary="Get all books"
)
def get_books():
    return book_service.get_all_books()

@router.get(
    "/{id}",
    response_model=BookResponse,
    status_code=status.HTTP_200_OK,
    summary="Get a book by ID"
)
def get_book(id: str):
    book = book_service.get_book_by_id(id)
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with id '{id}' not found"
        )
    return book

@router.patch(
    "/{id}",
    response_model=BookResponse,
    status_code=status.HTTP_200_OK,
    summary="Partially update a book by ID"
)
def update_book(id: str, book_update: BookUpdate):
    updated = book_service.update_book(id, book_update)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with id '{id}' not found"
        )
    return updated

@router.delete(
    "/{id}",
    status_code=status.HTTP_200_OK,
    summary="Delete a book by ID"
)
def delete_book(id: str):
    success = book_service.delete_book_by_id(id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with id '{id}' not found"
        )
    return {"message": f"Book with id '{id}' deleted successfully"}

@router.delete(
    "",
    status_code=status.HTTP_200_OK,
    summary="Delete all books"
)
def delete_all_books():
    deleted_count = book_service.delete_all_books()
    return {
        "message": "All books deleted successfully",
        "deleted_count": deleted_count
    }

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from app.models.book import BookCreate, BookUpdate, BookResponse
from app.core.dependencies import get_current_user
from app.services import book_service

router = APIRouter(prefix="/books", tags=["Books"])

@router.post(
    "",
    response_model=BookResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add a new book (tied to current user)"
)
def add_book(book_in: BookCreate, current_user: dict = Depends(get_current_user)):
    return book_service.create_book(book_in, user_id=current_user["id"])

@router.get(
    "",
    response_model=List[BookResponse],
    status_code=status.HTTP_200_OK,
    summary="Get all books belonging to current user"
)
def get_books(current_user: dict = Depends(get_current_user)):
    return book_service.get_user_books(user_id=current_user["id"])

@router.get(
    "/{id}",
    response_model=BookResponse,
    status_code=status.HTTP_200_OK,
    summary="Get a book by ID (only if owned by current user)"
)
def get_book(id: str, current_user: dict = Depends(get_current_user)):
    book = book_service.get_user_book_by_id(book_id=id, user_id=current_user["id"])
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
    summary="Partially update a book by ID (only if owned by current user)"
)
def update_book(id: str, book_update: BookUpdate, current_user: dict = Depends(get_current_user)):
    updated = book_service.update_user_book(book_id=id, user_id=current_user["id"], update_data=book_update)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with id '{id}' not found"
        )
    return updated

@router.delete(
    "/{id}",
    status_code=status.HTTP_200_OK,
    summary="Delete a book by ID (only if owned by current user)"
)
def delete_book(id: str, current_user: dict = Depends(get_current_user)):
    success = book_service.delete_user_book_by_id(book_id=id, user_id=current_user["id"])
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with id '{id}' not found"
        )
    return {"message": f"Book with id '{id}' deleted successfully"}

@router.delete(
    "",
    status_code=status.HTTP_200_OK,
    summary="Delete all books belonging to current user"
)
def delete_all_books(current_user: dict = Depends(get_current_user)):
    deleted_count = book_service.delete_all_user_books(user_id=current_user["id"])
    return {
        "message": "All books belonging to the current user deleted successfully",
        "deleted_count": deleted_count
    }

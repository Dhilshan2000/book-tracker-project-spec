from typing import List, Optional
from bson import ObjectId
from app.database import get_books_collection
from app.models.book import BookCreate, BookUpdate

def serialize_book(doc: dict) -> dict:
    if not doc:
        return doc
    book = dict(doc)
    book["id"] = str(book.pop("_id"))
    return book

def create_book(book_data: BookCreate, user_id: str) -> dict:
    collection = get_books_collection()
    data = book_data.model_dump()
    data["user_id"] = user_id
    result = collection.insert_one(data)
    created = collection.find_one({"_id": result.inserted_id})
    return serialize_book(created)

def get_user_books(user_id: str) -> List[dict]:
    collection = get_books_collection()
    cursor = collection.find({"user_id": user_id})
    return [serialize_book(doc) for doc in cursor]

def get_user_book_by_id(book_id: str, user_id: str) -> Optional[dict]:
    if not ObjectId.is_valid(book_id):
        return None
    collection = get_books_collection()
    doc = collection.find_one({
        "_id": ObjectId(book_id),
        "user_id": user_id
    })
    if not doc:
        return None
    return serialize_book(doc)

def update_user_book(book_id: str, user_id: str, update_data: BookUpdate) -> Optional[dict]:
    if not ObjectId.is_valid(book_id):
        return None
    collection = get_books_collection()
    
    fields_to_update = update_data.model_dump(exclude_unset=True)
    if fields_to_update:
        collection.update_one(
            {"_id": ObjectId(book_id), "user_id": user_id},
            {"$set": fields_to_update}
        )
    
    updated_doc = collection.find_one({
        "_id": ObjectId(book_id),
        "user_id": user_id
    })
    if not updated_doc:
        return None
    return serialize_book(updated_doc)

def delete_user_book_by_id(book_id: str, user_id: str) -> bool:
    if not ObjectId.is_valid(book_id):
        return False
    collection = get_books_collection()
    result = collection.delete_one({
        "_id": ObjectId(book_id),
        "user_id": user_id
    })
    return result.deleted_count > 0

def delete_all_user_books(user_id: str) -> int:
    collection = get_books_collection()
    result = collection.delete_many({"user_id": user_id})
    return result.deleted_count


from datetime import datetime, timezone
from typing import Optional
from bson import ObjectId
from app.database import get_users_collection
from app.models.user import UserCreate
from app.core.security import hash_password, verify_password

def serialize_user(doc: dict) -> dict:
    if not doc:
        return doc
    user = dict(doc)
    user["id"] = str(user.pop("_id"))
    # Never expose hashed_password in serialized user response
    user.pop("hashed_password", None)
    return user

def get_user_by_email(email: str) -> Optional[dict]:
    collection = get_users_collection()
    return collection.find_one({"email": email.strip().lower()})

def get_user_by_id(user_id: str) -> Optional[dict]:
    if not ObjectId.is_valid(user_id):
        return None
    collection = get_users_collection()
    doc = collection.find_one({"_id": ObjectId(user_id)})
    if not doc:
        return None
    return serialize_user(doc)

def signup_user(user_in: UserCreate) -> Optional[dict]:
    collection = get_users_collection()
    email_clean = user_in.email.strip().lower()
    
    # Check if user already exists
    existing_user = collection.find_one({"email": email_clean})
    if existing_user:
        return None

    hashed_pw = hash_password(user_in.password)
    user_doc = {
        "email": email_clean,
        "hashed_password": hashed_pw,
        "created_at": datetime.now(timezone.utc)
    }
    result = collection.insert_one(user_doc)
    created = collection.find_one({"_id": result.inserted_id})
    return serialize_user(created)

def authenticate_user(email: str, password: str) -> Optional[dict]:
    collection = get_users_collection()
    user = collection.find_one({"email": email.strip().lower()})
    if not user:
        return None
    if not verify_password(password, user.get("hashed_password", "")):
        return None
    return serialize_user(user)


from typing import Optional, Dict, Any
from datetime import datetime, timezone
import uuid
import bcrypt
from app.config import settings
from app.database import get_users_collection
from app.models.user import UserCreate
from app.firebase.firebase_app import (
    init_firebase,
    is_mock_mode,
    generate_mock_id_token,
    FirebaseAuthError
)

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
    except Exception:
        return False

def signup_user(user_in: UserCreate) -> Dict[str, Any]:
    collection = get_users_collection()
    email_clean = user_in.email.strip().lower()

    # Check if user already exists in MongoDB
    if collection.find_one({"email": email_clean}):
        raise FirebaseAuthError("Email already registered", status_code=400)

    uid = str(uuid.uuid4())
    user_doc = {
        "uid": uid,
        "email": email_clean,
        "hashed_password": hash_password(user_in.password),
        "created_at": datetime.now(timezone.utc)
    }
    collection.insert_one(user_doc)

    return {
        "id": uid,
        "email": email_clean
    }

def login_user(email: str, password: str) -> Optional[str]:
    collection = get_users_collection()
    email_clean = email.strip().lower()
    user = collection.find_one({"email": email_clean})

    if not user:
        return None

    if not verify_password(password, user.get("hashed_password", "")):
        return None

    init_firebase()
    if not is_mock_mode():
        from firebase_admin import auth as fb_auth
        try:
            custom_token = fb_auth.create_custom_token(
                user["uid"],
                developer_claims={"email": user["email"]}
            )
            return custom_token.decode("utf-8") if isinstance(custom_token, bytes) else custom_token
        except Exception as e:
            print(f"[Firebase Admin SDK Error] Failed to create custom token: {e}")
            return None
    else:
        return generate_mock_id_token(user["uid"], user["email"])

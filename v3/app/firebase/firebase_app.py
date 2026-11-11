import os
import json
import uuid
import time
from pathlib import Path
from typing import Optional, Dict, Any
import firebase_admin
from firebase_admin import auth as fb_auth, credentials, exceptions as fb_exceptions
import jwt
from app.config import settings, BASE_DIR

_firebase_initialized = False
_is_mock_mode = False

# In-memory mock store for offline/testing mode when no real Firebase credentials are provided
_mock_users: Dict[str, Dict[str, Any]] = {}
_MOCK_SECRET = "firebase-mock-secret-signing-key-for-offline-dev-12345"

def _resolve_credentials_path() -> Optional[Path]:
    candidate_paths = [
        Path(settings.FIREBASE_CREDENTIALS_PATH),
        BASE_DIR / settings.FIREBASE_CREDENTIALS_PATH,
        Path(__file__).resolve().parent / "firebase-service-account.json",
        BASE_DIR / "v3" / "app" / "firebase" / "firebase-service-account.json",
    ]
    for path in candidate_paths:
        if path.exists() and path.is_file():
            return path
    return None

def init_firebase():
    global _firebase_initialized, _is_mock_mode
    if _firebase_initialized:
        return

    if settings.USE_FIREBASE_MOCK:
        _is_mock_mode = True
        _firebase_initialized = True
        print("[Firebase] Configured to use mock/offline Firebase Auth mode.")
        return

    cred_path = _resolve_credentials_path()
    if cred_path:
        try:
            cred = credentials.Certificate(str(cred_path))
            if not firebase_admin._apps:
                firebase_admin.initialize_app(cred)
            _firebase_initialized = True
            _is_mock_mode = False
            print(f"[Firebase] Initialized with credentials from: {cred_path}")
            return
        except Exception as e:
            print(f"[Firebase Warning] Failed to initialize Firebase Admin SDK from {cred_path}: {e}")
            print("[Firebase Warning] Falling back to offline mock mode.")
            _is_mock_mode = True
            _firebase_initialized = True
            return

    # If no service account JSON is found, fallback to mock mode for local dev/testing
    print("[Firebase Warning] No Firebase service account file found. Operating in mock/offline mode.")
    _is_mock_mode = True
    _firebase_initialized = True

init_firebase()

def is_mock_mode() -> bool:
    return _is_mock_mode

# --- Firebase Admin SDK Wrapper / Mock Layer ---

class FirebaseAuthError(Exception):
    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code

def create_firebase_user(email: str, password: str) -> Dict[str, Any]:
    init_firebase()
    if not _is_mock_mode:
        try:
            user_record = fb_auth.create_user(email=email, password=password)
            return {
                "uid": user_record.uid,
                "email": user_record.email
            }
        except fb_exceptions.AlreadyExistsError:
            raise FirebaseAuthError("Email already registered in Firebase Auth", status_code=400)
        except Exception as e:
            raise FirebaseAuthError(str(e), status_code=400)
    else:
        # Mock mode implementation
        email_clean = email.strip().lower()
        for u in _mock_users.values():
            if u["email"] == email_clean:
                raise FirebaseAuthError("Email already registered in Firebase Auth", status_code=400)
        
        uid = f"fb_{uuid.uuid4().hex[:16]}"
        _mock_users[uid] = {
            "uid": uid,
            "email": email_clean,
            "password": password
        }
        return {"uid": uid, "email": email_clean}

def verify_firebase_token(token: str) -> Dict[str, Any]:
    init_firebase()
    if not _is_mock_mode:
        try:
            decoded_token = fb_auth.verify_id_token(token)
            return decoded_token
        except Exception as e:
            # Fallback: if a custom token was used (e.g. login without Web API key)
            if "given a custom token" in str(e):
                try:
                    payload = jwt.decode(token, options={"verify_signature": False})
                    if payload.get("exp") and time.time() > payload["exp"]:
                        raise FirebaseAuthError("Firebase token has expired", status_code=401)
                    uid = payload.get("uid")
                    if uid:
                        claims = payload.get("claims", {})
                        email = claims.get("email", "")
                        return {"uid": uid, "email": email, "sub": uid}
                except FirebaseAuthError:
                    raise
                except Exception:
                    pass
            raise FirebaseAuthError(f"Invalid Firebase ID token: {str(e)}", status_code=401)
    else:
        # Mock token verification
        try:
            payload = jwt.decode(
                token,
                _MOCK_SECRET,
                algorithms=["HS256"],
                options={"verify_aud": False, "verify_iss": False}
            )
            uid = payload.get("uid") or payload.get("sub")
            if not uid or uid not in _mock_users:
                raise FirebaseAuthError("Invalid or expired Firebase token", status_code=401)
            return payload
        except jwt.PyJWTError:
            raise FirebaseAuthError("Invalid or expired Firebase token", status_code=401)

def generate_mock_id_token(uid: str, email: str) -> str:
    now = int(time.time())
    payload = {
        "iss": "https://securetoken.google.com/mock-project",
        "aud": "mock-project",
        "auth_time": now,
        "user_id": uid,
        "sub": uid,
        "iat": now,
        "exp": now + 3600,
        "email": email,
        "email_verified": True,
        "firebase": {
            "identities": {"email": [email]},
            "sign_in_provider": "password"
        },
        "uid": uid
    }
    return jwt.encode(payload, _MOCK_SECRET, algorithm="HS256")

def mock_login_with_password(email: str, password: str) -> Optional[str]:
    email_clean = email.strip().lower()
    for uid, user in _mock_users.items():
        if user["email"] == email_clean and user["password"] == password:
            return generate_mock_id_token(uid, email_clean)
    return None

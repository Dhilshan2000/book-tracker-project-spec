from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.firebase.firebase_app import verify_firebase_token, FirebaseAuthError
from app.database import get_users_collection

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate Firebase credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        decoded_token = verify_firebase_token(token)
    except FirebaseAuthError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e.message,
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception:
        raise credentials_exception

    uid = decoded_token.get("uid") or decoded_token.get("sub") or decoded_token.get("user_id")
    if not uid:
        raise credentials_exception

    users_col = get_users_collection()
    user = users_col.find_one({"uid": uid})
    if not user:
        # Fallback check by email if claims contained it
        email_claim = decoded_token.get("email") or (decoded_token.get("claims", {}) or {}).get("email")
        if email_claim:
            user = users_col.find_one({"email": email_claim})

    if not user:
        raise credentials_exception

    return {
        "id": user["uid"],
        "email": user["email"]
    }

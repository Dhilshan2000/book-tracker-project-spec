from fastapi import APIRouter, HTTPException, Request, status
from app.models.user import UserCreate, UserResponse, Token
from app.services import auth_service
from app.core.security import create_access_token

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post(
    "/signup",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register with email + password"
)
def signup(user_in: UserCreate):
    created_user = auth_service.signup_user(user_in)
    if not created_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    return created_user

@router.post(
    "/login",
    response_model=Token,
    status_code=status.HTTP_200_OK,
    summary="OAuth2 password flow / Login with email and password",
    openapi_extra={
        "requestBody": {
            "required": True,
            "content": {
                "application/x-www-form-urlencoded": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "username": {"type": "string", "description": "Email or username"},
                            "password": {"type": "string", "format": "password", "description": "Password"}
                        },
                        "required": ["username", "password"]
                    }
                },
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "email": {"type": "string", "format": "email", "description": "User email"},
                            "password": {"type": "string", "format": "password", "description": "User password"}
                        },
                        "required": ["email", "password"]
                    }
                }
            }
        }
    }
)
async def login(request: Request):
    content_type = request.headers.get("content-type", "")
    username = None
    password = None

    if "application/json" in content_type:
        try:
            body = await request.json()
            username = body.get("email") or body.get("username")
            password = body.get("password")
        except Exception:
            pass
    else:
        try:
            form = await request.form()
            username = form.get("username") or form.get("email")
            password = form.get("password")
        except Exception:
            pass

    if not username or not password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email/username and password are required"
        )

    user = auth_service.authenticate_user(username, password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"}
        )

    access_token = create_access_token(
        data={"sub": user["id"], "email": user["email"]}
    )
    return {"access_token": access_token, "token_type": "bearer"}

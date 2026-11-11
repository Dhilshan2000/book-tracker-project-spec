import sys
from pathlib import Path

# Ensure version root is on sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi import FastAPI
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import HTMLResponse
from app.routes.auth import router as auth_router
from app.routes.books import router as books_router

app = FastAPI(
    title="Personal Book Tracker API - v3",
    description="FastAPI + MongoDB with Firebase Authentication",
    version="3.0.0",
    docs_url=None
)

app.include_router(auth_router)
app.include_router(books_router)

@app.get("/docs", include_in_schema=False)
def swagger_ui_html():
    res = get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - Swagger UI",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        init_oauth=app.swagger_ui_init_oauth,
    )
    sorter_script = """
    operationsSorter: function(a, b) {
        const order = [
            'post /auth/signup',
            'post /auth/login',
            'post /books',
            'get /books',
            'get /books/{id}',
            'patch /books/{id}',
            'delete /books/{id}',
            'delete /books'
        ];
        const keyA = (a.get('method') + ' ' + a.get('path')).toLowerCase();
        const keyB = (b.get('method') + ' ' + b.get('path')).toLowerCase();
        const idxA = order.indexOf(keyA);
        const idxB = order.indexOf(keyB);
        if (idxA !== -1 && idxB !== -1) return idxA - idxB;
        if (idxA !== -1) return -1;
        if (idxB !== -1) return 1;
        return keyA.localeCompare(keyB);
    },
    """
    custom_html = res.body.decode("utf-8").replace(
        "const ui = SwaggerUIBundle({",
        "const ui = SwaggerUIBundle({\n" + sorter_script
    )
    return HTMLResponse(custom_html)

@app.get("/", tags=["Health"])
def root():
    return {
        "status": "online",
        "version": "v3",
        "message": "Personal Book Tracker API v3 (Firebase Auth) is running"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8002, reload=True)

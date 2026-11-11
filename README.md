# Personal Book Tracker API

A FastAPI + MongoDB project to practice HTTP, CRUD operations, and authentication, built in three progressively complex versions (`v1`, `v2`, `v3`), each isolated in its own folder.

---

## Overview

| Version | Focus | Auth |
| :--- | :--- | :--- |
| **v1** | Core CRUD basics | None |
| **v2** | Custom auth from scratch | OAuth2 + JWT (self-built) |
| **v3** | Managed auth provider | Firebase Auth |

Each version is a complete, standalone FastAPI app. Building the same feature three times with increasing auth complexity makes it easy to see exactly what each layer adds.

---

## Folder Structure

```text
book-tracker/
├── v1/
│   └── app/
│       ├── main.py         # FastAPI app instance, includes routers
│       ├── database.py     # MongoDB connection (pymongo client)
│       ├── config.py       # loads .env values
│       ├── models/         # Pydantic schemas
│       ├── routes/         # /books endpoints
│       └── services/       # DB logic (insert, find, update, delete)
│
├── v2/
│   └── app/
│       ├── main.py
│       ├── database.py
│       ├── config.py
│       ├── models/         # Book + User schemas
│       ├── routes/         # /auth and /books endpoints
│       ├── services/       # auth logic + book DB logic
│       └── core/           # JWT handling, get_current_user dependency
│
├── v3/
│   └── app/
│       ├── main.py
│       ├── database.py
│       ├── config.py
│       ├── firebase/       # Firebase Admin SDK init
│       ├── models/
│       ├── routes/
│       ├── services/
│       └── core/           # Firebase token verification, get_current_user
│
├── .env
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

### Folder Responsibilities (Applies across v1 / v2 / v3)

| Folder | Responsibility |
| :--- | :--- |
| **`models/`** | Pydantic schemas only — request/response shapes, validation. No DB logic. |
| **`routes/`** | HTTP layer — defines endpoints, handles request/response, calls `services/`. No direct DB calls. |
| **`services/`** | Business logic + actual MongoDB operations (`insert_one`, `find`, `find_one`, `update_one`, `delete_one`, `delete_many`). |
| **`core/`** *(v2, v3 only)* | Auth utilities — token creation/verification, the `get_current_user` dependency used to protect routes. |
| **`database.py`** | MongoDB client/connection, shared across routes and services. |
| **`config.py`** | Reads `.env` values (Mongo URI, JWT secret, token expiry, Firebase config path). |

---

## Environment & Config Management

* **`.env`** — Actual secrets (MongoDB URI, JWT secret key, Firebase credentials). Never committed to version control.
* **`.env.example`** — Same keys as `.env`, but with placeholder values. Committed to the repo so anyone cloning it knows exactly what environment variables are required.
* **`.gitignore`** — Excludes:
  * `.env`
  * `__pycache__/`
  * `venv/` or `.venv/`
  * `*.pyc`
  * any Firebase service account JSON file (e.g. `firebase-service-account.json`)

### Example `.env.example`

```env
# MongoDB
MONGO_URI=mongodb+srv://<user>:<password>@cluster.mongodb.net
DB_NAME=book_tracker

# v2 - JWT
JWT_SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# v3 - Firebase
FIREBASE_CREDENTIALS_PATH=./app/firebase/firebase-service-account.json
```

---

## Setup & Running Each Version

### 1. Install Dependencies
```bash
python -m venv venv
.\venv\Scripts\activate   # On Windows
pip install -r requirements.txt
```

### 2. Suggested Build Order & Running Standalone Servers
Each version should run independently — you can `cd` into `v1/`, `v2/`, or `v3/` and start that version's server on its own:

#### v1 — Core CRUD API (no auth)
```bash
cd v1
uvicorn app.main:app --reload --port 8000
```
* Interactive Swagger UI docs: [http://localhost:8000/docs](http://localhost:8000/docs)

**Endpoints:**
* `POST /books` — add a new book
* `GET /books` — get all books
* `GET /books/{id}` — get a book by id
* `PATCH /books/{id}` — partially update a book by id
* `DELETE /books/{id}` — delete a book by id
* `DELETE /books` — delete all books

---

#### v2 — Custom OAuth2 + JWT Auth (self-built, no Firebase)
```bash
cd v2
uvicorn app.main:app --reload --port 8001
```
* Interactive Swagger UI docs: [http://localhost:8001/docs](http://localhost:8001/docs)

**Auth endpoints:**
* `POST /auth/signup` — register with email + password (password is hashed and the user is stored in MongoDB)
* `POST /auth/login` — OAuth2 password flow; returns a JWT access token

**Book endpoints (all protected, all scoped to the logged-in user via `user_id`):**
* `POST /books` — add a new book (tied to the current user)
* `GET /books` — get all books belonging to the current user
* `GET /books/{id}` — get a book by id (only if owned by the current user)
* `PATCH /books/{id}` — partially update a book by id (only if owned by the current user)
* `DELETE /books/{id}` — delete a book by id (only if owned by the current user)
* `DELETE /books` — delete all books belonging to the current user

*Every `/books` route requires a valid Bearer token. Missing or invalid tokens return 401 Unauthorized.*

---

#### v3 — Firebase Auth
```bash
cd v3
uvicorn app.main:app --reload --port 8002
```
* Interactive Swagger UI docs: [http://localhost:8002/docs](http://localhost:8002/docs)

Same endpoint shape as v2, but authentication is delegated to Firebase instead of hand-rolled JWT:

**Auth endpoints:**
* `POST /auth/signup` — register with email + password via Firebase Auth
* `POST /auth/login` — login via Firebase Auth, returns a Firebase ID token

**Book endpoints:**
* Identical set and behavior to v2, but the Bearer token is a Firebase ID token, verified server-side using the Firebase Admin SDK.

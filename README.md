# Math Test Generator

A backend API that generates individualized math tests. A teacher builds a test out of parameterized problem types (for example, "derivatives: power rule" with coefficient and exponent bounds), uploads a list of student names, and gets back a zip with one PDF per student. Every student gets different problems, and a given student always gets the same ones.

**Status:** the backend is working. A desktop client (Electron), a combined answer-key PDF, and AWS deployment are planned (see [Roadmap](#roadmap)).

## Features

- Signup and login with email and password (Argon2 password hashing, JWT access tokens)
- Per-user data: every test belongs to one user, and users can only see and change their own tests
- Create, list, open, and delete tests; add and remove problems within a test
- Registry of problem types, each declaring its own parameters, defaults, and validation rules
- Server-side validation of problem parameters (invalid input is rejected with HTTP 422)
- Problems are generated with [SymPy](https://www.sympy.org), so questions and answers are computed symbolically and exported as LaTeX
- Deterministic per-student generation: the random seed comes from the test and the student's name
- Batch endpoint: upload a text file of student names, receive a zip of PDFs compiled with `pdflatex`
- Audit log table recording signup and login events

## Tech stack

Python, FastAPI, SQLAlchemy, MySQL 8 (Docker), Pydantic, SymPy, LaTeX (`pdflatex`), PyJWT, argon2-cffi

## How it works

```
client  ->  FastAPI  ->  MySQL            (users, tests, test problems, logs)
                |
                +->  problem registry  ->  SymPy  ->  LaTeX strings
                |
                +->  LaTeX document builder  ->  pdflatex  ->  PDFs  ->  zip
```

1. A test is stored as an ordered list of rows, each holding a problem type id and its parameters as JSON.
2. To generate, each student's name plus the test id is turned into a random seed. Each problem gets its own random generator derived from that seed, so removing one problem doesn't change the others.
3. Each problem type's `generate` method returns a question and an answer as LaTeX.
4. The document builder places them in an exam template and `pdflatex` compiles one PDF per student.

## Getting started

### Prerequisites

- Python 3.11 or newer (developed on 3.13)
- Docker Desktop
- A LaTeX distribution that provides `pdflatex` and the `mathexam` package (MiKTeX or TeX Live)

### Setup

```bash
# 1. Start MySQL (listens on localhost:3307)
docker compose up -d

# 2. Create and activate a virtual environment
cd backend
python -m venv .venv
# Windows (PowerShell):  .venv\Scripts\Activate.ps1
# macOS / Linux:         source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment variables
cp .env.example .env        # Windows: copy .env.example .env
# edit .env and set SECRET_KEY, for example with:
# python -c "import secrets; print(secrets.token_urlsafe(32))"

# 5. Run the API
uvicorn main:app --reload
```

Then open http://127.0.0.1:8000/docs for interactive API documentation. If port 8000 is in use, add `--port 8001` (and use that port in the URL).

The tables are created automatically on startup. The credentials in `docker-compose.yml` are for local development only.

### Try it

In the `/docs` page:

1. **POST /signup**, then **POST /login**, and copy the `access_token`.
2. Click **Authorize** and paste the token.
3. **POST /tests** to create a test, then **POST /tests/{id}/problems** to add problems. Use **GET /problem-types** to see the available types and their parameters.
4. **POST /tests/{id}/generate** with a `.txt` file containing one student name per line, and download the zip.

## API overview

| Method | Path | Description |
|---|---|---|
| POST | `/signup` | Create an account |
| POST | `/login` | Get an access token |
| GET | `/me` | Current user |
| GET | `/problem-types` | Available problem types and their parameters |
| GET, POST | `/tests` | List your tests, create a test |
| GET, DELETE | `/tests/{id}` | Open or delete a test |
| POST | `/tests/{id}/problems` | Add a validated problem to a test |
| DELETE | `/tests/{id}/problems/{problem_id}` | Remove a problem |
| POST | `/tests/{id}/generate` | Upload a names file, get a zip of per-student PDFs |
| GET | `/tests/{id}/preview` | Generated questions and answers as JSON (development helper) |
| GET | `/tests/{id}/tex` | LaTeX source for one student (development helper) |
| GET | `/tests/{id}/pdf` | PDF for one student (development helper) |

All `/tests` endpoints require a bearer token.

## Adding a problem type

Problem types live in `backend/problems/`. A new type is a class that declares its parameters and implements `generate`; optional `check` enforces rules between parameters:

```python
class MyProblem(ProblemType):
    id = "topic.subtopic.name"
    topic = "Topic"
    label = "Readable name"
    params = [Param("max_value", "Largest value", 10)]

    def check(self, params):
        if params["max_value"] < 1:
            raise ValueError("Largest value must be at least 1")

    def generate(self, params, rng):
        ...  # build a SymPy expression using rng
        return Problem(question=r"Find $...$.", answer="$...$")
```

Register it in `problems/__init__.py`. It then appears in `GET /problem-types` and can be added to tests with no other changes.

## Security notes

- Passwords are hashed with Argon2 and never stored or returned.
- Every test query is scoped to the authenticated user; other users' tests return 404.
- Student names and test titles are escaped before they enter LaTeX, and `pdflatex` runs with shell escape disabled in a temporary directory.
- Uploaded names files are size-limited, and the number and length of names are capped.
- Secrets are read from environment variables and `.env` is git-ignored.

## Roadmap

- Combined answer-key PDF covering every student's test
- Electron desktop client (login, test list, editor with problem-type sidebar)
- More problem types (limits, integrals, algebra)
- Automated tests and database migrations (Alembic)
- Deployment to AWS (RDS for MySQL, hosted API)
- Per-test course name, date, and instructions

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import select
from sqlalchemy.orm import Session

import models
import schemas
from database import engine, Base, get_db
from security import (
    hash_password, verify_password, create_access_token, decode_access_token,
)
from audit import log_action
from problems import REGISTRY
from random import Random

Base.metadata.create_all(bind=engine)

app = FastAPI()

bearer = HTTPBearer()

# jwt auth token -> user
def get_current_user(
    creds: HTTPAuthorizationCredentials = Depends(bearer),
    db: Session = Depends(get_db),
) -> models.User:
    user_id = decode_access_token(creds.credentials)
    user = db.get(models.User, user_id) if user_id is not None else None
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return user

def get_owned_test(test_id: int, user: models.User, db: Session) -> models.Test:
    test = db.get(models.Test, test_id)
    if test is None or test.user_id != user.id:
        raise HTTPException(status_code=404, detail="Test not found")
    return test

# api endpoint to return current user via the auth jwt that requested it
@app.get("/me", response_model=schemas.UserOut)
def me(user: models.User = Depends(get_current_user)):
    return user

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/signup", response_model=schemas.UserOut, status_code=status.HTTP_201_CREATED)
def signup(data: schemas.UserCreate, db: Session = Depends(get_db)):
    email = data.email.lower()

    existing = db.scalar(select(models.User).where(models.User.email == email))
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered")

    user = models.User(email=email, password_hash=hash_password(data.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    log_action(db, user.id, "signup")
    return user

@app.post("/login", response_model=schemas.Token)
def login(data: schemas.UserLogin, db: Session = Depends(get_db)):
    user = db.scalar(select(models.User).where(models.User.email == data.email.lower()))
    if user is None or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    log_action(db, user.id, "login")
    return schemas.Token(access_token=create_access_token(user.id))

# add a test to a db associated with the requesters id
@app.post("/tests", response_model=schemas.TestOut, status_code=status.HTTP_201_CREATED)
def create_test(
    data: schemas.TestCreate,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    test = models.Test(user_id=user.id, name=data.name)
    db.add(test)
    db.commit()
    db.refresh(test)
    return test

# return all tests of the requesters
@app.get("/tests", response_model=list[schemas.TestOut])
def list_tests(
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    stmt = (
        select(models.Test)
        .where(models.Test.user_id == user.id)
        .order_by(models.Test.updated_at.desc())
    )
    return db.scalars(stmt).all()

# request a test, reject if you dont own it
@app.get("/tests/{test_id}", response_model=schemas.TestDetail)
def get_test(
    test_id: int,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return get_owned_test(test_id, user, db)

# add problem to test_id
@app.post(
    "/tests/{test_id}/problems",
    response_model=schemas.ProblemOut,
    status_code=status.HTTP_201_CREATED,
)
def add_problem(
    test_id: int,
    data: schemas.ProblemCreate,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    test = get_owned_test(test_id, user, db)

    problem_type = REGISTRY.get(data.problem_type)
    if problem_type is None:
        raise HTTPException(
            status_code=422, detail=f"Unknown problem type: {data.problem_type}"
        )
    try:
        params = problem_type.validate(data.params)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    problem = models.TestProblem(
        test_id=test.id,
        position=len(test.problems),
        problem_type=data.problem_type,
        params=params,
    )
    db.add(problem)
    db.commit()
    db.refresh(problem)
    return problem

# remove problem_id from test_id
@app.delete(
    "/tests/{test_id}/problems/{problem_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def remove_problem(
    test_id: int,
    problem_id: int,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    test = get_owned_test(test_id, user, db)
    problem = next((p for p in test.problems if p.id == problem_id), None)
    if problem is None:
        raise HTTPException(status_code=404, detail="Problem not found")

    test.problems.remove(problem)
    for index, p in enumerate(test.problems):
        p.position = index
    db.commit()

# remove a test
@app.delete("/tests/{test_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_test(
    test_id: int,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    test = get_owned_test(test_id, user, db)
    db.delete(test)
    db.commit()

@app.get("/problem-types", response_model=list[schemas.ProblemTypeOut])
def list_problem_types():
    return list(REGISTRY.values())

@app.get("/tests/{test_id}/preview", response_model=list[schemas.GeneratedProblem])
def preview_test(
    test_id: int,
    seed: int = 0,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    test = get_owned_test(test_id, user, db)

    results = []
    for number, tp in enumerate(test.problems, start=1):
        problem_type = REGISTRY.get(tp.problem_type)
        if problem_type is None:
            raise HTTPException(status_code=500, detail=f"Unknown stored problem type: {tp.problem_type}")

        rng = Random(f"{seed}:{tp.id}")
        problem = problem_type.generate(tp.params, rng)
        results.append(
            schemas.GeneratedProblem(
                number=number, question=problem.question, answer=problem.answer
            )
        )
    return results

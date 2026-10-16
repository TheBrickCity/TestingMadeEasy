# format of json sent from api

from pydantic import BaseModel, EmailStr, Field
from datetime import datetime


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)

class UserOut(BaseModel):
    id: int
    email: EmailStr

    model_config = {"from_attributes": True}

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TestCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)


class TestOut(BaseModel):
    id: int
    name: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

class ProblemCreate(BaseModel):
    problem_type: str = Field(min_length=1, max_length=100)
    params: dict = {}

class ProblemOut(BaseModel):
    id: int
    position: int
    problem_type: str
    params: dict

    model_config = {"from_attributes": True}

class TestDetail(TestOut):
    problems: list[ProblemOut] = []

class ParamOut(BaseModel):
    name: str
    label: str
    default: int

    model_config = {"from_attributes": True}


class ProblemTypeOut(BaseModel):
    id: str
    topic: str
    label: str
    params: list[ParamOut]

    model_config = {"from_attributes": True}

class GeneratedProblem(BaseModel):
    number: int
    question: str
    answer: str
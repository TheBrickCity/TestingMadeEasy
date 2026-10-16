# database models

from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, JSON, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class Log(Base):
    __tablename__ = "logs"

    log_id: Mapped[int] = mapped_column(primary_key=True)
    action_type: Mapped[str] = mapped_column(String(200))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    action_date: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

class Test(Base):
    __tablename__ = "tests"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    name: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    problems: Mapped[list["TestProblem"]] = relationship(
        back_populates="test",
        cascade="all, delete-orphan",
        order_by="TestProblem.position",
    )

class TestProblem(Base):
    __tablename__ = "test_problems"

    id: Mapped[int] = mapped_column(primary_key=True)
    test_id: Mapped[int] = mapped_column(ForeignKey("tests.id"))
    position: Mapped[int]
    problem_type: Mapped[str] = mapped_column(String(100))
    params: Mapped[dict] = mapped_column(JSON)

    test: Mapped["Test"] = relationship(back_populates="problems")
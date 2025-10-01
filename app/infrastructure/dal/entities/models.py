from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True, unique=True, nullable=False)
    username = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    password_hashed = Column(String(64), nullable=False)


class UserSession(Base):
    __tablename__ = "user_sessions"

    id = Column(String(64), primary_key=True, nullable=False)
    user_id = Column(BigInteger, ForeignKey("users.id"), primary_key=True, nullable=False)
    expiration_date = Column(DateTime(timezone=True), nullable=False)

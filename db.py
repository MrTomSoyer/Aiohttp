import datetime
import os
from dotenv import load_dotenv

from sqlalchemy import DateTime, Integer, String, func, ForeignKey
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped

from werkzeug.security import generate_password_hash, check_password_hash

load_dotenv()

POSTGRES_USER = os.getenv("POSTGRES_USER", "app")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "secret")
POSTGRES_DB = os.getenv("POSTGRES_DB", "app")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "127.0.0.1")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5431")

POSTGRES_DSN = (
    f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@"
    f"{POSTGRES_HOST}:{POSTGRES_PORT}/"
    f"{POSTGRES_DB}"
)

engine = create_async_engine(POSTGRES_DSN)
Session_DB = async_sessionmaker(bind=engine, expire_on_commit=False)


class Base(DeclarativeBase, AsyncAttrs):

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    @property
    def id_json(self):
        return {"id": self.id}


class Ads(Base):
    __tablename__ = "ads"

    title: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(String(1000), nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=func.now())
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    @property
    def ads_json(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "created_at": int(self.created_at.timestamp()),
            "owner": self.owner_id,
        }

class User(Base):
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(String(100),unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    def hash_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str):
        return check_password_hash(self.password_hash, password)

    @property
    def user_json(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email
        }


async def init_orm():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_orm():
    await engine.dispose()
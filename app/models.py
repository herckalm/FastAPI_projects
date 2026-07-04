from typing import List, Optional

from sqlmodel import Field, Relationship, SQLModel


# User Models
class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    hashed_password: str
    is_admin: bool = Field(default=False)


class UserRegister(SQLModel):
    username: str
    password: str


class UserResponse(SQLModel):
    id: int
    username: str
    is_admin: bool


# Hero Models
class HeroBase(SQLModel):
    name: str = Field(index=True, min_length=3)
    power: str = Field(min_length=3)
    level: int = Field(default=1, ge=1, le=100)
    active: bool = Field(default=True)


class Hero(HeroBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    # Relationships
    missions: List["Mission"] = Relationship(
        back_populates="hero", cascade_delete=False
    )


class HeroCreate(HeroBase):
    pass


class HeroUpdate(SQLModel):
    name: Optional[str] = Field(default=None, min_length=3)
    power: Optional[str] = Field(default=None, min_length=3)
    level: Optional[int] = Field(default=None, ge=1, le=100)
    active: Optional[bool] = None


# mission models
class MissionBase(SQLModel):
    title: str = Field(min_length=5)
    difficulty: int = Field(ge=1, le=10)
    completed: bool = Field(default=False)
    hero_id: int = Field(foreign_key="hero.id")


class Mission(MissionBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    # Relationships
    hero: Optional[Hero] = Relationship(back_populates="missions")


class MissionCreate(MissionBase):
    pass


class MissionUpdate(SQLModel):
    title: Optional[str] = Field(default=None, min_length=5)
    difficulty: Optional[int] = Field(default=None, ge=1, le=10)
    completed: Optional[bool] = None
    hero_id: Optional[int] = None

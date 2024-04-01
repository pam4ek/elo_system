from pydantic import BaseModel

class UserBase(BaseModel):
    email: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    email: str
    is_active: bool

    class Config:
        orm_mode = True

class TeamBase(BaseModel):
    name: str

class TeamCreate(TeamBase):
    owner_id: int

class Team(TeamBase):
    id: int
    owner: User

    class Config:
        orm_mode = True

class MatchBase(BaseModel):
    team1_id: int
    team2_id: int
    score1: int
    score2: int

class MatchCreate(MatchBase):
    pass

class Match(MatchBase):
    id: int

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str
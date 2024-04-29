from pydantic import BaseModel


class User(BaseModel):
    username: str
    password: str 
    first_name: str

class UserReturn(BaseModel):
    username: str
    first_name: str
    email: str
    contact: str

class UserLogin(BaseModel):
    username : str
    password : str

    class Config:
        orm_model = True

class TokenSchema(BaseModel):
    access_token: str
    refresh_token: str
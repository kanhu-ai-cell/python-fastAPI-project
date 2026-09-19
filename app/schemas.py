from pydantic import BaseModel

class BlogSchema(BaseModel):
    title: str
    completed: str


class UserCO(BaseModel):    
    name:str
    username:str
    mobileno:str
    email:str

class UserLogin(BaseModel):
    username: str
    password: str

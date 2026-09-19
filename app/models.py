from sqlalchemy import Column, Integer, String
from database import Base


class Blog(Base):
    __tablename__ = "blogs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    completed = Column(String)

class UserDb(Base):
    __tablename__="user"

    id= Column(Integer, primary_key=True, index=True)
    name=Column(String)
    username = Column(String, unique=True)
    password=Column(String)
    mobileno=Column(String)
    email=Column(String)


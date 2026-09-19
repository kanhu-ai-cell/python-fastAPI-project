from fastapi import FastAPI,status,HTTPException,Request,Depends,Header
from pydantic import BaseModel
from fastapi.responses import JSONResponse
import time
import sqlite3
from learnsql import router as learnsql_router
from crud import router as crud_router
from authlogin import router as login_router
from thirdpartyapi import thirdpartyapi_router
from database import engine, Base
from models import Blog
import asyncio
# this is for CORS (Cross-Origin Resource Sharing) to allow cross-origin requests
from fastapi.middleware.cors import CORSMiddleware
# import os
# from dotenv import load_dotenv

# load_dotenv()
from config import Config
import requests
from bs4 import BeautifulSoup
import time

# for rate limiting the imports
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi.responses import JSONResponse

app=FastAPI()
# for routers
app.include_router(crud_router)
app.include_router(learnsql_router)
app.include_router(login_router)
app.include_router(thirdpartyapi_router)

# allow all origins for CORS(front-end url)

# ORIGINS=os.getenv("ORIGINS")
ORIGINS=Config.ORIGINS

app.add_middleware(
    CORSMiddleware,
    allow_origins=ORIGINS, # allowed FE
    allow_credentials=True,
    allow_methods=["*"], #GET, POST, PUT, DELETE
    allow_headers=["*"],
)
# for models and database creation
Base.metadata.create_all(bind=engine)


class User(BaseModel):
    name:str
    age:int
    gender:str



# 
@app.get("/")
def getdata():
    return {"message":"Hii welcome to the Fast API World"}

# about
@app.get("/about")
def about():
    return {"message":"this is about pages"}

@app.get("/users")
def users():
    return {
        "Users":["kanhu","api","testing"]
    }

# dynamic routes
@app.get("/users/{user_id}")
def users(user_id):
    return {
        "Users": user_id
    }

@app.get("/user/list/{user_id}")
def get_users(user_id: int):
    return {
        "Users": user_id
    }


# query parameters
# @app.get("/product")
# def get_products(name):
#     return {
#         "productName": name
#     }

# # optional parameters
# @app.get("/product")
# def get_products(name: str=None):
#     return {
#         "productName": name
#     }

# defult values
@app.get("/prod/list/")
def prod_list(limit: int=10):
    return {"limit": limit }


# multiple parameter values
@app.get("/item/list/")
def get_itemList(name:str=None,price:int=0):
    return {"name": name,"price":price }

# post method
@app.post("/create-user")
def create_user(name:str,age:int):
    return {
        "name":name,"age":age
    }

@app.post("/create-user-v1")
def create_userv1(user:dict):
    return {
        "message": "create user sucessfully"
    }


@app.post("/create-user-v1")
def create_userv1(user:dict):
    return {
        "message": "create user sucessfully"
    }

# for this we have use BaseModel here  to make users validation
@app.post("/create-user-v2")
def create_userv2(user:User):
    return {
        "message": "create user sucessfully",
        "data":user
    }

# @app.post("/create/student")
# def createStudent(stud:Student):
#     return {
#         "Message":"Student Created Sucessfully",
#         "data":stud
#     }

class Address(BaseModel):
    city:str
    pincode:int
    addLine1:str

class Student(BaseModel):
    name:str
    age:int
    email:str
    adress:Address

@app.post("/create/student")
def createStudent(stud:Student):
    return {
        "Message":"Student Created Sucessfully",
        "data":stud
    }

# ModelResponse & HTTP statuscode
# 1st import status
class staff(BaseModel):
    name:str
    age:int
    email:str
    password:str

class staffResponse(BaseModel):
    name:str
    age:int
    email:str

@app.get("/staff",response_model=staffResponse)
def createStaff():
    return {
        "name": "kanhu",
        "age": 26,
        "email": "kanhu.job@gmail.com",
        "password": "kanhu@#123"
        
    }

@app.post("/staff",status_code=status.HTTP_201_CREATED)
def createStaff():
    return {
        "message":"user created" 
    }

# custom responses
@app.get("/staff/list")
def staffList():
    return {
        "status":"Success",
        "message":"User Fetch",
        "data":{
            "name":"mohit",
            "age":23
        }

    }

# Error handling
# from fastapi import HTTPException

# @app.get("/staffs/{staffId}")
# def getstaff(staffId:int):
#     if staffId != 1:
#         raise HTTPException(
#             status_code=404,
#             detail="staff not found"
#         )
#     return {
#         "id":1,
#         "name":"mohit"
#     }

class UserNotFoundException(Exception):
    def __init__(self, name:str):
           self.name=name    

# for global exception
# from fastapi.responses import JSONResponse
# from fastapi import Request
@app.exception_handler(UserNotFoundException)
def user_not_forund(request:Request,ex=UserNotFoundException):
    return JSONResponse(
        status_code=404,
        content={
            "status":"error",
            "message": f"User {ex.name} not found"
        }
    )

@app.get("/staffs/{name}")
def getstaff(name:str):
    if name != "mohit":
        raise UserNotFoundException(name)
    return {
        "id":1,
        "name":"mohit"
    }

# for dependency injection we have to follow these steps
# from fastapi import FastAPI, Depends

def common_logic():
    return{
        "message":"common logic executed"
    }

@app.get("/home")
def home(data =Depends(common_logic)):
    return data

# Examples
def get_current_user():
    return {
     "name":"Kanhu"
    }

@app.get("/profile")
def getprofile(user=Depends(get_current_user)):
    return user

@app.get("/dashboard")
def gedashboard(user=Depends(get_current_user)):
    return user


# Auth example
# from fastapi import FastAPI,status,HTTPException,Request,Depends,Header
# create common function
def verify_token(token:str=Header(None)):
    if token !="mysecrettokn":
        raise HTTPException(
            status_code=401,
            detail="Unauthorized"
        )
    return {
        "user":"Authorized User"
    }

@app.get("/secure-data")
def secureData(user=Depends(verify_token)):
    return {
        "message":"Secure data accessed",
        "user":user
    }


# Middleware
# from fastapi import FastAPI,Request
@app.middleware("http")
async def my_middleware(request:Request,call_next):
    print("Request Received")
    response=await call_next(request)
    print("response Sent")
    return response

# logging middleware
# import time

@app.middleware("http/v1")
async def log_middleware(request:Request,call_next):
    start_time=time.time()
    response=await call_next(request)
    process_time = time.time()-start_time
    print(f"Path:{request.url.path} | Time:{process_time}")
    return response 

# SQLite
# import sqlite3
# from fastapi import FastAPI

conn=sqlite3.connect("test.db",check_same_thread=False)

crusor=conn.cursor()

crusor.execute("""
CREATE TABLE IF NOT EXISTS BLOGS(
        Id INTEGER PRIMARY KEY,
        title TEXT,
        completed Text
)
""")

conn.commit()

@app.get("/sql/run")
def sql_run():
    return {
        "Message":"sqlite connected Fine"
    }


# Asynchronous programming(async/await)
# import time
# import asyncio

# def task():
#     time.sleep(3)
#     return "Done"

# async def task():
#     await asyncio.sleep(3)
#     return "Done"

@app.get("/async/ex")
async def asyncV1():
    await asyncio.sleep(3)
    return {
        "message":"Async API"
    }

# for cors enabling we have to follow these steps
@app.get("/cors/enabled")
def corsEnabled():
    return {
        "message":"CORS enabled"
    }


# for web crawling taking some websites head line like
# import requests
# from bs4 import BeautifulSoup
# Also pagination implementaton

# @app.get("/news")
# def get_news(page:int=1,limit:int=5):
#     url="https://news.ycombinator.com/"
#     response=requests.get(url)
#     soup=BeautifulSoup(response.text,"html.parser")
#     title=[]
#     for item in soup.find_all("span",class_="titleline"):
#         title.append(item.text)

#     # pagination logic
#     start=(page-1)* limit
#     end=start+limit
#     return {
#         # "news":title[:50]
#         #  "news":title
#         "page":page,
#         "limit":limit,
#         "total": len(title),
#         "data":title[start:end]
#     }

# use for caching logic
# import time
cache_data=[]
last_fetch=0

@app.get("/news")
def get_news():
    global cache_data,last_fetch
    start=time.time()
    if time.time()-last_fetch > 60:
        url="https://news.ycombinator.com/"
        response=requests.get(url)
        soup=BeautifulSoup(response.text,"html.parser")
        title=[]
        cache_data=[
            item.text for item in soup.find_all("span",class_="titleline")
        ]
        last_fetch=time.time()

    else:
        print("using catche Data")
    end =time.time()
    time_taken= round(end-start,4)

    print("Time_taken:",time_taken)
   
    return {
        "Time_taken":time_taken,
        "news":cache_data[:5]
    }

# for Rate Limiting
# from slowapi import Limiter
# from slowapi.util import get_remote_address
# from slowapi.errors import RateLimitExceeded
# from fastapi.responses import JSONResponse

# Limiter setup
limiter =Limiter(key_func=get_remote_address)
app.state.limiter=limiter

# Error handle
@app.exception_handler(RateLimitExceeded)
def rate_limit_handler(request:Request,exec:RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={
            "detail":"Too many Requests"
        }
    )

# Rate Limiter API

@app.get("/data/v1")
@limiter.limit("5/minute")
def get_data(request:Request):
    return {
        "message":"Success"
    }
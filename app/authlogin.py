# Authentication Basics
from fastapi import FastAPI,APIRouter,status,HTTPException,Request,Depends,Header
from jose import jwt,JWTError
from datetime import datetime,timedelta,timezone
from schemas import UserLogin,UserCO
from models import UserDb
from database import SessionLocal
from fastapi.security import OAuth2PasswordBearer,OAuth2PasswordRequestForm
from passlib.context import CryptContext
import uuid
# import os
# from dotenv import load_dotenv


# load_dotenv()
from config import Config
# jose=java sript object signature & encription

router = APIRouter(
    prefix="/admin",
    tags=["AdminLogin"])

# JWT CONFIG
# SECRET_KEY = os.getenv("SECRET_KEY")
# ALGORITHM = os.getenv("ALGORITHM")
# ACCESS_TOKEN_EXPIRE_MINUTES=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
SECRET_KEY=Config.SECRET_KEY
ALGORITHM=Config.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES=Config.ACCESS_TOKEN_EXPIRE_MINUTES

# password hasing Setup
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OauthSetUp
oauth2_schema = OAuth2PasswordBearer(
    tokenUrl="/admin/login/v1"
)
# Dummy user Db
fake_user_db={
    "admin": {
        "username":"admin",
        "hashed_password": pwd_context.hash("1234")
    }
}
# def Password
def hash_password(password:str):
    return pwd_context.hash(password)

# varify password
def varify_password(plain_password,hashed_password):
    return pwd_context.verify(plain_password,hashed_password)

# create token
def create_token(data:dict):

    # JWT Header
    headers = {
            "typ": "JWT",
            "alg": ALGORITHM,
            "Developed By": "Kanhu",
            "Host": "AI-CELL"
        }   
    # JWT Payload
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = data.copy()

    to_encode.update({
        "sub": "Security Token",
        "iss": "AI-CELL",
        "nbf": now,
        "iat": now,
        "exp": expire,
        "sessionToken": str(uuid.uuid4()),
        "status": "ACTIVE"
    })
     # Generate JWT
    token = jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM,
        headers=headers
    )

    return token

# Login API(Token Genrate)
@router.post("/loginj")
def login(user: UserLogin):
   db = SessionLocal()
   try:
        # Find user by username
        db_user = db.query(UserDb).filter(
            UserDb.username == user.username
        ).first()

        # User not found
        if not db_user:
            raise HTTPException(
                status_code=401,
                detail="user not found "
            )
         # Check password
        if db_user.password != user.password:
            raise HTTPException(
                status_code=401,
                detail="Invalid Username and password"
            )
          # Generate token
        token = create_token({
            "userId": db_user.id,
            "username": db_user.username,
            "name": db_user.name,
            "mobileno": db_user.mobileno,
            "email": db_user.email
        })

        return {
            "access_token": token,
            "token_type": "bearer"
        }

   finally:
        db.close()

               
# varify token

def token_verify(token: str = Header(None)):
    try:
        if not token:
            raise HTTPException(
                status_code=401,
                detail="Token is missing"
            )

        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        return payload
    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired Token"
        )
    
# protected Route
@router.get("/secure")
def secure_data(user=Depends(token_verify)):
    return {
        "message": "Secure Data Access",
        "user": user
    }

# OAuth2 + JWT,token validation,Secure routes, password hashing
# pip install "python-jose" "passlib[bcrypt]" "python-multipart"
# from fastapi.security import OAuth2PasswordBearer,OAuth2PasswordRequestForm
# from passlib.context import CryptContext 
# Login api (OAuth2 Form)

@router.post("/login/v1")
def loginV1(form_data: OAuth2PasswordRequestForm= Depends()):
    user=fake_user_db.get(form_data.username)
    if not user or not varify_password(form_data.password,user["hashed_password"]):
        raise HTTPException(
            status_code=401,
            detail="INVALID username or password"
        )
    access_token =create_token({"sub":form_data.username})

    return {
        "access_token":access_token,
        "token_type":"bearer"
    }

# varify token for OAuth
def verify_tokenV1(token:str=Depends(oauth2_schema)):
    try:
        payload=jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
        username:str=payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid token"
                )
        return username
    except jwt.JWTError:
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )


# protected route for OAuth
@router.get("/potected")
def protected_route(username:str=Depends(verify_tokenV1)):
    return {
        "message":f"Hello{username},you have access to this protected route!",
        "user":username
    }


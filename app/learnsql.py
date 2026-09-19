from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker,declarative_base,Session
from fastapi import Depends,HTTPException
from fastapi import APIRouter
from database import get_db,SessionLocal
from schemas import BlogSchema
from models import Blog


class UserNotFoundException(Exception):
    def __init__(self, name:str):
           self.name=name    


router = APIRouter(
    prefix="/learnsql",
    tags=["Crud-Database"]
)

@router.get("/database")
def database(db: Session =Depends(get_db)):
    return {
        "message":"db connected fine"
    }


@router.post("/blog/add")
def createBlog(blog: BlogSchema):
    db = SessionLocal()
    try: 
        new_blog = Blog(
            title=blog.title,
            completed=blog.completed
        )

        db.add(new_blog)
        db.commit()
        db.refresh(new_blog)

        return {
            "message": "Blog created successfully",
            "data": new_blog
        }

    finally:
        db.close()

@router.get("/blog/list")
def bloglist():
    db=SessionLocal()
    try:
       bolgs= db.query(Blog).all()
       return {
           "messages":"Find all the datas",
           "data":bolgs
       }

    finally:
         db.close()


@router.get("/blog/list/{blogId}")
def get_byblog(blogId:int):
    db=SessionLocal()
    try:
    #    blog= db.query(Blog).filter(Blog.id==blogId).first()
       blog = db.get(Blog, blogId)

       if not blog:
           raise HTTPException(status_code=404,detail="Blog Not found")
       return {
           "messages":" FInd the blog",
           "data":blog
       }

    finally:
         db.close()


@router.put("/blog/update/{blogId}")
def update_blog(blogId: int, updated_blog: BlogSchema):
    db = SessionLocal()

    try:
        # Find blog by primary key
        blog = db.get(Blog, blogId)

        if not blog:
            raise HTTPException(
                status_code=404,
                detail="Blog Not found"
            )

        # Update fields
        blog.title = updated_blog.title
        blog.completed = updated_blog.completed

        # Save changes
        db.commit()
        db.refresh(blog)

        return {
            "message": "Blog updated successfully",
            "data": blog
        }

    finally:
        db.close()


@router.delete("/blog/delete/{blogId}")
def delete_blog(blogId: int):
    db = SessionLocal()

    try:
        # Find blog by ID
        blog = db.get(Blog, blogId)

        if not blog:
            raise HTTPException(
                status_code=404,
                detail="Blog Not found"
            )

        # Delete the blog
        db.delete(blog)

        # Save changes
        db.commit()

        return {
            "message": "Blog deleted successfully",
            "data": blogId
        }

    finally:
        db.close()
from fastapi import APIRouter
import requests

thirdpartyapi_router=APIRouter(
    prefix="/thirdpartyapi",
    tags=["ThirdPartyApi"]
)

@thirdpartyapi_router.get("/posts")
def get_posts():
    url = "https://jsonplaceholder.typicode.com/posts"
    response = requests.get(url)
    return response.json()

@thirdpartyapi_router.get("/posts/{post_id}")
def get_post(post_id: int):
    url = f"https://jsonplaceholder.typicode.com/posts/{post_id}"
    response = requests.get(url)
    return response.json()



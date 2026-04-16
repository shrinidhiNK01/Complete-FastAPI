from fastapi import FastAPI
from fastapi.params import Body
app=FastAPI()

@app.get("/")
def root():
    return {"message":"Hello World"}

@app.get("/posts")
def get_posts():
    return {"data":"This is my first post"}

@app.post("/createposts")
def create_posts(payload: dict = Body(...)):
    print(payload)
    return {"new_post":f"Post created with title {payload['title']} and content {payload['content']}"}
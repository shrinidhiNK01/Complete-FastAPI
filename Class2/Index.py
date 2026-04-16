from fastapi import FastAPI, Response ,HTTPException,status
from fastapi.params import Body
from pydantic import BaseModel
from typing import Optional 
from random import randrange

app=FastAPI()

class Post(BaseModel):
    title:str
    content:str
    published:bool = True
    rating: Optional[int]=None

my_post=[{"title":"My first post","content":"This is my first post content","published":True,"rating":5,"id":1},
         {"title":"My second post","content":"This is my second post content","published":False,"rating":None,"id":2}]

@app.get("/")
def root():
    return {"message":"Hello World2"}

@app.get("/posts")   #This is a get request to fetch all the posts
def get_posts():
    # return {"data":"This is my first post"}
    return {"data":my_post}

@app.post("/posts",status_code=status.HTTP_201_CREATED)   #This is a post request to create a new post    
def create_posts(post:Post):
    print(post)
    print(post.dict()) #Give it in dictionary format
    post_dict=post.dict()
    post_dict['id']=randrange(0,1000000)
    my_post.append(post_dict) 
    return {"data":post_dict}
 
# ===============================CRUD Operations========================================

def find_post(id):
    for i in my_post:
        if i['id']==id:
            return i

@app.get("/posts/{id}")
def get_post(id:int,response:Response):  #By default path parameter is string, so we need to convert it into int by using id:int
    print(id)
    print(type(id))
    post=find_post(id)
    # return {"post_detail":f"Post with id {id} is fetched"}
    if not post:
        # response.status_code=404   , Instead of writing this line we can also use HTTPException
        
        # raise HTTPException(status_code=404,detail=f"Post with id {id} is not found")
        # or
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"Post with id {id} is not found",headers={"X-Error":"There goes my error"})
    return {"message":post}

# Delete

def find_post(id:int):
    for i,j in enumerate(my_post):
        if j['id']==id:
            return i

@app.delete("/posts/{id}",status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id:int):
    index=find_post(id)
    if index == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"Post with id {id} is not found")
    my_post.pop(index)
    return {"message":f"Post with id {id} is deleted successfully"}

# Update
@app.put("/posts/{id}")
def update_post(id:int,post:Post):
    index=find_post(id)
    if index == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"Post with id {id} is not found")
    post_dict=post.dict()
    post_dict['id']=id
    my_post[index]=post_dict
    return {"message":post_dict}

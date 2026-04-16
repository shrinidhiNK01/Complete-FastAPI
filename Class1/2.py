from fastapi import FastAPI
app=FastAPI()

@app.get("/")
def one():
    return {"name":"Shrinidhi"}

@app.get("/contact")
def two():
    return {"My Contact Number":"8310452317"}

@app.get("/address")
def three():
    return {"My Address":"Bangalore"}



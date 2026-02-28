from fastapi import FastAPI

app=FastAPI()

@app.get("/")
def hello():
    return {"message":"Hi Harshit"}

@app.get("/about")
def about():
    return {"message":"Harshit is here"}
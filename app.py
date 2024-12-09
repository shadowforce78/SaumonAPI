from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Bienvenue sur mon API !"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q}

@app.get("/uvsq/bulletin/{id}+{password}")
def read_item(id: int, password: str):


    
    return {"id": id, "password": password}
from fastapi import FastAPI
from db.models import add_record

app = FastAPI()

@app.post("/add")
def add_domain(name: str, ip: str):
    add_record(name, 'A', ip)
    return {"status": "ok"}
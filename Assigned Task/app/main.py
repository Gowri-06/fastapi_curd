from fastapi import FastAPI
import models
from routes import router
from config import engine

models.Base.metadata.create_all(bind=engine)
# models.Base.metadata.drop_all(bind=engine)

app = FastAPI()

#define endpoint
@app.get("/")
def home():
    return "HALLO"

app.include_router(router, prefix="/books", tags=["books"])



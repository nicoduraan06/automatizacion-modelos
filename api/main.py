from fastapi import FastAPI

from api.upload import router as upload_router
from api.process import router as process_router

app = FastAPI(title="modelo303")


# Registrar endpoints
app.include_router(upload_router)
app.include_router(process_router)


@app.get("/")
def root():
    return {"message": "API modelo 303 funcionando"}
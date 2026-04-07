from fastapi import FastAPI

app = FastAPI(title="modelo303")

@app.get("/")
def root():
    return {
        "message": "Proyecto modelo 303 operativo",
        "status": "ok"
    }

@app.get("/health")
def health():
    return {
        "health": "ok"
    }
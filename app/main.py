from fastapi import FastAPI

app = FastAPI(title="RatBox API")


@app.get("/health")
def health_check():
    return {"status": "ok"}

from fastapi import FastAPI

from app.api.routes.recommend import router as recommend_router
from app.core.cors import add_cors

app = FastAPI(title="RatBox API")
add_cors(app)
app.include_router(recommend_router)


@app.get("/health")
def health_check():
    return {"status": "ok"}

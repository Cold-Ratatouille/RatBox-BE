from fastapi import FastAPI

from app.api.routes.allergen import router as allergen_router
from app.api.routes.auth import router as auth_router
from app.api.routes.recommend import router as recommend_router
from app.api.routes.user import router as user_router
from app.api.routes.user_allergen import router as user_allergen_router
from app.core.cors import add_cors

app = FastAPI(title="RatBox API")
add_cors(app)
app.include_router(auth_router)
app.include_router(allergen_router)
app.include_router(user_allergen_router)
app.include_router(user_router)
app.include_router(recommend_router)


@app.get("/health")
def health_check():
    return {"status": "ok"}

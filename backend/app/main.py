from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app import models
from backend.app.api.auth import router as auth_router
from backend.app.api.projects import router as projects_router
from backend.app.core.database import Base, engine

app = FastAPI(title="GeneLab API")
app.add_middleware(
	CORSMiddleware,
	allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
	allow_methods=["*"],
	allow_headers=["*"],
)
Base.metadata.create_all(bind=engine)
app.include_router(auth_router)
app.include_router(projects_router)


@app.get("/")
def read_root() -> dict[str, str]:
	return {"status": "ok", "project": "GeneLab"}


if __name__ == "__main__":
	import uvicorn

	uvicorn.run("backend.app.main:app", host="127.0.0.1", port=8000, reload=True)

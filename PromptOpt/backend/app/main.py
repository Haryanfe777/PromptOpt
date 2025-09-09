from fastapi import FastAPI
from app.routes import auth, prompt, chat
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS for development - adjust origins for production
app.add_middleware(
	CORSMiddleware,
	allow_origins=["*"],
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(prompt.router)
app.include_router(chat.router)

@app.get("/health")
def health_check():
	return {"status": "ok"}

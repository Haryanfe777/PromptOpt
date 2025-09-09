from fastapi import FastAPI
from app.routes import auth, prompt, chat

app = FastAPI()

app.include_router(auth.router)
app.include_router(prompt.router)
app.include_router(chat.router)

@app.get("/health")
def health_check():
    return {"status": "ok"}

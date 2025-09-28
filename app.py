from fastapi import FastAPI
import uvicorn
import db_ctl
from starlette.middleware.cors import CORSMiddleware # 追加

app = FastAPI()

# CORSを回避するために追加（今回の肝）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,   # 追記により追加
    allow_methods=["*"],      # 追記により追加
    allow_headers=["*"]       # 追記により追加
)

@app.get("/")
async def root():
    return {"message":"Hello World"}

@app.get("/ping")
async def ping():
    return {"message":"pong"}

@app.get("/genres")
async def genres():
    return db_ctl.select_genres()

if __name__ == "__main__":
    uvicorn.run(app,host="127.0.0.1",port=8000, log_level="debug")

from fastapi import FastAPI
import uvicorn
import db_ctl
import random
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

# ジャンル一覧を取得するAPI
@app.get("/genres")
async def genres():
    return db_ctl.select_genres()

# キャラクタ一覧を取得するAPI
@app.get("/characters")
async def characters():
    return db_ctl.select_characters()

# 質問一覧を取得するAPI
@app.get("/questions")
async def questions():
    return db_ctl.select_questions()

# 質問一覧からランダムで3つ質問を取得するAPI
@app.get("/random_questions")
async def random_questions():
    # DBから質問一覧を取得
    all_questions = db_ctl.select_questions()
    # 質問の数の範囲内で乱数を重複無しで取得
    extracted_nums = random.sample(range(0,len(all_questions)),3)
    print(extracted_nums)
    # 該当の番号の質問を取得
    extracted_questions = []
    for num in extracted_nums:
        extracted_questions.append(all_questions[num])
    return extracted_questions

# 新しく問題を開始するAPI
@app.post("/new_question")
async def new_question():
    # --- お題を1個弾く ---
    themes = db_ctl.select_theme() # お題一覧を取得
    theme = themes[random.randint(0,len(themes))] # 乱数でお題を1つ選定
    
    # お題をお題マスタへ登録
    session_id = db_ctl.insert_theme(theme)

    # キャラクタマスタの出題数をインクリメント
    db_ctl.increment_question_times(theme)

    # システムロールのプロンプトをDBにいれる
    db_ctl.insert_system_prompt(session_id,theme)

    return theme

# # AIへ質問を投げるAPI
# @app.post("/ask_ai")

if __name__ == "__main__":
    uvicorn.run(app,host="127.0.0.1",port=8000, log_level="debug")

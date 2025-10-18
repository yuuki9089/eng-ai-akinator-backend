from fastapi import FastAPI
import uvicorn
import db_ctl
import random
import request_body as rb
from starlette.middleware.cors import CORSMiddleware # 追加
import os
from dotenv import load_dotenv
import ollama

# --- .envファイルの読み込み ---
load_dotenv()

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
    convert_sid = sid_list_to_value_helper(session_id)

    # キャラクタマスタの出題数をインクリメント
    db_ctl.increment_question_times(theme)

    # システムロールのプロンプトをDBにいれる
    db_ctl.insert_system_prompt(convert_sid,theme)
    return session_id

# AIへ質問を投げるAPI
@app.post("/ask_ai")
async def ask_ai(data: rb.user_question_data):

    # 会話履歴マスタに登録
    db_ctl.insert_user_question(data.session_id,data.user_question_content)

    # 会話履歴マスタから同一のsession_idの会話履歴をすべて取得
    db_chat_history = db_ctl.select_conversation_history(data.session_id)
    
    # historyを結合
    history = [] # 会話履歴用のリスト
    history = {
          "model": os.environ['AI_MODEL'],
          "messages":db_chat_history,
          "stream":False
    }
    
    # AIに質問を投げる
    ai_answer = ollama.generate_inference_with_ollama(history)

    # 帰ってきた戻り値(回答を会話履歴マスタにinsert)
    db_ctl.insert_ai_answer(data.session_id,ai_answer)
    
    # AIの回答を戻り値にする。
    return {"ai_answer":ai_answer}

# 回答を受け取るAPI
@app.post("/answer_theme")
async def receive_ans_from_frontend(data:rb.user_answer_data):
    
    # セッションidを基にお題を取得する関数
    result = db_ctl.get_theme_info_on_session_id(data.session_id)
    for fetched_line in result:
       db_session_id = fetched_line['session_id']
       db_theme = fetched_line['theme']
       db_character_id = fetched_line['id']
    
    if data.user_answer_character_id == db_character_id:
        return {"ans_result":True}
    else:
        return {"ans_result":False}

# 会話履歴マスタから過去のQ＆Aを取得
@app.get("/past_q_and_a/{session_id}")
async def get_past_q_and_a(session_id:int):
    return db_ctl.get_chat_history(session_id)

# =================================
# 【Listのdictになっているsession_idから値だけを返すヘルパー関数】
# =================================


def sid_list_to_value_helper(before_converting: dict):
    session_id = before_converting['session_id']
    return session_id

if __name__ == "__main__":
    uvicorn.run(app,host="127.0.0.1",port=8000, log_level="debug")

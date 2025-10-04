from pydantic import BaseModel

# ユーザからの質問を受け取るときのデータ構造
class user_question_data(BaseModel):
    class Config:
        arbitrary_types_allowed = True
    
    session_id: int
    user_question_content: str
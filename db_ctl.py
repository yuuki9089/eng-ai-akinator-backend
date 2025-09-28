import mysql.connector
import os
from dotenv import load_dotenv

# --- .envファイルの読み込み ---
load_dotenv()

# =================================
# 【DBへの接続】
# =================================
try:
    conn = mysql.connector.connect(
        user=os.environ['DB_USER'],
        password=os.environ['DB_PW'],
        host=os.environ['DB_IPADDR'],
        database=os.environ['DB_SCHEMA']
    )

except:
    raise Exception("DBサーバへの接続に失敗しました。")

# 取得結果を辞書型で扱う設定
cur = conn.cursor(dictionary=True)


# =================================
# 【ジャンルマスタからジャンルを取得する関数】
# =================================
def select_genres():
    query__for_fetching = """
    SELECT
          *

    FROM ジャンルマスタ
    ORDER BY genre_code
    ;
    """
    cur.execute(query__for_fetching)
    return cur.fetchall()

# =================================
# 【キャラクタマスタからキャラクタを取得する関数】
# =================================
def select_characters():
    query__for_fetching = """
    SELECT
          *
    FROM キャラクタマスタ
    ORDER BY id
    ;
    """
    cur.execute(query__for_fetching)
    return cur.fetchall()

# =================================
# 【質問マスタから質問を取得する関数】
# =================================
def select_questions():
    query__for_fetching = """
    SELECT
          *
    FROM 質問マスタ
    ORDER BY question_id
    ;
    """
    cur.execute(query__for_fetching)
    return cur.fetchall()

# =================================
# 【メイン関数】
# =================================
if __name__ == "__main__":
    result = select_genres()
    for fetched_line in result:
        genre_code = fetched_line['genre_code']
        genre_name = fetched_line['genre_name']
        print(f'{genre_code}: {genre_name}')

    result = select_characters()
    for fetched_line in result:
        genre_code = fetched_line['id']
        genre_name = fetched_line['character_name']
        print(f'{genre_code}: {genre_name}')

    result = select_questions()
    for fetched_line in result:
        question_code = fetched_line['question_id']
        question_content = fetched_line['question_content']
        print(f'{question_code}: {question_content}')
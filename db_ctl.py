import mysql.connector
import os
from dotenv import load_dotenv

# --- .envファイルの読み込み ---
load_dotenv()

# --- DBへの接続 ---
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

# ジャンルマスタからジャンルを取得する関数
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


if __name__ == "__main__":
    result = select_genres()
    for fetched_line in result:
        genre_code = fetched_line['genre_code']
        genre_name = fetched_line['genre_name']
        print(f'{genre_code}: {genre_name}')
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
# 【出題回数が低いものからお題を1つ抽出する関数】
# =================================


def insert_theme(theme):

    query__for_insert = """
    INSERT INTO お題マスタ(theme,done)
    VALUES (%s, %s)
    """

    # SQL実行
    cur.execute(query__for_insert, (theme['id'], 0))

    # DBをコミット
    conn.commit()

    # セッションIDが最大のものをreturn
    query__for_fetching = """
    SELECT 
        max(session_id) AS session_id
    FROM お題マスタ 
    ;
    """
    cur.execute(query__for_fetching)
    return cur.fetchall()

# =================================
# 【お題をお題マスタへ登録する関数】
# =================================


def select_theme():
    query__for_fetching = """
    SELECT 
        * 
    FROM キャラクタマスタ 
    WHERE question_times=(
        SELECT
             min(question_times) 
        FROM キャラクタマスタ
    )
    ORDER BY id
    ;
    """
    cur.execute(query__for_fetching)
    return cur.fetchall()

# =================================
# 【キャラクタマスタの出題回数をインクリメントする関数】
# =================================


def increment_question_times(theme):
    query__for_update = """
    UPDATE キャラクタマスタ
    SET question_times = question_times + 1
    WHERE id = %s
    """

    # SQL実行
    cur.execute(query__for_update, (theme['id'],))

    # DBをコミット
    conn.commit()

# =================================
# 【システムプロンプトを会話履歴マスタに登録する関数】
# =================================


def insert_system_prompt(session_id, theme):
    query__for_insert = """
    INSERT INTO 会話履歴マスタ(session_id,role,message)
    VALUES (%s, %s, %s)
    """

    PROMPT = "あなたはゲームやアニメが大好きなオタクです。" \
        + "今からクイズを行います。あなたは出題者側です"\
        + "質問される内容にクイズ形式でヒントを出す形で回答してください。"\
        + f"今回のお題は{theme['character_name']}です。"\
        + "なお、質問者に絶対に答えを教えてはいけません。"
    
    converted_sid = sid_list_to_value_helper(session_id)
    # SQL実行
    cur.execute(query__for_insert, (converted_sid, "system", PROMPT))

    # DBをコミット
    conn.commit()

# =================================
# 【Listのdictになっているsession_idから値だけを返すヘルパー関数】
# =================================
def sid_list_to_value_helper(before_converting:list[dict]):
    session_id = before_converting[0]['session_id']
    return session_id

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

    result = select_theme()
    for fetched_line in result:
        question_code = fetched_line['id']
        question_content = fetched_line['character_name']
        genre_code = fetched_line['genre_code']
        question_times = fetched_line['question_times']
        print(f'{question_code}: {question_content}:{genre_code}:{question_times}')

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
    ORDER BY character_name
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
    return cur.fetchone()

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
# 【会話履歴マスタから同一のsession_idをすべて取得する関数】
# =================================


def select_conversation_history(session_id):
    query__for_fetching = """
    SELECT 
        role,message AS content
    FROM
        会話履歴マスタ
    WHERE
        session_id = %s
    ORDER BY id
    ;
    """
    cur.execute(query__for_fetching, (session_id,))
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

    # PROMPT = "あなたはゲームやアニメが大好きなオタクです。" \
    #     + "今からクイズを行います。あなたは出題者側です"\
    #     + "質問される内容にクイズ形式でヒントを出す形で回答してください。"\
    #     + f"今回のお題は{theme['character_name']}です。"\
    #     + "なお、質問者に絶対に答えを教えてはいけません。"

def insert_system_prompt(session_id: int, theme):
    query__for_insert = """
    INSERT INTO 会話履歴マスタ(session_id,id,role,message)
    VALUES (%s, %s, %s, %s)
    """
    PROMPT = "あなたはゲームやアニメが大好きなオタクです。"\
        + "これからクイズを行います。あなたは【出題者】の役割を担当します。  "\
        + f"今回のお題は「{theme['character_name']}」ですが、  "\
        + "絶対にキャラクター名や作品名を直接言ってはいけません。  "\
        + "あなたが行うのは「特徴的なヒントを小出しに提示すること」です。  "\
        + "ヒントはクイズ形式にしてください。  "\
        + "（例：性格、見た目、セリフ、活躍する場面、関係のあるキャラなど）  "\
        + "回答者が正解を推測できるように導きますが、  "\
        + "あなた自身が答えを言うのは禁止です。  "\
        + "もし答えを言いたくなっても、必ず「まだ秘密だよ」と濁してください。 "\

    # SQL実行
    cur.execute(query__for_insert, (session_id,
                get_max_conversation_history_id(session_id) + 1, "system", PROMPT))

    # DBをコミット
    conn.commit()

# =================================
# 【質問を会話履歴マスタに登録する関数】
# =================================


def insert_user_question(session_id: int, user_question: str):
    query__for_insert = """
    INSERT INTO 会話履歴マスタ(session_id,id,role,message)
    VALUES (%s, %s, %s, %s)
    """

    cur.execute(query__for_insert, (session_id, get_max_conversation_history_id(
        session_id) + 1, "user", user_question))

    # DBをコミット
    conn.commit()

# =================================
# 【AIの回答を会話履歴マスタに登録する関数】
# =================================


def insert_ai_answer(session_id: int, ai_answer: str):
    query__for_insert = """
    INSERT INTO 会話履歴マスタ(session_id,id,role,message)
    VALUES (%s, %s, %s, %s)
    """

    cur.execute(query__for_insert, (session_id, get_max_conversation_history_id(
        session_id) + 1, "assistant", ai_answer))

    # DBをコミット
    conn.commit()

# =================================
# 【会話履歴マスタから該当のセッションの最大のidを取得する関数】
# =================================


def get_max_conversation_history_id(session_id: int):

    # 結果がNULLだった場合は0を返す関数
    query__for_fetching = """
    SELECT
        IFNULL(max(id),0) AS id
    FROM 会話履歴マスタ
    WHERE session_id = %s
    """

    cur.execute(query__for_fetching, (session_id,))
    return cur.fetchone()['id']

# =================================
# 【現在のセッションidからお題のidとお題の和名を取得する関数】
# =================================
def get_theme_info_on_session_id(session_id:int):
        # 結果がNULLだった場合は0を返す関数
    query__for_fetching = """
    SELECT
        session_id,theme,id
    FROM お題マスタ
    LEFT JOIN キャラクタマスタ
        ON お題マスタ.theme = キャラクタマスタ.id
    WHERE session_id = %s
    ORDER BY session_id
    ;
    """

    cur.execute(query__for_fetching,(session_id,))
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

    result = select_theme()
    for fetched_line in result:
        question_code = fetched_line['id']
        question_content = fetched_line['character_name']
        genre_code = fetched_line['genre_code']
        question_times = fetched_line['question_times']
        print(f'{question_code}: {question_content}:{genre_code}:{question_times}')

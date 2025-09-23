import requests
import json
import os
from dotenv import load_dotenv

# --- .envファイルの読み込み ---
load_dotenv()

# =================================
# 【aiサーバ情報】
# =================================
# --- リクエスト先URL ---
OLLAMA_BASE_URL = f"http://{os.environ['OLLAMA_HOST']}:{os.environ['OLLAMA_PORT']}"

# --- モデル名 ---
MODEL_NAME = "elyza:jp8b"

# --- APIエンドポイント ---
GENERATE_API_URL = f"{OLLAMA_BASE_URL}/api/generate"
# print(OLLAMA_BASE_URL)

# =================================
# 【Ollamaで推論をして回答を取得する関数】
# =================================
def generate_inference_with_ollama(model: str, prompt: str) -> str | None:

    # --- リクエストの本文で指定する内容 ---
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }

    headers = {"Content-Type": "application/json"}

    try:
        # -- POSTリクエストを送信 ---
        response = requests.post(
            GENERATE_API_URL, headers=headers, json=payload, timeout=30)
        # --- ステータスコードが200番台(成功)以外なら例外をthrow ---
        response.raise_for_status()

        # レスポンスをjsonとして取得
        response_data = response.json()

        # --- 生成された回答を取得 ---
        generated_text = response_data.get("response")
        if generated_text:
            return generated_text.strip()
        else:
            print("エラー: レスポンスに 'response' キーが含まれていません。")
            print("レスポンス内容:", response_data)
            return None

    # --- サーバとの接続失敗 ---
    except requests.exceptions.ConnectionError as ex:
        print(f"エラー: Ollamaサーバー ({OLLAMA_BASE_URL}) に接続できませんでした。")
        print(f"詳細: {ex}")
        print("Ollamaサーバーが起動しているか、ネットワーク設定（ファイアウォール等）を確認してください。")
        return None
    
    # --- サーバータイムアウト ---
    except requests.exceptions.Timeout as ex:
        print(f"エラー: Ollamaサーバーへのリクエストがタイムアウトしました。")
        print(f"詳細: {ex}")
        return None
    
    # --- リクエスト中の例外 ---
    except requests.exceptions.RequestException as e:
        print(f"エラー: Ollama APIへのリクエスト中にエラーが発生しました。")
        print(f"URL: {e.request.url if e.request else 'N/A'}")
        if e.response is not None:
            print(f"ステータスコード: {e.response.status_code}")
            try:
                # エラーレスポンスの内容を表示試行
                error_content = e.response.json()
                print(f"エラー内容: {error_content}")
            except json.JSONDecodeError:
                print(f"エラーレスポンス (テキスト): {e.response.text}")
        else:
            print(f"詳細: {e}")
        return None
    
    # --- レスポンスのjson解析に失敗 ---
    except json.JSONDecodeError as e:
        print(f"エラー: Ollama APIからのレスポンスのJSON解析に失敗しました。")
        print(f"レスポンス内容: {response.text}")
        print(f"詳細: {e}")
        return None


if __name__ == "__main__":

    # --- 標準出力用 ---
    print("--- 【質問】 ---")
    PROMPT = input()
    print("----------------")
    print(f"モデル '{MODEL_NAME}' にプロンプトを送信します...")
    print(f"プロンプト: {PROMPT}")
    print("-" * 30)

        # テキスト生成を実行
    generated_response = generate_inference_with_ollama(MODEL_NAME,PROMPT)

    if generated_response:
        print("モデルからの応答:")
        print(generated_response)
    else:
        print("テキスト生成に失敗しました。")
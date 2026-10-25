"""第1回: 素のLLMに1回だけ質問するスクリプト。

使い方:
    uv run python -m app.ask "LoRAとは何ですか？"
    uv run python -m app.ask            # 質問を省略すると、講座に固有の質問をする

ツールも会話履歴も持たない「素の」呼び出し。
講座に固有のことを聞くと、「分からない」と答えるか、一般論でもっともらしく答える
（講座の実際とは違う）ことを確かめよう。
（第3回で、用語集を検索できるエージェントにして改善する）
"""

import argparse

from google import genai
from google.genai import errors, types

from app.config import MODEL, api_error_message, get_api_key

# 講座に固有の質問。正しい答えは data/glossary.json の homework-levels にある
DEFAULT_QUESTION = "AIE2026の講座の宿題にある「3レベル」とは何ですか？"


def ask(question: str) -> str:
    client = genai.Client(api_key=get_api_key())
    response = client.models.generate_content(model=MODEL, contents=question)

    # TODO(第1回 演習): response.usage_metadata から
    #   入力トークン数と出力トークン数を表示してみよう（Copilotに頼んでよい）

    return response.text

def print_usage(response) -> None:
    """入力・出力トークン数を表示する（演習で作った部分を関数にまとめたもの）。"""
    usage = response.usage_metadata
    print(f"\n[tokens] 入力 {usage.prompt_token_count} / 出力 {usage.candidates_token_count}")

def chat() -> None:
    """会話履歴を自分で持ち、続けて質問できるようにする。"""
    client = genai.Client(api_key=get_api_key())
    history: list[types.Content] = []  # これまでのやりとりを、古い順に積んでいく

    print("続けて質問できます（空行か exit で終了）")
    while True:
        question = input("\n質問> ").strip()
        if question in ("", "exit"):
            break

        # ポイント1: 新しい質問を履歴に足し、履歴をまるごと送る
        history.append(types.Content(role="user", parts=[types.Part(text=question)]))
        try:
            response = client.models.generate_content(model=MODEL, contents=history)
        except errors.APIError as e:
            print(api_error_message(e.code, e.message))
            history.pop()  # 失敗した質問は履歴から外し、送り直せるようにする
            continue

        print(response.text)
        print_usage(response)

        # ポイント2: モデルの答えも履歴に足す（role は "model"）
        history.append(types.Content(role="model", parts=[types.Part(text=response.text)]))

def main() -> None:
    parser = argparse.ArgumentParser(description="素のLLMに質問する")
    parser.add_argument("question", nargs="?", default=DEFAULT_QUESTION)
    parser.add_argument("--chat", action="store_true", help="会話履歴を保って続けて質問する")
    args = parser.parse_args()

    print(f"[model] {MODEL}")
    if args.chat:
        chat()
        return

    print(f"[質問] {args.question}\n")
    # ...ここから下は今のままでよい

    print_usage(response)

if __name__ == "__main__":
    main()

"""Anthropic(Claude) API 호출 전담 모듈."""
import time
from anthropic import Anthropic, APIError
from core.debug_utils import log, timer

DEFAULT_TEXT_MODEL = "claude-sonnet-5"


def generate_text(prompt: str, api_key: str, model: str = DEFAULT_TEXT_MODEL,
                   use_search: bool = True, max_retries: int = 3) -> str:
    """Claude로 텍스트를 생성합니다. (글쓰기/검수 공용)
    일시적인 서버 오류에 대비해 최대 max_retries번 재시도합니다.
    """
    client = Anthropic(api_key=api_key)
    last_error = None

    tools = [{"type": "web_search_20250305", "name": "web_search"}] if use_search else []

    for attempt in range(1, max_retries + 1):
        try:
            with timer(f"[Claude] 생성 시도 {attempt}/{max_retries}"):
                response = client.messages.create(
                    model=model,
                    max_tokens=8192,
                    tools=tools,
                    messages=[{"role": "user", "content": prompt}],
                )
            log(f"[Claude] 생성 성공 (시도 {attempt}번째)")
            text_parts = [block.text for block in response.content if block.type == "text"]
            return "".join(text_parts)

        except APIError as e:
            last_error = e
            wait_seconds = attempt * 3
            log(f"[Claude] 서버 오류 (시도 {attempt}/{max_retries}): {e}. {wait_seconds}초 후 재시도.")
            time.sleep(wait_seconds)

    raise RuntimeError(f"[Claude] {max_retries}번 재시도했지만 실패했습니다: {last_error}")
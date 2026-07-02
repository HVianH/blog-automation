"""OpenAI(GPT) API 호출 전담 모듈."""
import time
import base64
from openai import OpenAI, APIError
from core.debug_utils import log, timer

DEFAULT_TEXT_MODEL = "gpt-5.5"
DEFAULT_IMAGE_MODEL = "gpt-image-2"


def generate_text(prompt: str, api_key: str, model: str = DEFAULT_TEXT_MODEL,
                   use_search: bool = True, max_retries: int = 3) -> str:
    """GPT로 텍스트를 생성합니다. (글쓰기/검수 공용)
    일시적인 서버 오류에 대비해 최대 max_retries번 재시도합니다.
    """
    client = OpenAI(api_key=api_key)
    last_error = None

    tools = [{"type": "web_search"}] if use_search else []

    for attempt in range(1, max_retries + 1):
        try:
            with timer(f"[GPT] 생성 시도 {attempt}/{max_retries}"):
                response = client.responses.create(
                    model=model,
                    tools=tools,
                    input=prompt,
                )
            log(f"[GPT] 생성 성공 (시도 {attempt}번째)")
            return response.output_text

        except APIError as e:
            last_error = e
            wait_seconds = attempt * 3
            log(f"[GPT] 서버 오류 (시도 {attempt}/{max_retries}): {e}. {wait_seconds}초 후 재시도.")
            time.sleep(wait_seconds)

    raise RuntimeError(f"[GPT] {max_retries}번 재시도했지만 실패했습니다: {last_error}")


def generate_image(prompt: str, api_key: str, model: str = DEFAULT_IMAGE_MODEL,
                    size: str = "1024x1024", max_retries: int = 3) -> bytes:
    """GPT(gpt-image-2)로 이미지를 생성해서 PNG bytes를 반환합니다."""
    client = OpenAI(api_key=api_key)
    last_error = None

    for attempt in range(1, max_retries + 1):
        try:
            with timer(f"[GPT] 이미지 생성 시도 {attempt}/{max_retries}"):
                result = client.images.generate(
                    model=model,
                    prompt=prompt,
                    size=size,
                )
            log(f"[GPT] 이미지 생성 성공 (시도 {attempt}번째)")
            image_base64 = result.data[0].b64_json
            return base64.b64decode(image_base64)

        except APIError as e:
            last_error = e
            wait_seconds = attempt * 3
            log(f"[GPT] 이미지 서버 오류 (시도 {attempt}/{max_retries}): {e}. {wait_seconds}초 후 재시도.")
            time.sleep(wait_seconds)

    raise RuntimeError(f"[GPT] {max_retries}번 재시도했지만 이미지 생성에 실패했습니다: {last_error}")
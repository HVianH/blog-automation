"""Gemini(Google) API 호출 전담 모듈."""
import time
from google import genai
from google.genai import types
from google.genai.errors import ServerError
from core.debug_utils import log, timer

DEFAULT_TEXT_MODEL = "gemini-3.5-flash"
DEFAULT_IMAGE_MODEL = "gemini-2.5-flash-image"


def generate_text(prompt: str, api_key: str, model: str = DEFAULT_TEXT_MODEL,
                   use_search: bool = True, max_retries: int = 3) -> str:
    """Gemini로 텍스트를 생성합니다. (글쓰기/검수 공용)
    구글 서버 일시 오류(500/503)에 대비해 최대 max_retries번 재시도합니다.
    """
    client = genai.Client(api_key=api_key)
    last_error = None

    config_kwargs = {}
    if use_search:
        config_kwargs["tools"] = [types.Tool(google_search=types.GoogleSearch())]

    for attempt in range(1, max_retries + 1):
        try:
            with timer(f"[Gemini] 생성 시도 {attempt}/{max_retries}"):
                response = client.models.generate_content(
                    model=model,
                    contents=prompt,
                    config=types.GenerateContentConfig(**config_kwargs) if config_kwargs else None,
                )
            log(f"[Gemini] 생성 성공 (시도 {attempt}번째)")
            return response.text

        except ServerError as e:
            last_error = e
            wait_seconds = attempt * 3
            log(f"[Gemini] 서버 오류 (시도 {attempt}/{max_retries}): {e}. {wait_seconds}초 후 재시도.")
            time.sleep(wait_seconds)

    raise RuntimeError(f"[Gemini] {max_retries}번 재시도했지만 실패했습니다: {last_error}")


def generate_image(prompt: str, api_key: str, model: str = DEFAULT_IMAGE_MODEL,
                    aspect_ratio: str = "1:1", max_retries: int = 3) -> bytes:
    """Gemini로 이미지를 생성해서 PNG bytes를 반환합니다."""
    client = genai.Client(api_key=api_key)
    last_error = None

    for attempt in range(1, max_retries + 1):
        try:
            with timer(f"[Gemini] 이미지 생성 시도 {attempt}/{max_retries}"):
                response = client.models.generate_content(
                    model=model,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_modalities=["IMAGE"],
                        image_config=types.ImageConfig(aspect_ratio=aspect_ratio),
                    ),
                )

            if response.candidates:
                candidate = response.candidates[0]
                if candidate.content and candidate.content.parts:
                    for part in candidate.content.parts:
                        if part.inline_data:
                            log(f"[Gemini] 이미지 생성 성공 (시도 {attempt}번째)")
                            return part.inline_data.data
                raise RuntimeError(f"이미지 없음. 이유: {candidate.finish_reason}")
            raise RuntimeError("응답이 비어있습니다.")

        except ServerError as e:
            last_error = e
            wait_seconds = attempt * 3
            log(f"[Gemini] 이미지 서버 오류 (시도 {attempt}/{max_retries}): {e}. {wait_seconds}초 후 재시도.")
            time.sleep(wait_seconds)

    raise RuntimeError(f"[Gemini] {max_retries}번 재시도했지만 이미지 생성에 실패했습니다: {last_error}")
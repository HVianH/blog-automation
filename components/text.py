from core.content_generator import generate_draft


def generate_post(provider: str, api_key: str, keyword: str, blog: dict, model: str = None) -> str:
    """키워드 + 블로그 설정으로 글을 생성합니다. (본문 텍스트를 그대로 반환)

    provider: "gemini" | "openai" | "anthropic"
    model: 생략하면 해당 provider의 기본 모델 사용
    """
    return generate_draft(provider, api_key, keyword, blog, model=model)
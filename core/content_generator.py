from core.providers import gemini_provider, openai_provider, anthropic_provider

# provider 이름 문자열 -> 실제 호출 모듈 매핑
PROVIDERS = {
    "gemini": gemini_provider,
    "openai": openai_provider,
    "anthropic": anthropic_provider,
}


def build_prompt(keyword: str, blog: dict) -> str:
    return f"""
{blog['seo_prompt']}

목표 분량: 공백 포함 약 {blog['target_length']}자

키워드: "{keyword}"

최신 정보를 웹에서 조사한 뒤, 위 SEO 규칙에 맞춰서 이 키워드에 대한 블로그 글을 작성해줘.

[이미지 위치 표시 규칙]
본문에서 이미지가 들어가면 좋을 위치마다, 아래 형식으로 마커를 넣어줘.
[IMAGE: 이 위치에 들어갈 이미지에 대한 구체적인 설명(한글로)]

- 마커는 본문 전체에 걸쳐 2~4개 정도, 소제목 바로 아래나 문단 사이 자연스러운 위치에 넣어줘.
- 마커 자체는 그대로 남겨야 해. 이미지를 직접 만들라는 게 아니라, 위치와 설명만 표시하는 거야.
"""


def generate_draft(provider: str, api_key: str, keyword: str, blog: dict, model: str = None) -> str:
    """키워드 + 블로그 SEO 프롬프트로 초안 텍스트를 생성합니다.

    provider: "gemini" | "openai" | "anthropic" 중 하나
    model: 생략하면 해당 provider의 기본 모델을 사용
    """
    if provider not in PROVIDERS:
        raise ValueError(f"지원하지 않는 provider입니다: {provider} (사용 가능: {list(PROVIDERS.keys())})")

    prompt = build_prompt(keyword, blog)
    module = PROVIDERS[provider]

    kwargs = {"use_search": True}
    if model:
        kwargs["model"] = model

    return module.generate_text(prompt, api_key, **kwargs)
from core.providers import gemini_provider, openai_provider, anthropic_provider
from core.blog_config import load_prompt

# provider 이름 문자열 -> 실제 호출 모듈 매핑
PROVIDERS = {
    "gemini": gemini_provider,
    "openai": openai_provider,
    "anthropic": anthropic_provider,
}


def build_prompt(keyword: str, blog: dict, provider: str) -> str:
    """블로그 + 모델(provider) 조합에 맞는 SEO 프롬프트 파일을 읽어서, 최종 프롬프트를 조립합니다."""
    seo_prompt = load_prompt(blog["id"], provider)

    return f"""
{seo_prompt}

목표 분량: 공백 포함 약 {blog['target_length']}자

키워드: "{keyword}"

최신 정보를 웹에서 조사한 뒤, 위 SEO 규칙에 맞춰서 이 키워드에 대한 블로그 글을 작성해줘.
본문은 마크다운 소제목(##, ###)을 사용해서 논리적으로 구조를 나눠줘.
"""


def generate_draft(provider: str, api_key: str, keyword: str, blog: dict, model: str = None) -> str:
    """키워드 + 블로그별·모델별 SEO 프롬프트로 초안 텍스트를 생성합니다.

    provider: "gemini" | "openai" | "anthropic" 중 하나
    model: 생략하면 해당 provider의 기본 모델을 사용
    """
    if provider not in PROVIDERS:
        raise ValueError(f"지원하지 않는 provider입니다: {provider} (사용 가능: {list(PROVIDERS.keys())})")

    prompt = build_prompt(keyword, blog, provider)
    module = PROVIDERS[provider]

    kwargs = {"use_search": True}
    if model:
        kwargs["model"] = model

    return module.generate_text(prompt, api_key, **kwargs)
from core.providers import gemini_provider, openai_provider
from core.image_processing import optimize_for_blog

# 이미지 생성 가능한 provider만 (Claude는 이미지 생성 API가 없어서 제외)
IMAGE_PROVIDERS = {
    "gemini": gemini_provider,
    "openai": openai_provider,
}


def generate_image_bytes(provider: str, api_key: str, prompt: str, model: str = None) -> bytes:
    """설명(prompt)을 받아서 이미지를 생성하고, 블로그 규격(가로 900~1200px, 2MB 이하)에
    맞춰 최적화한 PNG/JPEG bytes를 반환합니다.

    provider: "gemini" | "openai" (Claude는 지원 안 함)
    model: 생략하면 해당 provider의 기본 이미지 모델 사용
    """
    if provider not in IMAGE_PROVIDERS:
        raise ValueError(
            f"이미지 생성을 지원하지 않는 provider입니다: {provider} "
            f"(사용 가능: {list(IMAGE_PROVIDERS.keys())})"
        )

    module = IMAGE_PROVIDERS[provider]
    kwargs = {}
    if model:
        kwargs["model"] = model

    raw_bytes = module.generate_image(prompt, api_key, **kwargs)
    return optimize_for_blog(raw_bytes)
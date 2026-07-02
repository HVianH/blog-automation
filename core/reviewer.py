from core.providers import gemini_provider, openai_provider, anthropic_provider

# 검수는 텍스트 작업이라 이미지 provider(openai 이미지 전용)는 필요 없고, 셋 다 사용 가능
PROVIDERS = {
    "gemini": gemini_provider,
    "openai": openai_provider,
    "anthropic": anthropic_provider,
}

REVIEW_INSTRUCTION = """
너는 블로그 글의 'AI 티'를 없애는 전문 편집자야.
아래 글을 다시 다듬어줘. 단, 다음 규칙을 반드시 지켜줘.

[절대 지켜야 할 것]
- [IMAGE: ...] 형태의 마커는 위치와 내용을 절대 바꾸지 말고 그대로 남겨줘.
- 소제목(##, ###)의 개수와 순서, 전체적인 글의 구조는 유지해줘.
- 사실 관계나 수치, 고유명사를 새로 추가하거나 바꾸지 마.
- 전체 글자 수는 원문과 비슷하게 유지해줘.

[AI 티를 없애기 위해 고쳐야 할 것]
- '또한', '따라서', '이처럼' 같은 기계적인 접속사 반복을 줄이고, 자연스러운 흐름으로 바꿔.
- 모든 문장이 비슷한 길이와 구조로 반복되지 않게, 문장 길이에 리듬감을 줘.
- '~것으로 보입니다', '~라고 할 수 있습니다' 같은 애매한 헤지 표현을 줄이고, 자신 있게 서술해.
- '결론적으로', '요약하자면' 같은 뻔한 마무리 문구를 자연스러운 표현으로 바꿔.
- 지나치게 균형 잡힌 문단 구성(모든 문단이 3문장씩 등)을 피하고, 문단 길이도 자연스럽게 섞어.
- 사람이 직접 쓴 것처럼, 약간의 구어체나 자연스러운 강조를 섞어줘.

원문:
---
{original_text}
---

위 규칙을 지켜서 다시 쓴 전체 글만 출력해줘. 다른 설명이나 코멘트는 붙이지 마.
"""


def build_review_prompt(original_text: str) -> str:
    return REVIEW_INSTRUCTION.format(original_text=original_text)


def humanize_post(provider: str, api_key: str, original_text: str, model: str = None) -> str:
    """생성된 글의 'AI 티'를 줄여서 자연스럽게 다듬습니다.

    provider: "gemini" | "openai" | "anthropic"
    model: 생략하면 해당 provider의 기본 모델 사용
    """
    if provider not in PROVIDERS:
        raise ValueError(f"지원하지 않는 provider입니다: {provider} (사용 가능: {list(PROVIDERS.keys())})")

    prompt = build_review_prompt(original_text)
    module = PROVIDERS[provider]

    kwargs = {"use_search": False}
    if model:
        kwargs["model"] = model

    return module.generate_text(prompt, api_key, **kwargs)
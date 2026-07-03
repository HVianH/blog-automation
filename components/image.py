import re
import streamlit as st
from core.image_generator import generate_image_bytes

HEADING_PATTERN = re.compile(r"^(#{2,3}\s*.+)$", re.MULTILINE)


def _is_heading(text: str) -> bool:
    return re.match(r"^#{2,3}\s*(.+)$", text.strip()) is not None


STYLE_GUIDE = """
[스타일 선택 기준]
아래 내용을 보고, 가장 적합한 시각 스타일을 스스로 판단해서 만들어줘.
- 숫자, 비교, 순위, 통계 데이터가 중심이면 → 그래프/표/인포그래픽 스타일 (이 경우엔 축 이름, 수치 같은 최소한의 텍스트는 넣어도 됨)
- 개념 설명이나 절차·순서를 다루면 → 일러스트/다이어그램 스타일
- 실제 사물, 장소, 행동, 사람의 동작을 다루면 → 사진처럼 자연스러운 스타일
- 가볍고 친근한 팁이나 재미 요소면 → 카툰/캐릭터 일러스트 스타일
- 위 경우가 아니면 사진 스타일을 기본으로 하되, 텍스트는 넣지 마.

[주의사항]
- 실존 인물(연예인, 정치인, 유명인 등)을 특정해서 닮게 그리지 마. 필요하면 익명의 일반인 실루엣이나 상징적인 오브젝트로 대체해줘.
- 특정 브랜드 로고나 저작권이 있는 캐릭터를 그대로 그리지 마.
- 자극적이거나 폭력적인 장면 대신, 상징적이고 은유적인 표현을 사용해줘.
"""


def _build_cover_image_prompt(intro_text: str) -> str:
    """제목/도입부 내용을 보고, 글 전체를 대표하는 표지(썸네일) 이미지 프롬프트를 만듭니다."""
    snippet = intro_text.strip()[:400]
    return (
        f"블로그 글의 표지(썸네일) 이미지를 만들어줘.\n\n"
        f"글의 제목/도입부 내용:\n{snippet}\n\n"
        f"이 글 전체를 대표할 수 있는, 한눈에 시선을 끄는 표지 이미지로 만들어줘.\n"
        f"{STYLE_GUIDE}"
    )


def _build_section_image_prompt(heading: str, body_snippet: str) -> str:
    """소제목 + 그 아래 실제 본문 내용을 같이 보고, 구체적인 이미지 프롬프트를 만듭니다."""
    snippet = body_snippet.strip()[:400]
    return (
        f"블로그 글의 '{heading}' 섹션에 어울리는 이미지를 만들어줘.\n\n"
        f"이 섹션의 실제 내용:\n{snippet}\n\n"
        f"위 내용을 구체적으로 반영한 이미지로 만들어줘. 소제목 문구를 그대로 그리지 말고, "
        f"내용이 담고 있는 장면·사물·상황·데이터를 시각적으로 표현해줘.\n"
        f"{STYLE_GUIDE}"
    )


def _generate_one_image(image_provider: str, api_key: str, prompt_text: str, label: str) -> dict:
    status = st.empty()
    status.caption(f"🖼️ 이미지 생성 중: {label}")
    try:
        with st.spinner("이미지 생성 중..."):
            image_bytes = generate_image_bytes(image_provider, api_key, prompt_text)
        status.empty()
        return {"type": "image", "content": image_bytes}
    except Exception as e:
        status.empty()
        return {"type": "image_error", "content": str(e)}


def generate_post_elements_by_headings(image_provider: str, api_key: str, draft_text: str) -> list:
    """표지 이미지 1개 + 소제목마다 어울리는 이미지를 생성해서 요소 목록을 만듭니다.
    (이 함수는 딱 한 번만 호출해서 결과를 저장해두고 재사용해야 해요. 다시 부르면 이미지가 또 생성됩니다!)
    """
    parts = HEADING_PATTERN.split(draft_text)
    elements = []

    # 1. 표지 이미지 (첫 소제목 나오기 전까지의 제목/도입부 기준)
    intro_text = parts[0] if parts and not _is_heading(parts[0]) else ""
    cover_context = intro_text.strip() or draft_text[:400]
    cover_prompt = _build_cover_image_prompt(cover_context)
    elements.append(_generate_one_image(image_provider, api_key, cover_prompt, "표지"))

    # 2. 소제목마다 이미지 -> 소제목 -> 본문
    i = 0
    while i < len(parts):
        part = parts[i]

        if _is_heading(part):
            heading_match = re.match(r"^#{2,3}\s*(.+)$", part.strip())
            heading_text = heading_match.group(1).strip()

            body_snippet = ""
            if i + 1 < len(parts) and not _is_heading(parts[i + 1]):
                body_snippet = parts[i + 1]

            section_prompt = _build_section_image_prompt(heading_text, body_snippet)
            elements.append(_generate_one_image(image_provider, api_key, section_prompt, heading_text))
            elements.append({"type": "text", "content": part})
        else:
            if part.strip():
                elements.append({"type": "text", "content": part})

        i += 1

    return elements


def render_elements(elements: list) -> None:
    """이미지/텍스트 요소 목록을 화면에 그리기만 합니다. API 호출이 없어서 몇 번을 다시 그려도 비용이 안 듭니다."""
    for el in elements:
        if el["type"] == "text":
            st.markdown(el["content"])
        elif el["type"] == "image":
            st.image(el["content"])
        elif el["type"] == "image_error":
            st.warning(f"이미지 생성 실패: {el['content']}")


def render_reviewed_with_cached_images(reviewed_text: str, original_elements: list) -> None:
    """검수본 텍스트를 화면에 그리되, 표지/소제목 이미지 자리에는 새로 만들지 않고
    원본에서 이미 생성해둔 이미지를 순서대로(표지 -> 소제목 순) 재사용합니다.
    """
    cached_images = [el for el in original_elements if el["type"] in ("image", "image_error")]
    image_iter = iter(cached_images)

    cover_cached = next(image_iter, None)
    if cover_cached:
        if cover_cached["type"] == "image":
            st.image(cover_cached["content"])
        else:
            st.warning(f"이미지 생성 실패: {cover_cached['content']}")

    parts = HEADING_PATTERN.split(reviewed_text)
    for part in parts:
        if _is_heading(part):
            cached = next(image_iter, None)
            if cached is None:
                st.warning("검수본의 소제목 개수가 원본보다 많아요. (검수 과정에서 구조가 달라진 것 같아요)")
            elif cached["type"] == "image":
                st.image(cached["content"])
            else:
                st.warning(f"이미지 생성 실패: {cached['content']}")
            st.markdown(part)
        else:
            if part.strip():
                st.markdown(part)
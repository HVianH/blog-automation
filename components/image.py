import re
import streamlit as st
from core.image_generator import generate_image_bytes


def generate_post_elements(provider: str, api_key: str, body_text: str) -> list:
    """본문 텍스트를 [IMAGE: 설명] 마커 기준으로 분석해서, 실제 이미지 생성까지 마친
    '요소 목록'을 만듭니다. (이 함수는 딱 한 번만 호출해서 결과를 저장해두고 재사용해야 해요.
    화면을 다시 그릴 때마다 이 함수를 또 부르면 이미지가 매번 새로 생성됩니다!)

    provider: "gemini" | "openai"
    """
    parts = re.split(r"(\[(?:IMAGE|이미지):.*?\])", body_text)
    elements = []

    for part in parts:
        match = re.match(r"\[(?:IMAGE|이미지):\s*(.*?)\]", part)
        if match:
            image_description = match.group(1)
            status = st.empty()
            status.caption(f"🖼️ 이미지 생성 중: {image_description}")
            try:
                with st.spinner("이미지 생성 중..."):
                    image_bytes = generate_image_bytes(provider, api_key, image_description)
                status.empty()
                elements.append({"type": "image", "content": image_bytes})
            except Exception as e:
                status.empty()
                elements.append({"type": "image_error", "content": str(e)})
        else:
            if part.strip():
                elements.append({"type": "text", "content": part})

    return elements


def render_elements(elements: list) -> None:
    """generate_post_elements()가 만들어둔 결과를 화면에 그리기만 합니다.
    API 호출이 전혀 없어서, 몇 번을 다시 그려도 비용이 들지 않아요.
    """
    for el in elements:
        if el["type"] == "text":
            st.markdown(el["content"])
        elif el["type"] == "image":
            st.image(el["content"])
        elif el["type"] == "image_error":
            st.warning(f"이미지 생성 실패: {el['content']}")


def render_reviewed_with_cached_images(reviewed_text: str, original_elements: list) -> None:
    """검수본 텍스트를 화면에 그리되, [IMAGE: ...] 마커 자리에는 새로 만들지 않고
    원본에서 이미 생성해둔 이미지를 순서대로 재사용합니다.
    """
    cached_images = [el for el in original_elements if el["type"] in ("image", "image_error")]
    image_iter = iter(cached_images)

    parts = re.split(r"(\[(?:IMAGE|이미지):.*?\])", reviewed_text)
    for part in parts:
        match = re.match(r"\[(?:IMAGE|이미지):\s*(.*?)\]", part)
        if match:
            cached = next(image_iter, None)
            if cached is None:
                st.warning("검수본의 이미지 자리가 원본보다 많아요. (검수 과정에서 마커 개수가 달라진 것 같아요)")
                continue
            if cached["type"] == "image":
                st.image(cached["content"])
            else:
                st.warning(f"이미지 생성 실패: {cached['content']}")
        else:
            if part.strip():
                st.markdown(part)
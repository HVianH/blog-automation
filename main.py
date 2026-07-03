# region 비밀번호 보호
import streamlit as st
from components.auth import check_password

if not check_password():
    st.stop()
# endregion


# region 설정 및 초기화
from core.blog_config import load_blogs
from components.ui import render_sidebar
from components.text import generate_post
from components.image import generate_post_elements_by_headings, render_elements, render_reviewed_with_cached_images

api_keys = {
    "gemini": st.secrets.get("GEMINI_API_KEY"),
    "openai": st.secrets.get("OPENAI_API_KEY"),
    "anthropic": st.secrets.get("ANTHROPIC_API_KEY"),
}

st.title("📝 블로그 자동화")

blogs = load_blogs()

if "draft_text" not in st.session_state:
    st.session_state.draft_text = None
if "rendered_elements" not in st.session_state:
    st.session_state.rendered_elements = None
if "reviewed_text" not in st.session_state:
    st.session_state.reviewed_text = None
# endregion


# region 사이드바
selected_blog, generate_images, text_provider, image_provider, review_provider = render_sidebar(blogs, api_keys)
# endregion


# region 글 작성 -> (이미지 켜져있으면) 소제목마다 이미지 생성
keyword = st.text_input("키워드를 입력하세요")

if st.button("글 작성"):
    try:
        with st.spinner("자료를 조사하고 글을 작성하는 중..."):
            draft_text = generate_post(text_provider, api_keys[text_provider], keyword, selected_blog)

        if generate_images:
            elements = generate_post_elements_by_headings(image_provider, api_keys[image_provider], draft_text)
        else:
            elements = None

        st.session_state.draft_text = draft_text
        st.session_state.rendered_elements = elements
        st.session_state.reviewed_text = None
        st.session_state.used_text_provider = text_provider
        st.session_state.used_image_provider = image_provider if generate_images else None

        st.rerun()

    except (RuntimeError, ValueError) as e:
        st.error(f"글 생성에 실패했습니다: {e}")
# endregion


# region 결과 표시
draft_text = st.session_state.draft_text

if draft_text:
    used_text = st.session_state.get("used_text_provider", "-")
    used_image = st.session_state.get("used_image_provider") or "사용 안 함"
    st.caption(f"✍️ 글쓰기: **{used_text}**  |  🖼️ 이미지: **{used_image}**")

    st.write("### 생성된 글 (원본)")

    if st.session_state.rendered_elements is not None:
        render_elements(st.session_state.rendered_elements)
    else:
        st.caption("🖼️ 이미지 생성이 꺼져있어요. (사이드바에서 켤 수 있어요)")
        st.markdown(draft_text)

    if st.session_state.reviewed_text:
        st.divider()
        st.write(f"### ✨ 검수본 (AI 티 줄임 — {review_provider})")
        if st.session_state.rendered_elements is not None:
            render_reviewed_with_cached_images(
                st.session_state.reviewed_text, st.session_state.rendered_elements
            )
        else:
            st.markdown(st.session_state.reviewed_text)
# endregion
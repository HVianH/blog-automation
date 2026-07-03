import streamlit as st
from core.blog_config import save_blogs, load_prompt, save_prompt

# 드롭다운에 보여줄 이름 <-> 실제 provider 코드 매핑
TEXT_PROVIDER_OPTIONS = {
    "gemini": "Gemini (gemini-3.5-flash)",
    "openai": "GPT (gpt-5.5)",
    "anthropic": "Claude (claude-sonnet-5)",
}

IMAGE_PROVIDER_OPTIONS = {
    "gemini": "Gemini (gemini-2.5-flash-image)",
    "openai": "GPT (gpt-image-2)",
    # Claude는 이미지 생성 API가 없어서 여기엔 없음
}


def render_sidebar(blogs: list, api_keys: dict):
    """사이드바 전체를 그립니다.

    api_keys: {"gemini": "...", "openai": "...", "anthropic": "..."} 형태의 딕셔너리
    반환값: (선택된 블로그 dict, 이미지 생성 여부 bool, 글쓰기 provider, 이미지 provider)
    """
    blog_names = {b["id"]: b["name"] for b in blogs}

    with st.sidebar:
        st.header("⚙️ 블로그 설정")

        selected_id = st.selectbox(
            "블로그 선택",
            options=list(blog_names.keys()),
            format_func=lambda x: blog_names[x],
        )
        selected_blog = next(b for b in blogs if b["id"] == selected_id)

        st.divider()
        st.subheader("🤖 사용할 모델")

        text_provider = st.selectbox(
            "글쓰기 모델",
            options=list(TEXT_PROVIDER_OPTIONS.keys()),
            format_func=lambda x: TEXT_PROVIDER_OPTIONS[x],
        )

        with st.expander(f"✏️ SEO 프롬프트 수정 ({TEXT_PROVIDER_OPTIONS[text_provider]})"):
            with st.form(f"edit_prompt_form_{selected_id}_{text_provider}"):
                current_prompt = load_prompt(selected_id, text_provider)
                edited_prompt = st.text_area(
                    "SEO 프롬프트",
                    value=current_prompt,
                    height=200,
                    key=f"prompt_{selected_id}_{text_provider}",
                )
                edited_length = st.number_input(
                    "목표 분량(자)",
                    value=selected_blog["target_length"],
                    key=f"length_{selected_id}",
                )
                submitted = st.form_submit_button("💾 저장")

                if submitted:
                    save_prompt(selected_id, text_provider, edited_prompt)
                    selected_blog["target_length"] = edited_length
                    save_blogs(blogs)
                    st.success("저장 완료!")
                    st.rerun()

        generate_images = st.checkbox(
            "🖼️ 이미지 생성",
            value=True,
            help="테스트 중 글만 반복해서 뽑아보고 싶을 때 꺼두면 이미지 생성 비용 없이 텍스트만 나옵니다.",
        )
        image_provider = st.selectbox(
            "이미지 모델",
            options=list(IMAGE_PROVIDER_OPTIONS.keys()),
            format_func=lambda x: IMAGE_PROVIDER_OPTIONS[x],
            disabled=not generate_images,
        )

        st.divider()
        st.link_button(
            "💳 남은 크레딧 확인하러 가기 (Gemini)",
            "https://aistudio.google.com/usage",
            use_container_width=True,
        )

    return selected_blog, generate_images, text_provider, image_provider
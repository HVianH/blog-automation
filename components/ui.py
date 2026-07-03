import streamlit as st
from core.blog_config import save_blogs, load_prompt, save_prompt
from core.reviewer import humanize_post

# 드롭다운에 보여줄 이름 <-> 실제 provider 코드 매핑
TEXT_PROVIDER_OPTIONS = {
    "gemini": "Gemini (gemini-3.5-flash)",
    "openai": "GPT (gpt-5.5)",
    "anthropic": "Claude (claude-sonnet-5)",
}

IMAGE_PROVIDER_OPTIONS = {
    "gemini": "Gemini (gemini-2.5-flash-image)",
    "openai": "GPT (gpt-image-2)",
}

REVIEW_PROVIDER_OPTIONS = {
    "gemini": "Gemini (gemini-3.5-flash)",
    "openai": "GPT (gpt-5.5)",
    "anthropic": "Claude (claude-sonnet-5)",
}

COMPARISON_LABELS = {
    "gemini": "🔵 Gemini",
    "openai": "🟢 GPT",
    "anthropic": "🟣 Claude",
}


@st.dialog("검수 결과 비교", width="large")
def show_comparison_dialog():
    results = st.session_state.get("multi_review_results", {})
    cols = st.columns(3)
    for col, provider in zip(cols, ["gemini", "openai", "anthropic"]):
        with col:
            st.markdown(f"**{COMPARISON_LABELS[provider]}**")
            result = results.get(provider)
            if result is None:
                st.caption("결과 없음")
            elif isinstance(result, str) and result.startswith("__ERROR__:"):
                st.warning(f"실패: {result.replace('__ERROR__:', '')}")
            else:
                st.markdown(result)


def render_sidebar(blogs: list, api_keys: dict):
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

        review_provider = st.selectbox(
            "검수 모델",
            options=list(REVIEW_PROVIDER_OPTIONS.keys()),
            format_func=lambda x: REVIEW_PROVIDER_OPTIONS[x],
        )

        st.divider()
        st.subheader("✍️ 검수")
        if st.session_state.get("draft_text") is None:
            st.caption("먼저 글을 작성하면 검수 버튼이 나타나요.")
        else:
            if st.button("작성글 검수하기 (AI 티 줄이기)", use_container_width=True):
                with st.spinner("AI 느낌을 줄이는 중..."):
                    original_text = st.session_state.draft_text
                    review_api_key = api_keys[review_provider]
                    st.session_state.reviewed_text = humanize_post(review_provider, review_api_key, original_text)
                st.success("검수 완료!")

            st.caption("여러 모델 결과를 한눈에 비교하고 싶다면:")
            if st.button("🔍 3개 모델로 검수 비교", use_container_width=True):
                original_text = st.session_state.draft_text
                results = {}
                for provider in ["gemini", "openai", "anthropic"]:
                    with st.spinner(f"{COMPARISON_LABELS[provider]} 검수 중..."):
                        try:
                            results[provider] = humanize_post(provider, api_keys[provider], original_text)
                        except (RuntimeError, ValueError) as e:
                            results[provider] = f"__ERROR__:{e}"
                st.session_state.multi_review_results = results
                show_comparison_dialog()

        st.divider()
        st.link_button(
            "💳 남은 크레딧 확인하러 가기 (Gemini)",
            "https://aistudio.google.com/usage",
            use_container_width=True,
        )

    return selected_blog, generate_images, text_provider, image_provider, review_provider
import streamlit as st
from components.auth import check_password

if not check_password():
    st.stop()

from core.blog_config import load_blogs, load_prompt, save_prompt
from core.content_generator import generate_draft
from core.reviewer import humanize_post

st.title("🔬 모델 비교 실험실")
st.caption("이미지 생성 없이, 글쓰기/검수 결과만 3개 모델로 나란히 비교하는 테스트 페이지입니다.")

api_keys = {
    "gemini": st.secrets.get("GEMINI_API_KEY"),
    "openai": st.secrets.get("OPENAI_API_KEY"),
    "anthropic": st.secrets.get("ANTHROPIC_API_KEY"),
}

PROVIDERS = ["gemini", "openai", "anthropic"]
LABELS = {"gemini": "🔵 Gemini", "openai": "🟢 GPT", "anthropic": "🟣 Claude"}

blogs = load_blogs()
blog_names = {b["id"]: b["name"] for b in blogs}

selected_id = st.selectbox(
    "블로그 선택",
    options=list(blog_names.keys()),
    format_func=lambda x: blog_names[x],
)
selected_blog = next(b for b in blogs if b["id"] == selected_id)

# ── 모델별 SEO 프롬프트 수정 (3개 모델 각각 따로) ─────
with st.expander("✏️ 모델별 SEO 프롬프트 수정", expanded=False):
    tabs = st.tabs([LABELS[p] for p in PROVIDERS])
    for tab, provider in zip(tabs, PROVIDERS):
        with tab:
            with st.form(f"edit_prompt_form_lab_{selected_id}_{provider}"):
                current_prompt = load_prompt(selected_id, provider)
                edited_prompt = st.text_area(
                    f"{LABELS[provider]} 프롬프트",
                    value=current_prompt,
                    height=250,
                    key=f"lab_prompt_{selected_id}_{provider}",
                    label_visibility="collapsed",
                )
                submitted = st.form_submit_button(f"💾 {LABELS[provider]} 프롬프트 저장")
                if submitted:
                    save_prompt(selected_id, provider, edited_prompt)
                    st.success("저장 완료!")
                    st.rerun()

keyword = st.text_input("키워드를 입력하세요")

if "write_results" not in st.session_state:
    st.session_state.write_results = None
if "review_results" not in st.session_state:
    st.session_state.review_results = None

# ── ① 글쓰기 3사 비교 ─────────────────────────────
st.divider()
st.subheader("① 글쓰기 비교")

if st.button("3개 모델로 글쓰기 비교", type="primary"):
    if not keyword.strip():
        st.warning("키워드를 입력해주세요.")
    else:
        results = {}
        for provider in PROVIDERS:
            with st.spinner(f"{LABELS[provider]} 글 작성 중..."):
                try:
                    results[provider] = generate_draft(provider, api_keys[provider], keyword.strip(), selected_blog)
                except (RuntimeError, ValueError) as e:
                    results[provider] = f"__ERROR__:{e}"
        st.session_state.write_results = results
        st.session_state.review_results = None

if st.session_state.write_results:
    cols = st.columns(3)
    for col, provider in zip(cols, PROVIDERS):
        with col:
            st.markdown(f"**{LABELS[provider]}**")
            result = st.session_state.write_results[provider]
            with st.container(border=True, height=400):
                if isinstance(result, str) and result.startswith("__ERROR__:"):
                    st.warning(f"실패: {result.replace('__ERROR__:', '')}")
                else:
                    st.markdown(result)

    st.divider()
    st.subheader("② 검수 비교")

    valid_providers = [
        p for p in PROVIDERS
        if not (isinstance(st.session_state.write_results[p], str)
                and st.session_state.write_results[p].startswith("__ERROR__:"))
    ]

    if not valid_providers:
        st.caption("검수할 수 있는 초안이 없어요. (① 단계에서 전부 실패한 것 같아요)")
    else:
        base_provider = st.selectbox(
            "어떤 모델의 초안을 검수할까요?",
            options=valid_providers,
            format_func=lambda x: LABELS[x],
        )

        if st.button("3개 모델로 검수 비교"):
            original_text = st.session_state.write_results[base_provider]
            review_results = {}
            for provider in PROVIDERS:
                with st.spinner(f"{LABELS[provider]} 검수 중..."):
                    try:
                        review_results[provider] = humanize_post(provider, api_keys[provider], original_text)
                    except (RuntimeError, ValueError) as e:
                        review_results[provider] = f"__ERROR__:{e}"
            st.session_state.review_results = review_results

if st.session_state.review_results:
    st.write(f"**검수 대상 원본**: {LABELS.get(base_provider, '-')}의 초안")
    cols = st.columns(3)
    for col, provider in zip(cols, PROVIDERS):
        with col:
            st.markdown(f"**{LABELS[provider]}**")
            result = st.session_state.review_results[provider]
            with st.container(border=True, height=400):
                if isinstance(result, str) and result.startswith("__ERROR__:"):
                    st.warning(f"실패: {result.replace('__ERROR__:', '')}")
                else:
                    st.markdown(result)
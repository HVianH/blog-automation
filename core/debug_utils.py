import time
from contextlib import contextmanager
import streamlit as st


def _get_debug_mode() -> bool:
    """secrets.toml의 DEBUG_MODE 값을 읽어옵니다. (true/false 문자열이든 진짜 불리언이든 둘 다 처리)"""
    value = st.secrets.get("DEBUG_MODE", False)
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() == "true"


DEBUG_MODE = _get_debug_mode()


@contextmanager
def timer(label: str):
    """
    특정 구간의 소요 시간을 측정해서 터미널(또는 Streamlit Cloud 로그)에 출력합니다.
    DEBUG_MODE가 꺼져있으면 아무것도 출력하지 않습니다.

    사용법:
        with timer("이미지 생성"):
            image_bytes = generate_image(...)
    """
    start = time.time()
    yield
    elapsed = time.time() - start
    if DEBUG_MODE:
        print(f"[DEBUG] {label}: {elapsed:.1f}초")


def log(message: str):
    """DEBUG_MODE가 켜져 있을 때만 터미널에 로그를 출력합니다."""
    if DEBUG_MODE:
        print(f"[DEBUG] {message}")
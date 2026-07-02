import time
import os
from contextlib import contextmanager

DEBUG_MODE = os.environ.get("DEBUG_MODE", "false").lower() == "true"


@contextmanager
def timer(label: str):
    start = time.time()
    yield
    elapsed = time.time() - start
    if DEBUG_MODE:
        print(f"[DEBUG] {label}: {elapsed:.1f}초")


def log(message: str):
    """DEBUG_MODE가 켜져 있을 때만 터미널에 로그를 출력합니다."""
    if DEBUG_MODE:
        print(f"[DEBUG] {message}")
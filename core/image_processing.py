"""블로그 업로드에 적합하게 이미지 크기/용량을 조정하는 후처리 모듈.
어떤 provider(Gemini/GPT)로 만들었든, 이 함수 하나를 거치면 규격에 맞춰져요.
"""
import io
from PIL import Image

TARGET_WIDTH = 1000       # 900~1200px 권장 범위의 중간값
MAX_FILE_SIZE_MB = 2.0     # 목표 상한
JPEG_QUALITY_START = 90
JPEG_QUALITY_MIN = 40


def optimize_for_blog(image_bytes: bytes) -> bytes:
    """이미지를 블로그 업로드 규격(가로 900~1200px, 2MB 이하)에 맞춰 반환합니다.
    - 가로폭이 TARGET_WIDTH보다 크면 비율 유지한 채 줄임 (작으면 그대로 둠, 억지로 키우면 화질만 나빠지므로)
    - JPEG로 저장하면서, 2MB를 넘으면 품질을 조금씩 낮춰가며 재저장
    """
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")

    if img.width > TARGET_WIDTH:
        ratio = TARGET_WIDTH / img.width
        new_size = (TARGET_WIDTH, int(img.height * ratio))
        img = img.resize(new_size, Image.LANCZOS)

    quality = JPEG_QUALITY_START
    buffer = io.BytesIO()

    while quality >= JPEG_QUALITY_MIN:
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=quality, optimize=True)
        size_mb = buffer.tell() / (1024 * 1024)
        if size_mb <= MAX_FILE_SIZE_MB:
            break
        quality -= 10

    return buffer.getvalue()
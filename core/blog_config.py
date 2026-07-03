import yaml
import os

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "config", "blogs.yaml")
PROMPTS_DIR = os.path.join(os.path.dirname(__file__), "..", "config", "prompts")


def load_blogs():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data.get("blogs", [])


def save_blogs(blogs):
    data = {"blogs": blogs}
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        yaml.dump(data, f, allow_unicode=True, sort_keys=False)


def get_blog(blog_id: str) -> dict | None:
    for b in load_blogs():
        if b["id"] == blog_id:
            return b
    return None


def _prompt_path(blog_id: str, provider: str) -> str:
    return os.path.join(PROMPTS_DIR, f"{blog_id}_{provider}.txt")


def load_prompt(blog_id: str, provider: str) -> str:
    """특정 블로그 + 특정 모델(provider) 조합의 SEO 프롬프트를 읽어옵니다."""
    path = _prompt_path(blog_id, provider)
    if not os.path.exists(path):
        return ""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def save_prompt(blog_id: str, provider: str, text: str) -> None:
    """특정 블로그 + 특정 모델(provider) 조합의 SEO 프롬프트를 저장합니다."""
    os.makedirs(PROMPTS_DIR, exist_ok=True)
    path = _prompt_path(blog_id, provider)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
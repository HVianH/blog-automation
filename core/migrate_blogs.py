import yaml
import shutil
import os

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "config", "blogs.yaml")
BACKUP_PATH = CONFIG_PATH + ".bak"

PROVIDERS = ["gemini", "openai", "anthropic"]


def main():
    if not os.path.exists(CONFIG_PATH):
        print(f"❌ {CONFIG_PATH} 파일을 찾을 수 없습니다.")
        return

    shutil.copy(CONFIG_PATH, BACKUP_PATH)
    print(f"✅ 백업 완료: {BACKUP_PATH}")

    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    changed = 0
    for blog in data.get("blogs", []):
        if "prompts" in blog:
            print(f"⏭️  '{blog['id']}'는 이미 변환되어 있어 건너뜁니다.")
            continue

        old_prompt = blog.pop("seo_prompt", "")
        blog["prompts"] = {provider: old_prompt for provider in PROVIDERS}
        changed += 1
        print(f"🔄 '{blog['id']}' 변환 완료 (3개 모델에 동일한 프롬프트로 복사됨)")

    if changed == 0:
        print("변환할 블로그가 없습니다. (이미 다 변환됨)")
        return

    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        yaml.dump(data, f, allow_unicode=True, sort_keys=False)

    print(f"\n🎉 총 {changed}개 블로그 변환 완료! config/blogs.yaml 저장했습니다.")


if __name__ == "__main__":
    main()
"""
config/blogs.yaml 안에 들어있는 각 블로그의 'prompts' 딕셔너리(모델별 프롬프트)를
config/prompts/{블로그id}_{모델}.txt 개별 파일로 분리하는 일회성 스크립트.

실행 전에 core/migrate_blogs.py 를 먼저 실행해서 blogs.yaml에 'prompts' 구조가
있어야 합니다. (아직 안 하셨으면 이 스크립트를 실행해도 아무 일도 안 일어나요)

실행 방법 (프로젝트 최상위 폴더에서, venv 활성화된 상태):
    python core/migrate_prompts_to_files.py

- 원본 blogs.yaml은 blogs.yaml.bak2 로 자동 백업합니다.
- 각 프롬프트를 config/prompts/{id}_{provider}.txt 파일로 저장합니다.
- blogs.yaml에서는 'prompts' 항목을 제거하고, id/name/tone/target_length만 남깁니다.
"""
import yaml
import shutil
import os

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "config", "blogs.yaml")
PROMPTS_DIR = os.path.join(os.path.dirname(__file__), "..", "config", "prompts")
BACKUP_PATH = CONFIG_PATH + ".bak2"

PROVIDERS = ["gemini", "openai", "anthropic"]


def main():
    if not os.path.exists(CONFIG_PATH):
        print(f"❌ {CONFIG_PATH} 파일을 찾을 수 없습니다.")
        return

    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    blogs = data.get("blogs", [])
    if not any("prompts" in b for b in blogs):
        print("⚠️  'prompts' 구조가 있는 블로그가 없습니다. 먼저 migrate_blogs.py를 실행해주세요.")
        return

    shutil.copy(CONFIG_PATH, BACKUP_PATH)
    print(f"✅ 백업 완료: {BACKUP_PATH}")

    os.makedirs(PROMPTS_DIR, exist_ok=True)

    file_count = 0
    for blog in blogs:
        if "prompts" not in blog:
            print(f"⏭️  '{blog['id']}'는 이미 파일로 분리되어 있어 건너뜁니다.")
            continue

        for provider in PROVIDERS:
            prompt_text = blog["prompts"].get(provider, "")
            file_path = os.path.join(PROMPTS_DIR, f"{blog['id']}_{provider}.txt")
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(prompt_text)
            file_count += 1
            print(f"📄 생성: config/prompts/{blog['id']}_{provider}.txt")

        del blog["prompts"]  # blogs.yaml에서는 이제 제거

    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        yaml.dump(data, f, allow_unicode=True, sort_keys=False)

    print(f"\n🎉 총 {file_count}개 프롬프트 파일 생성 완료!")
    print("blogs.yaml에서도 'prompts' 항목이 제거되어 훨씬 가벼워졌습니다.")


if __name__ == "__main__":
    main()
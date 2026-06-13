import time
import requests
from pathlib import Path

GITHUB_USER = "nadanaya"
VAULT_PATH = r"C:\Users\yeoh0\Brain"
PROJECTS_DIR = Path(VAULT_PATH) / "Projects"
PROJECTS_DIR.mkdir(parents=True, exist_ok=True)


# =========================
# 핵심 함수
# =========================
def sync_github():
    print("GitHub 저장소 동기화 시작...")

    repos_url = f"https://api.github.com/users/{GITHUB_USER}/repos?per_page=100"

    try:
        repos = requests.get(repos_url, timeout=10).json()
    except Exception as e:
        print("GitHub 연결 실패:", e)
        return

    for repo in repos:
        try:
            name = repo["name"]
            description = repo.get("description") or ""
            language = repo.get("language") or "Unknown"
            updated = repo["updated_at"][:10]
            html_url = repo["html_url"]

            readme_text = ""

            for branch in ["main", "master"]:
                readme_url = f"https://raw.githubusercontent.com/{GITHUB_USER}/{name}/{branch}/README.md"

                try:
                    r = requests.get(readme_url, timeout=5)
                    if r.status_code == 200:
                        readme_text = r.text[:5000]
                        break
                except:
                    pass

            content = f"""# {name}

## Repository
{html_url}

## Description
{description}

## Language
{language}

## Last Updated
{updated}

## README
{readme_text}

Tags:
#project
#{language.lower()}
"""

            md_file = PROJECTS_DIR / f"{name}.md"
            md_file.write_text(content, encoding="utf-8")

            print(f"생성 완료: {name}")

        except Exception as e:
            print(f"실패: {repo}")
            print(e)

    print("모든 저장소 동기화 완료")


# =========================
# 실행 루프
# =========================
if __name__ == "__main__":
    while True:
        try:
            sync_github()
        except Exception as e:
            print("전체 동기화 오류:", e)

        time.sleep(600)
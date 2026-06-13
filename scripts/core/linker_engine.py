import re
from pathlib import Path

VAULT = r"C:\Users\yeoh0\Brain"
EXCLUDED_TITLES = {"README", "🗂️ AI Brain OS 지식 지도 (MOC)"}
EXCLUDED_DIRS = {".git", ".obsidian", ".smart-env", "Archive", "__pycache__", "rag_db"}


def safe_print(message):
    print(str(message).encode("cp949", errors="replace").decode("cp949"))


def get_all_note_titles():
    """Vault 내의 모든 마크다운 파일명(제목)을 수집합니다 (길이가 긴 순서대로 정렬)"""
    titles = []
    for f in Path(VAULT).rglob("*.md"):
        if any(part in EXCLUDED_DIRS for part in f.parts):
            continue
        # 파일명에서 확장자 제외한 이름 추가
        if f.stem and f.stem not in EXCLUDED_TITLES:
            titles.append(f.stem)

    # 중요: 긴 단어부터 먼저 매칭해야 부분 매칭 버그가 안 생김
    # (e.g., 'DB 트랜잭션'을 'DB'보다 먼저 매칭해야 함)
    return sorted(list(set(titles)), key=len, reverse=True)


def auto_link_text(text, titles, current_note_title=""):
    """마크다운 본문을 분석하여 안전하게 위키링크([[ ]])를 자동으로 주입합니다."""
    protected_segments = []

    def protect(pattern, source, flags=0):
        def replace(match):
            protected_segments.append(match.group(0))
            return f"__PROTECTED_MARKDOWN_SEGMENT_{len(protected_segments) - 1}__"

        return re.sub(pattern, replace, source, flags=flags)

    # 안전장치 1: 코드 블록(```) 분리하여 보호하기
    text = protect(r"```.*?```", text, flags=re.DOTALL)

    # 안전장치 2: 인라인 코드(`) 분리하여 보호하기
    text = protect(r"`[^`\n]+`", text)

    # 안전장치 3: 기존 위키링크, 마크다운 링크, URL 보호하기
    text = protect(r"\[\[.*?\]\]", text)
    text = protect(r"!?\[[^\]]*?\]\([^)]+?\)", text)
    text = protect(r"https?://[^\s)>\]]+", text)

    # 핵심 치환 로직
    for title in titles:
        # 자기 자신의 이름으로 링크를 거는 뫼비우스의 띠 방지
        if title == current_note_title:
            continue

        # 글자 수가 너무 짧은 단어(1글자 등)는 오탐 방지를 위해 패스
        if len(title) < 2:
            continue

        # 정규식 조건: 이미 [[제목]]이나 [제목] 구조 내부에 있는 단어는 건너뜀
        # 단어 앞뒤가 마크다운 링크 문자가 아닐 때만 치환
        pattern = re.compile(r"(?<!\[)(?<![\w])(" + re.escape(title) + r")(?<!\])(?![\w])(?!\])")
        text = pattern.sub(r"[[\1]]", text)

    # 보호했던 마크다운 구조들 원상 복구
    for i, segment in enumerate(protected_segments):
        text = text.replace(f"__PROTECTED_MARKDOWN_SEGMENT_{i}__", segment)

    return text


def run_auto_linker():
    safe_print("🔗 지식 네트워크 관계 자동 연결(Auto-Linking) 엔진 가동...")
    titles = get_all_note_titles()
    safe_print(f"📚 현재 가상 두뇌가 기억하는 지식 개념: {len(titles)}개")

    linked_count = 0
    for f in Path(VAULT).rglob("*.md"):
        if any(part in EXCLUDED_DIRS for part in f.parts) or f.name.startswith("🗂️"):
            continue

        try:
            old_content = f.read_text(encoding="utf-8")
            # 자동 링크 치환 수행
            new_content = auto_link_text(old_content, titles, current_note_title=f.stem)

            # 변경사항이 있을 때만 파일 쓰기
            if old_content != new_content:
                f.write_text(new_content, encoding="utf-8")
                safe_print(f"🔗 링크 자동 연결 완료: {f.name}")
                linked_count += 1
        except Exception as e:
            safe_print(f"❌ {f.name} 링크 처리 중 에러: {e}")

    safe_print(f"✨ 모든 노트 검사 완료! 총 {linked_count}개의 노트가 새롭게 연결되었습니다.")


if __name__ == "__main__":
    run_auto_linker()

import os
import re
from collections import defaultdict

def analyze_vault(vault_path):
    md_files = []
    for root, dirs, files in os.walk(vault_path):
        if '.obsidian' in root:
            continue
        if '.git' in root:
            continue
        for file in files:
            if file.endswith('.md'):
                md_files.append(os.path.join(root, file))

    titles = {}
    for path in md_files:
        title = os.path.splitext(os.path.basename(path))[0]
        titles[title] = path

    graph = defaultdict(set)
    incoming = defaultdict(set)
    
    link_pattern = re.compile(r'\[\[([^\]|]+)(?:\|[^\]]+)?\]\]')

    for path in md_files:
        source_title = os.path.splitext(os.path.basename(path))[0]
        try:
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                links = link_pattern.findall(content)
                for link in links:
                    link = link.strip()
                    # Resolve link if possible (Obsidian style is often just filename)
                    graph[source_title].add(link)
                    incoming[link].add(source_title)
        except Exception as e:
            print(f"Error reading {path}: {e}")

    # 1. Isolated Notes (Orphans)
    # No outgoing links AND no incoming links (from existing notes)
    orphans = []
    for title in titles:
        has_outgoing = len(graph[title]) > 0
        # Incoming links from notes that exist in our vault
        real_incoming = [src for src in incoming[title] if src in titles]
        if not has_outgoing and not real_incoming:
            orphans.append(title)

    # 2. Under-connected Notes
    # Total links (in + out) <= 1
    under_connected = []
    for title in titles:
        if title in orphans:
            continue
        real_incoming = [src for src in incoming[title] if src in titles]
        total_degree = len(graph[title]) + len(real_incoming)
        if total_degree <= 1:
            under_connected.append(title)

    # 3. Link Recommendations
    # Suggest links based on title matches in content
    recommendations = defaultdict(list)
    for title in titles:
        try:
            with open(titles[title], 'r', encoding='utf-8') as f:
                content = f.read()
                # Simple check for other titles in content
                for other_title in titles:
                    if title == other_title:
                        continue
                    if len(other_title) < 4: # Skip very short titles
                        continue
                    if other_title in content and other_title not in graph[title]:
                        recommendations[title].append(other_title)
        except:
            pass

    # 4. MOC Candidates
    # Notes with many incoming links that don't have "MOC" in title
    moc_candidates = []
    for title in titles:
        if "MOC" in title.upper():
            continue
        real_incoming = [src for src in incoming[title] if src in titles]
        if len(real_incoming) >= 3: # Threshold for MOC candidate
            moc_candidates.append((title, len(real_incoming)))
    moc_candidates.sort(key=lambda x: x[1], reverse=True)

    # Output Report
    print("### 1. 고립된 노트 (Orphans)")
    if orphans:
        for o in orphans:
            print(f"- [[{o}]]")
    else:
        print("없음")

    print("\n### 2. 연결이 부족한 노트 (Under-connected)")
    if under_connected:
        for u in under_connected:
            print(f"- [[{u}]]")
    else:
        print("없음")

    print("\n### 3. 추가하면 좋은 링크 추천")
    found_rec = False
    for title, recs in recommendations.items():
        if recs:
            found_rec = True
            print(f"- [[{title}]]: {', '.join(['[[' + r + ']]' for r in recs])}")
    if not found_rec:
        print("없음")

    print("\n### 4. MOC 후보 추천")
    if moc_candidates:
        for title, count in moc_candidates[:5]:
            print(f"- [[{title}]] ({count}개의 연결됨)")
    else:
        print("없음")

if __name__ == "__main__":
    analyze_vault(".")

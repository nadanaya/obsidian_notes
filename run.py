import subprocess

print("🧠 Sync + Brain 실행")

subprocess.run(["python", "core/ingest.py"])
subprocess.run(["python", "core/brain.py"])
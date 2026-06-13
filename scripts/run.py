import subprocess

print("🚀 Brain System Start")

subprocess.run(["python", "scripts/ingest.py"])
subprocess.run(["python", "scripts/core/brain.py"])
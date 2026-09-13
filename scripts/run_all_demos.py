import subprocess
import sys

import os

def run(cmd):
    print(f"\n==========================================\nRunning: {cmd}\n==========================================")
    env = os.environ.copy()
    env["PYTHONPATH"] = "."
    subprocess.run(cmd, shell=True, check=True, env=env)

def main():
    run("python dataset.py")
    run("python scripts/build_index.py")
    run("python scripts/evaluate_rag.py")
    run("python scripts/evaluate_rag.py --triad")
    run("python scripts/evaluate_agent.py")
    print(f"\n==========================================\nRunning: pytest tests/ -v\n==========================================")
    run("pytest tests/ -v")

if __name__ == "__main__":
    main()

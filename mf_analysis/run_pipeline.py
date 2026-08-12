"""Simple pipeline orchestrator for mf_analysis.

Usage:
  python run_pipeline.py --list
  python run_pipeline.py --run build_report build_presentation
  python run_pipeline.py --run ALL

This is a minimal wrapper that calls the builders in this folder.
"""
import sys
import subprocess
import os

ROOT = os.path.dirname(__file__)

STEPS = {
    "build_report": "python build_report.py",
    "build_presentation": "python build_presentation.py",
}

def list_steps():
    print("Available steps:")
    for k in STEPS:
        print(" -", k)

def run_step(name):
    cmd = STEPS.get(name)
    if not cmd:
        print(f"Unknown step: {name}")
        return 1
    print(f"Running step: {name}")
    return subprocess.call(cmd, cwd=ROOT, shell=True)

def main(argv):
    if "--list" in argv:
        list_steps()
        return
    if "--run" in argv:
        idx = argv.index("--run")
        targets = argv[idx+1:]
        if not targets:
            print("Specify steps or ALL")
            return
        if "ALL" in targets:
            targets = list(STEPS.keys())
        rc = 0
        for t in targets:
            rc |= run_step(t)
        return rc
    print("Usage: --list | --run <steps...>")

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

"""Master execution script for the Bluestock MF capstone project.

This script orchestrates the full project workflow and final deliverables creation.

Usage:
    python run_pipeline.py --list
    python run_pipeline.py --run ALL
    python run_pipeline.py --run generate_datasets data_cleaning db_load eda build_report build_presentation
"""
import os
import subprocess
import sys

ROOT = os.path.dirname(__file__)

STEPS = {
    "generate_datasets": "python generate_datasets.py",
    "data_cleaning": "python data_cleaning.py",
    "db_load": "python db_load.py",
    "eda": "python eda_only.py",
    "build_report": "python build_report.py",
    "build_presentation": "python build_presentation.py",
}


def list_steps():
    """Print the available pipeline steps."""
    print("Available pipeline steps:")
    for step in STEPS:
        print(f" - {step}")


def run_step(step_name):
    """Execute a single pipeline step."""
    command = STEPS.get(step_name)
    if command is None:
        raise ValueError(f"Unknown pipeline step: {step_name}")
    print(f"Running: {step_name}")
    completed = subprocess.run(command, cwd=ROOT, shell=True)
    if completed.returncode != 0:
        raise RuntimeError(f"Pipeline step '{step_name}' failed with exit code {completed.returncode}")


def main(argv):
    if "--list" in argv:
        list_steps()
        return 0

    if "--run" in argv:
        index = argv.index("--run")
        targets = argv[index + 1 :]
        if not targets:
            raise ValueError("Please provide one or more pipeline steps after --run")
        if "ALL" in targets:
            targets = list(STEPS.keys())
        for target in targets:
            run_step(target)
        return 0

    print("Usage: python run_pipeline.py --list")
    print("       python run_pipeline.py --run ALL")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

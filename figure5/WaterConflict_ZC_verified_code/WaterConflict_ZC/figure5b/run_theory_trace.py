from pathlib import Path

from theory_trace_utils import run_pipeline


if __name__ == "__main__":
    results = run_pipeline()
    output_dir = Path(results["output_dir"].iloc[0, 0])
    print("Saved outputs to:")
    print(output_dir)

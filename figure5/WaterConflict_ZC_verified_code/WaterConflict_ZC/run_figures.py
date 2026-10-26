"""Run the two selected Figure 5 modules from their shared archived inputs."""

import os

os.environ.setdefault("MPLBACKEND", "Agg")

from figure5a.plot_radar import run_pipeline as run_figure5a
from figure5b.theory_trace_utils import run_pipeline as run_figure5b


def main():
    run_figure5a()
    run_figure5b()
    print("Completed Figure 5a and Figure 5b. See each module's outputs directory.")


if __name__ == "__main__":
    main()


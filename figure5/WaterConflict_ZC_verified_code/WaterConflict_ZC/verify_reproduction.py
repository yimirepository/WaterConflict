"""Verify event lineage, archived tables, radar values, and readable plot files.

This release helper uses a temporary output directory and leaves packaged
inputs, reference tables, and normal output directories unchanged.
"""

from pathlib import Path
import os
import tempfile
import xml.etree.ElementTree as ET

os.environ.setdefault("MPLBACKEND", "Agg")

import pandas as pd
from PIL import Image

from figure5a.plot_radar import ASPECT_ORDER, MODE_ALIASES, run_pipeline as run_figure5a
from figure5b.theory_trace_utils import run_pipeline as run_figure5b

ROOT = Path(__file__).resolve().parent


def validate_images(output_dir, expected_count):
    pngs = sorted(output_dir.rglob("*.png"))
    svgs = sorted(output_dir.rglob("*.svg"))
    if len(pngs) != expected_count or len(svgs) != expected_count:
        raise AssertionError(f"Expected {expected_count} PNG/SVG pairs in {output_dir}")
    for path in pngs:
        with Image.open(path) as image:
            image.load()
    for path in svgs:
        tree = ET.parse(path)
        if not tree.getroot().tag.endswith("svg"):
            raise AssertionError(f"Invalid SVG: {path}")
    print(f"PASS readable plots: {expected_count} PNG/SVG pairs")


def main():
    upstream = pd.read_excel(ROOT / "provenance" / "event_data_with_clusters.xlsx")
    for discipline in ("hydro", "IR", "sus"):
        labelled = pd.read_excel(
            ROOT / "figure5b" / "data" / f"event_data_relabel_{discipline}.xlsx"
        )
        pd.testing.assert_frame_equal(upstream, labelled[upstream.columns], check_dtype=False)
        print(f"PASS input lineage: {discipline}")

    reference_dir = ROOT / "figure5b" / "reference_tables"
    references = sorted(reference_dir.glob("*.csv"))
    if len(references) != 8:
        raise AssertionError(f"Expected 8 reference tables, found {len(references)}")
    with tempfile.TemporaryDirectory(prefix="waterconflict_verify_") as temporary:
        output_dir = Path(temporary)
        run_figure5b(output_dir=output_dir / "figure5b")
        for reference in references:
            actual = pd.read_csv(output_dir / "figure5b" / "tables" / reference.name)
            expected = pd.read_csv(reference)
            pd.testing.assert_frame_equal(
                actual, expected, check_exact=False, atol=1e-9, rtol=1e-9
            )
            print(f"PASS reference table: {reference.name}")

        result = run_figure5a(output_dir=output_dir / "figure5a")
        actual = pd.read_csv(result["plot_scores_csv"]).set_index("mode")[ASPECT_ORDER]
        expected = pd.read_csv(reference_dir / "radar_card_summary.csv")
        expected["mode"] = expected["mode"].replace(MODE_ALIASES)
        expected = expected.set_index("mode")[ASPECT_ORDER].reindex(actual.index)
        pd.testing.assert_frame_equal(actual, expected, check_exact=True)
        if actual.shape != (6, 6):
            raise AssertionError(f"Expected a 6-by-6 matrix, found {actual.shape}")
        print("PASS Figure 5a: all 36 plotted values equal the archived reference")
        validate_images(output_dir / "figure5a", 1)
        validate_images(output_dir / "figure5b", 4)
    print("PASS: three input lineages, eight reference tables, 36 radar values, five plot pairs.")


if __name__ == "__main__":
    main()


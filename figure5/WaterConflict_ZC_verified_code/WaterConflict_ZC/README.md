# WaterConflict: verified Figure 5 code

This merged release contains one selected offline implementation for each panel: the Figure 5a radar renderer recovered from `feedback.zip`, and the Figure 5b theory-trace pipeline from the previous `WaterConflict_ZC_verified_code.zip`. Required inputs, independent reference tables, English documentation, and a reproduction check are included.

Figure 5a and Figure 5b use one shared 36-score matrix. The feedback archive's `cooperation_mode_scores_v10.txt` is byte-identical to this input; all 36 values also agree with the archived narrative score record after two label changes. The Figure 5b pipeline reproduces all eight archived reference tables.

## Run both panels

Tested with Python 3.12.14. From the extracted `WaterConflict_ZC` directory:

```bash
python -m pip install -r requirements.txt
python run_figures.py
```

Outputs are written to `figure5a/outputs/` and `figure5b/outputs/`. Each panel has PNG and SVG output; Figure 5b also exports supporting plots and tables. After dependencies are installed, execution is offline and needs no API credentials. Rerunning overwrites generated outputs.

To run either module separately:

```bash
python figure5a/plot_radar.py
python figure5b/run_theory_trace.py
```

To verify the packaged version without writing into its normal output directories:

```bash
python verify_reproduction.py
```

The verifier checks the three event-table lineages, all eight independent reference tables, all 36 plotted radar values, and generated PNG/SVG files. The combined runner and verifier are release helpers, not historical analytical source.

## Contents

| Location | Purpose |
| --- | --- |
| `figure5a/plot_radar.py` | Selected radar plotting cell, extracted into a portable script |
| `figure5b/theory_trace_utils.py` | Verified offline theory-trace implementation |
| `figure5b/run_theory_trace.py` | Theory-trace entry point |
| `figure5b/data/` | Required input workbooks and the single shared score matrix |
| `figure5b/reference_tables/` | Eight unchanged archived CSVs for independent comparison |
| `provenance/` | Upstream event checkpoint and Figure 5a score evidence |
| `DATA_NORMALIZATION.md` | English-only workbook metadata and encoding corrections |
| `SELECTION.csv` | Inclusion, deduplication, and exclusion decisions |
| `MANIFEST.json` | File and source-archive SHA-256 inventory |
| `VALIDATION.json` | Completed checks and their limits |

The module READMEs explain the methods and outputs. Dependencies are pinned once in `figure5b/requirements.txt`; the root requirements file references that list. Input paths are resolved relative to the scripts, so the whole directory can be moved as a unit.

## Scope and provenance

Figure 5a is reproduced from archived ratings. Historical notebooks contain LLM-assisted score elicitation from machine-learning summaries, but the supplied files do not establish the exact API run or a deterministic RF/SHAP-to-rating transformation. See `provenance/FIGURE5A_SCORE_PROVENANCE.md`.

The recovered radar renderer uses colored title bands and a bottom legend. The manuscript uses white title bands, a top legend, and different spacing. The final manuscript assembly step is not supplied; this release preserves the recovered plotting source and the 36 manuscript values, rather than claiming pixel-identical final artwork. Font substitution can also change placement when Arial is unavailable.

Figure 5b maps existing disciplinary cluster labels to theories and final modes. It does not rerun event embedding, clustering, LLM relabelling, or online literature verification. The three original disciplinary workbooks are byte-identical across the two earlier archives, and their original event fields match the supplied upstream checkpoint. Published workbook copies have documented metadata and text-encoding normalization; analytical fields and all eight numerical outputs are preserved.

This is the verified Figure 5 contribution, not the complete manuscript codebase. Initial embedding/FAISS processing, final six-mode one-hot construction, SSP fitting/recommendation calculations, and exact upstream model runs remain outside its verified scope.

## Repository placement

The repository manager can upload this directory under `figure5/zc/` in `yimirepository/WaterConflict` and run the commands from there. No live credentials, online API clients, duplicate executable versions, bytecode caches, or historical output variants are included. No new license is asserted by this package; the repository manager should apply the project's agreed license.


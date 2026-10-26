# Figure 5b theory trace

This module maps disciplinary cooperation clusters to six final cooperation modes and produces the theory–cluster–mode alluvial diagram used for the Figure 5b analysis. It also produces two heatmaps, a discipline-support composition plot and supporting tables.

## Run

Tested with Python 3.12.14. From this directory:

```bash
python -m pip install -r requirements.txt
python run_theory_trace.py
```

The pinned dependencies record the environment used to test this release. No API credentials or network connection are needed after installing the dependencies. Results are written to `outputs/tables/` and `outputs/figures/`. Rerunning replaces files in these output directories. The plots request Arial; Matplotlib substitutes another font when Arial is unavailable, which can change text placement.

## Inputs and outputs

The required inputs are in `data/`:

- `event_data_relabel_hydro.xlsx`, `event_data_relabel_IR.xlsx` and `event_data_relabel_sus.xlsx`: previously labelled disciplinary event tables, including cluster names and descriptions.
- `latest_theory_reference_verification.xlsx`: theory-name updates and display labels/order.
- `cooperation_mode_scores.txt`: the existing six-criterion scores used in summary tables.

The program exports eight CSV tables, a workbook containing the same tables, and PNG/SVG versions of four plots. `reference_tables/` contains the eight corresponding CSVs from the supplied archive for comparison.

## Method and scope

The trace uses TF–IDF unigram/bigram cosine similarity weighted by 0.7, plus keyword-overlap terms weighted by 0.3. It retains the two highest-scoring links per source. Alluvial flow widths combine normalized theory-to-cluster and cluster-to-mode link weights with cluster event counts. These are weighted support values, not counts of distinct events. The theory-to-mode summary also adds a direct similarity term multiplied by 75. Theory descriptions, keywords and cluster-family mappings are defined in the source code.

This is the offline theory-mapping stage applied to existing cluster labels. It does not rerun the original event embedding, clustering, LLM labelling or online literature verification. It does not fit the Random Forest/SHAP model or calculate the six quantitative criterion scores. Those scores are loaded unchanged from `cooperation_mode_scores.txt`. The separate `../figure5a/plot_radar.py` module now draws the recovered six-card radar panel from the same score input.

## Provenance and release changes

Source: the supplied `thoery.zip`, under `thoery/`. The executable files are `theory_trace_utils.py` and its command-line entry point `run_theory_trace.py`. The notebook was another entry point to the same pipeline and is omitted to avoid duplication. Online reference-verification tools, caches and alternative figure versions are outside this module.

Only input/output path handling was changed in the analytical source: inputs now resolve from `data/`, and the default output directory is `outputs/`. Scientific formulas, catalogues, scores, parameters, plot settings and output names were preserved. The score file and reference CSVs remain byte-identical to the originals. Workbook metadata and pre-existing text-encoding errors in narrative event fields were normalized for this English-only release; see `../DATA_NORMALIZATION.md`. Analytical fields are unchanged.

## Validation

The full packaged pipeline was run in the pinned environment with output directed to a separate temporary directory. All eight regenerated CSV tables matched the archived references with numeric tolerance of 1e-9. Four PNG plots and four SVG plots were generated successfully. The original source archives were not modified.

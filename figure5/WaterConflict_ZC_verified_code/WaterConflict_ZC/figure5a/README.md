# Figure 5a: cooperation-mode radar panel

This is the single selected offline Figure 5a plotting implementation recovered from `feedback.zip`: `cooperation_radar_v6.ipynb`, code cell 7 using zero-based numbering (the eighth notebook cell). The other radar notebooks and earlier plotting cells are historical alternatives and are not included.

## Input and scope

The renderer reads `../figure5b/data/cooperation_mode_scores.txt`, shared with Figure 5b. This file is byte-identical to `cooperation_mode_scores_v10.txt` used by the recovered plotting cell. It contains 36 supplied scores: six cooperation modes by six aspects. These values match the labels in manuscript Figure 5a.

The code reproduces the panel from these fixed scores. It does not regenerate, infer, or independently validate how the scores were originally assigned. The archived v13 scoring narrative agrees with these 36 values after two mode-label changes, but the exact API run that produced the matrix is unverified. Online scoring cells, API configuration, credentials, and redundant copies of the score matrix are excluded.

## Run

From the package root:

```bash
python -m pip install -r figure5b/requirements.txt
python figure5a/plot_radar.py
```

To select a destination:

```bash
python figure5a/plot_radar.py --output-dir /path/to/output
```

The default input is resolved relative to this module, so execution does not require a particular working directory. An optional `--scores PATH` can select another file in the same format; it must contain the six expected modes and six expected aspects with finite values in the inclusive range 0 to 6. Malformed inputs fail explicitly.

Outputs:

- `cooperation_modes_radar_cards_panel.png`: six-card panel at 600 dpi.
- `cooperation_modes_radar_cards_panel.svg`: vector panel with editable text.
- `plot_scores.csv`: the exact 36 values passed to the plotting functions, ordered by panel and aspect.

The source alias `Collaborative Planning & Adaptation Strategies` is retained in the plotted-value CSV; it refers to `Collaborative Planning and Adaptation Strategies` in the shared score file.

## Provenance and limits

The recovered cell has SHA-256 `53234e4fe9f0ad47db843bc0ea8fe0b1fc5c43dde1d416e9609da4018e753cfe`.

The drawing code, panel order, aspect order, colors, limits, score values, and source layout are retained. Packaging changes add portable paths, a command-line entry point, isolated Matplotlib settings, explicit input validation, returned output paths, and the plotted-value CSV. Validation replaces the notebook's silent zero filling and clipping; it leaves all supplied valid scores unchanged.

The source renderer and archived card-panel output use colored title bands and a bottom aspect legend. The manuscript figure uses white title bands, a top legend, and different spacing. The manuscript assembly step that made those layout changes is not present in the recovered code. This package therefore reproduces the recovered plotting source and all 36 manuscript values, but does not claim a pixel-identical reconstruction of the final manuscript artwork. The combined Figure 5 panel labels and Figure 5b placement are not generated here.

The recovered card layout has crowded title and A-axis labels, also visible in its archived output; these source layout settings are retained. Font availability can also affect spacing. The retained font preference is Arial, followed by Helvetica, DejaVu Sans, and Liberation Sans.

## Python API

```python
from pathlib import Path
from figure5a.plot_radar import run_pipeline

result = run_pipeline(output_dir=Path("outputs/figure5a"))
# result["scores"]: nested dictionary of the actual plotted values
# result["plot_scores_csv"]: CSV path
# result["figures"]: {"png": Path, "svg": Path}
```

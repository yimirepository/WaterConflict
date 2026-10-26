# Figure 5a score provenance

## Verified final input

Both figure panels use `figure5b/data/cooperation_mode_scores.txt` as their single score input. Its bytes are identical to `cooperation_mode_scores_v10.txt` in `feedback.zip` and to `cooperation_mode_scores.txt` in the previously verified theory package.

The archived narrative record `cooperation_mode_scores_v13.txt` matches all **36 of 36** final numeric scores after these label substitutions:

- `Affordable` becomes `Supportive`.
- `Collaborative River Basin Planning` becomes `Collaborative Planning and Adaptation Strategies`.

That English narrative record is preserved without modification as `figure5a_score_rationale.txt` in this directory. It is historical evidence, not an additional runtime input or independently validated methodological justification. Alternative checkpoints, including `v10_2`, `v11`, and `v12`, do not contain the final matrix.

## Limits of the generation evidence

The scoring cells in `cooperation_radar_v5.ipynb` and `cooperation_radar_v6.ipynb` are identical. They ask an Azure/OpenAI deployment to assign ratings using `feature3.txt`, its feature metrics and rankings, and domain-based inference. They do not implement a deterministic RF/SHAP-to-rating transformation. The supplied `radar data_241124.docx` records the same six-aspect metrics and rankings as the feature summary.

The scorer truncates the 7,311-character feature summary to its first 2,000 characters, followed by an ellipsis. This ends within the Facilitative section, before Stress-relieving, Complementary, Preventive, and Prescriptive. The matching narrative record explicitly uses inference where direct evidence is unavailable. The code also appends a default rating of 3.0 when an aspect is absent from a model response.

The exact generation run cannot be established from the saved files. Both notebook scoring cells and their captured outputs target `v12` with temperature 0. The `cooperation_radar_v5.html` export instead contains code targeting `v10` with temperature 0.7, while its captured output reports `v11`. No supplied scoring code explicitly writes `v13`.

The Figure 5a plotting source and matching score record have been located. Reproduction from the archived score matrix is supported; reproducible regeneration of those ratings from upstream RF/SHAP results remains unverified. Executable online scoring drafts are excluded from this release.

## Source SHA-256 references

These hashes refer to the original source bytes in `feedback.zip`, before any release extraction or adaptation.

| Source | SHA-256 |
| --- | --- |
| `cooperation_mode_scores_v10.txt` | `76d3a2b146b26a1cfcae877e22b6b37c4e3240877591b4e431539b7242e2b226` |
| `cooperation_mode_scores_v13.txt` | `4d107af2dc812fa3db61f6652a11e0b833d9ba9bf31c38bc09610048ed47447f` |
| `feature3.txt` | `c030e51dafad4e94b9ba1ec0cbaf1dd1ee84e79d4b2a494e998908d2953f8e6f` |
| `cooperation_radar_v5.ipynb` | `b75c09113bfe4fb92b908a75104fafd85a724bdc0cdb526498d15cee9e6e8e15` |
| `cooperation_radar_v6.ipynb` | `92cc807f15ade75593f935802429aa77be5c624e363bca26a1a7d174950e3e36` |
| `cooperation_radar_v5.html` | `f9e467dfeb4d67dc03fc5484612bf8dad9f2e4a06923df34399123dae5626211` |
| `radar data_241124.docx` | `8954c129732c7dce52582f83d1e65ac0bbfc1c6154671d3d84977427f120d121` |

The shared release score file has the same hash as `v10`. The preserved rationale has the same hash as `v13`.

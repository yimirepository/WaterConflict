# Data normalization for the merged release

The XLSX files in this release are normalized copies of the supplied inputs. Original source archives and earlier release files were not modified. The changes below make workbook labels and metadata readable in English and remove corrupted CJK characters from existing English event narratives. They do not create or regenerate research observations.

## Narrative text repairs

The same 31 cells in column D of each of the following workbooks contained pre-existing encoding corruption:

- `provenance/event_data_with_clusters.xlsx`
- `figure5b/data/event_data_relabel_hydro.xlsx`
- `figure5b/data/event_data_relabel_IR.xlsx`
- `figure5b/data/event_data_relabel_sus.xlsx`

For unambiguous fragments, the original characters were encoded as GBK and decoded as UTF-8. This is a reversible byte-level correction. The transformations are recorded below using Unicode code points so that the documentation itself contains no CJK characters.

| Original code points | Restored code points | Restored character names |
| --- | --- | --- |
| U+8305 | U+00E9 | LATIN SMALL LETTER E WITH ACUTE |
| U+4E48 | U+00F4 | LATIN SMALL LETTER O WITH CIRCUMFLEX |
| U+832B | U+00E3 | LATIN SMALL LETTER A WITH TILDE |
| U+5E3D | U+00F1 | LATIN SMALL LETTER N WITH TILDE |
| U+8C29 | U+00E1 | LATIN SMALL LETTER A WITH ACUTE |
| U+679A | U+00F6 | LATIN SMALL LETTER O WITH DIAERESIS |
| U+7709 | U+00FC | LATIN SMALL LETTER U WITH DIAERESIS |
| U+9225, U+6A9A | U+2019, U+0073 | RIGHT SINGLE QUOTATION MARK, LATIN SMALL LETTER S |
| U+8D38 | U+00F3 | LATIN SMALL LETTER O WITH ACUTE |
| U+62E2 | U+00A3 | POUND SIGN |
| U+9225, U+6A6D | U+2019, U+004F | RIGHT SINGLE QUOTATION MARK, LATIN CAPITAL LETTER O |
| U+94C6 | U+00ED | LATIN SMALL LETTER I WITH ACUTE |
| U+81B7 | U+010D | LATIN SMALL LETTER C WITH CARON |
| U+811F | U+00C7 | LATIN CAPITAL LETTER C WITH CEDILLA |

One ambiguous fragment, `U+9227` followed by `?`, could not be reversed safely. It is stored literally as the ASCII text `\u9227?` in cell `D1688`. All following text, including `.6 million`, is unchanged. The release does not infer a currency symbol, amount, or missing digit. This fragment occurs twice within that narrative cell in each of the four workbooks.

Affected worksheet rows (including the header as row 1):

`19, 258, 265, 285, 300, 363, 422, 427, 437, 518, 540, 545, 555, 556, 565, 574, 581, 618, 664, 707, 869, 941, 1208, 1369, 1420, 1453, 1565, 1678, 1680, 1688, 1695`.

No CJK text was found in the cluster labels or cluster descriptions used by the pipeline. Those cells were not changed.

## Workbook metadata

Built-in style names, theme labels, worksheet-category metadata, and East Asian font names were converted to their English identifiers. Examples include `Normal`, `Heading 1`, `Accent 1`, `Worksheets`, `SimSun`, `PMingLiU`, `DengXian`, and `Yu Gothic`. Stored absolute source-folder paths were removed. Sheet names, sheet order, worksheet dimensions, style indexes, numerical values, formulas, and workbook relationships were preserved. No shared-string entries were deleted.

`latest_theory_reference_verification.xlsx` received metadata changes only; every cell value is unchanged.

## Validation

- All five workbooks open successfully after normalization.
- All XML and relationship parts were parsed, including numeric character references; no CJK characters remain in their decoded text or attributes.
- Each event workbook still contains 1,713 records plus one header row.
- Exactly 31 narrative cells changed in each event workbook, solely by the transformations documented above. Every other cell value is identical to its source.
- The first five columns remain identical across the normalized checkpoint and all three disciplinary input workbooks.
- Numeric values, event identifiers, time values, cluster assignments, cluster names, and cluster descriptions remain unchanged.
- No worksheets, records, or columns were added or removed.

## File hashes

Original hashes identify the supplied release inputs before these changes. Normalized hashes identify the copies included in this merged release.

| File | Original SHA-256 | Normalized SHA-256 |
| --- | --- | --- |
| `provenance/event_data_with_clusters.xlsx` | `1a8626c910539bb59c41ee9fddb8bbe1784c9501ba5d9043a241669c711fcd0d` | `186ce8e1e015a065dc5229a93f0cb0fafe292c34395278102f4653dd092a893f` |
| `figure5b/data/event_data_relabel_sus.xlsx` | `f1f2f7f0b2f295ed4116645fd65cdc68d4a5799ad2c3fc3878762e5a040667dd` | `8caa57acb95e133d55aa4482bd566d8b9ec19b1364617021b132b2be20b935ca` |
| `figure5b/data/latest_theory_reference_verification.xlsx` | `9950264431f46a29457dd023f9e58ced0bf8e0500ce4f8b4c8e608f638a08f7a` | `2a786c11f756dd3c2dada127036f58f6479c614364bef1d1a9819d92ee98d9a6` |
| `figure5b/data/event_data_relabel_hydro.xlsx` | `41b92461871e37e2950d0f8ea8b87e314fdc92acf06984f9cbbd37dceaee5ec1` | `36dc795397602ef47cff80ec15745320a4c89c5f86041b153d3aa2bfc95ad1b1` |
| `figure5b/data/event_data_relabel_IR.xlsx` | `0dfa24a29cb492d43dd842c65fcd2c9be1afef6b4cafd7c8930ff3383658b5d3` | `7aa37e023cfb83b5fe1e9d49ee774af2e898c8dd54b9eb964047e116fedc8b85` |

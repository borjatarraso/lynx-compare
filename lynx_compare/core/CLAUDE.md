# lynx_compare/core/ — domain logic & metadata

Pure comparison logic and project constants. **No terminal, GUI, file, or
network I/O** lives here, and nothing in `core` imports from `render`,
`interfaces`, `tui`, or `gui`. It depends only on the external
`lynx-investor-core` types (`lynx.models.AnalysisReport`) and the package-level
version constants.

## Modules & public interface

- **`engine.py`** — binary (A vs B) comparison.
  - Dataclasses: `MetricResult`, `SectionResult`, `Warning`, `ComparisonResult`.
  - `compare(report_a, report_b) -> ComparisonResult` — the core entry point.
  - `fmt_value(...)` — formats a raw metric value for display (no Rich markup).
  - Lookup tables: `METRIC_DIRECTION`, `METRIC_LABELS`, `SECTIONS`
    (plus private helpers `_INFO_ONLY`, `_ordinal_value`).
- **`multi.py`** — N-way (2+) comparison built on the same tables.
  - Dataclasses: `MultiMetricResult`, `MultiSectionResult`, `MultiComparisonResult`.
  - `compare_many(...)`, `compare_many_reports(...)`.
- **`about.py`** — metadata constants (`APP_NAME`, `DEVELOPER`,
  `DEVELOPER_EMAIL`, `LICENSE_NAME`, `LICENSE_TEXT`) and the easter egg
  (`about_text`, `about_lines`, `check_easter_egg`, `easter_egg_text`).

## Conventions

- A metric's ranking comes from `METRIC_DIRECTION`: `higher`, `lower`,
  `lower_positive`, or `abs_lower`. Informational-only metrics
  (`_INFO_ONLY`) are never scored. Add new metrics by extending these tables
  plus `METRIC_LABELS` — keep keys consistent across all three.
- `winner` fields use the string codes `"a"`, `"b"`, `"tie"`, `"na"`.
- Keep this layer free of presentation concerns: return data, never print.
- These modules are also reachable at the legacy paths
  `lynx_compare.engine` / `.multi` / `.about` via shims — edit them **here**.

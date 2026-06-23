# Real demo: audits on real Turkish Hugging Face resources

Run date: 2026-06-23




Install command used:

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install -e ".[dev]"
```

Tool check:

```bash
tr-card-radar --help
tr-card-radar audit --help
```

## Hugging Face source verification

These model repositories were verified with `huggingface_hub.HfApi().model_info(...)` before audit runs:

| Repo | Verified SHA | Last modified from HF API | Selected for audit |
|---|---:|---|---|
| `ytu-ce-cosmos/turkish-gpt2` | `683453f58f3615e597c2608c710b82ed96b74f90` | `2024-05-07 18:46:44+00:00` | yes |
| `asafaya/kanarya-750m` | `b27eef7948d4570e536ef0fa01b1c141fcd77f5a` | `2024-03-17 14:10:37+00:00` | yes |
| `asafaya/kanarya-750m-chat` | not found by HF API | n/a | no |
| `asafaya/kanarya-2b-chat` | not found by HF API | n/a | no |

`asafaya/kanarya-2b` was also found, but the three selected repositories above were enough for the requested 2 to 3 real Turkish HF sources.

## Commands actually run

```bash
tr-card-radar audit Trendyol/Trendyol-LLM-7b-chat-v1.0 --repo-type model --out-dir examples/real_reports/trendyol-llm-7b-chat-v1.0
tr-card-radar audit ytu-ce-cosmos/turkish-gpt2 --repo-type model --out-dir examples/real_reports/ytu-ce-cosmos-turkish-gpt2
tr-card-radar audit asafaya/kanarya-750m --repo-type model --out-dir examples/real_reports/asafaya-kanarya-750m
```

Each command exited with status `0`. Each `command_output.txt` file contains the command, UTC start and end timestamps, exit status, and the real CLI stdout and stderr captured during that run.

## Generated report files

```text
examples/real_reports/asafaya-kanarya-750m/command_output.txt
examples/real_reports/asafaya-kanarya-750m/report.json
examples/real_reports/asafaya-kanarya-750m/report.md
examples/real_reports/asafaya-kanarya-750m/reuse_warnings.tsv
examples/real_reports/trendyol-llm-7b-chat-v1.0/command_output.txt
examples/real_reports/trendyol-llm-7b-chat-v1.0/report.json
examples/real_reports/trendyol-llm-7b-chat-v1.0/report.md
examples/real_reports/trendyol-llm-7b-chat-v1.0/reuse_warnings.tsv
examples/real_reports/ytu-ce-cosmos-turkish-gpt2/command_output.txt
examples/real_reports/ytu-ce-cosmos-turkish-gpt2/report.json
examples/real_reports/ytu-ce-cosmos-turkish-gpt2/report.md
examples/real_reports/ytu-ce-cosmos-turkish-gpt2/reuse_warnings.tsv
```

## Actual report summaries

| Repo | Checked at | Blockers | Warnings | Info | Warning checks |
|---|---|---:|---:|---:|---|
| `Trendyol/Trendyol-LLM-7b-chat-v1.0` | `2026-06-23T12:31:46.282504Z` | 0 | 0 | 1 | none |
| `ytu-ce-cosmos/turkish-gpt2` | `2026-06-23T12:31:47.633132Z` | 0 | 2 | 1 | `missing_base_model`, `missing_limitations` |
| `asafaya/kanarya-750m` | `2026-06-23T12:31:48.858848Z` | 0 | 1 | 1 | `missing_base_model` |

The info item in each report is:

```text
This report is a metadata warning aid and does not provide legal advice.
```

## README demo block candidate

````markdown
## Real Turkish model card demo

The following reports were generated from live Hugging Face model repositories on 2026-06-23:

```bash
tr-card-radar audit Trendyol/Trendyol-LLM-7b-chat-v1.0 --repo-type model --out-dir examples/real_reports/trendyol-llm-7b-chat-v1.0
tr-card-radar audit ytu-ce-cosmos/turkish-gpt2 --repo-type model --out-dir examples/real_reports/ytu-ce-cosmos-turkish-gpt2
tr-card-radar audit asafaya/kanarya-750m --repo-type model --out-dir examples/real_reports/asafaya-kanarya-750m
```

Generated files:

- `examples/real_reports/trendyol-llm-7b-chat-v1.0/report.md`
- `examples/real_reports/ytu-ce-cosmos-turkish-gpt2/report.md`
- `examples/real_reports/asafaya-kanarya-750m/report.md`

Summary:

| Repo | Blockers | Warnings | Info |
|---|---:|---:|---:|
| `Trendyol/Trendyol-LLM-7b-chat-v1.0` | 0 | 0 | 1 |
| `ytu-ce-cosmos/turkish-gpt2` | 0 | 2 | 1 |
| `asafaya/kanarya-750m` | 0 | 1 | 1 |

These reports are metadata warning aids. They are not legal advice, clinical validation, model rankings, or reuse permission.
````

## Push status

No commit was made and no push was performed.

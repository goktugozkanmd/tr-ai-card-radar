# tr-ai-card-radar

`tr-ai-card-radar` audits public Hugging Face model and dataset cards for Turkish AI resources and writes small, reproducible metadata reports.

It checks card metadata, card text, repository tags, access flags, and reuse warning signals. It does not download protected dataset rows and it does not decide whether a dataset or model can legally be reused.

## Short Turkish summary

`tr-ai-card-radar`, Türkçe AI model ve veri setleri için Hugging Face kartlarını kontrol eden küçük bir açık kaynak araçtır. Lisans, dil, kaynak, erişim durumu, kullanım amacı ve sınırlamalar gibi alanları raporlar. Hukuki karar vermez, klinik doğrulama iddiası taşımaz, veri satırı indirmez.

## Why this exists

Turkish AI resources are spread across model cards, dataset cards, repository metadata, papers, and discussions. A small audit tool helps maintainers and users notice missing or inconsistent metadata before copying data, publishing reports, or comparing systems.

This project is built from a clinician led perspective: evidence discipline, provenance, scope limits, and reproducible review artifacts matter. The tool is not a medical device, not a clinical validation tool, and not a model quality leaderboard.

## What it checks

For model and dataset repositories, the first version checks:

- missing license metadata
- possible mismatch between Hub metadata license and card prose license mentions
- missing language metadata
- gated access flags
- missing model base model metadata
- missing model intended use section
- missing model limitations section
- missing dataset source or creation process statement
- missing dataset split or file surface notes when visible from public metadata
- card text availability

The checks are intentionally conservative. They produce warnings for human review.

## What it does not do

- It does not download protected dataset rows.
- It does not bypass gated repository access.
- It does not provide legal advice.
- It does not certify a license.
- It does not rank models.
- It does not claim clinical validation, safety, deployment readiness, or institutional endorsement.
- It does not decide whether a card is complete enough for publication.
- It does not open upstream pull requests or discussions.

## Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Audit one repository

```bash
tr-card-radar audit Trendyol/Trendyol-LLM-7b-chat-v1.0 --repo-type model --out-dir reports/trendyol-7b
```

For dataset repositories:

```bash
tr-card-radar audit emre/TARA_Turkish_LLM_Benchmark --repo-type dataset --out-dir reports/tara
```

Use `--repo-type auto` only when you are not sure whether the resource is a model or dataset repository:

```bash
tr-card-radar audit alibayram/turkish_mmlu --repo-type auto --out-dir reports/turkish-mmlu
```

## Audit a resource list

```bash
tr-card-radar audit-list examples/resources.yaml --out-dir reports
```

This writes:

- `report.json`
- `report.md`
- `reuse_warnings.tsv`

For `audit-list`, each repository receives its own output directory under the selected report directory.

## Optional Hugging Face token

For public repositories, no token is usually needed. If a repository requires authenticated metadata access and you already have permission, set:

```bash
export HF_TOKEN="..."
```

The tool does not request access, bypass access controls, or download protected rows.

## Example resource list

See `examples/resources.yaml`. The initial list is based on checked Turkish AI resources from 2026 06 23. Before publishing any generated report, rerun the audit and manually inspect the source pages because cards and metadata can change.

## Output interpretation

Warnings are grouped by severity:

- `blocker`: do not present the resource as cleared for reuse until this is resolved or explicitly explained.
- `warning`: human review needed before relying on the metadata.
- `info`: useful context, not necessarily a problem.

The report is a card quality and provenance aid. It is not a legal opinion and not an endorsement of any repository.

## Scope for v0.1

In scope:

- Hugging Face model cards
- Hugging Face dataset cards
- public card metadata
- public card text
- public repository tags
- reusable JSON, Markdown, and TSV reports
- tests with mocked API snapshots

Out of scope:

- downloading dataset rows
- private or patient data
- clinical validation
- model performance scoring
- leaderboard claims
- automated upstream pull requests
- legal clearance

## Suggested first public command

```bash
tr-card-radar audit-list examples/resources.yaml --out-dir reports/first-run
```

Review the generated warnings before publishing anything.

## Maintainer note

This repository is intended to make Turkish AI metadata easier to inspect. It should stay small, reproducible, and careful with claims.

## Example audits on real Turkish AI resources

Real, reproducible audit outputs are included under `examples/real_reports/` for three verified public Turkish Hugging Face models:

- `Trendyol/Trendyol-LLM-7b-chat-v1.0`
- `ytu-ce-cosmos/turkish-gpt2`
- `asafaya/kanarya-750m`

Each folder contains `report.json`, `report.md`, `reuse_warnings.tsv`, and the captured command output. See `docs/REAL_DEMO.md` for the run commands and Hugging Face source verification (verified repo SHAs). These are metadata-audit examples only — no model ranking, no clinical or legal claims.

# Contributing

Thanks for helping improve `tr-ai-card-radar`.

This project is intentionally small. Good contributions make card audits clearer, more reproducible, or safer to interpret.

## Ground rules

- Do not add copied dataset rows.
- Do not add private, patient, or sensitive data.
- Do not claim legal clearance.
- Do not claim clinical validation.
- Do not add model rankings.
- Do not add automated upstream PR behavior.
- Do not hard code claims about a resource unless the source was checked and dated.

## Adding a Turkish AI resource

Open an issue or pull request with:

- Hugging Face repository id
- repository type: `model` or `dataset`
- public source URL
- why it belongs in the Turkish AI resource list
- checked date
- any known access limitation

If the repository is gated, do not paste protected content.

## Adding a check

A check should return a warning, not a final judgment. Include:

- a clear check id
- severity: `blocker`, `warning`, or `info`
- the evidence field used
- a test with mocked metadata
- wording that does not overclaim

## Local setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest
ruff check .
```

## Pull request checklist

- Tests pass.
- No protected dataset rows were added.
- No private data was added.
- Report wording says "warning" or "needs review" where the tool cannot decide.
- README scope and limitations still match the code.
- Any new external claim has a checked source and date.

# Release Checklist

Before a public release:

- Check GitHub repository name availability.
- Check PyPI package name availability before publishing to PyPI.
- Check Hugging Face namespace and optional report dataset name availability before creating any Hub repository.
- Run tests.
- Run `tr-card-radar audit-list examples/resources.yaml --out-dir reports/release-candidate`.
- Manually inspect generated warnings.
- Confirm no protected dataset rows were downloaded or committed.
- Confirm README does not include model ranking or clinical validation claims.
- Confirm resource metadata claims include checked date or are generated live by the tool.
- Confirm generated reports say they are not legal advice.
- Tag only after reviewing the generated report bundle.

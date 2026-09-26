# Release validation

The repository cleanup was checked locally on 2026-09-26:

- Python syntax compilation for all files under `scripts/`.
- Ten documented experiment, aggregation, QA-preparation, and human-demo entry points returned successful `--help` output.
- Unit tests verified media-path conversion, annotation preservation, missing-media reporting, and rejection of invalid output/path traversal.
- One public Hugging Face profile was downloaded and prepared; the RQ3 loader read 36 sessions and 128 QAs from it. Only the JSON was downloaded for this check, so missing media were correctly reported.
- The static demo's HTML, JavaScript, CSS, five JSON files, and 60 referenced media URLs returned HTTP 200 locally. Three referenced audio files missing from the imported repository were restored from the original project.
- JavaScript syntax and repository diff whitespace checks passed.

These checks do not reproduce paper scores. Full inference, external memory backends, GPU embedding, provider credentials, and complete media downloads were not exercised. CLI checks used the existing research environment, not a fresh dependency installation.

To run the local unit tests:

```bash
python -m unittest discover -s tests -v
```

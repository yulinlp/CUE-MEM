# CUE-Mem static demo

The live project website is https://reichenbach1854-hash.github.io/CUE-Mem/.

From the repository root, run:

```bash
python -m http.server 8000 --bind 127.0.0.1 --directory docs
```

Open http://127.0.0.1:8000. The demo includes selected text, image, and audio examples, construction steps, and experiment summaries. It requires no API key or Python dependencies beyond the standard library.

For GitHub Pages, select the `main` branch and `/docs` directory in repository Settings → Pages. This is optional; the project website above remains the primary demo.

The interactive human-evaluation server is a separate application in `scripts/human_baseline_demo/`; see the [main README](../README.md).

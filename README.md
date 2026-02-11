# Horse Racing Predictor

A Streamlit app for ingesting Brisnet race card files (`CSV`, `DRF`, `DRF2`, `DRF3`, `DRF4`) and historical results, generating proprietary speed figures, and tracking horse-level and track-level trends.

## Features

- Upload multiple race card files in Brisnet-like formats.
- Upload historical result files to infer track trends.
- Weighted speed-figure model that scores each horse from available metrics.
- Track analyzer with US track dropdown.
- SQLite horse database that stores generated speed figures by horse.

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy to Render

This repository includes `render.yaml` configured for web deployment.

## Runtime Requirements

- Python dependencies are defined in `requirements.txt`.
- Ruby version is pinned to `3.4.4` via `.ruby-version` (and mirrored in `render.yaml` as `RUBY_VERSION`) for Render/runtime consistency.

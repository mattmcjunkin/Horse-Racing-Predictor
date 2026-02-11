# Horse Racing Predictor

A Streamlit app for ingesting Brisnet race card files (`CSV`, `DRF`, `DR2`, `DR3`, `DR4`) and historical results, generating proprietary speed figures, and tracking horse-level and track-level trends.

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


## Ruby compatibility

This repository now includes Ruby support artifacts so the project is usable from Ruby environments as well:

- `.ruby-version` is pinned to `3.4.4`.
- `Gemfile` defines Ruby dependencies.
- `scripts/analyze_card.rb` provides a Ruby CLI to compute proprietary speed figures from a CSV card file.

Example:

```bash
bundle install
ruby scripts/analyze_card.rb sample_card.csv dr4
```

# CineMatch

CineMatch is a Flask movie recommendation website. It uses a precomputed similarity matrix and TMDB poster data to recommend movies from the TMDB 5000 dataset.

## Run Locally

```bash
pip install -r requirements.txt
python app_flask.py
```

Open `http://localhost:5000`.

## Deploy

The app is ready for platforms such as Render or Railway with:

- build command: `pip install -r requirements.txt`
- start command: `gunicorn app_flask:app`

Set these environment variables in the deployment dashboard:

- `TMDB_API_KEY`: your TMDB API key
- `MOVIE_DICT_URL`: direct download URL for `movie_dict.pkl`
- `SIMILARITY_URL`: direct download URL for `similarity.pkl`

`similarity.pkl` is larger than GitHub's normal file limit, so keep it outside the repo and provide it with `SIMILARITY_URL`.

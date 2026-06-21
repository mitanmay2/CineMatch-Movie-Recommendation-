# Quick Deploy

1. Upload this project to GitHub.
2. Upload `movie_dict.pkl` and `similarity.pkl` to a file host that supports direct downloads.
3. Create a new Render Web Service from the GitHub repo.
4. Use `pip install -r requirements.txt` as the build command.
5. Use `gunicorn app_flask:app` as the start command.
6. Add `TMDB_API_KEY`, `MOVIE_DICT_URL`, and `SIMILARITY_URL` in environment variables.
7. Deploy.

Note: `similarity.pkl` is about 185 MB, so it cannot be uploaded to GitHub as a normal file.

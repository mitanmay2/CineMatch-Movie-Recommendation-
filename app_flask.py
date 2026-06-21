from flask import Flask, render_template, request, jsonify
import os
import pickle
from pathlib import Path
import pandas as pd
import requests
import json

app = Flask(__name__)

BASE_DIR = Path(__file__).resolve().parent
TMDB_API_KEY = os.getenv("TMDB_API_KEY", "e61a5a30b0eca2040040c677579bc3a9")


def ensure_data_file(filename, url_env_name):
    path = BASE_DIR / filename
    if path.exists():
        return path

    url = os.getenv(url_env_name)
    if not url:
        raise RuntimeError(
            f"{filename} is missing. Add it locally or set {url_env_name} to a direct download URL."
        )

    response = requests.get(url, stream=True, timeout=60)
    response.raise_for_status()

    with path.open("wb") as file:
        for chunk in response.iter_content(chunk_size=1024 * 1024):
            if chunk:
                file.write(chunk)

    return path


# Load Data
movie_dict_path = ensure_data_file("movie_dict.pkl", "MOVIE_DICT_URL")
similarity_path = ensure_data_file("similarity.pkl", "SIMILARITY_URL")

movies_data = pickle.load(movie_dict_path.open("rb"))

if callable(movies_data):
    movies_data = movies_data()

if isinstance(movies_data, pd.DataFrame):
    movies = movies_data
elif isinstance(movies_data, dict):
    movies = pd.DataFrame(movies_data)
else:
    movies = pd.DataFrame()

similarity = pickle.load(similarity_path.open("rb"))


def fetch_poster(movie_id):
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}&language=en-US"
        response = requests.get(url, timeout=5)

        if response.status_code != 200:
            return None

        data = response.json()

        if data.get("poster_path"):
            return "https://image.tmdb.org/t/p/w500" + data["poster_path"]

        return None
    except Exception:
        return None


def recommend(movie):
    try:
        movie_index = movies[movies['title'] == movie].index[0]
        distances = similarity[movie_index]

        recommended_movies = []
        recommended_posters = []
        recommended_ids = []

        movie_list = sorted(
            list(enumerate(distances)),
            reverse=True,
            key=lambda x: x[1]
        )[1:6]

        for i in movie_list:
            movie_id = int(movies.iloc[i[0]].movie_id)
            title = movies.iloc[i[0]].title

            recommended_movies.append(title)
            recommended_ids.append(movie_id)
            recommended_posters.append(fetch_poster(movie_id))

        return recommended_movies, recommended_posters, recommended_ids
    except Exception as e:
        print(f"Error in recommend: {e}")
        return [], [], []


@app.route('/')
def index():
    movie_list = movies['title'].values.tolist()
    return render_template('index.html', movies=movie_list)


@app.route('/api/movie/<movie_name>')
def get_movie(movie_name):
    try:
        movie_row = movies[movies['title'] == movie_name].iloc[0]
        movie_id = int(movie_row['movie_id'])
        poster = fetch_poster(movie_id)

        return jsonify({
            'title': movie_row['title'],
            'id': movie_id,
            'poster': poster,
            'tags': movie_row.get('tags', '')
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 404


@app.route('/api/recommend', methods=['POST'])
def get_recommendations():
    try:
        data = request.json
        movie_name = data.get('movie')

        names, posters, ids = recommend(movie_name)

        recommendations = []
        for name, poster, movie_id in zip(names, posters, ids):
            recommendations.append({
                'title': name,
                'poster': poster,
                'id': movie_id
            })

        return jsonify({'recommendations': recommendations})
    except Exception as e:
        return jsonify({'error': str(e)}), 400


if __name__ == '__main__':
    app.run(debug=True, port=5000)

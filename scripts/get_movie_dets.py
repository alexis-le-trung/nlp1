"""
Get the genres of movies 
"""
from os.path import join

import urllib
import urllib.request
import json
from unidecode import unidecode

import config_tmdb as config
tmdb_api_key = config.tmdb_api_key # get your key from https://www.themoviedb.org/settings/api

from imdb import Cinemagoer
ia = Cinemagoer()

META_DIR = join("scripts", "metadata")
TMDB_MOVIE_URL = "https://api.themoviedb.org/3/movie/%d?api_key=%s&language=en-US"
TMDB_TV_URL = "https://api.themoviedb.org/3/tv/?api_key=%s&language=en-US&query=%s&page=1"
TMDB_SEARCH_MOVIE_URL = "https://api.themoviedb.org/3/search/movie?api_key=%s&language=en-US&query=%s&page=1"
TMDB_SEARCH_TV_URL = "https://api.themoviedb.org/3/search/tv?api_key=%s&language=en-US&query=%s&page=1"
TMDB_DISCOVER_MOVIE = "https://api.themoviedb.org/3/discover/movie?api_key=%s&language=en-US&page=1&with_genre=%s&adult=false"
# TMDB_ID_URL = "https://api.themoviedb.org/3/find/%s?api_key=%s&language=en-US&external_source=imdb_id"
# from imdb to tmdb
genres_map = {
    "Sci-Fi" : "Science Fiction"
}
tmdb_genres_map = {
    28: "Action",
    12: "Adventure",
    16: "Animation",
    35: "Comedy",
    80: "Crime",
    99: "Documentary",
    18: "Drama",
    10751: "Family",
    14: "Fantasy",
    36: "History",
    27: "Horror",
    10402: "Music",
    9648: "Mystery",
    10749: "Romance",
    878: "Science Fiction",
    10770: "TV Movie",
    53: "Thriller",
    10752: "War",
    37: "Western"
}

def get_tmdb(movie: int|str, type="movie") -> dict:
    """
    Get the movie details from tmdb
    """
    if type == "movie":
        base_url = TMDB_SEARCH_MOVIE_URL
        date = "release_date"
        title = "title"
    elif type == "tv":
        base_url = TMDB_SEARCH_TV_URL
        date = "first_air_date"
        title = "name"

    if isinstance(movie, str):
        url = base_url % (tmdb_api_key, urllib.parse.quote(movie))
    else :
        url = base_url % (tmdb_api_key, urllib.parse.quote(movie))
    response = urllib.request.urlopen(url)
    res_data = response.read()
    jres = json.loads(res_data)

    if jres['total_results'] > 0:
        movie = jres['results'][0]
        if title in movie and date in movie and "id" in movie and "overview" in movie:
            return {
                "title": unidecode(movie[title]),
                "release_date": movie[date],
                "id": movie["id"],
                "overview": unidecode(movie["overview"]),
                "genres" : movie["genre_ids"]
            }
        else:
            print("Field missing in response")
            return {}
    else:
        return {}

def discover_tmdb(with_genre="") :
    """
    Get tmdb movies with genre
    """
    url = TMDB_DISCOVER_MOVIE % (tmdb_api_key, urllib.parse.quote(with_genre))
    response = urllib.request.urlopen(url)
    res_data = response.read()
    jres = json.loads(res_data)
    print(jres.keys)
    return jres["total_pages"]


def get_imdb(name: str) -> dict:
    """
    Get the movie details from imdb
    """
    movies = ia.search_movie(name)
    if len(movies) > 0 :
        id = (movies[0].getID())
        data = ia.get_movie(id)
        d = {"title": unidecode(data["title"]), "id":id}
        if "year" in data:
            d["year"] = data["year"]
        if "genres" in data :
            d["genres"] = data["genres"]
        if "plot" in data:
            d["overview"] = data["plot"]
        if "synopsis" in data :
            d["synopsis"] = data["synopsis"]
        return d
    return None

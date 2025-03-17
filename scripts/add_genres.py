"""
Add genres to the script database
"""
import pandas as pd
import numpy as np
from get_movie_dets import get_imdb, get_tmdb, tmdb_genres_map
from tqdm.std import tqdm


# Download the data from https://www.kaggle.com/datasets/bwandowando/40k-movie-scripts-from-springfield-springfield
path = "../data/Scripts.csv"


def update_tmdb_data(row):
    movie = row.Title
    parts = movie.split()
    try :
        imdb_data = get_imdb(movie)
        if imdb_data :
            row["imdb_id"] = imdb_data["id"]
            if "synopsis" in imdb_data :
                row["synopsis"] = imdb_data["synopsis"][0]
            if "genres" in imdb_data :
                genres = imdb_data["genres"]
                for g in range(len(genres)) :
                    genre = "imdb_" + genres[g].lower()
                    row[genre] = g + 1
    except Exception as e:
        print(f"Could not get data from IMDB for {movie}: {e}")
    
    try:
        tmdb_data = get_tmdb(' '.join(parts[:-1]))
        if tmdb_data:
            row['tmdb_id'] = tmdb_data['id']
            if 'genres' in tmdb_data:
                for g, genre_id in enumerate(tmdb_data['genres']):
                    genre = f"tmdb_{tmdb_genres_map[genre_id].lower()}"
                    row[genre] = g + 1
    except Exception as e:
        print(f"Could not get data from TMDB for {movie}: {e}")
    return row

if __name__ == "__main__":
    print("Loading data")
    df = pd.read_csv(path, delimiter=",", quotechar="\"")
    df = df.dropna()
    df = df.drop(columns=["URL"])

    # Since the database is large we will process it in chunks
    print("Split data into chunks")
    try:
        with open('last_chunk.txt', 'r') as file:
            last_chunk = int(file.read())
    except FileNotFoundError:
        last_chunk = -1
    chunk_size = 1200
    chunks = np.array_split(df, len(df) // chunk_size)
    nbchunks = len(chunks)
    
    if last_chunk == -1:
        print("Processing chunk 0")
        chunkFrame = chunks[0].apply(update_tmdb_data, axis=1)
        last_chunk = 1
        chunkFrame.to_csv("MovieData.csv", mode='w', header=True, index=False)
        print("chunk 0 done")
    else:
        print("Resuming from chunk " + str(last_chunk))
        last_chunk += 1
    
    for chunk in tqdm(last_chunk, nbchunks) :
        chunkFrame = chunks[chunk].apply(update_tmdb_data, axis=1)
        chunkFrame.to_csv("MovieData.csv", mode='a', header=False, index=False)
        print("chunk " + str(chunk) + " done")
        with open('last_chunk.txt', 'w') as file:
            file.write(str(chunk))


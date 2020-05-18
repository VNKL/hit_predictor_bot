import pickle
from spotipy_framework import Spotify
import pandas as pd
import numpy as np

from settings import SPOTIFY_SID, SPOTIFY_SECRET


with open('ml_models/random_forest.pkl', 'rb') as file:
    forest = pickle.load(file)

with open('ml_models/scaler.pkl', 'rb') as file:
    scaler = pickle.load(file)

spotify = Spotify(SPOTIFY_SID, SPOTIFY_SECRET)


def _search_track(q):
    result = spotify.search_tracks(q)
    if result[q]:
        artist_name = ''
        for i in result[q][0]['artists']:
            artist_name += f'{i[0]}, '
        artist_name = artist_name[:-2]
        track_name = result[q][0]['track'][0]
        track_id = result[q][0]['track'][1]
        return artist_name, track_name, track_id
    else:
        return None, None, None


def _create_df(features):
    df = pd.DataFrame({
        'danceability': [features['danceability']],
        'energy': [features['energy']],
        'loudness': [features['loudness']],
        'mode': [features['mode']],
        'speechiness': [features['speechiness']],
        'acousticness': [features['acousticness']],
        'instrumentalness': [features['instrumentalness']],
        'liveness': [features['liveness']],
        'valence': [features['valence']],
        'tempo': [features['tempo']],
        'duration_ms': [features['duration_ms']],
        'key_1': [1 if features['key'] == 1 else 0],
        'key_2': [1 if features['key'] == 2 else 0],
        'key_3': [1 if features['key'] == 3 else 0],
        'key_4': [1 if features['key'] == 4 else 0],
        'key_5': [1 if features['key'] == 5 else 0],
        'key_6': [1 if features['key'] == 6 else 0],
        'key_7': [1 if features['key'] == 7 else 0],
        'key_8': [1 if features['key'] == 8 else 0],
        'key_9': [1 if features['key'] == 9 else 0],
        'key_10': [1 if features['key'] == 10 else 0],
        'key_11': [1 if features['key'] == 11 else 0],
        'time_signature_3': [1 if features['time_signature'] == 3 else 0],
        'time_signature_4': [1 if features['time_signature'] == 4 else 0],
        'time_signature_5': [1 if features['time_signature'] == 5 else 0],
    })
    return df


def _preprocess_df(df):
    numerical = ['danceability', 'energy', 'loudness', 'speechiness', 'acousticness', 'instrumentalness',
                 'liveness', 'valence', 'tempo', 'duration_ms']
    df['duration_ms'] = (df['duration_ms'] + 1).apply(np.log)
    df['instrumentalness'] = (df['instrumentalness'] + 1).apply(np.log)
    df['liveness'] = (df['liveness'] + 1).apply(np.log)
    df['speechiness'] = (df['speechiness'] + 1).apply(np.log)
    df[numerical] = scaler.transform(df[numerical])
    return df


def predict(q):
    artist_name, track_name, track_id = _search_track(q)
    if not track_id:
        return None
    else:
        track_features = spotify.get_audio_features(track_id)[0]
        df = _create_df(track_features)
        df = _preprocess_df(df)
        predict_proba = forest.predict_proba(df)
        hit_proba = predict_proba[0][1]
        return {'artist_name': artist_name,
                'track_name': track_name,
                'hit_proba': hit_proba}


def main():

    while True:

        q = input('\nInput release name: ')
        if q == 'stop':
            break

        predicts = predict(q)
        if not predicts:
            print("\nDon't finded track on Spotify:", q)
            print('\n----------------------------------------')
        else:
            print(f"\n{predicts['artist_name']} - {predicts['track_name']}\n"
                  f"Hit probability: {predicts['hit_proba'] * 100}%\n")
            print('----------------------------------------')


if __name__ == '__main__':
    main()
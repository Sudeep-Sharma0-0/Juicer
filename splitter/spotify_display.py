import spotipy


def get_tracks(request, playlist_id):
    access_token = request.session.get('access_token')

    sp = spotipy.Spotify(auth=access_token)

    fields = 'items(track(name, artists(name), album(name, release_date)))'
    tracks = sp.playlist_items(playlist_id, fields=fields)

    useful_data = []
    for item in tracks['items']:
        track_info = item['track']
        artists = [artist['name'] for artist in track_info['artists']]
        track_data = {
            'name': track_info['name'],
            'artists': artists,
            'release_date': track_info['album']['release_date']
        }
        artist_id = sp.search(q=f"artist:{artists[0]}", type='artist')[
            'artists']['items'][0]['id']
        artist_info = sp.artist(artist_id)
        genres = artist_info['genres'] if 'genres' in artist_info else None
        track_data['genres'] = genres

        useful_data.append(track_data)
    return useful_data

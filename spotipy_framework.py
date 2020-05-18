import spotipy
from spotipy.oauth2 import SpotifyClientCredentials


class Spotify:

    def __init__(self, cid, secret, country=None, album_ids=None, artist_ids=None, album_type=None,
                 track_ids=None, qs=None):
        """
        Подключение к API Spotify и передача известных параметров для работы.
        Если параметры становятся известны в процессе работы, их можно добавлять
        к объекту на лету, не создавая новый объект. При этом атрибуты объекта
        будут перезаписаны.

        :param cid:             str / client_cid приложения в Spotify
        :param secret:          str / client_secret приложения в Spotify
        :param country:         str / RU, US, DE и т.д.
        :param album_ids:       list or str
        :param artist_ids:      list or str
        :param album_type:      str / album, single, appears_on, compilation
        :param track_ids:       list or str
        """

        login = SpotifyClientCredentials(client_id=cid, client_secret=secret)
        self.spotify = spotipy.Spotify(client_credentials_manager=login)

        self.country = self._check_country(country)
        self.album_ids = self._check_album_ids(album_ids)
        self.artist_ids = self._check_artist_ids(artist_ids)
        self.album_type = self._check_album_type(album_type)
        self.track_ids = self._check_track_ids(track_ids)
        self.qs = self._check_qs(qs)

    def get_new_releases(self, country=None):
        """
        Получает список из 100 новых альбомов.
        Тут будут как альбомы, так и синглы, компиляции

        :param country:     id страны в формате ISO 3166-1 (RU, US, DE и т.д.)
        :return:            словарь списков, ключи корневого словаря - альбом, сингл, сборник
                            {albums: [
                                    {artists: [artist_name, artist_id],
                                    track: [track_name, track_id],
                                    id: album_id},
                                    ],
                            singles: [...],
                            compilations: [...]}
        """
        if country is not None:
            self.country = self._check_country(country)

        new_releases = {}
        albums = []
        singles = []
        compilations = []
        for _offset in range(0, 100, 50):
            api_response = self.spotify.new_releases(country=self.country, limit=50, offset=_offset)
            for release in api_response['albums']['items']:
                temp_dict = {}

                temp_artists_list = []
                for artist in release['artists']:
                    temp_artists_list.append(artist['name'])
                    temp_artists_list.append(artist['id'])

                temp_dict['artists'] = temp_artists_list
                temp_dict['name'] = release['name']
                temp_dict['id'] = release['id']

                if release['album_type'] == 'album':
                    albums.append(temp_dict)
                elif release['album_type'] == 'single':
                    singles.append(temp_dict)
                elif release['album_type'] == 'compilation':
                    compilations.append(temp_dict)

        new_releases['albums'] = albums
        new_releases['singles'] = singles
        new_releases['compilations'] = compilations

        return new_releases

    def get_album_tracks(self, album_ids=None):
        """
        Возвращает треки альбома по айди альбома

        :param album_id:    айди альбома (можно доставать из других методов)
        :return:            словарь словарей:
                            {album_id:
                                {track_number: {
                                    artists: {[
                                        [artist_name, artist_id],
                                        [artist_name, artist_id],
                                        ]},
                                    track: [track_name, track_id],
        """

        if album_ids is not None:
            self.album_ids = self._check_album_ids(album_ids)

        albums_tracks = {}
        for album_id in self.album_ids:
            api_response = self.spotify.album_tracks(album_id)

            tracks = {}
            for n, track in enumerate(api_response['items']):
                track_temp = {}
                artists = []
                for artist in track['artists']:
                    artist_temp = []
                    artist_temp.append(artist['name'])
                    artist_temp.append(artist['id'])
                    artists.append(artist_temp)
                track_temp['artists'] = artists
                track_temp['track'] = [track['name'], track['id']]
                tracks[n] = track_temp

            albums_tracks[album_id] = tracks

        return albums_tracks

    def get_artist_albums(self, artist_ids=None, album_type=None, country=None):
        """
        Вовзращает альбомы артиста по айди артиста

        :param artist_id:   айди артиста (можно получить из других методов)
        :param album_type:  тип альбома:
                                 'album' - альбом
                                 'single' - сингл
                                 'appears_on' - фиты
                                 'compilation' - сборник
        :param country:     id страны в формате ISO 3166-1 (RU, US, DE и т.д.)
        :return:            словарь списков: {artist_id: [[artist_name, artist_id], [track_name, track_id]]}
        """

        if artist_ids is not None:
            self.artist_ids = self._check_artist_ids(artist_ids)

        if album_type is not None:
            self.album_type = self._check_album_type(album_type)

        if country is not None:
            self.country = self._check_country(country)

        albums_dict = {}
        for artist_id in self.artist_ids:

            tracks = []
            offset = 0
            check = True
            while check:
                api_response = self.spotify.artist_albums(artist_id, self.album_type, self.country, 50, offset)
                check = api_response['items']
                if check:
                    for track in check:
                        for artist in track['artists']:
                            if artist['name'] != 'Various Artists':
                                track_temp = []
                                track_temp.append([artist['name'], artist['id']])
                                track_temp.append([track['name'], track['id']])
                                tracks.append(track_temp)
                    offset += 50

            albums_dict[artist_id] = tracks

        return albums_dict

    def get_similar_artists(self, artist_ids=None):
        """
        Возвращает список списков похожих артистов

        :param artist_id:       айди артиста
        :return:                словарь списков: {artist_id: [artist_name, artist_id, followers, popularity]}
        """

        if artist_ids is not None:
            self.artist_ids = self._check_artist_ids(artist_ids)

        similar_artists = {}
        for artist_id in self.artist_ids:

            api_response = self.spotify.artist_related_artists(artist_id)

            artists = []
            for artist in api_response['artists']:
                artist_temp = []
                artist_temp.append(artist['name'])
                artist_temp.append(artist['id'])
                artist_temp.append(artist['followers']['total'])
                artist_temp.append(artist['popularity'])
                artists.append(artist_temp)

            similar_artists[artist_id] = artists

        return similar_artists

    def get_artist_top_tracks(self, artist_ids=None, country=None):
        """
        Возвращает список списков топовых треков артиста в стране

        :param artist_id:       айди артиста
        :param country:         страна
        :return:                словарь списков: {artist_id: [track_name, track_id, popularity]}
        """

        if artist_ids is not None:
            self.artist_ids = self._check_artist_ids(artist_ids)

        if country is not None:
            self.country = self._check_country(country)

        top_tracks = {}
        for artist_id in self.artist_ids:

            api_response = self.spotify.artist_top_tracks(artist_id, self.country)

            top = []
            for track in api_response['tracks']:
                track_temp = []
                track_temp.append(track['name'])
                track_temp.append(track['id'])
                track_temp.append(track['popularity'])
                top.append(track_temp)

            top_tracks[artist_id] = top

        return top_tracks

    def get_audio_features(self, track_ids=None):
        """
        Возвращает аудио фичи треков по их айди

        :param track_ids:       list
        :return:                список словарей с фичами
        """

        if track_ids is not None:
            self.track_ids = self._check_track_ids(track_ids)

        tracks_count = len(self.track_ids)
        tracks_batches = []
        for i in range(0, tracks_count, 50):
            x = 50
            if i + x > tracks_count:
                x -= i + x - tracks_count
            tracks_batches.append(self.track_ids[i:i + x])

        tracks_features = []
        for track_ids in tracks_batches:
            api_response = self.spotify.audio_features(track_ids)
            for i in api_response:
                tracks_features.append(i)

        return tracks_features

    def get_tracks_info(self, track_ids=None):
        """
        Возвращает инфу о треке по его айди

        :param track_ids:       str или list
        :return:                словарь словарей
                                {track_id: {artists: [[], []]}, track: [], popularity: int}, ...}
        """

        if track_ids is not None:
            if isinstance(track_ids, list):
                self.track_ids = track_ids
            elif isinstance(track_ids, str):
                self.track_ids = [track_ids]
            else:
                raise TypeError('track_ids должен быть list или str')
        elif track_ids is None:
            if self.track_ids is None:
                raise AttributeError('не передан track_ids')

        tracks = {}
        for track_id in self.track_ids:
            api_response = self.spotify.track(track_id)
            track_temp = {}
            artists = []
            for artist in api_response['artists']:
                artist_temp = []
                artist_temp.append(artist['name'])
                artist_temp.append(artist['id'])
                artists.append(artist_temp)
            track_temp['artists'] = artists
            track_temp['track'] = api_response['name']
            track_temp['popularity'] = api_response['popularity']
            tracks[track_id] = track_temp

        return tracks

    def search_tracks(self, qs=None, country=None, limit=50):
        """
        Вовзращает найденные по запросу треки

        :param limit:       количество возвращаемых результатов, максимум 50
        :param qs:          list или str, поисковые запросы
        :param country:     айди страны
        :return:            словарь словарей
                            {search: {number: {artists: [[], []]}, track: [], popularity: int}, ...}
        """

        if qs is not None:
            self.qs = self._check_qs(qs)

        if country is not None:
            self.country = self._check_country(country)

        finded_tracks = {}
        for q in self.qs:
            api_response = self.spotify.search(q=q, limit=limit, market=country)

            tracks = {}

            for n, track in enumerate(api_response['tracks']['items']):
                track_temp = {}
                artists = []
                for artist in track['artists']:
                    artist_temp = []
                    artist_temp.append(artist['name'])
                    artist_temp.append(artist['id'])
                    artists.append(artist_temp)
                track_temp['artists'] = artists
                track_temp['track'] = [track['name'], track['id']]
                track_temp['popularity'] = track['popularity']
                tracks[n] = track_temp

            finded_tracks[q] = tracks

        return finded_tracks

    def get_tracks_by_years(self, year, country=None, limit=100):
        """
        Вовзращает найденные по запросу треки

        :param limit:       количество возвращаемых результатов, максимум 50
        :param qs:          list или str, поисковые запросы
        :param country:     айди страны
        :return:            словарь словарей
                            {search: {number: {artists: [[], []]}, track: [], popularity: int}, ...}
        """

        if country is not None:
            self.country = self._check_country(country)

        finded_tracks = []
        for off in range(0, limit, 50):
            api_response = self.spotify.search(q=f'year:{year}', limit=50, offset=off, market=country)

            tracks = []

            for n, track in enumerate(api_response['tracks']['items']):
                track_temp = {}
                artists = []
                for artist in track['artists']:
                    artist_temp = []
                    artist_temp.append(artist['name'])
                    artist_temp.append(artist['id'])
                    artists.append(artist_temp)
                track_temp['artists'] = artists
                track_temp['track'] = [track['name'], track['id']]
                track_temp['popularity'] = track['popularity']
                tracks.append(track_temp)

            finded_tracks.extend(tracks)

        return finded_tracks

    def _check_country(self, country):
        if country is not None:
            if isinstance(country, str) and len(country) == 2:
                return country
            else:
                raise TypeError('country должен быть str из двух символов (RU, EN, DE и т.д.)')
        else:
            return 'US'

    def _check_album_ids(self, album_ids):
        if album_ids is not None:
            if isinstance(album_ids, list):
                return album_ids
            elif isinstance(album_ids, str):
                return [album_ids]
            else:
                raise TypeError('album_ids должен быть list или str')
        else:
            return None

    def _check_artist_ids(self, artist_ids):
        if artist_ids is not None:
            if isinstance(artist_ids, list):
                return artist_ids
            elif isinstance(artist_ids, str):
                return [artist_ids]
            else:
                raise TypeError('artist_id должен быть list или str')
        else:
            return None

    def _check_album_type(self, album_type):
        if album_type is not None:
            if isinstance(album_type, str):
                return album_type
            else:
                raise TypeError('album_type должен быть str')
        else:
            return None

    def _check_track_ids(self, track_ids):
        if track_ids is not None:
            if isinstance(track_ids, list):
                return track_ids
            elif isinstance(track_ids, str):
                return [track_ids]
            else:
                raise TypeError('track_ids должен быть list или str')
        else:
            return None

    def _check_qs(self, qs):
        if qs is not None:
            if isinstance(qs, list):
                return qs
            elif isinstance(qs, str):
                return [qs]
            else:
                raise TypeError('qs должен быть list или str')
        else:
            return None



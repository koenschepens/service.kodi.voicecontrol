from __future__ import unicode_literals
from ..states.statebase import StateBase

import spotify

session = None

class spotifyState(StateBase):
    playlist = []
    _is_playing = False

    def __init__(self, context):
        StateBase.__init__(self, context)
        self.context = context
        if(spotify._session_instance is None):
            self.session = spotify.Session()
            self.session.login(context.config.get("spotify", "username"), context.config.get("spotify", "password"))
            client_secret = context.config.get("spotify", "ClientSecret")
        else:
            self.session = spotify._session_instance

        while(self.session.connection.state <> 1):
            self.session.process_events()

        self.session.on(spotify.SessionEvent.MESSAGE_TO_USER, self._on_message)
        self.session.on(spotify.SessionEvent.END_OF_TRACK, self._on_end_of_track)

    def _on_message(self, session, data):
        self.context.show_notification(data)

    def _on_end_of_track(self, session):
        self.play()

    def play(self, command):
        while(self.session.connection.state <> 1):
            self.session.process_events()

        tracks = self.search(command)
        if(tracks is not None):
            for track in tracks:
                self.playlist.append(track)

            self._play()

    def _play(self, track = None):
        if(track is None):
            track = self.playlist.pop()

        if(track is None):
            return

        while(self.session.connection.state <> 1):
            self.session.process_events()

        audio = spotify.PortAudioSink(self.session)
        track.load()
        self.session.player.load(track)
        self.session.player.play()

    def search(self, command, track=None):
        event_loop = spotify.EventLoop(self.session)
        event_loop.start()

        if(command.artist is not None):
            search = self.session.search(query=command.artist)
            search.load()
            if len(search.tracks) > 0:
                return search.tracks

        if(command.search_query is not None):
            search = self.session.search(query=command.search_query)
            search.load()
            if len(search.tracks) > 0:
                return search.tracks

        return None
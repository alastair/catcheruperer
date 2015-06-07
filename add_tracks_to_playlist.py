
# Adds tracks to a playlist

import pprint
import sys

import conf

import spotipy
import spotipy.util as util

if len(sys.argv) > 3:
    username = sys.argv[1]
    playlist_name = sys.argv[2]
    track_ids = sys.argv[3:]
else:
    print "Usage: %s username playlist_name track_id ..." % (sys.argv[0],)
    sys.exit()

scope = 'playlist-modify-public'
token = util.prompt_for_user_token(username, scope)

if token:
    sp = spotipy.Spotify(auth=token)
    sp.trace = False
    playlists = sp.user_playlist_create(username, playlist_name)
    print playlists

    results = sp.user_playlist_add_tracks(username, playlist_id, track_ids)
    print results
else:
    print "Can't get token for", username

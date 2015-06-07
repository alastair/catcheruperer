from flask import Flask
from flask import render_template
from flask import request
from flask import jsonify
from flask import Response
from flask import redirect, url_for

import json
import os

import db
import conf
import playlist
import swplaylist

app = Flask(__name__)

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/hacks")
def hacks():
    years = range(1980, 2016)
    return render_template('hacks.html', years=years)

def quote(s):
    return json.dumps(s)

@app.route("/artist/<artist>/<path:title>")
def track(artist, title):
    data = db.trackdata(db.Chart, artist, title)

    dates = [d.week for d in data]
    positions = [d.position for d in data]
    positions = json.dumps(positions)
    dates = json.dumps(dates)

    stats = db.stats(artist, title)

    arttitle = "%s - %s" % (artist, title)
    arttitle = quote(arttitle)

    if stats and data:
        ret = {"artist": artist, "title": title, "dates": dates,
                "positions": positions, "stats": stats, "arttitle": arttitle}
    else:
        ret = {"missing": True}

    return render_template('track.html', **ret)

@app.route("/artist/<artistname>")
def artist(artistname):
    tracks = db.artist(artistname)

    newdata= []
    for d in tracks:
        stats = db.stats(d[0], d[1])
        if stats:
            newdata.append(stats)
    tracks = sorted(newdata, key=lambda x: x["rank"], reverse=True)

    return render_template('artist.html', artist=artistname, tracks=tracks)

@app.route("/year/<theyear>")
def year(theyear):
    yeardata = db.year(theyear)

    return render_template('year.html', year=theyear, data=yeardata)

@app.route("/charts")
def charts():
    longest = db.longest()[:10]
    longestone = db.longest_one()[:10]

    return render_template('charts.html', longest=longest, longestone=longestone)

@app.route("/complete/artist")
def completeartist():
    q = request.args.get('q')
    if q:
        sugg = db.get_artist_suggestions(q)
        return Response(json.dumps(sugg),  mimetype='application/json')
    return None

@app.route("/complete/track")
def completetrack():
    q = request.args.get('q')
    if q:
        sugg = db.get_track_suggestions(q)
        return Response(json.dumps(sugg),  mimetype='application/json')
    return None

@app.route("/playlist/<playid>")
def playlisturl(playid):

    pl = json.load(open(os.path.join("playlists", "%s.json" % playid)))
    meta = pl["meta"]
    url = meta["playlistopen"]
    title= meta["title"]

    endpoint = url_for('playlistjson', playid=playid)

    return render_template('playlist.html', title=title, endpoint=endpoint, url=url)

@app.route("/playlist/<playid>.json")
def playlistjson(playid):

    pl = json.load(open(os.path.join("playlists", "%s.json" % playid)))

    data = pl["data"]

    return Response(json.dumps(data),  mimetype='application/json')

@app.route("/back/<artist>/<path:title>/<hours>")
def back(artist, title, hours):

    actual_hours, tracks = playlist.make_playlist(artist, title, hours)
    trackids = playlist.songs_to_spotifyid(tracks)

    title = "Catchup from %s - %s in %s hours" % (artist, title, actual_hours)
    playlistid, playlistopen, playlistspoturl = playlist.create_spotify_playlist(title, trackids)

    meta = {"title": title, "playlistid": playlistid, "playlistopen": playlistopen}

    playlist.cache_playlist(meta, tracks)

    return redirect(url_for('playlisturl', playid=playlistid))

@app.route("/forward/<artist>/<path:title>/<hours>")
def forward(artist, title, hours):
    actual_hours, tracks = playlist.make_playlist(artist, title, hours)

    trackids = playlist.songs_to_spotifyid(tracks)

    title = "Catchup from %s - %s in %s hours" % (artist, title, actual_hours)
    playlistid, playlistopen, playlistspoturl = playlist.create_spotify_playlist(title, trackids)

    meta = {"title": title, "playlistid": playlistid, "playlistopen": playlistopen}

    playlist.cache_playlist(meta, tracks)

    return redirect(url_for('playlisturl', playid=playlistid))

@app.route("/sweden/<hours>")
def sweden(hours):

    actual_hours, tracks = swplaylist.make_playlist(hours)
    trackids = swplaylist.songs_to_spotifyid(tracks)

    title = "Swedish popular music catchup in %s hours" % (actual_hours, )
    playlistid, playlistopen, playlistspoturl = swplaylist.create_spotify_playlist(title, trackids)

    meta = {"title": title, "playlistid": playlistid, "playlistopen": playlistopen}

    swplaylist.cache_playlist(meta, tracks)

    return redirect(url_for('playlisturl', playid=playlistid))

if __name__ == "__main__":
    app.run(debug=True)

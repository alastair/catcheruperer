from flask import Flask
from flask import render_template
from flask import request
from flask import jsonify
from flask import Response

import db
import json

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

@app.route("/artist/<artist>/<title>")
def track(artist, title):
    data = db.trackdata(artist, title)

    dates = [d.week for d in data]
    positions = [d.position for d in data]
    positions = json.dumps(positions)
    dates = json.dumps(dates)

    stats = db.stats(artist, title)

    arttitle = "%s - %s" % (artist, title)
    arttitle = quote(arttitle)

    return render_template('track.html', artist=artist, title=title,
            dates=dates, positions=positions, stats=stats, arttitle=arttitle)

@app.route("/artist/<artistname>")
def artist(artistname):
    tracks = db.artist(artistname)

    newdata= []
    for d in tracks:
        stats = db.stats(d[0], d[1])
        newdata.append(stats)
    tracks = sorted(newdata, key=lambda x: x["rank"], reverse=True)

    return render_template('artist.html', artist=artistname, tracks=tracks)

@app.route("/year/<theyear>")
def year(theyear):
    yeardata = db.year(theyear)

    newdata= []
    for d in yeardata:
        stats = db.stats(d[2], d[3])
        newdata.append(stats)
    yeardata = sorted(newdata, key=lambda x: x["rank"], reverse=True)

    return render_template('year.html', year=theyear, data=yeardata)

@app.route("/charts")
def charts():
    longest = db.longest()[:10]
    longestone = db.longest_one()[:10]

    return render_template('charts.html', longest=longest, longestone=longestone)

@app.route("/autocomplete")
def autocomplete():
    q = request.args.get('q')
    if q:
        sugg = db.get_suggestions(q)
        return Response(json.dumps(sugg),  mimetype='application/json')
    return None

if __name__ == "__main__":
    app.run(debug=True)

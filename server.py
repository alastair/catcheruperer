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
    years = range(1980, 2016)
    return render_template('index.html', years=years)

@app.route("/artist/<artist>/<title>")
def track(artist, title):
    data = db.trackdata(artist, title)

    dates = [d.week for d in data]
    positions = [d.position for d in data]
    positions = json.dumps(positions)
    dates = json.dumps(dates)

    return render_template('track.html', artist=artist, title=title, dates=dates, positions=positions)

@app.route("/artist/<artist>")
def artist(artistname):
    data = db.trackdata(artist, title)

    return render_template('artist.html', artist=artist, tracks=tracks)

@app.route("/year/<theyear>")
def year(theyear):
    return render_template('year.html', year=theyear)

@app.route("/charts")
def charts():

    return render_template('charts.html')

@app.route("/autocomplete")
def autocomplete():
    q = request.args.get('q')
    if q:
        sugg = db.get_suggestions(q)
        return Response(json.dumps(sugg),  mimetype='application/json')
    return None

if __name__ == "__main__":
    app.run(debug=True)

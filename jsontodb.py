import db
import os
import sys
import json

def import_file(fname):
    j = json.load(open(fname))
    date = j["date"]
    entries = j["entries"]
    for e in entries:
        artist = e["artist"]
        change = e["change"]
        last = e["lastPos"]
        peak = e["peakPos"]
        rank = e["rank"]
        title = e["title"]
        weeks = e["weeks"]

        chart = db.Chart(week=date, position=rank, lastweek=last, change=change,
                            peak=peak, weeks=weeks, artist=artist, title=title)
        db.session.add(chart)

def main(thedir):
    for root, dirs, files in os.walk(thedir):
        for f in files:
            import_file(os.path.join(root, f))
    db.session.commit()

if __name__ == "__main__":
    main(sys.argv[1])

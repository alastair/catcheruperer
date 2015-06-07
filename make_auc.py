import db
import json

def main():
    done = {}
    tracks = db.session.query(db.Sweden).all()
    for i, t in enumerate(tracks):
        artist = t.artist
        title = t.title
        key = "%s - %s" % (artist, title)
        if key not in done:
            stats = db.swstats(artist, title)
            done[key] = stats["rank"]
        if i % 1000 == 0:
            print ".",
    json.dump(done, open("swauc.json", "w"))

if __name__ == "__main__":
    main()

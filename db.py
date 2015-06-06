from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy import func
from sqlalchemy import desc

import json

Base = declarative_base()
engine = create_engine('postgresql://alastair:@/billboard') #, echo=True)

from sqlalchemy.orm import sessionmaker
Session = sessionmaker(bind=engine)

session = Session()

def load_auc():
    return json.load(open("auc.json"))
auc = load_auc()

class Chart(Base):
    __tablename__ = "chart"
    id = Column(Integer, primary_key=True)
    week = Column(String(50))
    position = Column(Integer)
    lastweek = Column(Integer)
    change = Column(String(50))
    peak = Column(String(50))
    weeks = Column(String(50))
    artist = Column(String(500))
    title = Column(String(500))
    spotifyid = Column(String(50))

    def __repr__(self):
        return "<Chart: %s - %s (%s:%s)>" % (self.artist, self.title, self.week, self.position)


def get_track_suggestions(query):
    charts = session.query(
        func.count(Chart.id), func.min(Chart.position), Chart.artist, Chart.title)\
            .filter(Chart.title.ilike('%%%s%%' % query))\
            .group_by(Chart.artist, Chart.title).all()

    # sort by number of weeks on chart, chart position
    # num weeks * by -1 because highest number of weeks
    # should come first ('lowest')
    charts = sorted(charts, key=lambda x: (x[0]*-1, x[1]))
    return [{"value": "%s - %s" % (c[2], c[3]), "artist": c[2], "title": c[3]} for c in charts][:10]

def get_artist_suggestions(query):
    charts = session.query(
        func.count(Chart.id), func.min(Chart.position), Chart.artist)\
            .filter(Chart.artist.ilike('%%%s%%' % query))\
            .group_by(Chart.artist).all()

    # sort by number of weeks on chart, chart position
    # num weeks * by -1 because highest number of weeks
    # should come first ('lowest')
    charts = sorted(charts, key=lambda x: (x[0]*-1, x[1]))
    return [{"value": c[2], "artist": c[2]} for c in charts][:10]

def trackdata(artist, title):
    return session.query(Chart).filter(Chart.artist==artist).filter(Chart.title==title).all()

def longest_one():
    """ Find the tracks that have been at number one
        on the charts for the longest time """
    charts = session.query(
        func.count(Chart.position), Chart.artist, Chart.title)\
            .filter(Chart.position==1)\
        .group_by(Chart.artist, Chart.title)\
        .order_by(desc(func.count(Chart.position)))\
        .all()
    return charts

def longest():
    """ Find tracks that have been on the charts for the longest """
    charts = session.query(
        func.count(Chart.position), Chart.artist, Chart.title)\
        .group_by(Chart.artist, Chart.title)\
        .order_by(desc(func.count(Chart.position)))\
        .all()
    return charts

def year(theyear):
    fr = '%s-01-01' % theyear
    to = '%-s-12-31' % theyear

    charts = session.query(
        func.min(Chart.week), Chart.artist, Chart.title)\
        .filter(Chart.week>=fr).filter(Chart.week <=to)\
        .group_by(Chart.artist, Chart.title)\
        .all()

    ret = []
    for c in charts:
        k = "%s - %s" % (c[1], c[2])
        ret.append((auc.get(k, 0), c[1], c[2], c[0]))
    return sorted(ret, key=lambda x: x[3])

def between(fr, to):
    """ Unique list of tracks on the chart in a year. Ordered by
    (entry date, chart position)
    """
    #  select artist, title, min(week), position from chart where week like '1990%' group by artist, title, position order by min(week), position;
    charts = session.query(
        Chart.artist, Chart.title, Chart.position, Chart.week)\
        .filter(Chart.week>=fr).filter(Chart.week <=to)\
        .order_by(Chart.week, Chart.position)\
        .all()
    return charts

def artist(artistname):
    """ An artist's tracks. Ordered by (entry on charts, position) """
    charts = session.query(
        Chart.artist, Chart.title)\
        .filter(Chart.artist==artistname)\
        .group_by(Chart.artist, Chart.title)\
        .all()
    return charts

def stats(artist, title):
    """ Stats for a single track:
       - (highest rank, weeks on chart, weeks at 1, chart start date, chart end date)
    """
    data = trackdata(artist, title)
    weeks = len(data)
    weeksone = len([d for d in data if d.position==1])
    datesort = sorted(data, key=lambda x: x.week)
    if datesort:
        first = datesort[0].week
        last = datesort[-1].week
        positionsort = sorted(data, key=lambda x: x.position)
        highest = positionsort[0].position

        positions = [101 - d.position for d in data]
        rank = sum(positions)

        return {"artist": artist, "title": title, "highest": highest, "weeks": weeks,
                "weeksone": weeksone, "first": first, "last": last, "rank": rank}
    else:
        return {}

def makedb():
    Base.metadata.create_all(engine)

if __name__ == "__main__":
    makedb()

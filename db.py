from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy import func
from sqlalchemy import desc

Base = declarative_base()
engine = create_engine('postgresql://alastair:@/billboard', echo=True)

from sqlalchemy.orm import sessionmaker
Session = sessionmaker(bind=engine)

session = Session()

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

def get_suggestions(query):
    charts = session.query(
        func.count(Chart.id), func.min(Chart.position), Chart.artist, Chart.title)\
            .filter(Chart.title.ilike('%%%s%%' % query))\
            .group_by(Chart.artist, Chart.title).all()

    # sort by number of weeks on chart, chart position
    # num weeks * by -1 because highest number of weeks
    # should come first ('lowest')
    charts = sorted(charts, key=lambda x: (x[0]*-1, x[1]))
    return [{"value": "%s - %s" % (c[2], c[3])} for c in charts][:10]

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
    """ Unique list of tracks on the chart in a year. Ordered by
    (entry date, chart position)
    """
    pass

def artist(artistname):
    """ An artist's tracks. Ordered by (entry on charts, position) """
    pass

def stats(artist, title):
    """ Stats for a single track:
       - (highest rank, weeks on chart, weeks at 1, chart start date, chart end date)
    """
    data = trackdata(artist, title)
    weeks = len(data)
    weeksone = len([d for d in data if d.position==1])
    datesort = sorted(data, key=lambda x: x.week)
    first = datesort[0].week
    last = datesort[-1].week
    positionsort = sorted(data, key=lambda x: x.position)
    highest = positionsort[0].position

    return {"highest": highest, "weeks": weeks, "weeksone": weeksone, "first": first, "last": last}



def makedb():
    Base.metadata.create_all(engine)

if __name__ == "__main__":
    makedb()

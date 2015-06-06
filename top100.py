
import billboard
from bs4 import BeautifulSoup
import os
import time

def download_year(year):
    url = "http://www.billboard.com/archive/charts/%s/hot-100" % year
    html = billboard.downloadHTML(url)
    b = BeautifulSoup(html)

    charts = b.findAll("span", {"class":"date-display-single"})
    for c in charts:
        date = c.attrs["content"][:10]
        print date
        dl = download_issue(date)
        if dl:
            time.sleep(2)


def download_issue(issue):
    year = issue[:4]
    if not os.path.exists(year):
        os.makedirs(year)
    fname = os.path.join(year, "%s.json" % issue)
    if not os.path.exists(fname):
        bb = billboard.ChartData('hot-100', date=issue)
        with open(fname, "w") as fp:
            fp.write(bb.to_JSON())
        return True
    return False


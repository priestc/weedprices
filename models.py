import datetime
import requests
import json

from giotto import get_config

from crawl import parse_listings
from sqlalchemy import Column, String, DateTime, Float, Integer
import numpy as np

Base = get_config("Base")

def stats():
    stats = []
    for drug in ['mdma', 'weed']:
        latest = CrawlResult.get_latest(drug)
        stats.append({
            'drug': drug,
            'price': latest.worldwide_avg_per_ounce,
            'date': latest.created
        })
    return stats

def show_listings(drug):
    latest = CrawlResult.get_latest(drug=drug)
    listings = json.loads(latest.json)
    if drug == "weed":
        drug = "Weed"
    if drug == 'mdma':
        drug = "MDMA"
    return {
        'drug': drug,
        'listings': listings,
        'bitcoin_price': latest.bitcoin_to_usd,
        'last_updated': latest.created,
        'outliers': latest.outliers_count,
        'worldwide_avg_per_ounce': latest.worldwide_avg_per_ounce
    }

def reject_outliers(data, m = 2.):
    d = np.abs(data - np.median(data))
    mdev = np.median(d)
    s = d/mdev if mdev else 0
    return data[s<m]

class CrawlResult(Base):
    json = Column(String)
    bitcoin_to_usd = Column(Float)
    created = Column(DateTime, primary_key=True)
    drug = Column(String)
    worldwide_avg_per_ounce = Column(Float)
    outliers_count = Column(Integer)

    @classmethod
    def do_crawl(cls, drug, total_pages):
        bitcoin_price = float(requests.get("http://api.bitcoinaverage.com/ticker/USD").json()['last'])
        try:
            parsed = open("%s_data/parsed.json" % drug).read()
            listings = json.loads(parsed)
        except IOError:
            listings = parse_listings(drug=drug, total_pages=total_pages)
            parsed = json.dumps(listings)
            with open("%s_data/parsed.json" % drug, 'w') as f:
                f.write(parsed)

        new = []
        for listing in listings:
            listing["unit_price"] = listing['price'] * bitcoin_price / listing['quantity']
            new.append(listing)

        prices = np.array([listing['unit_price'] for listing in listings])
        filtered = reject_outliers(prices)
        outliers_count = len(prices) - len(filtered)
        average_price = sum(filtered) / len(filtered)

        m = cls(
            json=parsed,
            bitcoin_to_usd=bitcoin_price,
            created=datetime.datetime.now(),
            drug=drug,
            outliers_count=outliers_count,
            worldwide_avg_per_ounce=average_price,
        )

        session = get_config("db_session")
        session.add(m)
        session.commit()

    @classmethod
    def get_latest(cls, drug):
        session = get_config("db_session")
        return session.query(cls).filter_by(drug=drug).order_by("-created")[0]
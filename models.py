import datetime
import requests
import json

from giotto import get_config

from crawl import get_listings
from sqlalchemy import Column, String, DateTime, Float

Base = get_config("Base")

def all_listings():
    data = []
    for i in range(1, 16):
        data = data + get_listings(i)
    return data

def show_listings():
	latest = CrawlResult.get_latest()
	items = json.loads(latest.json)
	return {
		'items': items,
		'current_bitcoin_price': latest.bitcoin_to_usd,
		'last_updated': latest.created
	}

class CrawlResult(Base):
	json = Column(String)
	bitcoin_to_usd = Column(Float)
	created = Column(DateTime, primary_key=True)

	@classmethod
	def do_crawl(cls):
		m = cls(
			json=json.dumps(all_listings()),
			bitcoin_to_usd=requests.get("http://api.bitcoinaverage.com/ticker/USD").json()['last'],
			created=datetime.datetime.now()
		)
		session = get_config("db_session")
		session.add(m)
		session.commit()

	@classmethod
	def get_latest(cls):
		session = get_config("db_session")
		return session.query(cls).order_by("-created")[0]
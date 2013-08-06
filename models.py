import datetime
import requests
import json

from giotto import get_config

from crawl import get_listings
from sqlalchemy import Column, String, DateTime, Float

Base = get_config("Base")

def all_listings(drug, total_pages):
    data = []
    for i in range(1, int(total_pages)):
        data = data + get_listings(drug=drug, page=i)
    return data

def show_listings(drug):
	latest = CrawlResult.get_latest(drug=drug)
	items = json.loads(latest.json)
	return {
		'drug': drug,
		'items': items,
		'current_bitcoin_price': latest.bitcoin_to_usd,
		'last_updated': latest.created
	}

class CrawlResult(Base):
	json = Column(String)
	bitcoin_to_usd = Column(Float)
	created = Column(DateTime, primary_key=True)
	drug = Column(String)

	@classmethod
	def do_crawl(cls, drug, total_pages):
		m = cls(
			json=json.dumps(all_listings(drug=drug, total_pages=total_pages)),
			bitcoin_to_usd=requests.get("http://api.bitcoinaverage.com/ticker/USD").json()['last'],
			created=datetime.datetime.now(),
			drug=drug
		)
		session = get_config("db_session")
		session.add(m)
		session.commit()

	@classmethod
	def get_latest(cls, drug):
		session = get_config("db_session")
		return session.query(cls).filter_by(drug=drug).order_by("-created")[0]
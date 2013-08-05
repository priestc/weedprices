from giotto.contrib.static.programs import StaticServe
from giotto.programs import Program, Manifest
from giotto.programs.management import management_manifest
from giotto.views import BasicView, jinja_template
from models import show_listings, CrawlResult

manifest = Manifest({
    'listings': Program(
        model=[show_listings],
        view=BasicView(
        	html=jinja_template("show_listings.html")
        )
    ),
    'crawl': Program(
    	controllers=['cmd'],
    	model=[CrawlResult.do_crawl],
    	view=BasicView,
    ),
    'static': StaticServe('/static'),
    'mgt': management_manifest,
})
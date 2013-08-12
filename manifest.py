from giotto.contrib.static.programs import StaticServe
from giotto.programs import Program, Manifest
from giotto.programs.management import management_manifest
from giotto.views import BasicView, jinja_template
from models import show_listings, CrawlResult, stats

manifest = Manifest({
    '': '/stats',
    'stats': Program(
        model=[stats],
        view=BasicView(
            html=jinja_template('landing.html')
        )
    ),
    'api_docs': Program(
        view=BasicView(
            html=jinja_template('api.html')
        )
    ),
    'listings': Program(
        model=[show_listings],
        view=BasicView(
            html=jinja_template("show_listings.html")
        )
    ),
    'crawl': Program(
        controllers=['cmd'],
        model=[CrawlResult.do_crawl],
    ),
    'static': StaticServe('/static'),
    'mgt': management_manifest,
})
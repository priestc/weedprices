import re
import requests

from bs4 import BeautifulSoup

def strip_all_but_numbers(num):
    return re.compile(r'[^\d.]+').sub('', num)

def get_page(page=1, download=False):
    if download:
        # XXX: This needs to be done later
        # crawling over tor is a pain.
        # we'll use manual crawlinf for now
        url = "http://silkroadvb5piz3r.onion.to/"
        cookies = dict(cookies_are='working')
        response = requests.get(url, cookies={})
        return response.content
    else:
        return open('page%s.html' % page).read()

def get_listings(page):
    """
    Given a large string of HTML code from a page on silkroad's site,
    return a json structore representing the listings.
    """
    html = get_page(page)
    soup = BeautifulSoup(html)

    container = soup.findAll("div", id="cat_item")
    
    items = []
    for item in container:
        title_elem = item.find(class_="h2")
        title = title_elem.text
        if "lottery" in title.lower():
            # ignore lottery listings because they don't count
            continue
        quantity = guess_quantity(title)
        if not quantity:
            continue

        url = title_elem.attrs['href']
        price = item.find(class_="price_big").text[1:] # remove bitcoin glyph
        seller = item.find("a", href=re.compile("/silkroad/user/")).text
        thumb = item.find("img", src=re.compile("^data:"))
        thumb = (thumb and thumb.attrs['src']) or ""
        items.append({
            'title': title,
            "seller": seller,
            "price": float(price),
            "quantity": quantity,
            "url": url,
            "thumb": thumb,
        })
    return items

def guess_quantity(title):
    """
    In comes a title of a silkroad listing.
    Returned is a best guess on the quantity of that listing.
    Works by doing a fuzzy search. All values are in ounces.
    """
    title = title.lower()
    regex = "(half|quarter|\d/\d|\d+\.*\d+|\d+)[\s-]*(%s|%s)"
    grams = re.search(regex % ('g', 'grams'), title)
    if grams:
        numeric = grams.groups()[0]
        #print "found grams", numeric, "**", title
        try:
            return float(numeric) / 28.35
        except:
            import debug
    ounces = re.search(regex % ('oz', 'ounce'), title)
    if ounces:
        numeric = ounces.groups()[0] # just the numeric value
        #print "found ounces", value
        if numeric == 'half':
            return 0.5
        if numeric == 'quarter':
            return 0.25
        if '/' in numeric:
            num, denom = numeric.split('/')
            return float(num) / float(strip_all_but_numbers(denom))
        return float(numeric)

    pounds = re.search(regex % ('lb|lbs', 'pound'), title)
    if pounds:
        numeric = pounds.groups()[0] # just the numeric value
        #print "found pounds", value
        if numeric == 'half':
            return 8
        if numeric == 'quarter':
            return 4
        if numeric == 'eighth':
            return 2
        if '/' in numeric:
            num, denom = numeric.split('/')
            return float(num) / float(strip_all_but_numbers(denom))
        return float(numeric) * 16

    if "1/8" in title:
        return 0.123456
    if "1/4" in title:
        return 0.25
    if "1/2" in title:
        return 0.5
    if "pound" in title:
        return 16
    if "qp" in title:
        #print "found qp"
        return 4
    if "hp" in title:
        #print "found hp"
        return 8
    if "oz" in title:
        return 1

def test():
    cases = (
        ("Half pound blackberry kush", 8),
        ("Very High Grade Commercial 1 OZ", 1),
        ("Quarter oz Dark Purple Grape Ape", 0.25),
        ("1 pound og kush", 16),
        ("29-GRAMS-BORDER-BLASTER", 1.02294),
    )
    
    for title, oz in cases:
        result = guess_quantity(title)
        assert result == oz, (title, oz, result)
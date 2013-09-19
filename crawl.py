import hashlib
import re
import requests

from bs4 import BeautifulSoup

def strip_all_but_numbers(num):
    return re.compile(r'[^\d.]+').sub('', num)

def parse_listings(drug, total_pages):
    data = []
    for i in range(1, int(total_pages) + 1):
        data = data + get_listings(drug=drug, page=i)
    return data

def get_listings(drug, page):
    """
    Given a large string of HTML code from a page on silkroad's site,
    return a json structure representing the listings.
    """
    file_number = (page-1) * 25
    html = open('%s_data/%s.html' % (drug, file_number)).read()
    soup = BeautifulSoup(html, "lxml")

    container = soup.findAll("div", id="cat_item")
    
    items = []
    for item in container:
        title_elem = item.find(class_="h2")
        title = title_elem.text
        if "lottery" in title.lower():
            # ignore lottery listings because they mess up the average price
            continue
        try:
            quantity = guess_quantity(title)
        except:
            print "failed:", title 
        
        if not quantity:
            continue

        url = title_elem.attrs['href']
        price = item.find(class_="price_big").text[1:] # remove bitcoin glyph
        price = float(price.replace(',', ''))
        seller = item.find("a", href=re.compile("/silkroad/user/")).text
        thumb_e = item.find("img", src=re.compile("^data:"))
        thumb = (thumb_e and thumb_e.attrs['src']) or ""
        ships_from = [x for x in item.find(id="cat_item_description").children][8]
        country = ships_from[12:]

        items.append({
            'title': title,
            "seller": seller,
            "price": price,
            "quantity": quantity,
            "url": url,
            "country": silkroad_country_to_iso(country),
            "thumb": uri_to_file(thumb),
        })

    print "parsed page: %s (%s.html)" % (page, file_number)
    return items

def uri_to_file(uri):
    """
    Convert a data URI to an image file. Save to disk, use the 
    md5 of the data as the filename.
    """
    if not uri:
        return

    header, data = uri.split(',')
    md5_hash = hashlib.md5(data).hexdigest()
    with open("static/images/%s.jpg" % md5_hash, 'wb') as f:
        f.write(data.decode('base64'))
    return md5_hash


def silkroad_country_to_iso(sr_country):
    if sr_country == 'Saipan':
        return "MP"
    if sr_country == 'United States of America':
        return "US"
    if sr_country == 'Canada':
        return "CA"
    if sr_country == 'Germany':
        return "DE"
    if sr_country == 'South Africa':
        return "ZA"
    if sr_country == 'Germany':
        return "DE"
    if sr_country == 'Netherlands':
        return "NL"
    if sr_country == 'Sweden':
        return "SE"
    if sr_country == 'United Kingdom':
        return "GB"
    if sr_country == 'undeclared':
        return ""
    if sr_country == 'France':
        return "FR"
    if sr_country == 'Czech Republic':
        return "CZ"
    if sr_country == 'Poland':
        return "PL"
    if sr_country == 'Italy':
        return "IT"
    if sr_country == 'Australia':
        return "AU"
    if sr_country == 'Spain':
        return "ES"
    if sr_country == 'Denmark':
        return "DK"
    if sr_country == 'Finland':
        return "FI"
    if sr_country == 'India':
        return "IN"
    if sr_country == 'Belgium':
        return "BE"
    if sr_country == 'Thailand':
        return "TH"
    if sr_country == 'Ukraine':
        return "UA"
    if sr_country == 'Ghana':
        return "GH"
    if sr_country == 'Austria':
        return "AT"
    if sr_country == 'China':
        return "CN"
    if sr_country == 'Portugal':
        return 'PT'
    if sr_country == 'Ireland':
        return 'IE'
    if sr_country == 'Switzerland':
        return 'CH'
    if sr_country == 'Philippines':
        return 'PH'

    raise Exception("New country: %s" % sr_country)
    





def guess_quantity(title):
    """
    In comes a title of a silkroad listing.
    Returned is a best guess on the quantity of that listing.
    Works by doing a fuzzy search. All return values are in ounces.
    """
    title = title.lower()
    regex = "(half|quarter|\d/\d|\d+\.*\d+|\d+)[\s-]*(%s|%s)"
    grams = re.search(regex % ('g|gr', 'gram'), title)
    if grams:
        numeric = grams.groups()[0]
        if numeric == 'half':
            return 0.5 / 28.35
        if numeric == 'quarter':
            return 0.25 / 28.35
        if '/' in numeric:
            num, denom = numeric.split('/')
            return float(num) / float(strip_all_but_numbers(denom))
        return float(numeric) / 28.35
    
    ounces = re.search(regex % ('oz', 'ounce'), title)
    if ounces:
        numeric = ounces.groups()[0] # just the numeric value
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
        return 4
    if "hp" in title:
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
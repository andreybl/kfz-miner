import json
from urllib.error import HTTPError

import requests

__author__ = 'agolovko'
import ssl
from bs4 import BeautifulSoup
import re
import locale
from datetime import datetime
import hashlib

# Matches "27.900,01" in "27.900,01 € (Brutto)"
PATTERN_EURO = re.compile("([\d\.,]*)\s€")
PATTERN_KMSTAND = re.compile("([\d\.,]*)\skm")
PATTERN_POWER = re.compile("\((\d+)(.*PS)\)")
PATTERN_EMISSION_STICKER = re.compile("(\d+)")

PATTERN_URL_PAGE_NUMBER = re.compile(".*pageNumber\=(\d+).*")

DIV_ID_NUM_OF_SEATS = re.compile(".*rbt-numSeats-v.*")
DIV_ID_NUM_OF_PREV_OWNERS = re.compile(".*rbt-numberOfPreviousOwners-v.*")
DIV_ID_FIRST_REGISTRATION = re.compile(".*rbt-firstRegistration-v.*")
DIV_ID_EMISSION_STICKER = re.compile(".*rbt-emissionsSticker-v.*")
DIV_ID_EMISSION_CLASS = re.compile(".*rbt-emissionClass-v.*")
DIV_ID_FUEL = re.compile(".*rbt-fuel-v.*")
DIV_ID_POWER = re.compile(".*rbt-power-v.*")
DIV_ID_KMSTAND = re.compile(".*rbt-mileage-v.*")
SPAN_CLASS_PRICE = re.compile(".*rbt-prime-price.*")
DIV_CLASS_ERROR_MESSAGE = re.compile(".*cBox-body cBox-body--notification-error.*")

gcontext = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
locale.setlocale(locale.LC_ALL, 'de_DE.UTF-8')


def crawlSearchPages(searchPages, db):
    foundItems = set()
    for searchPage in searchPages:
        items = crawlSearchPage(searchPage, db)
        foundItems.update(items)
    return foundItems


# TODO: maybe refactor, iterate and persist items in db outside of the method
def crawlSearchPage(nextPage, db):
    foundItems = set()

    while True:
        pageNumberMatch = PATTERN_URL_PAGE_NUMBER.search(nextPage)
        if pageNumberMatch:
            print("Mining: {}".format(pageNumberMatch.group(1)))
        else:
            print("Mining: 1 (initial)")

        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:48.0) Gecko/20100101 Firefox/48.0'}
            html = requests.get(nextPage, headers=headers)
            if isRobotDetected(html.content.decode('utf-8')):
                return
        except Exception as e:
            print("Failed to urlopen with {}".format(e))
            return

        htmlContent = html.content
        hexDigestOfNextPage = hashlib.md5(nextPage.encode('utf-8')).hexdigest()
        print("{}: {}".format(hexDigestOfNextPage, nextPage))
        with open("tmp/{}.html".format(hexDigestOfNextPage), 'w') as outfile:
            outfile.write(htmlContent.decode("utf-8"))

        bsObj = BeautifulSoup(htmlContent, "html5lib")

        # iterate inside of the single search page, over items on the page
        for itemDiv in bsObj.findAll("div", {"class": re.compile(".*x-body--resultitem.*")}):
            # TODO: check with md5 for changes in the block
            summary = itemDiv.findAll("div", {"class": re.compile(".*g-col-9.*")})[0].get_text()

            aList = itemDiv.findAll("a", {"class": re.compile(".*result-item.*")})

            try:
                a = aList.pop()
            except Exception as e:
                print("Failed on URL: {} with {}".format(nextPage, e))
                continue

            id_ = a.attrs["data-ad-id"]

            if db.find_one({"id": id_}):
                # we assume, that the items on the search page was ordered by creation time.
                # as consequence, break out as soon as we see a known item.
                return foundItems
                # continue

            item = {"id": id_,
                    "isMined": False,
                    "summary": summary,
                    "firstSeenOn": datetime.now(),
                    "uri": a.attrs["href"]}

            db.insert(item);
            foundItems.add(a)

        # get the url to the next page of search results
        nextPageSpan = bsObj.findAll("span", {"class": re.compile(".*next-resultitems-page.*")})
        if len(nextPageSpan) <= 0:
            return foundItems

        nextPage = nextPageSpan[0].attrs["data-href"]

    return foundItems


def getText(bsObj, tag, tagClass, regex):
    found = bsObj.find(tag, {tagClass: regex})
    return found.get_text() if found else ''


def getTextByRegex(htmlContent, regex, groupNum):
    search = re.search(regex, htmlContent.decode("utf-8"))
    if search:
        return search.group(groupNum)
    else:
        return ""


def crawlSingleItemForGone(dbItem, forceIsGoneCheck=False):
    # do not crawl over items, which we have seen in near past
    if "lastSeenOn" in dbItem:
        delta = datetime.now() - dbItem['lastSeenOn']
        # print("{} ###### {} ## {}".format(delta, dbItem['lastSeenOn'], delta.days))
        # 86400: seconds in the day #
        # 43200: seconds in the 12 hours #
        if (forceIsGoneCheck):
            # check the isGone
            print("!", end='', flush=True)
        elif (delta.days <= 1):
            print(";", end='', flush=True)
            return dbItem

    try:
        # urlopen1 = urlopen(dbItem["uri"], context=gcontext)
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:48.0) Gecko/20100101 Firefox/48.0'}
        html = requests.get(dbItem["uri"], headers=headers)

        if (isRobotDetected(html) or html.status_code == 404):
            handle404PageNotFound(dbItem)
        else:
            print(".", end='', flush=True)
            dbItem['lastSeenOn'] = datetime.now()
    except HTTPError as e:
        handle404PageNotFound(dbItem, e)
    return dbItem


def isRobotDetected(htmlContent):
    if "Are you a human?" in htmlContent:
        print("\n\n!!We are catched!!\n\n", end='', flush=True)
        return True
    return False


def handle404PageNotFound(dbItem, e=None):
    print(":", end='', flush=True)
    # check if the item is still available online
    dbItem["goneOn"] = datetime.now()
    if (e != None and e.code == 404):
        print("The page for item is 404, but no idea what happend ", e)
    elif (e != None):
        print("Exception after urlopen {}", e)


def crawlSingleItem(dbItem):
    if "isMined" in dbItem and dbItem["isMined"]:
        print(";", end='', flush=True)
        return dbItem

    # TODO: add check for exclusion

    # do not crawl over items, which we have seen in near past
    if "lastSeenOn" in dbItem:
        try:
            delta = datetime.now() - dbItem['lastSeenOn']
            if (delta.hours <= 36):
                print(":", end='', flush=True)
                return dbItem
        except Exception:
            pass

    # dbItem = dbItem.next()
    try:
        try:
            uri = dbItem["uri"]
        except Exception:
            dbItem = dbItem.next()
            uri = dbItem["uri"]

        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:48.0) Gecko/20100101 Firefox/48.0'}
        html = requests.get(uri, headers=headers)

        if isRobotDetected(html.content.decode('utf-8')):
            return
    except Exception as e:
        # check if the item is still available online
        print("fail: {} http://suchen.mobile.de/fahrzeuge/details.html?id={}".format(e.code, dbItem["id"]))
        bsObj = BeautifulSoup(e.file.fp, "html5lib")
        itemIsGone = True if "Das gesuchte Inserat ist nicht (mehr) verfügbar" in bsObj \
            .find("div", {"class": DIV_CLASS_ERROR_MESSAGE}) \
            .get_text() else False
        if itemIsGone:
            dbItem["goneOn"] = datetime.now()
            return dbItem

    # print("PASS: 200 http://suchen.mobile.de/fahrzeuge/details.html?id={}".format(dbItem["id"]))

    # htmlContent = html.read()
    htmlContent = html.content

    # Parse the string in <script> tag
    # "adSpecificsMake":"Opel","adSpecificsMakeId":19000,"adSpecificsModel":"Corsa","adSpecificsModelId":10,"adSpecificsMakeModel":"Opel Corsa"
    #

    adDataJson = json.loads(getTextByRegex(htmlContent, r"mobile\.dart\.setAdData\((.*)\)", 1))
    try:
        make = adDataJson["ad"]["specifics"]["make"]
        model = adDataJson["ad"]["specifics"]["model"]
    except Exception as e:
        print(e)

    bsObj = BeautifulSoup(htmlContent, "html5lib")
    idWeb = bsObj.find("div", {"class": re.compile(".*parking-block.*")}).attrs["data-parking"]

    # pure text, often with units like "7000 km" etc.
    price = getText(bsObj, "span", "class", SPAN_CLASS_PRICE)
    kmstand = getText(bsObj, "div", "id", DIV_ID_KMSTAND)
    power = getText(bsObj, "div", "id", DIV_ID_POWER)
    fuel = getText(bsObj, "div", "id", DIV_ID_FUEL)
    emissionClass = getText(bsObj, "div", "id", DIV_ID_EMISSION_CLASS)
    emissionSticker = getText(bsObj, "div", "id", DIV_ID_EMISSION_STICKER)
    firstRegistration = getText(bsObj, "div", "id", DIV_ID_FIRST_REGISTRATION)
    numOfPrevOwners = getText(bsObj, "div", "id", DIV_ID_NUM_OF_PREV_OWNERS)
    numOfSeats = getText(bsObj, "div", "id", DIV_ID_NUM_OF_SEATS)

    # TODO: add geocoded current address of the vehicle. Can be used for heatmap on maps
    address = getText(bsObj, "p", "id", re.compile(".*rbt-seller-address.*"))

    dbItem['id'] = idWeb
    dbItem['priceEur'] = locale.atof(PATTERN_EURO.search(price).group(1).replace(".", "")) if price else ''
    dbItem['kmState'] = locale.atoi(PATTERN_KMSTAND.search(kmstand).group(1).replace(".", "")) if kmstand else ''
    dbItem['power'] = int(PATTERN_POWER.search(power).group(1)) if power else ''
    dbItem['fuel'] = fuel if fuel else ''
    dbItem['emissionClass'] = emissionClass if emissionClass else ''
    dbItem['emissionSticker'] = PATTERN_EMISSION_STICKER.search(emissionSticker).group(0) if emissionSticker else ''
    dbItem['firstRegistration'] = datetime.strptime(firstRegistration, "%m/%Y") if firstRegistration else ''
    dbItem['numOfPrevOwners'] = int(numOfPrevOwners) if numOfPrevOwners else ''
    dbItem['numOfSeats'] = int(numOfSeats) if numOfSeats else ''
    dbItem['address'] = address
    dbItem['isMined'] = True
    dbItem['makeModel'] = "{}/{}".format(make, model) if make and model else ''
    dbItem['goneOn'] = ''
    dbItem['lastSeenOn'] = datetime.now()

    print(".", end='', flush=True)

    return dbItem

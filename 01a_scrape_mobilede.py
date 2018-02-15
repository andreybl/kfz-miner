from pymongo import MongoClient

import crawling

# note: the radius is like "rd=100" in km
searchPages = [

    # sevel (fiat/pegeuot/citroen), ab 2008, bis 250K km, radius 200km
    "https://suchen.mobile.de/fahrzeuge/search.html?cn=DE&damageUnrepaired=NO_DAMAGE_UNREPAIRED&fuels=DIESEL&fuels=HYBRID_DIESEL&gn=81375%2C+Hadern%2C+M%C3%BCnchen%2C+Bayern&isSearchRequest=true&ll=48.1211184%2C11.4860576&makeModelVariant1.makeId=8800&makeModelVariant1.modelId=19&makeModelVariant2.makeId=19300&makeModelVariant2.modelId=25&makeModelVariant3.makeId=5900&makeModelVariant3.modelId=10&maxMileage=250000&maxPowerAsArray=PS&minFirstRegistrationDate=2008-01-01&minPowerAsArray=PS&rd=250&scopeId=C",

    # crafter, sprinter, master, radius 200km
    "https://suchen.mobile.de/fahrzeuge/search.html?ambitAddress=81375%2C+Hadern%2C+M%C3%BCnchen%2C+Bayern&damageUnrepaired=NO_DAMAGE_UNREPAIRED&fuels=DIESEL&fuels=HYBRID_DIESEL&isSearchRequest=true&maxMileage=250000&minFirstRegistrationDate=2008-01-01&ms=17200%3B116&ms=20700%3B16&ms=25200%3B3&od=down&sb=doc&scopeId=C&sset=1517303889&ssid=23943616&userPosition=48.1211%2C11.4861&zipcodeRadius=250"

];

# sort results by time to allow efficient scraping: already scraped items are ignored
searchPages = ["{}&sortOption.sortBy=creationTime&sortOption.sortOrder=DESCENDING".format(updatedUrl) for updatedUrl in
               searchPages]

connection = MongoClient("mongodb://admin:mypasswd@localhost", port=27017)
db = connection.admin.mobilede

# dbItem = db.find_one({"id": "247984799"})
# dbItem = crawling.crawlSingleItem(dbItem, True)
# exit(0)

foundItems = crawling.crawlSearchPages(searchPages, db)
print("New items from search page: {}".format(len(foundItems)))

connection.close()

print("=================================================================================")
print("=================================================================================")

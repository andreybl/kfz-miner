import locale
from datetime import datetime, date, time
from bson import ObjectId
from pymongo import MongoClient
import re

locale.setlocale(locale.LC_ALL, 'de_DE.UTF-8')

DAYS_IN_YEAR = 365

PATTERN_PLZ = re.compile("(\d{5})")

connection = MongoClient("mongodb://admin:mypasswd@localhost", port=27017)
db = connection.admin.mobilede

# update only mined. For instance, we update numOfOwners with "1", if it is not set.
# but we must be sure in this case, that the scraper did not try to resolve this
# value from the web
cursor = db.find({"isMined" : True})

counterAll = 0
counterNoFirstRegistration = 0
counterExcludedFromRegression = 0
for row in cursor:

    if not row["numOfPrevOwners"]:
        row["numOfPrevOwners"] = 1

    if "inputIsRegressionExcluded" in row.keys() and row["inputIsRegressionExcluded"]:
        # print("Excluded from regression: {}. Skipping.".format(row["id"]))
        counterExcludedFromRegression += 1
        continue

    summary = row["summary"]
    if summary.lower().find("pritsche") != -1 or summary.lower().find(" doka ") != -1:
        row["inputIsRegressionExcluded"] = 1

    if "address" in row.keys() and row["address"]:
        plzSearch = PATTERN_PLZ.search(row["address"])
        if plzSearch:
            plz = plzSearch.group(0)
            row["plz"] = plz

    if "firstRegistration" in row.keys() and row["firstRegistration"]:
        diffDays = (datetime.now() - row["firstRegistration"]).days
        derivedKmPerYear = (row["kmState"]/diffDays) * DAYS_IN_YEAR
        row["derivedKmPerYear"] = int(derivedKmPerYear)

    selector = {"_id" : row["_id"]}
    db.update({"_id":row["_id"]}, row)

    counterAll += 1

print("Processed {:.0f} items".format(counterAll))
connection.close()


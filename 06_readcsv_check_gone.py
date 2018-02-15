import csv
import locale

from bson import ObjectId
from pymongo import MongoClient

import commons
import crawling

locale.setlocale(locale.LC_ALL, 'de_DE.UTF-8')

connection = MongoClient("mongodb://admin:mypasswd@localhost", port=27017)
db = connection.admin.mobilede

csvFields = commons.mongoDbCollectionToFields(db)

csvInputFields = [inputField for inputField in csvFields if inputField.startswith("input")]

dumpFile = "/Users/agolovko/Google Drive/Documents/Wohnmobile/price_observed_vs_predicted.csv"
counter = 0
with open(dumpFile, 'r+', encoding="ISO-8859-1") as csvFile:
    importedData = csv.DictReader(csvFile, delimiter=';')

    for row in importedData:
        counter += 1
        selector = {"_id": ObjectId(row["_id"])}
        dbItem = db.find_one(selector)
        for fieldName in csvInputFields:
            dbItem[fieldName] = row[fieldName]

        dbItem = crawling.crawlSingleItemForGone(dbItem, True)
        db.update(selector, dbItem)

    connection.close()

    print("Imported {:.0f} items from {} for fields {}".format(counter, dumpFile, csvInputFields))
    print("*** DONE *** DONE **")

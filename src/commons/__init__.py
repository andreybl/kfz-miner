from __future__ import (absolute_import, division, print_function, unicode_literals)

__author__ = 'agolovko'

import csv
import re
import warnings
import os
import pandas as pd
import commons
import crawling
import json

from datetime import datetime
from bson import ObjectId
from bson.code import Code
from pymongo import MongoClient

# locale.setlocale(locale.LC_ALL, 'de_DE.UTF-8')
DAYS_IN_YEAR = 365
PATTERN_PLZ = re.compile("(\d{5})")


def mongoDbCollectionToFields(db):
    map = Code('function() {for (var key in this) { emit(key, null); }}')
    reduce = Code('function(key, stuff) { return null; }')
    result = db.map_reduce(map, reduce, "myresults")
    csvFields = result.distinct("_id")
    return csvFields


def deriveFurtherField():
    connection = MongoClient(os.environ["MONGODB_URL"])
    db = connection.admin.mobilede

    # update only mined. For instance, we update numOfOwners with "1", if it is not set.
    # but we must be sure in this case, that the scraper did not try to resolve this
    # value from the web
    cursor = db.find({"isMined": True})

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
            derivedKmPerYear = (row["kmState"] / diffDays) * DAYS_IN_YEAR
            row["derivedKmPerYear"] = int(derivedKmPerYear)

        selector = {"_id": row["_id"]}
        db.update({"_id": row["_id"]}, row)

        counterAll += 1

    print("Processed {:.0f} items".format(counterAll))
    connection.close()


def dumpForAnalysis():
    connection = MongoClient(os.environ["MONGODB_URL"])
    db = connection.admin.mobilede

    csvFields = mongoDbCollectionToFields(db)

    #
    # dump the dB into the CSV. The CSV is an intermediarry data file, with purpose:
    # 1) make it easier to see, what data we are working with
    # 2) convenient input format for data analysis
    # 3) contains calculated, reformated etc. values compared to dB

    dumpFile = os.environ['DIR-WORKING'] + "/vehicles.csv"
    with open(dumpFile, 'w') as outfile:

        writer = csv.DictWriter(outfile, fieldnames=csvFields, delimiter=';')
        writer.writeheader()

        cursor = db.find({})
        counterAll = 0
        counterNoFirstRegistration = 0
        counterExcludedFromRegression = 0
        for row in cursor:
            if "inputIsRegressionExcluded" in row.keys() and row["inputIsRegressionExcluded"]:
                # print("Excluded from regression: {}. Skipping.".format(row["id"]))
                counterExcludedFromRegression += 1
                continue
            try:
                counterAll += 1
                writer.writerow(row)
            except Exception as e:
                print("Failed to dump ID {} with '{}'".format(row["id"], e))
                continue

        print("Written {:.0f} rows to CSV".format(counterAll))
        print("Excluded from regression: {:.0f} rows".format(counterExcludedFromRegression))
        connection.close()

    with open(dumpFile, 'r+') as f:
        content = f.read()
        f.seek(0)
        f.truncate()
        f.write(content.replace('unknown', ''))

    print("*** DONE *** DONE **")


def dumpForUser():
    pd.options.display.float_format = '{:.2f}'.format

    # can not run in docker (no ui)
    # init_notebook_mode(connected=True)

    warnings.simplefilter('ignore')

    connection = MongoClient(os.environ["MONGODB_URL"])
    db = connection.admin.mobilede

    with open(os.environ['DIR-CONFIGS'] + '/dumpExpression.json') as json_data:
        expression = json.load(json_data)
        print(expression)

    csvFields = commons.mongoDbCollectionToFields(db)
    dumpFile = os.environ['DIR-DATA'] + "/price_observed_vs_predicted.csv"
    with open(dumpFile, 'w') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=csvFields, delimiter=';')
        writer.writeheader()

        cursor = db.find(expression)

        counter = 0
        for row in cursor:
            counter += 1
            writer.writerow(row)

        print("=============")
        print("Written {:.0f} rows to CSV".format(counter))
        print("=============")
        connection.close()

    print("*** DONE **** DONE ***")


def readCsvCheckGone():
    connection = MongoClient(os.environ["MONGODB_URL"])
    db = connection.admin.mobilede

    csvFields = commons.mongoDbCollectionToFields(db)

    csvInputFields = [inputField for inputField in csvFields if inputField.startswith("input")]

    dumpFile = os.environ['DIR-DATA'] + "/price_observed_vs_predicted.csv"
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

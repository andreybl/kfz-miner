import locale
from datetime import datetime, date, time
from pymongo import MongoClient
import csv
import commons

locale.setlocale(locale.LC_ALL, 'de_DE.UTF-8')

DAYS_IN_YEAR = 365

connection = MongoClient("mongodb://admin:mypasswd@localhost", port=27017)
db = connection.admin.mobilede

csvFields = commons.mongoDbCollectionToFields(db)

#
# dump the dB into the CSV. The CSV is an intermediarry data file, with purpose:
# 1) make it easier to see, what data we are working with
# 2) convenient input format for data analysis
# 3) contains calculated, reformated etc. values compared to dB

dumpFile = "tmp/vehicles.csv"
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


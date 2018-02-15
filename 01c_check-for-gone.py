import locale

from pymongo import MongoClient

import crawling

locale.setlocale(locale.LC_ALL, 'de_DE.UTF-8')

connection = MongoClient("mongodb://admin:mypasswd@localhost", port=27017)
db = connection.admin.mobilede

# examples for find:
#   {"id": "237309500", 'goneOn': { '$exists': False }}
#   {"_id": "5a6f188872dea147804ebab4"}
#

# DEBUG: debug why isGone can not be checked for specific item
# cursor = db.find({"id": "254027675"})
cursor = db.find({"$or": [{"goneOn": {"$eq": ''}}, {"goneOn": {"$exists": False}}]})

print("Going to check for gone for {} items".format(cursor.count()))
for dbItem in cursor:
    try:
        dbItem = crawling.crawlSingleItemForGone(dbItem)
        db.update({"_id": dbItem["_id"]}, dbItem)
    except Exception as e:
        print("Failed to crawl id {} with {}".format(dbItem["id"], e))

print("*** DONE *** DONE **")

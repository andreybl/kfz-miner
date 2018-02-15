import locale
from pymongo import MongoClient
import crawling

locale.setlocale(locale.LC_ALL, 'de_DE.UTF-8')

connection = MongoClient("mongodb://admin:mypasswd@localhost", port=27017)
db = connection.admin.mobilede

# examples for find:
#   {"id": "237309500", 'goneOn': { '$exists': False }}
#
cursor = db.find({"isMined": False, "$or": [{"goneOn": {"$eq": ''}}, {"goneOn": {"$exists": False}}]})
print("Going to scrape at most {} items".format(cursor.count()))
for dbItem in cursor:
    try:
        dbItem = crawling.crawlSingleItem(dbItem)
        db.update({"_id" : dbItem["_id"]}, dbItem)
    except Exception as e:
        print("Failed to crawl id {} with {}".format(dbItem["id"], e))


print("*** DONE *** DONE **")



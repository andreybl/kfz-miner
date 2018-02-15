__author__ = 'agolovko'
from bson.code import Code

def mongoDbCollectionToFields(db):
    map = Code('function() {for (var key in this) { emit(key, null); }}')
    reduce = Code('function(key, stuff) { return null; }')
    result = db.map_reduce(map, reduce, "myresults")
    csvFields = result.distinct("_id")
    return csvFields

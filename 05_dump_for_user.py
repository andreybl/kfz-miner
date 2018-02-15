from __future__ import (absolute_import, division, print_function, unicode_literals)

import csv
import re
import warnings

import pandas as pd
from plotly.offline import init_notebook_mode
from pymongo import MongoClient

import commons

pd.options.display.float_format = '{:.2f}'.format

init_notebook_mode(connected=True)

warnings.simplefilter('ignore')

connection = MongoClient("mongodb://admin:mypasswd@localhost", port=27017)
db = connection.admin.mobilede

csvFields = commons.mongoDbCollectionToFields(db)
# dumpFile = "output/price_observed_vs_predicted.csv"
dumpFile = "/Users/agolovko/Google Drive/Documents/Wohnmobile/price_observed_vs_predicted.csv"
with open(dumpFile, 'w') as outfile:
    writer = csv.DictWriter(outfile, fieldnames=csvFields, delimiter=';')
    writer.writeheader()

    expression = {
        "goneOn": {"$eq": ""},
        "inputIsRegressionExcluded": {"$eq": ""},
        "address": re.compile("DE-(\d{5})"),  # vehicles from germany (match by PLZ)
        # "plz": re.compile("^8"),
        # "derivedKmPerYear": {"$lte": 30000},
        "$or": [
            # {"makeModel": re.compile("^Volkswagen\/Caddy"),
            #  "firstRegistration": {"$gte": datetime(2009, 1, 1)},
            #  "priceEur": {"$lte": 8000}
            #  },
            #
            # {"makeModel": re.compile("^Volkswagen\/T4"),
            #  "firstRegistration": {"$gte": datetime(1999, 1, 1)},
            #  "priceEur": {"$lte": 8000}
            #  },
            #
            # {"makeModel": re.compile("^Volkswagen\/T5"),
            #  "firstRegistration": {"$gte": datetime(2009, 11, 1)},
            #  "priceEur": {"$lte": 8000}
            #  },
            #
            # {"makeModel": re.compile("^Fiat"),
            #  "firstRegistration": {"$gte": datetime(2008, 11, 1)},
            #  "priceEur": {"$lte": 8000}
            #  },
            #
            # {"makeModel": re.compile("^Peugeot"),
            #  "firstRegistration": {"$gte": datetime(2008, 11, 1)},
            #  "priceEur": {"$lte": 8000}
            #  },
            #
            # {"makeModel": re.compile("^Citroën"),
            #  "firstRegistration": {"$gte": datetime(2008, 11, 1)},
            #  "priceEur": {"$lte": 8000}
            #  }

            {"makeModel": re.compile("Sprinter")
                , "priceEur": {"$lte": 15000}
             },
            {"makeModel": re.compile("Master")
                , "priceEur": {"$lte": 15000}
             },
            {"makeModel": re.compile("Crafter")
                , "priceEur": {"$lte": 15000}
             },
            {"makeModel": re.compile("Boxer")
                , "priceEur": {"$lte": 15000}
             },
            {"makeModel": re.compile("Jumper")
                , "priceEur": {"$lte": 15000}
             },
            {"makeModel": re.compile("Ducato")
                , "priceEur": {"$lte": 15000}
             }
        ]
    }

    print(expression)
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

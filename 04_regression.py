from __future__ import (absolute_import, division, print_function, unicode_literals)
from plotly.offline import init_notebook_mode
from sklearn.model_selection import cross_val_predict
from sklearn import linear_model
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import csv
from dateutil import parser
from pymongo import MongoClient
from bson.code import Code

# turn off Anaconda warnings
import warnings
import commons

warnings.filterwarnings('ignore')

pd.options.display.float_format = '{:.2f}'.format

init_notebook_mode(connected=True)

warnings.simplefilter('ignore')

connection = MongoClient("mongodb://admin:mypasswd@localhost", port=27017)
db = connection.admin.mobilede

allData = pd.read_csv('tmp/vehicles.csv', delimiter=';')
allDataUnmodified = pd.read_csv('tmp/vehicles.csv', delimiter=';')

# Print some basic data
print("Price of all vehicles: {:6.2f} EUR".format(allData['priceEur'].mean()))

# decide on columns - features and target - with which we are going to work
target_column = 'priceEur'
feature_columns = [ 'id',
                    'kmState',
                    'numOfPrevOwners',
                    'makeModel',
                    'power',
                    'firstRegistration',
                    'derivedKmPerYear',
                    'emissionSticker',
                    'plz',
                    'numOfSeats']

feature_and_target_columns = list(feature_columns)
feature_and_target_columns.append(target_column)
regressionData = allData[feature_and_target_columns]

# transform strings to NaN where appropriate and drop the rows,
# where at least one feature value is missed
prevSize = regressionData.shape[0]
regressionData = regressionData.replace('unknown', np.NaN)
regressionData = regressionData.replace('NaN', np.NaN)
regressionData = regressionData.replace('nan', np.NaN)
regressionData = regressionData.dropna()

# make some features conversion, like from numerical into categorical
regressionData['makeModel'] = regressionData['makeModel'].astype('category').cat.codes
regressionData['plz'] = regressionData['plz'].astype('category').cat.codes
regressionData['firstRegistration'] = regressionData['firstRegistration'].astype('category').cat.codes
regressionData['emissionSticker'] = regressionData['emissionSticker'].astype('category').cat.codes
regressionData['numOfPrevOwners'] = regressionData['numOfPrevOwners'].astype('float64')

# remember the order of IDs, and do not use it in regression
idValues = regressionData['id']
del regressionData['id']
feature_columns.remove('id')
feature_and_target_columns.remove('id')

print("Left {}/{} entries after clean up and drop".format(regressionData.shape[0], prevSize))

featuresData = regressionData[feature_columns]
y = regressionData[target_column]

# Calculate Regression
regr = linear_model.LinearRegression(normalize=True)

regr.fit(featuresData, y)
predictions = regr.predict(featuresData)

print()
zipped = zip(feature_columns, regr.coef_)
for name, coef in zipped:
    print("{}: {}".format(name, coef))

predicted = cross_val_predict(regr, featuresData, y, cv=5)

# x - predicted values
# y - actual values
fix, ax = plt.subplots()
ax.scatter(y, predicted, color='green', s=9)
ax.plot([y.min(), y.max()], [y.min(), y.max()], 'k--', lw=1)
ax.set_xlabel("Observed")
# TODO: add regression coefficient to the plot
ax.set_ylabel("Predicted")

plt.savefig('output/price_observed_vs_predicted.png')

zipped = zip(idValues, y, predicted)

for itemId, observedValue, predictedValue in zipped:
    itemIdStr = str(itemId)
    origRow = allData.loc[allData['id'] == itemId]
    goneOnStr = "{}".format(origRow['goneOn'].asobject[0])
    firstSeenOn = "{}".format(origRow['firstSeenOn'].asobject[0])

    if not "nan" in goneOnStr:
        daysOnline = (parser.parse(goneOnStr) - parser.parse(firstSeenOn)).days
    else:
        daysOnline = -1

    try:
        derivedKmPerYear = "{:.0f}".format(origRow['derivedKmPerYear'].asobject[0])
    except Exception as e:
        print("Failed on derivedKmPerYear, id {} with {}".format(itemId, e))

    dbItem = db.find_one({"id": itemIdStr})
    dbItem["daysOnline"] = daysOnline
    dbItem["derivedKmPerYear"] = derivedKmPerYear
    dbItem["predictedPrice"] = '{:.0f}'.format(predictedValue)
    dbItem["diffSaving"] = int(predictedValue - observedValue)
    dbItem["diffSavingPercent"] = '{:.03f}'.format((predictedValue - observedValue)/observedValue)
    dbItem["inputIsRegressionExcluded"] = ""
    dbItem["inputIsFavoured"] = ""

    result = db.update({"id": itemIdStr}, dbItem)

print("*** DONE **** DONE ***")
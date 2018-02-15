# Intro

The motivation of the current code is to find the vehicles proposed on the mobile.de for attractive price.

The code scrapes the mobile.de and apply regression analysis to its data.

# Mongo DB with docker
The data is saved in the mongodb.

docker exec -it dscience_mongodb /bin/bash
docker exec -it dscience_mongodb mongo admin

db.auth("admin", "mypasswd")
show collections
db.mobilede.find().size()
db.mobilede.find({}, {firstSeenOn : 1}).size()
db.mobilede.find({firstSeenOn: "{$exists: False}"}).size()


db.createCollection("mobiledeCopy")

# Debug the app
## Start debug
## Debug when searching for gone

# TODO

* put the urls which are used for scraping into a separate file

* dockerize the kfz-scraper, provide docker-compose.yml to run in docker
  - use volume to input URLs to dump
  - use volume to export CSV result

* control the command over the console from docker container, see .sh files for prototype of commands

* clean log output to the console


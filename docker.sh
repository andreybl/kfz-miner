# build base image, takes time
docker build -t agofm/pybase --file ./Dockerfile.base .

# build image with script, fast
docker build -t agofm/simple .

#
# execute the scraper cli. Run both scraper and db. Db container is NOT removed after exit,
# but the scraper is removed.
#
docker-compose run --rm kfzscraper

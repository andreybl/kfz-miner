FROM agofm/pybase

RUN mkdir -p /dir-working
RUN mkdir -p /dir-data

COPY ./src /src
COPY ./dir-configs /dir-configs
COPY .env.docker /src/.env

CMD ["python3", "/src/simple.py"]
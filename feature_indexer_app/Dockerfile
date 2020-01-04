FROM python:3.6.3

ENV BIND_PORT 7000
ENV REDIS_HOST localhost
ENV REDIS_PORT 6379
ENV ES_HOST localhost
ENV ES_PORT 9200
ENV ZMQ_SERVER_HOST localhost
ENV ZMQ_SERVER_PORT 5454

COPY ./requirements.txt /requirements.txt

RUN pip install -r /requirements.txt

COPY . ./

EXPOSE $BIND_PORT

CMD [ "python", "/feature_indexer_app_redis.py" ]
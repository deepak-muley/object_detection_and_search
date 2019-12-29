FROM python:3.6.3

ENV BIND_PORT 5000
ENV REDIS_HOST localhost
ENV REDIS_PORT 6379
ENV ZMQ_SERVER_HOST localhost
ENV ZMQ_SERVER_PORT 5454

RUN adduser video_user --uid 10000 --ingroup video --disabled-password

COPY ./requirements.txt /requirements.txt

RUN pip install -r /requirements.txt

COPY ./*.py ./
COPY ./data ./data

EXPOSE $BIND_PORT

USER video_user

CMD [ "python", "/video_frame_extraction_app_redis.py" ]
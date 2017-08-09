FROM python:3.6

MAINTAINER Mark Palmeri <mlp6@duke.edu>

RUN apt-get update \
    && pip install -r requirements.txt

FROM python:3.5

MAINTAINER Mark Palmeri <mlp6@duke.edu>

RUN apt-get update \
    && pip install numpy scipy pytest pytest-cov

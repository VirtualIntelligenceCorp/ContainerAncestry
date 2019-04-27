FROM python:3.7

RUN pip3 install docker-registry-client neo4j

COPY scripts/ /scripts

ENV PATH=$PATH:/scripts

CMD digest.py

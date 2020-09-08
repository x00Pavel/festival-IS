FROM postgres:latest

ENV POSTGRES_USER=admin
ENV POSTGRES_PASSWORD=admin
ENV POSTGRES_DB=festival

ADD 1-schema.sql /docker-entrypoint-initdb.d
ADD 2-data.sql /docker-entrypoint-initdb.d
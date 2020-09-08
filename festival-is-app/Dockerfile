FROM python:3.8-alpine
WORKDIR /src
RUN apk update && apk add postgresql-dev gcc python3-dev musl-dev
RUN pip install flask
RUN pip install psycopg2
COPY ./src /src
EXPOSE 5000
CMD python main.py
 
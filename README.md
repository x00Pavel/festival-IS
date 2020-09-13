To create database tables: `python src/manage.py init_db`

To fill database tables with information: `python src/manage.py import_db` (From src/data folder !fileName=tableName! without priority number and .csv)

To backup information from databes: `python src/manage.py export_db` (To src/data/backup/{datetime>}/ folder)

To drop all database tables: `python src/manage.py drop_db`


FOR LOCAL TEST PLEASE ADD TO YOURS .ENV FILES

```
# NETWORK TEST URL

# DATABASE_URL=postgres://****:****@****:5432/****   <--->   you know it 

# LOCAL TEST URL
# To start local database use: docker-compose up -d; 
# To stop local database use: docker-compose down --rmi all
# Standard local URL: postgres://admin:admin@localhost:5432/festival (you can change it in docker-compose file)

# DATABASE_URL=postgres://admin:admin@localhost:5432/festival
```

To use local db comment our remote db and uncomment local db
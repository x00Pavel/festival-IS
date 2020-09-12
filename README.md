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
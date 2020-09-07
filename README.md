{WHAT_APP} Application

This is an implementation of the {FUTURE_PROJECT}, {SHORT_DESCRIPTION}

This project is consisted of three parts:

- PostgreSQL database
- Golang backend
- Angular frontend

---

### Prerequisites to work with Docker 

In order to run this application you need to install two tools: **Docker** & **Docker Compose**.

Instructions how to install **Docker** on [Ubuntu](https://docs.docker.com/install/linux/docker-ce/ubuntu/), [Windows](https://docs.docker.com/docker-for-windows/install/) , [Mac](https://docs.docker.com/docker-for-mac/install/) .

**Docker Compose** is already included in installation packs for *Windows* and *Mac*, so only Ubuntu users needs to follow [this instructions](https://docs.docker.com/compose/install/) .


---

### How to run it?

An entire application can be ran with a single command in a terminal:

```
$ docker-compose up -d
```

The entry point for a user is a website which is available under the
address: **http://localhost:4200/**

To see generated images:

```
docker ps
```

If you want to stop it use following command:

```
$ docker-compose down
```

---

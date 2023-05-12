# 🛠 Educational project
The service allows you to register couriers, orders. Calculate the rating and salary of couriers based on completed orders, as well as optimally distribute orders to maximize the number of completed orders per shift of the courier, as well as to minimize the cost.

The following tools were used in the backend part of the project:

- FastAPI
- SQLAlchemy
- Alembic
- Pytest

The infrastructure part used:
- PostgreSQL
- Docker
- Uvicorn

# 🚀 Project installation
Install Docker and docker-compose:
```sh
sudo apt-get update
sudo apt install docker.io
sudo apt-get install docker-compose-plugin
```
Clone repository:
```sh
git clone git@git.yandex-academy.ru:school/2023-06/enrollments/8709-ivan-drobyshev7-97.git
```
##### 🐳 Running Docker containers
When deploying to a server, you need to create a file with the values of the .env variables in the docker_compose folder.
```sh
sudo docker-compose  up -d --build
```

[Api documentation](http://localhost:8080/api/openapi)

 # :dependabot: Project Tests
To run tests You need to create a file with the values of the .env variables before that

# :smirk_cat: Authors
Drobyshev Ivan


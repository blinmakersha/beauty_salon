#!/bin/bash

pip install -r requirements/requirements.txt

# create docker container
docker run -d \
--name container-BS \
-p 5525:5432 \
-v $HOME/postgresql/crypto_server:/var/lib.postgresql/docker_container_BS \
-e POSTGRES_PASSWORD=242002 \
-e POSTGRES_USER=app \
-e POSTGRES_DB=BeautySalon \
postgres
sleep 2

python3 requirements/setup_env.py

# create tables
cd beauty_salon
python3 manage.py makemigrations
python3 manage.py migrate
sleep 3

# mount all changes
export PGPASSWORD=242002
psql -h 127.0.0.1 -p 5525 -U app BeautySalon -f requirements/db_init.ddl


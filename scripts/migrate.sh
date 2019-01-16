#!/usr/bin/env bash
if [ -n "$1" ]; then
    export $(grep -v '^#' .env | xargs) &&
    docker-compose run -p 3306:3306 -d database &&
    echo Waiting 30 seconds so the database come online... &&
    sleep 30 &&
    echo Done waiting. &&
    mysql --protocol=TCP -u root -p$MYSQL_ROOT_PASSWORD < $1 &&
    docker-compose down &&
    docker-compose up --build -d &&
    sleep 60 &&
    docker-compose down &&
    docker-compose run -p 3306:3306 -d database &&
    cd RadioDns-PlugIt &&
    source venv/bin/activate &&
    python postmigration.py $MYSQL_ROOT_PASSWORD &&
    cd .. &&
    docker-compose down &&
    docker-compose up -d &&
    unset $(grep -v '^#' .env | sed -E 's/(.*)=.*/\1/' | xargs) &&
    echo Migration done.
else
    echo Usage: ./migrate.sh path_to_mysqldump
fi

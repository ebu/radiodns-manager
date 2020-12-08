# To do the migration

Prepare the DB:

    python manage.py makemigrations
    python manage.py migrate
    python manage.py create_ecc_records
    python manage.py create_language_records

Migrate:

    python manage.py loaddata fixtures/json_fixtures/new_organizations.json --app manager.Organization
    python manage.py loaddata fixtures/json_fixtures/new_logo_images.json --app manager.LogoImage
    python manage.py loaddata fixtures/json_fixtures/new_clients.json --app clients.Client
    python manage.py loaddata fixtures/json_fixtures/new_stations.json --app stations.Station
    python manage.py loaddata fixtures/json_fixtures/new_station_instances.json --app stations.StationInstance

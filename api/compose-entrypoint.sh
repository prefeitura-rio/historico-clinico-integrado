#!/bin/bash
# Run aerich init-db if migrations folder does not exist
if [ ! -d "./migrations/app/" ]; then
    echo "Migrations folder does not exist, ASSUMING FIRST RUN"

    echo "Running aerich init-db to create initial migration"
    aerich init-db || true

else
    echo "./migrations/app/ folder exist, skipping initialization"
fi

echo "Running Migrations"
aerich upgrade

echo "Atempt to create user"
python create_user.py --create-admin

echo "Initializing Database Data"
python database_init_table.py --entity-model-name Gender --source-csv-name gender --conflict-column slug
python database_init_table.py --entity-model-name Race --source-csv-name race --conflict-column slug
python database_init_table.py --entity-model-name Nationality --source-csv-name nationality --conflict-column slug
python database_init_table.py --entity-model-name ConditionCode --source-csv-name conditioncode --conflict-column type value
python database_init_table.py --entity-model-name Country --source-csv-name country --conflict-column code
python database_init_table.py --entity-model-name State --source-csv-name state --conflict-column code
python database_init_table.py --entity-model-name City --source-csv-name city --conflict-column code

# Start server
uvicorn app.main:app --host 0.0.0.0 --port 80
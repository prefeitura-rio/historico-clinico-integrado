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

#echo "Initializing Database Data"
#python database_init_table.py

# Start server
uvicorn app.main:app --host 0.0.0.0 --port 80
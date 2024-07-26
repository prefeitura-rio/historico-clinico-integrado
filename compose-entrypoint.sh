#!/bin/bash

# ---------------------
# Migration Handling
# ---------------------

# Run aerich init-db if migrations folder does not exist
if [ ! -d "./migrations/app/" ]; then
    echo "Migrations folder does not exist, ASSUMING FIRST RUN"

    echo "Running aerich init-db to create initial migration"
    aerich init-db || true

else
    echo "./migrations/app/ folder exist, skipping initialization"
fi

aerich upgrade

# ----------------------
# Data Initialization
# ----------------------

# Creating admin user (in background)
python create_user.py --create-admin &

# Verify/create data in constant tables (in background)
python database_init_table.py &

# ----------------------
# Begin Server
# ----------------------
uvicorn app.main:app --host 0.0.0.0 --port 80
#!/bin/bash

# Run aerich init-db
aerich init-db

# Run migrations
aerich upgrade

# Start server
uvicorn app.main:app --host 0.0.0.0 --port 80
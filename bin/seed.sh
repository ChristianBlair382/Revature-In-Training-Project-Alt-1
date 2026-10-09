#!/usr/bin/env bash

set -e

TARGET = "{$:local}" # $1 is the first argument typed after the script name

ROOT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"

# redirects the database to be seeded depending on the value of $1
if [ "$TARGET" == "local" ]; then
    # TODO: Please put your postgres login details here
    export DATABASE_URL = "postgresql+asyncpg://postgres:<password>@127.0.0.1:5432/agricore_dev_2478"
    PSQL_HOST="127.0.0.1"
    PSQL_DB="agricore_dev_2478"
elif [ "$TARGET" == "rds" ] then 
    # TODO: Please put your postgres login details here
    export DATABASE_URL = "postgresql+asyncpg://<user>:<password>@<your-rds-endpoint>:5432/agricore_2478"
    PSQL_HOST="<your-rds-endpoint>"
    PSQL_DB="agricore_2478"
else # Catches any TARGET that isn't either of the provided
    echo "Usage: bin/seed.sh [local|rds]"
    exit 1
fi

echo "Seeding target: $TARGET"
cd "$ROOT_DIR/backend"

# Step 1: Create tables.
python -m scripts.create_tables
# Step 2: Seed tables with dummy data.
python -m scripts.seed_tables

echo "Seed complete for $TARGET"
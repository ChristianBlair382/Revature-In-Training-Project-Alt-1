#!/usr/bin/env bash

set -e

echo "== AGRICORE LOCAL SETUP =="

ROOT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"

require_file() {
    local file="$ROOT_DIR/$1"
    if [[ ! -f "$file" ]]; then
        printf 'Missing prerequisite: %s\nExpected file: %s\n' "$1" "$file" >&2
        exit 1
    fi
}

require_file "backend/requirements.txt"
require_file "frontend/package.json"

if [[ ! -f "$ROOT_DIR/backend/.env" ]]; then
    require_file "backend/.env.example"
fi

cd "$ROOT_DIR/backend"

if [ ! -d ".venv" ]; then
    echo "Virtual Environment not found. Creating new .venv..."
    python -m venv .venv
fi

case "$(uname -s)" in
    MINGW*|MSYS*|CYGWIN*)
        echo "Windows OS detected. Activating via Windows..."
        source .venv/Scripts/activate
        ;;
    *)
        echo "Linux/macOS detected. Activating via Linux/macOS..."
        source .venv/bin/activate
        ;;
esac

pip install -r requirements.txt

if [ ! -f ".env" ]; then
    echo ".env not found. Copying from .env.example..."
    echo "Fill in real values in backend/.env before running this application"
    cp .env.example .env
fi

cd ../frontend
npm install

echo "Setup Complete!"
#!/usr/bin/env bash
# exit on error
set -o errexit

echo "Installing backend dependencies..."
pip install -r requirements.txt

echo "Building frontend..."
cd frontend
npm install
npm run build
echo "Running database migrations..."
cd ../backend
alembic upgrade head

echo "Build complete."

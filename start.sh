#!/usr/bin/env bash
cd "$(dirname "$0")"
echo "Starting AHMZ Artisan Clothing E-Commerce server..."
./venv/bin/python manage.py runserver 0.0.0.0:8000

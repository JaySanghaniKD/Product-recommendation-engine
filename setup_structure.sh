#!/bin/bash

# Create folder structure inside current directory (already in genai_project/)
mkdir -p app/{core,services,models,db,utils}
mkdir -p scripts

# Create Python module files
touch app/__init__.py
touch app/main.py

touch app/core/__init__.py
touch app/core/search_agent.py

touch app/services/__init__.py
touch app/services/cart_service.py
touch app/services/history_service.py

touch app/models/__init__.py
touch app/models/schemas.py

touch app/db/__init__.py
touch app/db/database.py

touch app/utils/__init__.py

# Script file
touch scripts/ingest_data.py

# Root files
touch .env
touch requirements.txt
touch README.md

echo "✅ Folder structure created inside $(pwd)"

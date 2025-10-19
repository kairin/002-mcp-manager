#!/bin/bash

# Local CI/CD script

echo "Running local CI/CD..."

echo "Linting..."
cd web && npx prettier --check .

echo "Testing..."

echo "Building..."
cd web && npm run build




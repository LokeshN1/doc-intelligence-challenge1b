# This script builds the Docker image for the Persona-Driven Document Intelligence System.

#!/bin/bash   
set -e

echo "Building Persona-Driven Document Intelligence System..."

# Build Docker image
docker build -t persona-doc-intelligence .

echo "Build complete! Image: persona-doc-intelligence"
echo ""
echo "To run the system:"
echo "  ./run.sh"
echo ""
echo "Make sure to place your PDFs in the input/ directory and configure input/config.json"
./run.sh

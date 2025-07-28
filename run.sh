# This script runs the Persona-Driven Document Intelligence System using Docker.
#!/bin/bash
set -e

echo "Running Persona-Driven Document Intelligence System..."

# Check if input directory exists
if [ ! -d "input" ]; then
    echo "Error: input/ directory not found!"
    echo "Please create input/ directory and add your PDF files and config.json"
    exit 1
fi

# Check if config.json exists
if [ ! -f "input/config.json" ]; then
    echo "Error: input/config.json not found!"
    echo "Please create config.json with persona and job_to_be_done fields"
    exit 1
fi

# Create output directory
mkdir -p output

# Run the container
docker run --rm \
    -v "$(pwd)/input:/app/input" \
    -v "$(pwd)/output:/app/output" \
    persona-doc-intelligence

echo "Processing complete! Check output/analysis_result.json for results"

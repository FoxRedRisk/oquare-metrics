#!/usr/bin/env bash

set -e  # Exit immediately if a command exits with a non-zero status.

# Check if running on Windows
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    # Use forward slashes for paths on Windows
    SCRIPT_DIR=$(dirname "$(readlink -f "$0")" | sed 's/\\/\//g')
else
    SCRIPT_DIR=$(dirname "$(readlink -f "$0")")
fi

# Function to log messages
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >&2
}

# Function to handle errors
error_handler() {
    local exit_code=$?
    log "Error occurred in line $1 with exit code $exit_code"
    log "Last command executed: $BASH_COMMAND"
    exit $exit_code
}

# Set up error handling
trap 'error_handler $LINENO' ERR

# Log script start
log "Starting fullparse.sh with arguments: $@"

# Check if the OQuaRE tool exists
OQUARE_PATH="$SCRIPT_DIR/../libs/oquare-versions.jar"
if [ ! -f "$OQUARE_PATH" ]; then
    log "Error: OQuaRE tool not found at $OQUARE_PATH"
    exit 1
fi

# Function to display usage
usage() {
    echo "Usage: $0 -i <contents_folder> -s <ontology_folders> -f <ontology_files> [-g <ignore_files>] [-r <reasoner>] [-M] [-c] [-S] [-m] [-e]"
    echo "  -i: Contents folder"
    echo "  -s: Ontology folders"
    echo "  -f: Ontology files"
    echo "  -g: Ignore files (optional)"
    echo "  -r: Reasoner (optional, default: HermiT)"
    echo "  -M: Generate model plot"
    echo "  -c: Generate characteristics plot"
    echo "  -S: Generate subcharacteristics plot"
    echo "  -m: Generate metrics plot"
    echo "  -e: Generate evolution plot"
    exit 1
}

# Initialize variables
contents_folder=""
ontology_folders=""
ontology_files=""
ignore_files=""
reasoner="HermiT"
model_plot=false
characteristics_plot=false
subcharacteristics_plot=false
metrics_plot=false
evolution_plot=false

# Convert Windows paths to Unix-style paths
convert_path() {
    echo "$1" | sed 's/\\/\//g' | sed 's/://' | sed 's/^/\//'
}

# Parse command-line options
while [[ $# -gt 0 ]]; do
    case $1 in
        -i) contents_folder=$(convert_path "$2"); shift 2 ;;
        -s) ontology_folders=$(convert_path "$2"); shift 2 ;;
        -f) ontology_files=$(convert_path "$2"); shift 2 ;;
        -g) ignore_files=$(convert_path "$2"); shift 2 ;;
        -r) reasoner="$2"; shift 2 ;;
        -M) model_plot=true; shift ;;
        -c) characteristics_plot=true; shift ;;
        -S) subcharacteristics_plot=true; shift ;;
        -m) metrics_plot=true; shift ;;
        -e) evolution_plot=true; shift ;;
        *) usage ;;
    esac
done

# Check for required arguments
if [ -z "$contents_folder" ] || [ -z "$ontology_folders" ] || [ -z "$ontology_files" ]; then
    log "Error: Missing required arguments"
    usage
fi

# Convert backslashes to forward slashes in ontology_files
ontology_files=$(echo "$ontology_files" | sed 's/\\/\//g')

# Log all input parameters
log "Input parameters:"
log "Contents folder: $contents_folder"
log "Ontology folders: $ontology_folders"
log "Ontology files: $ontology_files"
log "Ignore files: $ignore_files"
log "Reasoner: $reasoner"
log "Model plot: $model_plot"
log "Characteristics plot: $characteristics_plot"
log "Subcharacteristics plot: $subcharacteristics_plot"
log "Metrics plot: $metrics_plot"
log "Evolution plot: $evolution_plot"
log "All arguments: $@"

date=$(date '+%Y-%m-%d_%H-%M-%S')

log "Starting fullparse.sh"
log "Contents folder: $contents_folder"
log "Ontology folders: $ontology_folders"
log "Ontology files: $ontology_files"
log "Reasoner: $reasoner"

# Create necessary directories
mkdir -p "$contents_folder/temp_results/ontologies/imports"
log "Created directory: $contents_folder/temp_results/ontologies/imports"

# Process individual ontology file
log "Processing individual ontology file: $ontology_files"
outputFile=$(basename "$ontology_files")
outputFile="${outputFile%.*}"
outputFilePath="$contents_folder/temp_results/ontologies/imports/$outputFile/$date/metrics/$outputFile.xml"
mkdir -p "$(dirname "$outputFilePath")"
log "Created directory: $(dirname "$outputFilePath")"

# Run OQuaRE tool
log "Running OQuaRE tool..."
java -jar "$(convert_path "../libs/oquare-versions.jar")" -o "$(convert_path "$ontology_files")" -m "$(convert_path "$outputFilePath")" -r "$reasoner"

if [ ! -f "$outputFilePath" ]
then
    log "Error: Metrics file was not generated for $ontology_files"
    exit 1
else
    log "Metrics file generated successfully: $outputFilePath"
fi

log "fullparse.sh completed successfully"

#!/bin/bash

set -e  # Exit immediately if a command exits with a non-zero status.

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
if [ ! -f "./libs/oquare-versions.jar" ]; then
    log "Error: OQuaRE tool not found at ./libs/oquare-versions.jar"
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

# Parse command-line options
while getopts "i:s:f:g:r:McSme" opt; do
    case $opt in
        i) contents_folder="$OPTARG" ;;
        s) ontology_folders="$OPTARG" ;;
        f) ontology_files="$OPTARG" ;;
        g) ignore_files="$OPTARG" ;;
        r) reasoner="$OPTARG" ;;
        M) model_plot=true ;;
        c) characteristics_plot=true ;;
        S) subcharacteristics_plot=true ;;
        m) metrics_plot=true ;;
        e) evolution_plot=true ;;
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

oquare_command="java -jar ./libs/oquare-versions.jar --ontology \"$ontology_files\" --reasoner \"$reasoner\" --outputFile \"$outputFilePath\""
log "Executing OQuaRE command: $oquare_command"
if ! eval $oquare_command > "$contents_folder/temp_results/ontologies/imports/$outputFile/$date/oquare_output.log" 2> "$contents_folder/temp_results/ontologies/imports/$outputFile/$date/oquare_error.log"
then
    log "OQuaRE command failed for $ontology_files. Check error log: $contents_folder/temp_results/ontologies/imports/$outputFile/$date/oquare_error.log"
    exit 1
fi

if [ ! -f "$outputFilePath" ]
then
    log "Error: Metrics file was not generated for $ontology_files"
    exit 1
else
    log "Metrics file generated successfully: $outputFilePath"
fi

log "fullparse.sh completed successfully"

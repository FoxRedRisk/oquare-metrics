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

# Check if the Java tool exists
if [ ! -f "./libs/oquare-versions.jar" ]; then
    log "Error: OQuaRE Java tool not found at ./libs/oquare-versions.jar"
    exit 1
fi

# Check Java version
java_version=$(java -version 2>&1 | awk -F '"' '/version/ {print $2}')
log "Java version: $java_version"

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

date=$(powershell -Command "Get-Date -Format 'yyyy-MM-dd_HH-mm-ss'")

log "Starting fullparse.sh"
log "Contents folder: $contents_folder"
log "Ontology folders: $ontology_folders"
log "Ontology files: $ontology_files"
log "Reasoner: $reasoner"

# Check if the Java tool exists
if [ ! -f "./libs/oquare-versions.jar" ]; then
    log "Error: OQuaRE Java tool not found at ./libs/oquare-versions.jar"
    exit 1
fi

# Check Java version
java_version=$(java -version 2>&1 | awk -F '"' '/version/ {print $2}')
log "Java version: $java_version"

for ontology_source in "$ontology_folders"
do
    if [ -d "$ontology_source" ]
    then
        log "Processing ontology source: $ontology_source"
        while IFS= read -r -d '' file
        do
            outputFile=$(basename "$file")
            outputFile="${outputFile%.*}"
            if [ -z "$(printf '%s\n' "$ignore_files" | grep -Fx "$file")" ] && [ -z "$(printf '%s\n' "$ontology_files" | grep -Fx "$file")" ]
            then
                outputFilePath="${contents_folder#./}/temp_results/ontologies/imports/$outputFile/$date/metrics/$outputFile.xml"
                mkdir -p "$(dirname "$outputFilePath")"
                if [ ! -f "$outputFilePath" ]; then
                    log "Running OQuaRE for file: $file"
                    if ! java -jar ./libs/oquare-versions.jar --ontology "$file" --reasoner "$reasoner" --outputFile "$outputFilePath" > "$contents_folder/temp_results/$ontology_source/$outputFile/$date/java_output.log" 2> "$contents_folder/temp_results/$ontology_source/$outputFile/$date/java_error.log"
                    then
                        log "Java command failed. Check error log: $contents_folder/temp_results/$ontology_source/$outputFile/$date/java_error.log"
                        exit 1
                    fi
                    log "Java command completed successfully"
                fi
                
                if [ ! -f "$outputFilePath" ]; then
                    log "Error: Metrics file was not generated: $outputFilePath"
                    exit 1
                fi
            fi
        done < <(find "$ontology_source" -maxdepth 1 -type f \( -name "*.rdf" -o -name "*.owl" -o -name "*.ttl" -o -name "*.nt" -o -name "*.n3" -o -name "*.jsonld" \) -print0)
    else
        log "Warning: Ontology source directory not found: $ontology_source"
    fi
done

for ontology_file in $ontology_files
do
    log "Processing individual ontology file: $ontology_file"
    full_ontology_path="$ontology_folders/$ontology_file"
    if [ -f "$full_ontology_path" ]
    then
        outputFile=$(basename "$full_ontology_path")
        outputFile="${outputFile%.*}"
        outputFilePath="${contents_folder#./}/temp_results/ontologies/imports/$outputFile/$date/metrics/$outputFile.xml"
        mkdir -p "$(dirname "$outputFilePath")"
        
        java_command="java -jar ./libs/oquare-versions.jar --ontology \"$ontology_file\" --reasoner \"$reasoner\" --outputFile \"$outputFilePath\""
        if ! eval $java_command > "$contents_folder/temp_results/$ontology_folders/$outputFile/$date/java_output.log" 2> "$contents_folder/temp_results/$ontology_folders/$outputFile/$date/java_error.log"
        then
            log "Java command failed for $ontology_file. Check error log: $contents_folder/temp_results/$ontology_folders/$outputFile/$date/java_error.log"
            exit 1
        fi

        if [ ! -f "$outputFilePath" ]
        then
            log "Error: Metrics file was not generated for $ontology_file"
            exit 1
        fi
    else
        log "Warning: Individual ontology file not found: $ontology_file"
    fi
done

log "fullparse.sh completed"

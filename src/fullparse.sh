#!/bin/bash

set -e  # Exit immediately if a command exits with a non-zero status.
set -x  # Print commands and their arguments as they are executed

# Function to log messages
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >&2
}

# Function to handle errors
error_handler() {
    local exit_code=$?
    log "Error occurred in line $1 with exit code $exit_code"
    log "Last command executed: $BASH_COMMAND"
    log "Current working directory: $(pwd)"
    log "Contents of current directory:"
    ls -la
    exit $exit_code
}

# Set up error handling
trap 'error_handler $LINENO' ERR

# Enable debug mode
set -o functrace
set -o errtrace

# Log script start
log "Starting fullparse.sh"
log "Arguments: $@"

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

for ontology_source in $ontology_folders
do
    if [ -d "$ontology_source" ]
    then
        log "Processing ontology source: $ontology_source"
        find "$ontology_source" -maxdepth 1 -type f \( -name "*.rdf" -o -name "*.owl" -o -name "*.ttl" -o -name "*.nt" -o -name "*.n3" -o -name "*.jsonld" \) | while read -r file
        do
            outputFile=$(basename "$file")
            if [ -z "$(printf '%s\n' "$ignore_files" | grep -Fx "$file")" ] && [ -z "$(printf '%s\n' "$ontology_files" | grep -Fx "$file")" ]
            then
                outputFile="${outputFile%.*}" 
                mkdir -p "$contents_folder/temp_results/$ontology_source/$outputFile/$date/metrics"
                mkdir -p "$contents_folder/temp_results/$ontology_source/$outputFile/$date/img"
                outputFilePath="${contents_folder#./}/temp_results/${ontology_source#./}/$outputFile/$date/metrics/$outputFile.xml"
                log "Checking if metrics file already exists: $outputFilePath"
                if [ -f "$outputFilePath" ]; then
                    log "Metrics file already exists, skipping Java execution"
                else
                    log "Running OQuaRE for file: $file"
                    log "Output path: $outputFilePath"
                    log "Reasoner: $reasoner"
                    log "Ontology file: $file"
                    java_command="java -jar ./libs/oquare-versions.jar --ontology \"$file\" --reasoner \"$reasoner\" --outputFile \"$outputFilePath\""
                    log "Executing Java command: $java_command"
                    if ! eval $java_command > >(tee "$contents_folder/temp_results/$ontology_source/$outputFile/$date/java_output.log") 2> >(tee "$contents_folder/temp_results/$ontology_source/$outputFile/$date/java_error.log" >&2)
                    then
                        exit_status=$?
                        log "Java command failed with exit status: $exit_status"
                        log "Java command error output:"
                        cat "$contents_folder/temp_results/$ontology_source/$outputFile/$date/java_error.log"
                        exit $exit_status
                    fi
                    log "Java command completed successfully"
                    log "Java command output:"
                    cat "$contents_folder/temp_results/$ontology_source/$outputFile/$date/java_output.log"
                
                    # Check if the output file was actually created
                    if [ ! -f "$outputFilePath" ]; then
                        log "Error: Output file was not created: $outputFilePath"
                        log "Contents of output directory:"
                        ls -R "$contents_folder/temp_results/$ontology_source/$outputFile/$date/"
                        exit 1
                    fi
                fi
                
                log "Checking metrics file"
                if [ -f "$outputFilePath" ]; then
                    log "Metrics file exists: $outputFilePath"
                    log "File size: $(du -h "$outputFilePath" | cut -f1)"
                    log "File contents (first 10 lines):"
                    head -n 10 "$outputFilePath"
                    
                    # Images will be generated separately using generate_images.py
                else
                    log "Error: Metrics file was not generated: $outputFilePath"
                    log "Current directory: $(pwd)"
                    log "Contents of output directory:"
                    ls -R "$contents_folder/temp_results/$ontology_source/$outputFile/$date/"
                    log "Contents of Java error log:"
                    cat "$contents_folder/temp_results/$ontology_source/$outputFile/$date/java_error.log"
                    exit 1
                fi
            fi
        done
    else
        log "Warning: Ontology source directory not found: $ontology_source"
    fi
done

for ontology_file in $ontology_files
do
    log "Processing individual ontology file: $ontology_file"
    if [ -f "$ontology_file" ]
    then
        dir=$(dirname "$ontology_file")
        outputFile=$(basename "$ontology_file")
        outputFile="${outputFile%.*}"
        mkdir -p "$contents_folder/temp_results/$dir/$outputFile/$date/metrics"
        mkdir -p "$contents_folder/temp_results/$dir/$outputFile/$date/img"
        outputFilePath="${contents_folder#./}/temp_results/${dir#./}/$outputFile/$date/metrics/$outputFile.xml"
        log "Ontology file: $ontology_file"
        log "Output file path: $outputFilePath"
        log "Checking if ontology file exists:"
        if [ -f "$ontology_file" ]; then
            log "Ontology file exists"
        else
            log "Error: Ontology file does not exist"
            log "Contents of $(dirname "$ontology_file"):"
            ls -la "$(dirname "$ontology_file")"
            exit 1
        fi
        
        # Create the directory for the output file if it doesn't exist
        mkdir -p "$(dirname "$outputFilePath")"
        
        # Create an empty metrics file
        touch "$outputFilePath"
        log "Created empty metrics file: $outputFilePath"
        
        java_command="java -jar ./libs/oquare-versions.jar --ontology \"$ontology_file\" --reasoner \"$reasoner\" --outputFile \"$outputFilePath\""
        log "Executing Java command: $java_command"
        if eval $java_command > >(tee "$contents_folder/temp_results/$dir/$outputFile/$date/java_output.log") 2> >(tee "$contents_folder/temp_results/$dir/$outputFile/$date/java_error.log" >&2)
        then
            log "Java command completed successfully"
            log "Java command output:"
            cat "$contents_folder/temp_results/$dir/$outputFile/$date/java_output.log"
        else
            exit_status=$?
            log "Java command failed with exit status: $exit_status"
            log "Java command error output:"
            cat "$contents_folder/temp_results/$dir/$outputFile/$date/java_error.log"
            log "Java command standard output:"
            cat "$contents_folder/temp_results/$dir/$outputFile/$date/java_output.log"
            log "Contents of $(dirname "$outputFilePath"):"
            ls -la "$(dirname "$outputFilePath")"
            exit $exit_status
        fi

        if [ -f "$outputFilePath" ]
        then
            log "Metrics file generated successfully: $outputFilePath"
            log "File size: $(du -h "$outputFilePath" | cut -f1)"
            log "File contents (first 10 lines):"
            head -n 10 "$outputFilePath"
            
            # Images will be generated separately using generate_images.py
        else
            log "Error: Metrics file was not generated for $ontology_file"
            log "Contents of Java error log:"
            cat "$contents_folder/temp_results/$dir/$outputFile/$date/java_error.log"
            exit 1
        fi
    else
        log "Warning: Individual ontology file not found: $ontology_file"
    fi
done

log "fullparse.sh completed"

#!/bin/bash

set -e  # Exit immediately if a command exits with a non-zero status.

# Function to log messages
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1"
}

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
                outputFilePath="$contents_folder/temp_results/$ontology_source/$outputFile/$date/metrics/$outputFile.xml"
                log "Running OQuaRE for file: $file"
                log "Output path: $outputFilePath"
                log "Reasoner: $reasoner"
                if java -jar ./libs/oquare-versions.jar --ontology "$file" --reasoner "$reasoner" --outputFile "$outputFilePath" > "$contents_folder/temp_results/$ontology_source/$outputFile/$date/java_output.log" 2> "$contents_folder/temp_results/$ontology_source/$outputFile/$date/java_error.log"
                then
                    log "Java command completed successfully"
                else
                    log "Java command failed with exit status: $?"
                fi
                
                if [ -f "$outputFilePath" ]
                then
                    log "Metrics file generated successfully: $outputFilePath"
                    python ./src/main.py -i "$contents_folder" -s "$ontology_source" -f "$outputFile" \
                        $([ "$model_plot" = true ] && echo "-M") \
                        $([ "$characteristics_plot" = true ] && echo "-c") \
                        $([ "$subcharacteristics_plot" = true ] && echo "-S") \
                        $([ "$metrics_plot" = true ] && echo "-m") \
                        $([ "$evolution_plot" = true ] && echo "-e")
                else
                    log "Error: Metrics file was not generated for $file"
                    log "Current directory: $(pwd)"
                    log "Contents of output directory:"
                    ls -R "$contents_folder/temp_results/$ontology_source/$outputFile/$date/"
                    log "Contents of Java error log:"
                    cat "$contents_folder/temp_results/$ontology_source/$outputFile/$date/java_error.log"
                fi
            fi
        done
    else
        log "Warning: Ontology source directory not found: $ontology_source"
    fi
done

for ontology_file in $ontology_files
do
    if [ -f "$ontology_file" ]
    then
        log "Processing individual ontology file: $ontology_file"
        dir=$(dirname "$ontology_file")
        outputFile=$(basename "$ontology_file")
        outputFile="${outputFile%.*}"
        mkdir -p "$contents_folder/temp_results/$dir/$outputFile/$date/metrics"
        mkdir -p "$contents_folder/temp_results/$dir/$outputFile/$date/img"
        outputFilePath="$contents_folder/temp_results/$dir/$outputFile/$date/metrics/$outputFile.xml"
        if java -jar ./libs/oquare-versions.jar --ontology "$ontology_file" --reasoner "$reasoner" --outputFile "$outputFilePath" > "$contents_folder/temp_results/$dir/$outputFile/$date/java_output.log" 2> "$contents_folder/temp_results/$dir/$outputFile/$date/java_error.log"
        then
            log "Java command completed successfully"
        else
            log "Java command failed with exit status: $?"
        fi

        if [ -f "$outputFilePath" ]
        then
            log "Metrics file generated successfully: $outputFilePath"
            python ./src/main.py -i "$contents_folder" -s "$dir" -f "$outputFile" \
                $([ "$model_plot" = true ] && echo "-M") \
                $([ "$characteristics_plot" = true ] && echo "-c") \
                $([ "$subcharacteristics_plot" = true ] && echo "-S") \
                $([ "$metrics_plot" = true ] && echo "-m") \
                $([ "$evolution_plot" = true ] && echo "-e")
        else
            log "Error: Metrics file was not generated for $ontology_file"
            log "Contents of Java error log:"
            cat "$contents_folder/temp_results/$dir/$outputFile/$date/java_error.log"
        fi
    else
        log "Warning: Individual ontology file not found: $ontology_file"
    fi
done

log "fullparse.sh completed"

#!/bin/bash

set -e  # Exit immediately if a command exits with a non-zero status.

# Function to log messages
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1"
}

# Inputs
contents_folder="$1"
ontology_folders="$2"
ignore_files="$3"
ontology_files="$4"
reasoner="$5"
model_plot="$6"
characteristics_plot="$7"
subcharacteristics_plot="$8"
metrics_plot="$9"
evolution_plot="${10}"

# Convert backslashes to forward slashes in ontology_files
ontology_files=$(echo "$ontology_files" | sed 's/\\/\//g')

# Log all input parameters
log "Input parameters:"
log "1. Contents folder: $contents_folder"
log "2. Ontology folders: $ontology_folders"
log "3. Ignore files: $ignore_files"
log "4. Ontology files: $ontology_files"
log "5. Reasoner: $reasoner"
log "6. Model plot: $model_plot"
log "7. Characteristics plot: $characteristics_plot"
log "8. Subcharacteristics plot: $subcharacteristics_plot"
log "9. Metrics plot: $metrics_plot"
log "10. Evolution plot: $evolution_plot"

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

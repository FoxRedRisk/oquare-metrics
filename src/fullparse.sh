#!/bin/sh

# Inputs
contents_folder=$1
ontology_folders=$2
ignore_files=$3
ontology_files=$4
reasoner=$5
model_plot=$6
characteristics_plot=$7
subcharacteristics_plot=$8
metrics_plot=$9
evolution_plot=${10}

date=$(powershell -Command "Get-Date -Format 'yyyy-MM-dd_HH-mm-ss'")

for ontology_source in $ontology_folders
do
    if [ -d "$ontology_source" ]
    then
        find $ontology_source -maxdepth 1 -type f \( -name "*.rdf" -o -name "*.owl" -o -name "*.ttl" -o -name "*.nt" -o -name "*.n3" -o -name "*.jsonld" \) | while read file
        do
            outputFile=$(basename "$file")
            if [ -z $(printf '%s\n' "$ignore_files" | grep -Fx "$file")] && [ -z $(printf '%s\n' "$ontology_files" | grep -Fx "$file")]
            then
                outputFile=$(basename "$file")
                outputFile="${outputFile%.*}" 
                mkdir -p $contents_folder/temp_results/$ontology_source/$outputFile/$date/metrics
                mkdir -p $contents_folder/temp_results/$ontology_source/$outputFile/$date/img
                outputFilePath="$contents_folder/temp_results/$ontology_source/$outputFile/$date/metrics/$outputFile.xml"
                echo "Running OQuaRE for file: $file"
                echo "Output path: $outputFilePath"
                echo "Reasoner: $reasoner"
                java -jar ./libs/oquare-versions.jar --ontology "$file" --reasoner "$reasoner" --outputFile "$outputFilePath" > >(tee "$contents_folder/temp_results/$ontology_source/$outputFile/$date/java_output.log") 2> >(tee "$contents_folder/temp_results/$ontology_source/$outputFile/$date/java_error.log" >&2)
                echo "Java command exit status: $?"
                
                if [ -f "$outputFilePath" ]
                then
                    echo "Metrics file generated successfully: $outputFilePath"
                    python ./src/main.py -i $contents_folder -s $ontology_source -f $outputFile \
                        $([ "$model_plot" = true ] && echo "-M") \
                        $([ "$characteristics_plot" = true ] && echo "-c") \
                        $([ "$subcharacteristics_plot" = true ] && echo "-S") \
                        $([ "$metrics_plot" = true ] && echo "-m") \
                        $([ "$evolution_plot" = true ] && echo "-e")
                else
                    echo "Error: Metrics file was not generated for $file"
                    echo "Current directory: $(pwd)"
                    echo "Contents of output directory:"
                    ls -R "$contents_folder/temp_results/$ontology_source/$outputFile/$date/"
                    echo "Contents of Java error log:"
                    cat "$contents_folder/temp_results/$ontology_source/$outputFile/$date/java_error.log"
                fi
            fi
        done
    fi
done

for ontology_file in $ontology_files
do
    if [ -f "$ontology_file" ]
    then
        dir=$(dirname "$ontology_file")
        outputFile=$(basename "$ontology_file")
        outputFile="${outputFile%.*}"
        mkdir -p $contents_folder/temp_results/$dir/$outputFile/$date/metrics
        mkdir -p $contents_folder/temp_results/$dir/$outputFile/$date/img
        outputFilePath="$contents_folder/temp_results/$dir/$outputFile/$date/metrics/$outputFile.xml"
        java -jar ./libs/oquare-versions.jar --ontology "$ontology_file" --reasoner "$reasoner" --outputFile "$outputFilePath"

        if [ -f "$outputFilePath" ]
        then
            python ./src/main.py -i $contents_folder -s $dir -f $outputFile \
                $([ "$model_plot" = true ] && echo "-M") \
                $([ "$characteristics_plot" = true ] && echo "-c") \
                $([ "$subcharacteristics_plot" = true ] && echo "-S") \
                $([ "$metrics_plot" = true ] && echo "-m") \
                $([ "$evolution_plot" = true ] && echo "-e")
        fi
    fi
done

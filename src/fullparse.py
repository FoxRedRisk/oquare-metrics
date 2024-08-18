import os
import subprocess
import glob
from datetime import datetime

def run_fullparse(contents_folder, ontology_folders, ignore_files, ontology_files, reasoner, model_plot, characteristics_plot, subcharacteristics_plot, metrics_plot, evolution_plot):
    date = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    for ontology_source in ontology_folders.split():
        if os.path.isdir(ontology_source):
            for file in glob.glob(os.path.join(ontology_source, "*.*")):
                if file.lower().endswith(('.rdf', '.owl', '.ttl', '.nt', '.n3', '.jsonld')):
                    outputFile = os.path.splitext(os.path.basename(file))[0]
                    if file not in ignore_files.split() and file not in ontology_files.split():
                        process_ontology(contents_folder, ontology_source, file, outputFile, date, reasoner, model_plot, characteristics_plot, subcharacteristics_plot, metrics_plot, evolution_plot)

    for ontology_file in ontology_files.split():
        if os.path.isfile(ontology_file):
            dir = os.path.dirname(ontology_file)
            outputFile = os.path.splitext(os.path.basename(ontology_file))[0]
            process_ontology(contents_folder, dir, ontology_file, outputFile, date, reasoner, model_plot, characteristics_plot, subcharacteristics_plot, metrics_plot, evolution_plot)

def process_ontology(contents_folder, ontology_source, file, outputFile, date, reasoner, model_plot, characteristics_plot, subcharacteristics_plot, metrics_plot, evolution_plot):
    output_dir = os.path.join(contents_folder, "temp_results", ontology_source, outputFile, date)
    os.makedirs(os.path.join(output_dir, "metrics"), exist_ok=True)
    os.makedirs(os.path.join(output_dir, "img"), exist_ok=True)
    outputFilePath = os.path.join(output_dir, "metrics", f"{outputFile}.xml")

    print(f"Running OQuaRE for file: {file}")
    print(f"Output path: {outputFilePath}")
    print(f"Reasoner: {reasoner}")

    java_command = [
        "java", "-jar", "./libs/oquare-versions.jar",
        "--ontology", file,
        "--reasoner", reasoner,
        "--outputFile", outputFilePath
    ]

    with open(os.path.join(output_dir, "java_output.log"), "w") as out_log, \
         open(os.path.join(output_dir, "java_error.log"), "w") as err_log:
        process = subprocess.run(java_command, stdout=out_log, stderr=err_log)

    print(f"Java command exit status: {process.returncode}")

    if os.path.isfile(outputFilePath):
        print(f"Metrics file generated successfully: {outputFilePath}")
        run_main_script(contents_folder, ontology_source, outputFile, model_plot, characteristics_plot, subcharacteristics_plot, metrics_plot, evolution_plot)
    else:
        print(f"Error: Metrics file was not generated for {file}")
        print(f"Current directory: {os.getcwd()}")
        print("Contents of output directory:")
        for root, dirs, files in os.walk(output_dir):
            for name in files:
                print(os.path.join(root, name))
        print("Contents of Java error log:")
        with open(os.path.join(output_dir, "java_error.log"), "r") as err_log:
            print(err_log.read())

def run_main_script(contents_folder, ontology_source, outputFile, model_plot, characteristics_plot, subcharacteristics_plot, metrics_plot, evolution_plot):
    command = [
        "python", "./src/main.py",
        "-i", contents_folder,
        "-s", ontology_source,
        "-f", outputFile
    ]
    if model_plot:
        command.append("-M")
    if characteristics_plot:
        command.append("-c")
    if subcharacteristics_plot:
        command.append("-S")
    if metrics_plot:
        command.append("-m")
    if evolution_plot:
        command.append("-e")

    subprocess.run(command, check=True)

if __name__ == "__main__":
    import sys
    run_fullparse(*sys.argv[1:])

import os
import subprocess
import logging
from datetime import datetime

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def run_fullparse(contents_folder, ontology_file, reasoner):
    date = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    logging.info(f"Starting fullparse with date: {date}")

    outputFile = os.path.splitext(os.path.basename(ontology_file))[0]
    output_dir = os.path.join(contents_folder, "temp_results", outputFile, date)
    os.makedirs(os.path.join(output_dir, "metrics"), exist_ok=True)
    outputFilePath = os.path.join(output_dir, "metrics", f"{outputFile}.xml")

    logging.info(f"Running OQuaRE for file: {ontology_file}")
    logging.info(f"Output path: {outputFilePath}")
    logging.info(f"Reasoner: {reasoner}")

    java_command = [
        "java", "-jar", "./libs/oquare-versions.jar",
        "--ontology", ontology_file,
        "--reasoner", reasoner,
        "--outputFile", outputFilePath
    ]

    try:
        process = subprocess.run(java_command, check=True, text=True, capture_output=True)
        logging.info(f"Java command completed successfully with exit code: {process.returncode}")
        logging.debug(f"Java command output: {process.stdout}")
    except subprocess.CalledProcessError as e:
        logging.error(f"Java command failed with exit code: {e.returncode}")
        logging.error(f"Error output: {e.stderr}")

    if os.path.isfile(outputFilePath):
        logging.info(f"Metrics file generated successfully: {outputFilePath}")
    else:
        logging.error(f"Error: Metrics file was not generated for {ontology_file}")

if __name__ == "__main__":
    import sys
    logging.info(f"Starting fullparse.py with arguments: {sys.argv[1:]}")
    run_fullparse(*sys.argv[1:])

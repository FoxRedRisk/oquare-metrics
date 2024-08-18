import argparse
import logging
import os
import subprocess
import os
from datetime import datetime

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# How to run:
# python src/main.py -i <input_path> -s <source_folder> -f <ontology_file> -r <reasoner> [-M] [-c] [-S] [-m] [-e]
# Example:
# python src/main.py -i ./output -s ./ontologies -f my_ontology.owl -r HermiT -M -c -S -m -e

def main():
    parser = argparse.ArgumentParser(description='OQuaRE Metrics Generator')
    parser.add_argument('-i', '--input', required=True, help='Input path')
    parser.add_argument('-s', '--source', required=True, help='Ontology source folder')
    parser.add_argument('-f', '--file', required=True, help='Ontology file name')
    parser.add_argument('-r', '--reasoner', default='HermiT', help='Reasoner to use (default: HermiT)')
    parser.add_argument('-M', '--model', action='store_true', help='Generate model plot')
    parser.add_argument('-c', '--characteristics', action='store_true', help='Generate characteristics plot')
    parser.add_argument('-S', '--subcharacteristics', action='store_true', help='Generate subcharacteristics plot')
    parser.add_argument('-m', '--metrics', action='store_true', help='Generate metrics plot')
    parser.add_argument('-e', '--evolution', action='store_true', help='Generate evolution plot')
    
    args = parser.parse_args()
    logging.info(f"Arguments: {args}")

    # Add .owl extension if not provided
    if not args.file.lower().endswith(('.owl', '.rdf', '.ttl')):
        args.file += '.owl'
    
    # Get the relative path of the ontology file
    ontology_file = os.path.normpath(os.path.join(args.source, args.file))
    
    # Log the constructed file path and current working directory
    logging.debug(f"Current working directory: {os.getcwd()}")
    logging.debug(f"Looking for ontology file at (relative path): {ontology_file}")
    
    # Check if the ontology file exists
    if not os.path.isfile(ontology_file):
        logging.error(f"Ontology file not found: {ontology_file}")
        if os.path.isdir(args.source):
            logging.error(f"Contents of {args.source}:")
            for file in os.listdir(args.source):
                logging.error(f"  {file}")
        else:
            logging.error(f"Source folder not found: {args.source}")
        exit(1)

    # Run fullparse.sh to generate the metrics XML file
    fullparse_command = [
        "bash", "./src/fullparse.sh",
        "-i", args.input,
        "-s", args.source,
        "-f", ontology_file,
        "-r", args.reasoner
    ]
    
    if args.model:
        fullparse_command.append("-M")
    if args.characteristics:
        fullparse_command.append("-c")
    if args.subcharacteristics:
        fullparse_command.append("-S")
    if args.metrics:
        fullparse_command.append("-m")
    if args.evolution:
        fullparse_command.append("-e")
    
    # Log the full command
    logging.info(f"Full fullparse.sh command: {' '.join(map(str, fullparse_command))}")
    logging.info(f"Running fullparse.sh with command: {' '.join(map(str, fullparse_command))}")
    
    # Check if the metrics file already exists
    metrics_file = os.path.join(args.input, "temp_results", args.source, os.path.splitext(args.file)[0], datetime.now().strftime("%Y-%m-%d_%H-%M-%S"), "metrics", f"{os.path.splitext(args.file)[0]}.xml")
    
    if os.path.exists(metrics_file):
        logging.info(f"Metrics file already exists: {metrics_file}")
        logging.info("Skipping fullparse.sh execution")
    else:
        try:
            logging.info("Starting execution of fullparse.sh")
            process = subprocess.Popen(fullparse_command, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Real-time logging of stdout and stderr
            while True:
                output = process.stdout.readline()
                error = process.stderr.readline()
                if output == '' and error == '' and process.poll() is not None:
                    break
                if output:
                    logging.info(f"fullparse.sh stdout: {output.strip()}")
                if error:
                    logging.error(f"fullparse.sh stderr: {error.strip()}")
            
            returncode = process.poll()
            logging.info(f"fullparse.sh exit code: {returncode}")
            
            if returncode != 0:
                raise subprocess.CalledProcessError(returncode, fullparse_command)
            
            logging.info("fullparse.sh completed successfully")
        except subprocess.CalledProcessError as e:
            logging.error(f"fullparse.sh failed with exit code: {e.returncode}")
        
        # Additional error handling and logging
        logging.error("Checking fullparse.sh file permissions:")
        try:
            permissions = subprocess.run(["ls", "-l", "src/fullparse.sh"], check=True, text=True, capture_output=True)
            logging.info(f"fullparse.sh permissions: {permissions.stdout.strip()}")
        except subprocess.CalledProcessError as perm_error:
            logging.error(f"Failed to check permissions: {perm_error}")
        
        logging.error("Checking if fullparse.sh exists:")
        if os.path.exists("src/fullparse.sh"):
            logging.info("fullparse.sh file exists")
        else:
            logging.error("fullparse.sh file does not exist in the expected location")
        
        # Check the content of fullparse.sh
        try:
            with open("src/fullparse.sh", "r") as f:
                logging.info("Content of fullparse.sh:")
                logging.info(f.read())
        except Exception as read_error:
            logging.error(f"Failed to read fullparse.sh: {read_error}")
        
        # Check if bash is available and its version
        try:
            bash_version = subprocess.run(["bash", "--version"], check=True, text=True, capture_output=True)
            logging.info(f"Bash version: {bash_version.stdout.split(os.linesep)[0]}")
        except subprocess.CalledProcessError as bash_error:
            logging.error(f"Failed to get bash version: {bash_error}")
            logging.error("Bash may not be installed or not in the system PATH.")
            logging.error("Please ensure that Bash is installed and accessible from the command line.")
        except FileNotFoundError:
            logging.error("Bash executable not found.")
            logging.error("Please ensure that Bash is installed and accessible from the command line.")
        
        exit(1)

    logging.info("Main script completed successfully")

if __name__ == '__main__':
    logging.info("Starting main.py")
    main()


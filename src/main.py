import argparse
import logging
import os
import subprocess
from datetime import datetime

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

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

    ontology_file = os.path.join(args.source, "imports", args.file)
    
    # Log the constructed file path
    logging.debug(f"Looking for ontology file at: {ontology_file}")
    
    # Check if the ontology file exists
    if not os.path.isfile(ontology_file):
        logging.error(f"Ontology file not found: {ontology_file}")
        exit(1)

    # Run fullparse.sh to generate the metrics XML file
    fullparse_command = [
        "bash", "src/fullparse.sh",
        args.input,
        args.source,
        "",  # ignore_files (empty for now)
        ontology_file,
        args.reasoner,
        str(args.model).lower(),
        str(args.characteristics).lower(),
        str(args.subcharacteristics).lower(),
        str(args.metrics).lower(),
        str(args.evolution).lower()
    ]
    logging.info(f"Running fullparse.sh with command: {' '.join(fullparse_command)}")
    result = subprocess.run(fullparse_command, text=True, capture_output=True)
    
    logging.info(f"fullparse.sh exit code: {result.returncode}")
    logging.info(f"fullparse.sh stdout:\n{result.stdout}")
    logging.info(f"fullparse.sh stderr:\n{result.stderr}")
    
    if result.returncode != 0:
        logging.error(f"fullparse.sh failed with exit code: {result.returncode}")
        
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
        
        exit(1)
    else:
        logging.info("fullparse.sh completed successfully")

    logging.info("Main script completed successfully")

if __name__ == '__main__':
    logging.info("Starting main.py")
    main()


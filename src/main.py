import argparse
import logging
import os
import subprocess
from datetime import datetime

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    parser = argparse.ArgumentParser(description='OQuaRE Metrics Generator')
    parser.add_argument('-i', '--input', required=True, help='Input path')
    parser.add_argument('-f', '--file', required=True, help='Ontology file name')
    parser.add_argument('-r', '--reasoner', default='HermiT', help='Reasoner to use (default: HermiT)')
    
    args = parser.parse_args()
    logging.info(f"Arguments: {args}")

    ontology_file = os.path.join(args.input, args.file)
    
    # Run fullparse.py to generate the metrics XML file
    fullparse_command = [
        "python", "src/fullparse.py",
        args.input, ontology_file, args.reasoner
    ]
    logging.info(f"Running fullparse.py with command: {' '.join(fullparse_command)}")
    try:
        subprocess.run(fullparse_command, check=True, text=True, capture_output=True)
        logging.info("fullparse.py completed successfully")
    except subprocess.CalledProcessError as e:
        logging.error(f"fullparse.py failed with exit code: {e.returncode}")
        logging.error(f"Error output: {e.stderr}")
        exit(1)

    logging.info("Main script completed successfully")

if __name__ == '__main__':
    logging.info("Starting main.py")
    main()


import argparse
import logging
import os
import subprocess
from datetime import datetime

"""
How to run:
python src/main.py -i <input_path> -s <source_folder> -f <ontology_file> -r <reasoner> [-M] [-c] [-S] [-m] [-e]

Example:
python src/main.py -i ./output -s ./ontologies -f my_ontology.owl -r HermiT -M -c -S -m -e

Arguments:
-i, --input: Input path for storing results
-s, --source: Ontology source folder
-f, --file: Ontology file name
-r, --reasoner: Reasoner to use (default: HermiT)
-M: Generate model plot
-c: Generate characteristics plot
-S: Generate subcharacteristics plot
-m: Generate metrics plot
-e: Generate evolution plot
"""

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

# Console handler
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(formatter)
logger.addHandler(ch)

# File handler
fh = logging.FileHandler('oquare_metrics.log')
fh.setLevel(logging.DEBUG)
fh.setFormatter(formatter)
logger.addHandler(fh)

def main():
    logger.info("Starting main.py")
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
    logger.info(f"Arguments: {args}")

    # Add .owl extension if not provided
    if not args.file.lower().endswith(('.owl', '.rdf', '.ttl')):
        args.file += '.owl'
    
    # Construct the ontology file path relative to the script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    ontology_file = os.path.abspath(os.path.join(script_dir, '..', args.source, args.file)).replace('\\', '/')
    
    # Log the constructed file path
    logger.debug(f"Script directory: {script_dir}")
    logger.debug(f"Constructed ontology file path: {ontology_file}")
    
    # Check if the ontology file exists
    if not os.path.isfile(ontology_file):
        logger.error(f"Ontology file not found: {ontology_file}")
        exit(1)

    # Generate timestamp once and use it consistently
    date_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    def construct_metrics_file_path(input_path, ontology_file, date_str):
        return os.path.join(input_path, "temp_results", "ontologies", "imports", os.path.splitext(os.path.basename(ontology_file))[0], date_str, "metrics", f"{os.path.splitext(os.path.basename(ontology_file))[0]}.xml").replace('\\', '/')

    metrics_file = construct_metrics_file_path(args.input, ontology_file, date_str)

    # Create necessary directories if they don't exist
    if not os.path.exists(os.path.dirname(metrics_file)):
        os.makedirs(os.path.dirname(metrics_file))
        logger.info(f"Created directory: {os.path.dirname(metrics_file)}")
    else:
        logger.info(f"Directory already exists: {os.path.dirname(metrics_file)}")

    # Run OQuaRE tool
    logger.info("Running OQuaRE tool...")
    full_ontology_path = os.path.join(args.source, args.file).replace('\\', '/')
    logger.info(f"Relative ontology file path: {full_ontology_path}")
    oquare_command = [
        "java", "-jar", os.path.join(script_dir, "../libs/oquare-versions.jar"),
        "--ontology", f"./{full_ontology_path}",
        "-m", f"./{metrics_file}",
        "-r", args.reasoner
    ]

    try:
        subprocess.run(oquare_command, check=True, text=True, capture_output=True)
        logger.info("OQuaRE tool completed successfully")
    except subprocess.CalledProcessError as e:
        logger.error(f"OQuaRE tool failed with exit code: {e.returncode}")
        logger.error(f"Error output: {e.stderr}")
        exit(1)

    # Check if the metrics file was created
    if not os.path.exists(metrics_file):
        logger.error(f"Metrics file not found after running OQuaRE tool: {os.path.normpath(metrics_file)}")
        metrics_dir = os.path.dirname(metrics_file)
        logger.error(f"Contents of {os.path.normpath(metrics_dir)}:")
        try:
            logger.error(os.listdir(metrics_dir))
        except FileNotFoundError:
            logger.error(f"Directory {os.path.normpath(metrics_dir)} does not exist")
        exit(1)

    # Generate images using generate_images.py
    generate_images_command = [
        "python", "./src/generate_images.py",
        "-i", args.input,
        "-s", args.source,
        "-f", args.file,
        "-d", date_str
    ]
    
    if args.model:
        generate_images_command.append("-M")
    if args.characteristics:
        generate_images_command.append("-c")
    if args.subcharacteristics:
        generate_images_command.append("-S")
    if args.metrics:
        generate_images_command.append("-m")
    if args.evolution:
        generate_images_command.append("-e")
    
    logger.info(f"Executing generate_images.py with command: {' '.join(generate_images_command)}")
    
    try:
        subprocess.run(generate_images_command, check=True, text=True, capture_output=True)
        logger.info("Image generation completed successfully")
    except subprocess.CalledProcessError as e:
        logger.error(f"Image generation failed with exit code: {e.returncode}")
        logger.error(f"Error output: {e.stderr}")
    
    logger.info("Main script completed successfully")

if __name__ == '__main__':
    main()


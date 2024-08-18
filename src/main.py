import argparse
import logging
import os
import subprocess
from datetime import datetime

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

# How to run:
# python src/main.py -i <input_path> -s <source_folder> -f <ontology_file> -r <reasoner> [-M] [-c] [-S] [-m] [-e]
# Example:
# python src/main.py -i ./output -s ./ontologies -f my_ontology.owl -r HermiT -M -c -S -m -e

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
    
    # Get the absolute path of the ontology file
    ontology_file = os.path.abspath(os.path.join(args.source, args.file))
    
    # Log the constructed file path and current working directory
    logger.debug(f"Current working directory: {os.getcwd()}")
    logger.debug(f"Looking for ontology file at (absolute path): {ontology_file}")
    
    # Check if the ontology file exists
    if not os.path.isfile(ontology_file):
        logger.error(f"Ontology file not found: {ontology_file}")
        if os.path.isdir(args.source):
            logger.error(f"Contents of {args.source}:")
            for file in os.listdir(args.source):
                logger.error(f"  {file}")
        else:
            logger.error(f"Source folder not found: {args.source}")
        exit(1)

    # Run fullparse.sh to generate the metrics XML file
    fullparse_command = [
        "bash", "./src/fullparse.sh",
        "-i", args.input,
        "-s", args.source,
        "-f", args.file,
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
    logger.info(f"Full fullparse.sh command: {' '.join(map(str, fullparse_command))}")
    
    # Check if the metrics file already exists
    metrics_file = os.path.join(args.input, "temp_results", args.source, os.path.splitext(args.file)[0], datetime.now().strftime("%Y-%m-%d_%H-%M-%S"), "metrics", f"{os.path.splitext(args.file)[0]}.xml")
    
    if os.path.exists(metrics_file):
        logger.info(f"Metrics file already exists: {metrics_file}")
        logger.info("Skipping fullparse.sh execution")
    else:
        try:
            logger.info("Starting execution of fullparse.sh")
            process = subprocess.Popen(fullparse_command, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Real-time logging of stdout and stderr
            while True:
                output = process.stdout.readline()
                error = process.stderr.readline()
                if output == '' and error == '' and process.poll() is not None:
                    break
                if output:
                    logger.info(f"fullparse.sh stdout: {output.strip()}")
                if error:
                    logger.error(f"fullparse.sh stderr: {error.strip()}")
            
            returncode = process.poll()
            logger.info(f"fullparse.sh exit code: {returncode}")
            
            if returncode != 0:
                raise subprocess.CalledProcessError(returncode, fullparse_command)
            
            logger.info("fullparse.sh completed successfully")
        except subprocess.CalledProcessError as e:
            logger.error(f"fullparse.sh failed with exit code: {e.returncode}")
            logger.exception("Exception details:")
        
        # Additional error handling and logging
        logger.error("Checking fullparse.sh file permissions:")
        try:
            permissions = subprocess.run(["ls", "-l", "src/fullparse.sh"], check=True, text=True, capture_output=True)
            logger.info(f"fullparse.sh permissions: {permissions.stdout.strip()}")
        except subprocess.CalledProcessError as perm_error:
            logger.error(f"Failed to check permissions: {perm_error}")
        
        logger.error("Checking if fullparse.sh exists:")
        if os.path.exists("src/fullparse.sh"):
            logger.info("fullparse.sh file exists")
        else:
            logger.error("fullparse.sh file does not exist in the expected location")
        
        # Check the content of fullparse.sh
        try:
            with open("src/fullparse.sh", "r") as f:
                logger.info("Content of fullparse.sh:")
                logger.info(f.read())
        except Exception as read_error:
            logger.error(f"Failed to read fullparse.sh: {read_error}")
        
        # Check if bash is available and its version
        try:
            bash_version = subprocess.run(["bash", "--version"], check=True, text=True, capture_output=True)
            logger.info(f"Bash version: {bash_version.stdout.split(os.linesep)[0]}")
        except subprocess.CalledProcessError as bash_error:
            logger.error(f"Failed to get bash version: {bash_error}")
            logger.error("Bash may not be installed or not in the system PATH.")
            logger.error("Please ensure that Bash is installed and accessible from the command line.")
        except FileNotFoundError:
            logger.error("Bash executable not found.")
            logger.error("Please ensure that Bash is installed and accessible from the command line.")
        
        exit(1)

    # Generate images using generate_images.py
    generate_images_command = [
        "python", "./src/generate_images.py",
        "-i", args.input,
        "-s", args.source,
        "-f", args.file,
        "-d", datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
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


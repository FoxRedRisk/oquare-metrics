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
    ontology_file = os.path.normpath(os.path.join(script_dir, '..', args.source, args.file))
    
    # Log the constructed file path
    logger.debug(f"Script directory: {script_dir}")
    logger.debug(f"Constructed ontology file path: {ontology_file}")
    
    # Check if the ontology file exists
    if not os.path.isfile(ontology_file):
        logger.error(f"Ontology file not found: {ontology_file}")
        exit(1)

    # Run fullparse.sh to generate the metrics XML file
    fullparse_command = [
        os.path.join(script_dir, "fullparse.sh").replace("\\", "/"),
        "-i", "/".join(os.path.abspath(args.input).split("\\")),
        "-s", "/".join(os.path.dirname(ontology_file).split("\\")),
        "-f", "/".join(os.path.abspath(ontology_file).split("\\")),
        "-r", args.reasoner
    ]
    if os.name == 'nt':  # Windows system
        # Check if bash is accessible
        try:
            subprocess.run(["bash", "--version"], check=True, capture_output=True, text=True)
            logger.info("Bash is accessible on this Windows system.")
            fullparse_command.insert(0, "bash")
        except subprocess.CalledProcessError:
            logger.warning("Bash is not accessible on this Windows system.")
        except FileNotFoundError:
            logger.warning("Bash is not found on this Windows system.")
    else:  # Non-Windows systems
        fullparse_command.insert(0, "bash")
    
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
    
    # Generate timestamp once and use it consistently
    date_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    metrics_file = os.path.normpath(os.path.join(args.input, "temp_results", "ontologies", "imports", os.path.splitext(os.path.basename(ontology_file))[0], date_str, "metrics", f"{os.path.splitext(os.path.basename(ontology_file))[0]}.xml"))
    
    # Run fullparse.sh to generate the metrics XML file
    try:
        logger.info("Starting execution of fullparse.sh")
        logger.info(f"Executing command: {' '.join(fullparse_command)}")
        process = subprocess.Popen(fullparse_command, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Real-time logging of stdout and stderr
        for line in process.stdout:
            logger.info(f"fullparse.sh stdout: {line.strip()}")
        for line in process.stderr:
            logger.error(f"fullparse.sh stderr: {line.strip()}")
        
        returncode = process.wait()
        logger.info(f"fullparse.sh exit code: {returncode}")
        
        if returncode != 0:
            raise subprocess.CalledProcessError(returncode, fullparse_command)
        
        logger.info("fullparse.sh completed successfully")
    except subprocess.CalledProcessError as e:
        logger.error(f"fullparse.sh failed with exit code: {e.returncode}")
        logger.error(f"Command that failed: {' '.join(e.cmd)}")
        logger.exception("Exception details:")
        exit(1)
    except Exception as e:
        logger.error(f"An unexpected error occurred while running fullparse.sh: {str(e)}")
        logger.exception("Exception details:")
        exit(1)

    # Check if the metrics file was created
    if not os.path.exists(metrics_file):
        logger.error(f"Metrics file not found after running fullparse.sh: {os.path.normpath(metrics_file)}")
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


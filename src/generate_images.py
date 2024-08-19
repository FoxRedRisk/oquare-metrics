import argparse
import logging
import os
import traceback
from datetime import datetime
from Controller import Controller

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
fh = logging.FileHandler('generate_images.log')
fh.setLevel(logging.DEBUG)
fh.setFormatter(formatter)
logger.addHandler(fh)

# Example usage:
# python src/generate_images.py -i ./output -s ./ontologies -f my_ontology.owl -d 2023-08-18_14-30-00 -M -c -S -m -e

def main():
    logger.info("Starting generate_images.py")
    try:
        parser = argparse.ArgumentParser(description='Generate OQuaRE Metrics Images')
        parser.add_argument('-i', '--input', required=True, help='Input path')
        parser.add_argument('-s', '--source', required=True, help='Ontology source folder')
        parser.add_argument('-f', '--file', required=True, help='Ontology file name')
        parser.add_argument('-d', '--date', required=True, help='Date of the metrics file (YYYY-MM-DD_HH-MM-SS)')
        parser.add_argument('-M', '--model', action='store_true', help='Generate model plot')
        parser.add_argument('-c', '--characteristics', action='store_true', help='Generate characteristics plot')
        parser.add_argument('-S', '--subcharacteristics', action='store_true', help='Generate subcharacteristics plot')
        parser.add_argument('-m', '--metrics', action='store_true', help='Generate metrics plot')
        parser.add_argument('-e', '--evolution', action='store_true', help='Generate evolution plot')
    
        args = parser.parse_args()
        logger.info(f"Arguments: {args}")

        # Add .xml extension if not provided
        if not args.file.lower().endswith('.xml'):
            args.file += '.xml'
        
        # Define the location for the metrics file
        metrics_file = os.path.join(args.input, "metrics", f"{os.path.splitext(os.path.basename(args.file))[0]}.xml").replace('\\', '/')
        
        logger.info(f"Checking for metrics file at: {metrics_file}")
        if not os.path.exists(metrics_file):
            logger.error(f"Metrics file not found at: {metrics_file}")
            exit(1)
        
        logger.info(f"Found metrics file at: {metrics_file}")

        logger.info(f"Using metrics file: {metrics_file}")
        
        # Verify the content of the metrics file
        try:
            with open(metrics_file, 'r') as f:
                metrics_content = f.read()
                logger.info(f"Metrics file content (first 100 characters): {metrics_content[:100]}")
        except Exception as e:
            logger.error(f"Error reading metrics file: {str(e)}")

        # Initialize the Controller
        controller = Controller()

        # Generate the images
        output_path = os.path.normpath(os.path.join(args.input, "metrics")).replace('\\', '/')
        if not output_path.startswith("./"):
            output_path = f"./{output_path}"
        logger.info(f"Output path for images: {output_path}")

        file_name = os.path.normpath(os.path.splitext(os.path.basename(args.file))[0]).replace('\\', '/')
        if args.model:
            controller.handle_oquare_model(file_name, args.input, args.source, args.date)
        if args.characteristics:
            controller.handle_characteristics(output_path, file_name)
        if args.subcharacteristics:
            controller.handle_subcharacteristics(output_path, file_name)
        if args.metrics:
            controller.handle_metrics(output_path, file_name)
        if args.evolution:
            controller.handle_metrics_evolution(file_name, args.input, args.source, args.date)
            controller.handle_characteristics_evolution(file_name, args.input, args.source, args.date)
            controller.handle_subcharacteristics_evolution(file_name, args.input, args.source, args.date)

        logger.info("Image generation completed successfully")
    except Exception as e:
        logger.error(f"An error occurred during image generation: {str(e)}")
        logger.error(traceback.format_exc())

if __name__ == '__main__':
    logger.info("Starting generate_images.py")
    main()

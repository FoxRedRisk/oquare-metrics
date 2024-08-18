import argparse
import logging
import os
from datetime import datetime
from Controller import Controller

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Example usage:
# python src/generate_images.py -i ./output -s ./ontologies -f my_ontology.owl -d 2023-08-18_14-30-00 -M -c -S -m -e

def main():
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
    logging.info(f"Arguments: {args}")

    # Add .owl extension if not provided
    if not args.file.lower().endswith(('.owl', '.rdf', '.ttl')):
        args.file += '.owl'
    
    # Construct the path to the metrics file
    metrics_file = os.path.join(
        args.input,
        "results",
        "ontologies",
        "imports",
        os.path.splitext(args.file)[0],
        args.date,
        "metrics",
        f"{os.path.splitext(args.file)[0]}.xml"
    )
    
    logging.info(f"Looking for metrics file at: {metrics_file}")
    
    if not os.path.exists(metrics_file):
        logging.error(f"Metrics file not found: {metrics_file}")
        logging.error(f"Current working directory: {os.getcwd()}")
        logging.error(f"Input path: {args.input}")
        logging.error(f"Source path: {args.source}")
        logging.error(f"File: {args.file}")
        logging.error(f"Date: {args.date}")
        
        # Check if the input directory exists
        if not os.path.exists(args.input):
            logging.error(f"Input directory does not exist: {args.input}")
        else:
            logging.info(f"Contents of input directory {args.input}:")
            logging.info(os.listdir(args.input))
        
        # Check the temp_results directory
        temp_results_dir = os.path.join(args.input, "temp_results")
        if not os.path.exists(temp_results_dir):
            logging.error(f"temp_results directory does not exist: {temp_results_dir}")
        else:
            logging.info(f"Contents of temp_results directory {temp_results_dir}:")
            logging.info(os.listdir(temp_results_dir))
        
        # Try to list contents of parent directories
        parent_dir = os.path.dirname(metrics_file)
        for _ in range(4):  # Go up to 4 levels
            logging.error(f"Checking contents of {parent_dir}:")
            try:
                logging.error(os.listdir(parent_dir))
            except FileNotFoundError:
                logging.error(f"Directory {parent_dir} does not exist")
            parent_dir = os.path.dirname(parent_dir)
        
        exit(1)

    # Initialize the Controller
    controller = Controller()

    # Generate the images
    output_path = os.path.dirname(os.path.dirname(metrics_file))
    logging.info(f"Output path for images: {output_path}")

    file_name = os.path.splitext(os.path.basename(args.file))[0]
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

    logging.info("Image generation completed successfully")

if __name__ == '__main__':
    logging.info("Starting generate_images.py")
    main()

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
    metrics_file = os.path.normpath(os.path.join(
        args.input,
        args.source.lstrip('./\\'),  # Remove leading ./ or .\ if present
        os.path.splitext(args.file)[0],
        args.date,
        "metrics",
        f"{os.path.splitext(args.file)[0]}.xml"
    ))
    
    logging.info(f"Looking for metrics file at: {metrics_file}")
    
    if not os.path.exists(metrics_file):
        logging.error(f"Metrics file not found: {metrics_file}")
        logging.error(f"Current working directory: {os.getcwd()}")
        logging.error(f"Input path: {args.input}")
        logging.error(f"Source path: {args.source}")
        logging.error(f"File: {args.file}")
        logging.error(f"Date: {args.date}")
        logging.error(f"Directory contents of {os.path.dirname(metrics_file)}:")
        try:
            logging.error(os.listdir(os.path.dirname(metrics_file)))
        except FileNotFoundError:
            logging.error(f"Directory {os.path.dirname(metrics_file)} does not exist")
        
        # Try to list contents of parent directories
        parent_dir = os.path.dirname(metrics_file)
        for _ in range(3):  # Go up to 3 levels
            parent_dir = os.path.dirname(parent_dir)
            logging.error(f"Contents of {parent_dir}:")
            try:
                logging.error(os.listdir(parent_dir))
            except FileNotFoundError:
                logging.error(f"Directory {parent_dir} does not exist")
        
        exit(1)

    # Initialize the Controller
    controller = Controller()

    # Generate the images
    output_path = os.path.dirname(os.path.dirname(metrics_file))
    output_path = os.path.normpath(output_path)
    logging.info(f"Output path for images: {output_path}")

    if args.model:
        controller.plot_oquare_values(metrics_file, output_path)
    if args.characteristics:
        controller.plot_oquare_characteristics(metrics_file, output_path)
    if args.subcharacteristics:
        controller.plot_oquare_subcharacteristics(metrics_file, output_path)
    if args.metrics:
        controller.plot_metrics(metrics_file, output_path)
    if args.evolution:
        controller.plot_evolution(metrics_file, output_path)

    logging.info("Image generation completed successfully")

if __name__ == '__main__':
    logging.info("Starting generate_images.py")
    main()

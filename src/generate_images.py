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
    # Try to find the metrics file in different locations
    possible_locations = [
        os.path.join(args.input, "results", "ontologies", "imports", os.path.splitext(args.file)[0], args.date, "metrics"),
        os.path.join(args.input, "temp_results", "ontologies", "imports", os.path.splitext(args.file)[0], args.date, "metrics"),
        os.path.join(args.input, "temp_results", args.source, os.path.splitext(args.file)[0], args.date, "metrics")
    ]

    metrics_file = None
    for location in possible_locations:
        potential_file = os.path.join(location, f"{os.path.splitext(args.file)[0]}.xml")
        if os.path.exists(potential_file):
            metrics_file = potential_file
            break

    if metrics_file is None:
        logging.error("Metrics file not found in any of the expected locations.")
        for location in possible_locations:
            logging.error(f"Checked location: {location}")
            if os.path.exists(os.path.dirname(location)):
                logging.info(f"Contents of {os.path.dirname(location)}:")
                logging.info(os.listdir(os.path.dirname(location)))
            else:
                logging.error(f"Directory does not exist: {os.path.dirname(location)}")
        exit(1)

    logging.info(f"Found metrics file at: {metrics_file}")

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

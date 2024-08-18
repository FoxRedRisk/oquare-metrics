import sys
import os
import argparse
import subprocess
import logging
from datetime import datetime
from Controller import Controller

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    parser = argparse.ArgumentParser(description='OQuaRE Metrics Generator')
    parser.add_argument('-i', '--input', required=True, help='Input path')
    parser.add_argument('-s', '--source', required=True, help='Ontology source folder')
    parser.add_argument('-f', '--file', required=True, help='Ontology file name')
    parser.add_argument('-M', '--model', action='store_true', help='Plot OQuaRE model metrics')
    parser.add_argument('-c', '--characteristics', action='store_true', help='Plot OQuaRE characteristics metrics')
    parser.add_argument('-S', '--subcharacteristics', action='store_true', help='Plot OQuaRE subcharacteristics metrics')
    parser.add_argument('-m', '--metrics', action='store_true', help='Plot OQuaRE fine-grained metrics')
    parser.add_argument('-e', '--evolution', action='store_true', help='Plot evolution of metrics')
    
    args = parser.parse_args()
    logging.info(f"Arguments: {args}")

    date = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    
    # Run fullparse.py to generate the metrics XML file
    fullparse_command = [
        "python", "src/fullparse.py",
        args.input, args.source, "", args.file, "HermiT",
        str(args.model).lower(), str(args.characteristics).lower(),
        str(args.subcharacteristics).lower(), str(args.metrics).lower(),
        str(args.evolution).lower()
    ]
    logging.info(f"Running fullparse.py with command: {' '.join(fullparse_command)}")
    try:
        subprocess.run(fullparse_command, check=True, text=True, capture_output=True)
        logging.info("fullparse.py completed successfully")
    except subprocess.CalledProcessError as e:
        logging.error(f"fullparse.py failed with exit code: {e.returncode}")
        logging.error(f"Error output: {e.stderr}")
        sys.exit(1)

    controller = Controller()

    temp_path = f"{args.input}/temp_results/"
    logging.info(f"Temporary path: {temp_path}")

    if args.model:
        logging.info(f"Handling OQuaRE model: {temp_path}, {args.file}, {args.input}, {args.source}, {date}")
        controller.handle_oquare_model(args.file, args.input, args.source, date)

    temp_path += f"{args.source}/{args.file}/{date}"
    logging.info(f"Updated temporary path: {temp_path}")

    metrics_file = f"{temp_path}/metrics/{args.file}.xml"
    logging.info(f"Checking for metrics file: {metrics_file}")
    if not os.path.exists(metrics_file):
        logging.error(f"Error: Metrics file not found: {metrics_file}")
        logging.error("Please check if the fullparse.py script generated the metrics file correctly.")
        logging.debug("Contents of temp_path directory:")
        for root, dirs, files in os.walk(temp_path):
            for name in files:
                logging.debug(os.path.join(root, name))
        sys.exit(1)
    else:
        logging.info(f"Metrics file found: {metrics_file}")

    if args.characteristics:
        logging.info("Handling characteristics")
        controller.handle_characteristics(temp_path, args.file)
        if args.evolution:
            logging.info("Handling characteristics evolution")
            controller.handle_characteristics_evolution(args.file, args.input, args.source, date)

    if args.subcharacteristics:
        logging.info("Handling subcharacteristics")
        controller.handle_subcharacteristics(temp_path, args.file)
        if args.evolution:
            logging.info("Handling subcharacteristics evolution")
            controller.handle_subcharacteristics_evolution(args.file, args.input, args.source, date)

    if args.metrics:
        logging.info("Handling metrics")
        controller.handle_metrics(temp_path, args.file)
        if args.evolution:
            logging.info("Handling metrics evolution")
            controller.handle_metrics_evolution(args.file, args.input, args.source, date)

    logging.info("Main script completed successfully")

if __name__ == '__main__':
    logging.info("Starting main.py")
    main()


import sys
import argparse
from datetime import datetime
from Controller import Controller

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

    date = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    controller = Controller()

    temp_path = f"{args.input}/temp_results/"

    if args.model:
        print(temp_path, args.file, args.input, args.source, date)
        controller.handle_oquare_model(args.file, args.input, args.source, date)

    temp_path += f"{args.source}/{args.file}/{date}"

    if args.characteristics:
        controller.handle_characteristics(temp_path, args.file)
        if args.evolution:
            controller.handle_characteristics_evolution(args.file, args.input, args.source, date)

    if args.subcharacteristics:
        controller.handle_subcharacteristics(temp_path, args.file)
        if args.evolution:
            controller.handle_subcharacteristics_evolution(args.file, args.input, args.source, date)

    if args.metrics:
        controller.handle_metrics(temp_path, args.file)
        if args.evolution:
            controller.handle_metrics_evolution(args.file, args.input, args.source, date)

if __name__ == '__main__':
    main()


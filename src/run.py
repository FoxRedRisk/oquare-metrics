import subprocess
import argparse

def main():
    parser = argparse.ArgumentParser(description="Run OQuaRE ontology evaluation")
    parser.add_argument("contents_folder", help="Folder to store results")
    parser.add_argument("ontology_folders", help="Folders containing ontologies")
    parser.add_argument("ignore_files", help="Files to ignore")
    parser.add_argument("ontology_files", help="Specific ontology files to process")
    parser.add_argument("reasoner", help="Reasoner to use")
    parser.add_argument("--model-plot", choices=['true', 'false'], default='true', help="Plot OQuaRE model")
    parser.add_argument("--characteristics-plot", choices=['true', 'false'], default='true', help="Plot characteristics")
    parser.add_argument("--subcharacteristics-plot", choices=['true', 'false'], default='true', help="Plot subcharacteristics")
    parser.add_argument("--metrics-plot", choices=['true', 'false'], default='true', help="Plot metrics")
    parser.add_argument("--release", choices=['true', 'false'], default='false', help="Run as release")

    args = parser.parse_args()

    cmd = [
        "bash",
        "fullparse.sh",
        args.contents_folder,
        args.ontology_folders,
        args.ignore_files,
        args.ontology_files,
        args.reasoner,
        args.model_plot,
        args.characteristics_plot,
        args.subcharacteristics_plot,
        args.metrics_plot,
        args.release
    ]

    if args.release == 'true':
        cmd.append('true')  # evolution_plot

    subprocess.run(cmd, check=True)

if __name__ == "__main__":
    main()

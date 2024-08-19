# OQuaRE Metrics

A module to automatically obtain metrics from ontology files based on the OQuaRE framework for ontology quality evaluation, generating visual reports which showcase the quality of each ontology.

## OQuaRE

OQuaRE is a framework developed by Astrid Duque Ramos which defines an ontology evaluation system based on ISO/IEC 25000:2005 (SQuaRE). It is presented as an ontology quality evaluation adapted to the software quality standard SQuaRE, which allows traceability within requirements and metrics of an ontology, with the goal of measuring its characteristics in an objective and reproducible way, as well as bringing assistance to users and developers in making informed decisions.

## Features

* Robust tool for ontology metrics, based on OQuaRE framework for ontology quality evaluation
* Set of different plots and graphs, showcasing various aspects of ontology quality and how modifications affect them
* Multiple ontology source folders
* Two different ontology reasoners for ontology metrics calculation (ELK and HermiT)
* Possibility to ignore certain files that might not want to be parsed
* Individual ontology file parsing instead of by folders

## Requirements

* Java 17
* Python 3.9 or higher
* Required Python libraries (matplotlib, matplotx)

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/your-repo/OQuaRE-Metrics.git
   cd OQuaRE-Metrics
   ```

2. Install the required Python libraries:
   ```
   pip install -r requirements.txt
   ```

## Usage

You can run the application using the main Python script:

```
python src/main.py -i <input_path> -s <source_folder> -f <ontology_file> -r <reasoner> [-M] [-c] [-S] [-m] [-e]
```

### Parameters:

- `-i <input_path>`: Path where you want to store the results
- `-s <source_folder>`: Folder containing your ontology files
- `-f <ontology_file>`: Name of the specific ontology file you want to analyze
- `-r <reasoner>`: Reasoner to use (default: HermiT)
- `-M`: Generate model plot
- `-c`: Generate characteristics plot
- `-S`: Generate subcharacteristics plot
- `-m`: Generate metrics plot
- `-e`: Generate evolution plot

### Example:

```
python src/main.py -i ./output -s ./ontologies -f my_ontology.owl -r HermiT -M -c -S -m -e
```

This example will run the analysis on the ontology file "my_ontology.owl" in the "./ontologies" folder, using the HermiT reasoner, and generate all available plots. The output will be stored in the "./output" directory.

Note: The script will automatically add the .owl extension to the ontology file name if it's not provided.

## Output

After running the script, you will find the following in your specified output directory:

1. A `README.md` file containing a summary of the analysis
2. An `img` folder containing various plots:
   - OQuaRE model values plot
   - Characteristics values plot
   - Subcharacteristics metrics plots
   - Metrics and scaled metrics plots
   - Evolution plots for characteristics, subcharacteristics, and metrics (if `-e` option is used)

## Troubleshooting

If you encounter any issues with OWL files, you can use the `fixowl.py` script to attempt to fix common problems:

```
python fixowl.py
```

This script will check OWL files in the `ontologies/imports` folder for errors and try to fix them.

## Contact

If you encounter any issues or have questions about this module, please:

1. Create an issue in this repository explaining the problem
2. Or contact gonzalo.nicolasm@um.es

Your feedback is valuable and helps improve the tool. Thank you!


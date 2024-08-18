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

## Usage

1. Clone this repository
2. Install the required Python libraries:
   ```
   pip install matplotlib matplotx
   ```
3. Run the main script:
   ```
   python src/main.py -i <input_path> -s <ontology_source> -f <file> -d <date> -M <model_plot> -c <characteristics_plot> -S <subcharacteristics_plot> -m <metrics_plot> -e <evolution_plot>
   ```

   Where:
   - `<input_path>`: Path to the input folder
   - `<ontology_source>`: Source folder containing the ontology file
   - `<file>`: Name of the ontology file
   - `<date>`: Current date in format YYYY-MM-DD_HH-MM-SS
   - `<model_plot>`, `<characteristics_plot>`, `<subcharacteristics_plot>`, `<metrics_plot>`, `<evolution_plot>`: Boolean values (true/false) to indicate which plots to generate

## Contact

If there are any issues regarding this module, please contact gonzalo.nicolasm@um.es, or create an issue in this repository explaining the error. Thank you!


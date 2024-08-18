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
   pip install -r requirements.txt
   ```
3. You can run the application in two ways:

   a. Using the main Python script:
   ```
   python src/main.py -i <input_path> -s <ontology_source> -f <file> -r <reasoner> [-M] [-c] [-S] [-m] [-e]
   ```

   b. Directly using the fullparse.sh script:
   ```
   bash ./src/fullparse.sh -i <input_path> -s <ontology_source> -f <file> -r <reasoner> [-M] [-c] [-S] [-m] [-e]
   ```

   Where:
   - `<input_path>`: Path to the input folder
   - `<ontology_source>`: Source folder containing the ontology file
   - `<file>`: Name of the ontology file
   - `<reasoner>`: Reasoner to use (default: HermiT)
   - `-M`: Generate model plot
   - `-c`: Generate characteristics plot
   - `-S`: Generate subcharacteristics plot
   - `-m`: Generate metrics plot
   - `-e`: Generate evolution plot

   Example:
   ```
   python src/main.py -i ./output -s ./ontologies -f my_ontology.owl -r HermiT -M -c -S -m -e
   ```
   or
   ```
   bash ./src/fullparse.sh -i ./output -s ./ontologies -f my_ontology.owl -r HermiT -M -c -S -m -e
   ```

   These examples will run the application on the ontology file "my_ontology.owl" in the "./ontologies" folder, using the HermiT reasoner, and generate all available plots. The output will be stored in the "./output" directory.

## Contact

If there are any issues regarding this module, please contact gonzalo.nicolasm@um.es, or create an issue in this repository explaining the error. Thank you!


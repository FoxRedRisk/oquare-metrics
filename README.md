# OQuaRE Metrics

A module to automatically obtain metrics from ontology files based on the OQuaRE framework for ontology quality evaluation, generating visual reports which showcase the quality of each ontology.

## OQuaRE

OQuaRE is a framework developed by Astrid Duque Ramos which defines an ontology evaluation system based on ISO/IEC 25000:2005 (SQuaRE). It is presented as an ontology quality evaluation adapted to the software quality standard SQuaRE, which allows traceability within requirements and metrics of an ontology, with the goal of measuring its characteristics in an objective and reproducible way, as well as bringing assistance to users and developers in making informed decisions.

## Features

* Robust tool for ontology metrics, based on OQuaRE framework for ontology quality evaluation
* Set of different plots and graphs, showcasing various aspects of ontology quality and how modifications affect them
* **Side-by-side ontology comparison** with comprehensive visualizations and reports
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
python src/main.py -i ./output -s ./ontologies/imports -f TD1.owl -r HermiT -M -c -S -m -e
```

```
D:/Code/oquare-metrics/src/fullparse.sh -i "./output" -s "./ontologies/imports" -f "TD1.owl" -r HermiT -M -c -S -m -e
```
```
 java -jar D:/Code/oquare-metrics/libs/oquare-versions.jar --ontology "/ontologies/imports/TD1" --reasoner "HermiT" --outputFil "D:/Code/oquare-metrics/output/metrics/TD1.xml"
```

```
python src/generate_images.py -i ./output -s ./ontologies -f TD1.owl -d 2023-08-18_14-30-00 -M -c -S -m -e
```


This example will run the analysis on the ontology file "my_ontology.owl" in the "./ontologies" folder, using the HermiT reasoner, and generate all available plots. The output will be stored in the "./output" directory.

Note: The script will automatically add the .owl extension to the ontology file name if it's not provided.

## Comparing Ontologies

OQuaRE Metrics now supports comparing quality metrics between two ontologies, enabling you to:
- Track quality improvements across ontology versions
- Validate refactoring efforts
- Compare alternative design approaches
- Benchmark against reference ontologies

### Usage

Compare two ontologies using their metrics XML files:

```bash
python src/compare.py \
  --ontology1 path/to/first/ontology.xml \
  --ontology2 path/to/second/ontology.xml
```

### Command-Line Options

- `--ontology1`: Path to first ontology XML metrics file (required)
- `--ontology2`: Path to second ontology XML metrics file (required)
- `--output`: Output directory for comparison results (default: `output/comparisons`)
- `--name1`: Custom display name for first ontology (optional)
- `--name2`: Custom display name for second ontology (optional)
- `--verbose`: Enable verbose logging (optional)

### Examples

**Basic comparison:**
```bash
python src/compare.py \
  --ontology1 output/lecture/metrics/lecture.xml \
  --ontology2 output/lecture_improved/metrics/Lecture_improved.xml
```

**Comparison with custom names:**
```bash
python src/compare.py \
  --ontology1 output/lecture/metrics/lecture.xml \
  --ontology2 output/lecture_improved/metrics/Lecture_improved.xml \
  --name1 "Original Version" \
  --name2 "Improved Version"
```

**Comparison with custom output directory:**
```bash
python src/compare.py \
  --ontology1 output/lecture/metrics/lecture.xml \
  --ontology2 output/lecture_improved/metrics/Lecture_improved.xml \
  --output ./my_comparisons
```

### Comparison Output

The comparison tool generates comprehensive results in `output/comparisons/{ontology1}_vs_{ontology2}/`:

**Generated Files:**
1. **README.md** - Comprehensive comparison report with:
   - Executive summary with improvement/degradation counts
   - Characteristics comparison table
   - Metrics comparison table with status indicators (✅/❌/➖)
   - Top 5 improvements and degradations
   - Embedded visualizations

2. **comparison_summary.json** - Machine-readable summary containing:
   - Raw and scaled metrics for both ontologies
   - Characteristics and subcharacteristics values
   - Difference calculations and percent changes
   - Timestamp and metadata

3. **img/** - 11 visualization files:
   - `*_characteristics_comparison.png` - Spider plot of all 7 characteristics
   - `*_metrics_comparison.png` - Side-by-side lollipop plot of all metrics
   - `*_scaled_metrics_comparison.png` - Scaled metrics (1-5 scale) comparison
   - `*_metrics_difference.png` - Difference chart (green=improvement, red=degradation)
   - 7 subcharacteristics comparison plots (one per characteristic)

### Interpreting Results

**Status Indicators:**
- ✅ **Improved** - Metric/characteristic increased (better quality)
- ❌ **Degraded** - Metric/characteristic decreased (lower quality)
- ➖ **Unchanged** - No change in value

**Metrics vs Scaled Metrics:**
- **Raw Metrics**: Absolute values from ontology analysis
- **Scaled Metrics**: Normalized to 1-5 scale for easier comparison
- Both are important: raw metrics show actual changes, scaled metrics show relative quality

**Understanding Percent Changes:**
- Positive percentages (+) indicate improvements
- Negative percentages (-) indicate degradations
- "N/A" appears when dividing by zero (original value was 0)

### Use Cases

1. **Version Comparison**: Track quality evolution between releases
2. **Refactoring Validation**: Verify improvements after restructuring
3. **Design Alternatives**: Compare different architectural approaches
4. **Quality Benchmarking**: Measure against reference ontologies
5. **Documentation**: Generate professional comparison reports

### Testing

For detailed testing documentation and validation results, see [`COMPARISON_TESTING.md`](COMPARISON_TESTING.md).

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
2. Or contact info@foxredrisk.com

Your feedback is valuable and helps improve the tool. Thank you!


# OQuaRE Metrics

A comprehensive Python-based tool for automatically calculating and visualizing ontology quality metrics based on the OQuaRE (Ontology Quality Evaluation) framework. This tool analyzes ontology files, generates detailed quality reports, and provides visual comparisons to help developers improve their ontologies.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
  - [Basic Usage](#basic-usage)
  - [Command-Line Options](#command-line-options)
  - [Examples](#examples)
- [Comparing Ontologies](#comparing-ontologies)
- [GitHub Actions Integration](#github-actions-integration)
- [OQuaRE Metrics](#oquare-metrics)
- [Output Structure](#output-structure)
- [Supported Formats](#supported-formats)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [Contact](#contact)

## Overview

**OQuaRE** (Ontology Quality Evaluation) is a framework developed by Astrid Duque Ramos that defines an ontology evaluation system based on ISO/IEC 25000:2005 (SQuaRE). It provides an ontology quality evaluation adapted to the software quality standard SQuaRE, enabling:

- **Traceability** within requirements and metrics of an ontology
- **Objective and reproducible** measurement of ontology characteristics
- **Informed decision-making** for users and developers
- **Quality improvement** through actionable recommendations

This tool implements the complete OQuaRE framework, providing automated metrics calculation, visualization, and comparison capabilities.

## Features

### Core Functionality

- **🎯 Comprehensive Metrics Calculation**: Implements all 14 OQuaRE quality metrics with detailed formulas and explanations
- **📊 Rich Visualizations**: Multiple plot types including spider charts, bar charts, lollipop plots, and evolution graphs
- **🔄 Ontology Comparison**: Side-by-side comparison of two ontologies with detailed difference analysis
- **📈 Evolution Tracking**: Track quality metrics across up to 20 versions of an ontology
- **⚙️ Multiple Reasoners**: Support for both ELK and HermiT reasoners for ontology reasoning
- **🤖 GitHub Actions Integration**: Automated quality checks in CI/CD pipelines
- **📝 Detailed Reports**: Auto-generated README files with comprehensive analysis and recommendations
- **🎨 Publication-Ready Graphics**: High-quality visualizations suitable for papers and presentations

### Advanced Features

- **Quality Scoring**: L1-L5 scoring system for each metric based on OQuaRE thresholds
- **Improvement Recommendations**: Actionable suggestions for metrics with low scores
- **Batch Processing**: Analyze multiple ontologies or folders in a single run
- **Change Detection**: Automatically process only modified ontologies in workflows
- **Force Parsing**: Override change detection to reprocess specific ontologies
- **Flexible Output**: JSON, XML, and Markdown formats for integration with other tools
- **Extensive Logging**: Detailed logs for debugging and monitoring

## Requirements

### System Requirements

- **Java 17** or higher (for OQuaRE JAR execution)
- **Python 3.9** or higher
- Minimum 4GB RAM (8GB+ recommended for large ontologies)

### Python Dependencies

All required Python libraries are listed in `requirements.txt`:

- `matplotlib` - Plotting and visualization
- `matplotx` - Enhanced plot styling
- `owlready2` - OWL ontology manipulation
- Additional dependencies for reasoner support

## Installation

1. **Clone this repository**:
   ```bash
   git clone https://github.com/your-repo/oquare-metrics.git
   cd oquare-metrics
   ```

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Verify Java installation**:
   ```bash
   java -version
   ```
   Ensure Java 17 or higher is installed.

4. **Test the installation**:
   ```bash
   python src/main.py --help
   ```

## Usage

### Basic Usage

The primary script for analyzing ontologies is `main.py`:

```bash
python src/main.py -i <output_path> -s <source_folder> -f <ontology_file> -r <reasoner> [options]
```

### Command-Line Options

#### Required Arguments

| Argument | Description |
|----------|-------------|
| `-i`, `--input` | Output path for storing results |
| `-s`, `--source` | Folder containing ontology files |
| `-f`, `--file` | Ontology file name to analyze |

#### Optional Arguments

| Argument | Default | Description |
|----------|---------|-------------|
| `-r`, `--reasoner` | HermiT | Reasoner to use (`HermiT` or `ELK`) |
| `-M`, `--model` | False | Generate OQuaRE model plot |
| `-c`, `--characteristics` | False | Generate characteristics plot |
| `-S`, `--subcharacteristics` | False | Generate subcharacteristics plots |
| `-m`, `--metrics` | False | Generate metrics plots |
| `-e`, `--evolution` | False | Generate evolution plots (requires previous versions) |

### Examples

#### Analyze a single ontology with all visualizations

```bash
python src/main.py -i ./output -s ./ontologies/imports -f lecture.owl -r HermiT -M -c -S -m -e
```

#### Use ELK reasoner for faster processing

```bash
python src/main.py -i ./output -s ./ontologies -f bfo-core.owl -r ELK -M -c -S -m
```

#### Analyze without evolution plots

```bash
python src/main.py -i ./output -s ./ontologies -f my_ontology.owl -r HermiT -M -c -S -m
```

#### PowerShell example (Windows)

```powershell
python src/main.py -i "./output" -s "./ontologies/imports" -f "my_ontology.owl" -r "HermiT" -M -c -S -m -e
```

#### Using Java JAR directly (advanced)

```bash
java -jar libs/oquare-versions.jar --ontology "./ontologies/imports/lecture.owl" --reasoner "HermiT" --outputFile "./output/metrics/lecture.xml"
```

## Comparing Ontologies

The comparison tool enables detailed quality comparison between two ontologies, making it ideal for:

- **Version comparison**: Track quality improvements across releases
- **Refactoring validation**: Verify quality improvements after restructuring
- **Design alternatives**: Compare different architectural approaches
- **Benchmarking**: Measure against reference ontologies

### Basic Comparison

```bash
python src/compare.py \
  --ontology1 output/lecture/metrics/lecture.xml \
  --ontology2 output/lecture_improved/metrics/Lecture_improved.xml
```

### Advanced Comparison Options

| Option | Description |
|--------|-------------|
| `--ontology1` | Path to first ontology XML metrics file (required) |
| `--ontology2` | Path to second ontology XML metrics file (required) |
| `--output` | Output directory (default: `output/comparisons`) |
| `--name1` | Custom display name for first ontology |
| `--name2` | Custom display name for second ontology |
| `--verbose`, `-v` | Enable verbose logging |

### Comparison Examples

**Compare with custom names:**
```bash
python src/compare.py \
  --ontology1 output/lecture/metrics/lecture.xml \
  --ontology2 output/lecture_improved/metrics/Lecture_improved.xml \
  --name1 "Original Lecture Ontology" \
  --name2 "Improved Lecture Ontology"
```

**Compare with custom output directory:**
```bash
python src/compare.py \
  --ontology1 output/bfo/metrics/bfo-core.xml \
  --ontology2 output/iao/metrics/iao.xml \
  --output ./custom_comparisons \
  --verbose
```

### Comparison Output

The comparison generates a comprehensive report in `output/comparisons/{ontology1}_vs_{ontology2}/`:

#### Generated Files

1. **README.md** - Comprehensive comparison report including:
   - Executive summary with improvement/degradation counts
   - Characteristics comparison table
   - Complete metrics comparison with status indicators (✅ improved / ❌ degraded / ➖ unchanged)
   - Top 5 improvements and degradations
   - Embedded visualization images

2. **comparison_summary.json** - Machine-readable data containing:
   - Raw and scaled metrics for both ontologies
   - All characteristics and subcharacteristics values
   - Difference calculations and percent changes
   - Timestamp and metadata

3. **img/** directory - 11 visualization files:
   - `*_characteristics_comparison.png` - Spider plot comparing all 7 characteristics
   - `*_metrics_comparison.png` - Side-by-side lollipop plot of all metrics
   - `*_scaled_metrics_comparison.png` - Scaled metrics (1-5 scale) comparison
   - `*_metrics_difference.png` - Difference chart (green=improvement, red=degradation)
   - 7 subcharacteristics plots (one per characteristic)

### Interpreting Comparison Results

**Status Indicators:**
- ✅ **Improved** - Metric/characteristic value increased (better quality)
- ❌ **Degraded** - Metric/characteristic value decreased (lower quality)
- ➖ **Unchanged** - No change in value

**Understanding Metrics:**
- **Raw Metrics**: Absolute values from ontology analysis (e.g., number of classes, properties)
- **Scaled Metrics**: Normalized to 1-5 scale for standardized comparison
- Both views are important: raw metrics show actual changes, scaled metrics show relative quality

**Percent Changes:**
- Positive percentages (+) indicate improvements
- Negative percentages (-) indicate degradations
- "N/A" appears when original value was 0 (division by zero)

## GitHub Actions Integration

Automate ontology quality checks in your CI/CD pipeline using the included GitHub Action.

### Quick Setup

1. Create `.github/workflows/oquare-metrics.yml` in your repository:

```yaml
name: OQuaRE Metrics

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Calculate OQuaRE Metrics
        uses: tecnomod-um/oquare-metrics@main
        with:
          ontology-folders: 'ontologies/src'
          contents-folder: 'OQuaRE'
          reasoner: 'ELK'
          model-plot: 'true'
          characteristics-plot: 'true'
          subcharacteristics-plot: 'true'
          metrics-plot: 'true'
          evolution-plot: 'true'
```

### Action Inputs

| Input | Required | Default | Description |
|-------|----------|---------|-------------|
| `ontology-folders` | No | `''` | Folders containing ontology source files (space-separated) |
| `ontology-files` | No | `''` | Individual ontology files to parse (space-separated) |
| `contents-folder` | No | `'OQuaRE'` | Folder for results and archives |
| `reasoner` | Yes | `'ELK'` | Reasoner to use (`ELK` or `HermiT`) |
| `ignore-files` | No | `''` | Files to ignore (space-separated patterns) |
| `model-plot` | No | `'true'` | Generate OQuaRE model value plots |
| `characteristics-plot` | No | `'true'` | Generate characteristics value plots |
| `subcharacteristics-plot` | No | `'true'` | Generate subcharacteristics plots |
| `metrics-plot` | No | `'true'` | Generate fine-grained metrics plots |
| `evolution-plot` | No | `'true'` | Generate evolution plots (last 20 versions) |
| `release` | No | `'false'` | Scan all ontologies (for release versions) |
| `force-parse` | No | `''` | Parse specified ontologies regardless of changes |

### Action Features

- **Change Detection**: Automatically analyzes only modified ontology files
- **First Run Support**: Processes all ontologies on initial workflow run
- **Archiving**: Preserves previous results in archives folder
- **Git Integration**: Automatically commits results back to repository
- **Release Mode**: Process all ontologies for release versions
- **Force Parsing**: Override change detection for specific files

### Advanced GitHub Actions Example

```yaml
name: Advanced OQuaRE Analysis

on:
  push:
    branches: [ main ]
    paths:
      - 'ontologies/**'
  schedule:
    - cron: '0 0 * * 0'  # Weekly on Sunday

jobs:
  analyze-ontologies:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 0  # Full history for evolution plots
      
      - name: Analyze Changed Ontologies
        uses: tecnomod-um/oquare-metrics@main
        with:
          ontology-folders: 'ontologies/core ontologies/modules'
          ontology-files: 'ontologies/special/custom.owl'
          contents-folder: 'quality-reports'
          reasoner: 'ELK'
          ignore-files: '*.backup.owl *-test.owl'
          model-plot: 'true'
          characteristics-plot: 'true'
          subcharacteristics-plot: 'true'
          metrics-plot: 'true'
          evolution-plot: 'true'
          release: 'false'
          force-parse: ''
      
      - name: Archive Results
        uses: actions/upload-artifact@v3
        with:
          name: oquare-reports
          path: quality-reports/
```

## Reasoners

OQuaRE Metrics supports three different OWL reasoners for ontology analysis. The choice of reasoner can significantly impact processing time and the types of inferences performed.

### Supported Reasoners

#### HermiT Reasoner (Default)

**HermiT** is a highly expressive OWL 2 DL reasoner that provides complete reasoning capabilities.

**Characteristics:**
- **Expressivity**: Full OWL 2 DL support (most expressive)
- **Correctness**: Highly accurate with complete inference capabilities
- **Speed**: Slower, especially on large or complex ontologies
- **Memory**: Higher memory consumption
- **Best for**: Small to medium ontologies requiring complete reasoning

**When to use HermiT:**
- When you need full OWL 2 DL reasoning capabilities
- For ontologies with complex axioms and relationships
- When correctness is more important than speed
- For research and validation purposes
- For ontologies under 10,000 classes

**Example:**
```bash
python src/main.py -i ./output -s ./ontologies -f my_ontology.owl -r HermiT -M -c -S -m
```

#### Pellet Reasoner

**Pellet** is another OWL 2 DL reasoner with full reasoning capabilities, similar to HermiT.

**Characteristics:**
- **Expressivity**: Full OWL 2 DL support
- **Correctness**: Complete OWL 2 reasoning with good standards compliance
- **Speed**: Similar to HermiT, slower than ELK
- **Memory**: Moderate to high memory consumption
- **Best for**: Alternative to HermiT for OWL 2 reasoning
- **Availability**: Supported in Python-based direct metrics calculation

**When to use Pellet:**
- As an alternative to HermiT for full OWL 2 reasoning
- When HermiT encounters specific reasoning issues
- For ontologies requiring complete OWL 2 DL semantics
- In Python-based workflows with direct ontology loading

**Example (Python metrics):**
```bash
python src/test_python_metrics.py --ontology ./ontologies/lecture.owl --reasoner Pellet --output ./output
```

**Note**: Pellet is available when using the Python-based metrics calculation directly. For the main workflow (`main.py`) and GitHub Actions, HermiT and ELK are the primary supported reasoners.

#### ELK Reasoner

**ELK** (Efficient Large-scale Knowledge base reasoning) is a specialized reasoner optimized for the EL++ profile of OWL 2.

**Characteristics:**
- **Expressivity**: Limited to EL++ profile (less expressive than HermiT)
- **Speed**: Very fast, can handle large ontologies efficiently
- **Memory**: Lower memory footprint
- **Scalability**: Excellent for large ontologies (100,000+ classes)
- **Best for**: Large ontologies, batch processing, CI/CD pipelines

**When to use ELK:**
- For large ontologies (10,000+ classes)
- When processing speed is critical
- In automated workflows and GitHub Actions
- For production environments with resource constraints
- When working with EL++ compatible ontologies

**Example:**
```bash
python src/main.py -i ./output -s ./ontologies -f large_ontology.owl -r ELK -M -c -S -m
```

### Reasoner Comparison

| Feature | HermiT | Pellet | ELK |
|---------|--------|--------|-----|
| **OWL Profile** | Full OWL 2 DL | Full OWL 2 DL | EL++ subset |
| **Speed** | Slower | Slower | Much faster |
| **Memory Usage** | Higher | Moderate-High | Lower |
| **Max Ontology Size** | ~10K classes | ~10K classes | 100K+ classes |
| **Inference Completeness** | Complete | Complete | Limited to EL++ |
| **Use Case** | Research, validation | Alternative to HermiT | Production, large ontologies |
| **Main Workflow** | ✅ Yes | ⚠️ Python only | ✅ Yes |
| **GitHub Actions** | ✅ Yes | ❌ No | ✅ Yes |
| **Default** | Yes | No | No |

### EL++ Profile

The EL++ profile is a subset of OWL 2 that includes:

**Supported constructs:**
- ✅ Subclass relationships (`SubClassOf`)
- ✅ Existential restrictions (`ObjectSomeValuesFrom`)
- ✅ Conjunctions (class intersections)
- ✅ Nominals (enumerated classes with individuals)
- ✅ Domain and range restrictions
- ✅ Transitive object properties

**Not supported:**
- ❌ Universal restrictions (`ObjectAllValuesFrom`)
- ❌ Disjunctions (unions)
- ❌ Negations (complements)
- ❌ Cardinality restrictions
- ❌ Functional properties (in some cases)

**Note**: Most biomedical and scientific ontologies (like GO, SNOMED CT, GALEN) are EL++ compatible, making ELK an excellent choice for these domains.

### Choosing the Right Reasoner

**Use HermiT if:**
- Your ontology has fewer than 10,000 classes
- You need complete OWL 2 DL reasoning
- Your ontology uses complex axioms beyond EL++
- Processing time is not a critical factor
- You're validating ontology correctness
- Using the main workflow or GitHub Actions

**Use Pellet if:**
- You need an alternative to HermiT for OWL 2 DL reasoning
- HermiT encounters specific issues with your ontology
- You're using Python-based direct metrics calculation
- Your ontology requires full OWL 2 semantics
- Your ontology has fewer than 10,000 classes

**Use ELK if:**
- Your ontology has more than 10,000 classes
- Speed and scalability are priorities
- Your ontology is EL++ compatible (most are)
- You're running automated quality checks
- You're working in a resource-constrained environment
- You're processing multiple ontologies in batch

### Performance Considerations

#### Small Ontology (< 1,000 classes)
- **HermiT**: 10-30 seconds
- **Pellet**: 10-30 seconds
- **ELK**: 5-15 seconds
- **Recommendation**: Any reasoner works well

#### Medium Ontology (1,000-10,000 classes)
- **HermiT**: 1-10 minutes
- **Pellet**: 1-10 minutes
- **ELK**: 10-60 seconds
- **Recommendation**: ELK for routine analysis, HermiT/Pellet for validation

#### Large Ontology (10,000-100,000 classes)
- **HermiT**: 10+ minutes (may timeout)
- **Pellet**: 10+ minutes (may timeout)
- **ELK**: 1-5 minutes
- **Recommendation**: ELK strongly recommended

#### Very Large Ontology (> 100,000 classes)
- **HermiT**: May fail or timeout (30 min limit)
- **Pellet**: May fail or timeout (30 min limit)
- **ELK**: 5-15 minutes
- **Recommendation**: ELK only

### Troubleshooting Reasoner Issues

#### HermiT Timeout or Out of Memory

**Problem**: HermiT takes too long or runs out of memory

**Solutions:**
1. Switch to ELK reasoner:
   ```bash
   python src/main.py -i ./output -s ./ontologies -f ontology.owl -r ELK -M -c -S -m
   ```

2. Increase Java heap space:
   ```bash
   java -Xmx8g -jar libs/oquare-versions.jar --ontology "ontology.owl" --reasoner "HermiT" --outputFile "output.xml"
   ```

3. Simplify the ontology:
   - Remove unnecessary imports
   - Reduce axiom complexity
   - Split into smaller modules

#### ELK Reasoning Incomplete

**Problem**: ELK doesn't infer all expected relationships

**Solution**: Your ontology may use OWL constructs beyond EL++. Either:
1. Simplify to EL++ compatible constructs
2. Use HermiT reasoner if ontology size permits
3. Accept partial reasoning for metrics calculation

### Reasoner Configuration in GitHub Actions

For automated workflows, we recommend ELK for better performance:

```yaml
- name: Calculate OQuaRE Metrics
  uses: tecnomod-um/oquare-metrics@main
  with:
    ontology-folders: 'ontologies/src'
    reasoner: 'ELK'  # Faster for CI/CD
    contents-folder: 'OQuaRE'
```

Switch to HermiT only if you need complete reasoning:

```yaml
- name: Calculate OQuaRE Metrics (Complete Reasoning)
  uses: tecnomod-um/oquare-metrics@main
  with:
    ontology-folders: 'ontologies/src'
    reasoner: 'HermiT'  # More complete but slower
    contents-folder: 'OQuaRE'
```

## OQuaRE Metrics

The tool calculates 14 comprehensive quality metrics across multiple dimensions:

### Structural Metrics

| Metric | Name | Description | Formula |
|--------|------|-------------|---------|
| **DITOnto** | Depth of Inheritance | Length of longest path from root to leaf class | Max(∑D\|Ci\|) |
| **NACOnto** | Number of Ancestors | Mean number of ancestor classes per leaf class | ∑\|SupC(Leaf)i\| / ∑\|C(leaf)i\| |
| **NOCOnto** | Number of Children | Mean number of direct subclasses | ∑\|RCi\| / (∑\|Ci\| - \|RThing\|) |
| **CBOOnto** | Coupling Between Objects | Number of related classes | ∑\|SupCi\| / (∑\|Ci\| - \|RThing\|) |

### Functional Metrics

| Metric | Name | Description | Formula |
|--------|------|-------------|---------|
| **ANOnto** | Annotation Richness | Mean number of annotations per class | ∑\|ACi\| / ∑\|Ci\| |
| **CROnto** | Class Richness | Mean number of instances per class | ∑\|ICi\| / ∑\|Ci\| |
| **NOMOnto** | Number of Properties | Properties per class | ∑\|PCi\| / ∑\|Ci\| |
| **INROnto** | Instance Relationships | Mean relationships per class | ∑\|RCi\| / ∑\|Ci\| |
| **AROnto** | Attribute Richness | Mean attributes per class | ∑\|AttCi\| / ∑\|Ci\| |

### Complexity Metrics

| Metric | Name | Description | Formula |
|--------|------|-------------|---------|
| **WMCOnto** | Weighted Method Count | Mean properties and relationships per class | (∑\|PCi\| + ∑\|RCi\|) / ∑\|Ci\| |
| **RFCOnto** | Response For Class | Properties directly accessible from class | (∑\|PCi\| + ∑\|SupCi\|) / (∑\|Ci\| - \|RThing\|) |
| **RROnto** | Properties Richness | Proportion of properties to relationships | ∑\|PCi\| / (∑\|RCi\| + ∑\|Ci\|) |
| **LCOMOnto** | Lack of Cohesion | Semantic relatedness of classes | ∑path(\|C(leaf)i\|) / m |
| **TMOnto** | Tangledness | Mean number of parents per class | ∑\|RCi\| / (∑\|Ci\| - ∑\|C(DP)i\|) |

### Quality Characteristics

Metrics are aggregated into 7 high-level quality characteristics:

1. **Structural** (Maintainability)
2. **Functional Adequacy**
3. **Reliability**
4. **Operability**
5. **Compatibility**
6. **Transferability**
7. **Maintainability**

### Scoring System

Each metric receives a score from L1 (lowest) to L5 (highest) based on thresholds defined in the OQuaRE framework:

- **L5**: Excellent quality (80-100%)
- **L4**: Good quality (60-80%)
- **L3**: Acceptable quality (40-60%)
- **L2**: Poor quality (20-40%)
- **L1**: Very poor quality (0-20%)

### Improvement Recommendations

For metrics scoring L1-L3, the tool provides actionable recommendations:

- Specific issues identified
- Concrete improvement strategies
- Target values to achieve higher scores
- Best practices for ontology design

## Output Structure

After analysis, the tool generates a structured output directory:

```
output/
├── metrics/
│   ├── ontology_name.xml          # Raw metrics data
│   ├── README.md                   # Analysis report
│   └── img/                        # Visualizations
│       ├── *_characteristics_values.png
│       ├── *_metrics.png
│       ├── *_scaled_metrics.png
│       └── *_*_subcharacteristics_metrics.png (7 files)
├── comparisons/
│   └── ont1_vs_ont2/
│       ├── README.md               # Comparison report
│       ├── comparison_summary.json # Machine-readable data
│       └── img/                    # Comparison visualizations (11 files)
└── archives/                       # Previous analysis results
```

### Output Files

#### README.md
- **Summary Table**: Overview of all metrics with scores
- **Characteristics Analysis**: High-level quality assessment
- **Detailed Metrics**: Individual metric explanations and values
- **Recommendations**: Actionable improvement suggestions for low-scoring metrics
- **Embedded Visualizations**: All generated plots included inline

#### XML Files
- Raw metrics data in OQuaRE-compatible XML format
- Contains all basic metrics and derived metrics
- Suitable for programmatic processing and integration

#### JSON Files (Comparisons)
- Structured comparison data
- Metrics, characteristics, and subcharacteristics
- Differences, percent changes, and metadata
- Easily parseable for custom analysis tools

#### Visualizations
- **Spider Charts**: Multi-dimensional characteristic comparison
- **Bar Charts**: Metric values and comparisons
- **Lollipop Plots**: Clear metric value visualization
- **Evolution Plots**: Trends across multiple versions
- **Difference Charts**: Visual representation of changes

## Supported Formats

The tool supports multiple ontology formats:

| Format | Extension | Description |
|--------|-----------|-------------|
| **OWL** | `.owl` | Web Ontology Language (most common) |
| **RDF** | `.rdf` | Resource Description Framework |
| **Turtle** | `.ttl` | Terse RDF Triple Language |
| **N-Triples** | `.nt` | Line-based RDF format |
| **N3** | `.n3` | Notation3 |
| **JSON-LD** | `.jsonld` | JSON for Linking Data |

### Format Conversion

If you need to convert between formats, use the included utility:

```bash
python src/ttl2OWL.py input.ttl output.owl
```

## Troubleshooting

### Common Issues

#### Java Version Issues

**Problem**: `java.lang.UnsupportedClassVersionError`

**Solution**: Ensure Java 17 or higher is installed:
```bash
java -version
# Should show version 17 or higher
```

#### OWL File Errors

**Problem**: Errors parsing OWL files

**Solution**: Use the fix utility:
```bash
python fixowl.py
```

This script checks OWL files in `ontologies/imports` and attempts to fix:
- XML parsing errors
- Namespace issues
- Invalid declarations
- Syntax problems

#### Memory Issues

**Problem**: `OutOfMemoryError` for large ontologies

**Solution**: Increase Java heap size:
```bash
java -Xmx8g -jar libs/oquare-versions.jar --ontology "path/to/ontology.owl" --reasoner "ELK" --outputFile "output.xml"
```

#### Reasoner Timeout

**Problem**: Processing takes too long or hangs

**Solution**: 
1. Try switching to ELK reasoner (faster than HermiT):
   ```bash
   python src/main.py -i ./output -s ./ontologies -f large.owl -r ELK -M -c -S -m
   ```

2. For very large ontologies, consider:
   - Splitting into smaller modules
   - Removing unnecessary imports
   - Using a more powerful machine

#### Missing Dependencies

**Problem**: `ModuleNotFoundError` or import errors

**Solution**: Reinstall dependencies:
```bash
pip install --upgrade -r requirements.txt
```

### Getting Help

If you encounter issues not covered here:

1. Check the log files:
   - `oquare_metrics.log` - Main script logs
   - `generate_images.log` - Image generation logs

2. Enable verbose logging:
   ```bash
   python src/main.py -i ./output -s ./ontologies -f test.owl -r HermiT -M -v
   ```

3. Review the detailed documentation in the `Markdown/` directory:
   - `PYTHON_METRICS_IMPLEMENTATION.md` - Metrics calculation details
   - `COMPARISON_TESTING.md` - Comparison feature guide
   - `MetricsMaths.md` - Mathematical formulas and explanations

## Contributing

We welcome contributions! Here's how you can help:

### Reporting Issues

When reporting bugs, please include:
- Python version (`python --version`)
- Java version (`java -version`)
- Operating system
- Complete error message and stack trace
- Minimal example to reproduce the issue
- Contents of log files

### Submitting Pull Requests

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes with clear commit messages
4. Add tests if applicable
5. Update documentation as needed
6. Submit a pull request with a clear description

### Development Setup

```bash
# Clone the repository
git clone https://github.com/tecnomod-um/oquare-metrics.git
cd oquare-metrics

# Install development dependencies
pip install -r requirements.txt

# Run tests
python -m pytest TestFiles/

# Generate documentation
python scripts/generate_docs.py
```

## License

This project is part of the OQuaRE framework. Please refer to the LICENSE file for details.

## Citation

If you use this tool in your research, please cite:

```bibtex
@article{duque2014oquare,
  title={OQuaRE: A SQuaRE-based approach for evaluating the quality of ontologies},
  author={Duque-Ramos, Astrid and Fern{\'a}ndez-Breis, Jesualdo Tom{\'a}s and Stevens, Robert and Aussenac-Gilles, Nathalie},
  journal={Journal of Research and Practice in Information Technology},
  volume={43},
  number={2},
  pages={159},
  year={2011}
}
```

## Contact

For questions, suggestions, or collaboration opportunities:

- **Issues**: Create an issue in this repository with a detailed description
- **Email**: info@foxredrisk.com
- **Documentation**: See `Markdown/` directory for detailed guides

Your feedback helps improve this tool. Thank you for using OQuaRE Metrics!

---

**Note**: The `.owl` extension is automatically added to file names if not provided. Large ontologies may take several minutes to process depending on complexity and reasoner choice.

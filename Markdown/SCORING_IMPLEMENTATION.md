# OQuaRE Metrics Scoring Implementation

## Overview
This document describes the implementation of the scoring system for OQuaRE metrics based on the evaluation criteria defined in `src/metrics/Scores.md`.

## Changes Made

### 1. Added Scoring Method to `src/metrics/oquare_metrics.py`

#### `get_metric_score(metric_name: str, value: float) -> str`
- Determines the score level (L1-L5) for each metric based on the OQuaRE scoring table
- Handles both regular metrics and percentage metrics
- Returns the appropriate score level or "N/A" if the value falls outside defined ranges

#### Scoring Levels
- **L5**: Excellent quality (best score)
- **L4**: Good quality
- **L3**: Fair quality
- **L2**: Poor quality
- **L1**: Very Poor quality (worst score)

### 2. Updated Display Method

#### `print_metrics_summary()`
- Enhanced to display scores alongside metric values
- Shows metric name, calculated value, score level, and description
- Formatted output width increased to 85 characters to accommodate score column

### 3. Test Script

Created `test_scoring.py` to verify the scoring functionality:
- Loads a sample ontology
- Calculates all OQuaRE metrics
- Displays metrics with their scores
- Shows detailed score interpretation

## Scoring Criteria

### Metrics with Lower Values Being Better (L5 when low)
- **LCOMOnto**: L5 ≤ 2, L4 (2-4], L3 (4-6], L2 (6-8], L1 > 8
- **WMCOnto**: L5 ≤ 5, L4 (5-8], L3 (8-11], L2 (11-15], L1 > 15
- **NOMOnto**: L5 ≤ 2, L4 (2-4], L3 (4-6], L2 (6-8], L1 > 8

### Metrics with Specific Ranges (L5 when in optimal range)
- **DITOnto**: L5 [1-2], L4 (2-4], L3 (4-6], L2 (6-8], L1 > 8
- **NACOnto**: L5 [1-2], L4 (2-4], L3 (4-6], L2 (6-8], L1 > 8
- **NOCOnto**: L5 [1-3], L4 (3-6], L3 (6-8], L2 (8-12], L1 > 12
- **CBOOnto**: L5 [1-2], L4 (2-4], L3 (4-6], L2 (6-8], L1 > 8
- **RFCOnto**: L5 [1-3], L4 (3-6], L3 (6-8], L2 (8-12], L1 > 12
- **TMOnto**: L5 (1-2], L4 (2-4], L3 (4-6], L2 (6-8], L1 > 8

### Percentage Metrics (L5 when high percentage)
These metrics are automatically converted to percentages for scoring:
- **RROnto**: L5 > 80%, L4 (60-80]%, L3 (40-60]%, L2 (20-40]%, L1 [0-20]%
- **AROnto**: L5 > 80%, L4 (60-80]%, L3 (40-60]%, L2 (20-40]%, L1 [0-20]%
- **INROnto**: L5 > 80%, L4 (60-80]%, L3 (40-60]%, L2 (20-40]%, L1 [0-20]%
- **CROnto**: L5 > 80%, L4 (60-80]%, L3 (40-60]%, L2 (20-40]%, L1 [0-20]%
- **ANOnto**: L5 > 80%, L4 (60-80]%, L3 (40-60]%, L2 (20-40]%, L1 [0-20]%

## Usage

### In Python Code
```python
from src.metrics.ontology_loader import load_ontology
from src.metrics.basic_metrics import OntologyBasicMetrics
from src.metrics.oquare_metrics import OQuaREMetrics

# Load ontology
ontology = load_ontology("path/to/ontology.owl")

# Calculate metrics
basic_metrics = OntologyBasicMetrics(ontology)
oquare_metrics = OQuaREMetrics(basic_metrics)

# Print summary with scores
oquare_metrics.print_metrics_summary()

# Get individual metric score
anonto_value = oquare_metrics.calculate_ANOnto()
anonto_score = oquare_metrics.get_metric_score('ANOnto', anonto_value)
print(f"ANOnto score: {anonto_score}")
```

### Running the Test Script
```bash
python test_scoring.py
```

## Example Output

```
=====================================================================================
OQUARE QUALITY METRICS WITH SCORES
=====================================================================================
Metric                    Value    Score Description
-------------------------------------------------------------------------------------
ANOnto                 0.000000       L1 Annotation Richness
CROnto                 0.000000       L1 Class Richness
NOMOnto                0.750000       L5 Number of Properties
INROnto                0.500000       L3 Relationships per Class
AROnto                 0.250000       L2 Attribute Richness
DITOnto                       2       L5 Depth of Inheritance
NACOnto                1.000000       L5 Number of Ancestors
NOCOnto                1.000000       L5 Number of Children
CBOOnto                2.000000       L5 Coupling Between Objects
WMCOnto                1.250000       L5 Weighted Method Count
RFCOnto                3.500000       L4 Response for Class
RROnto                 0.500000       L3 Properties Richness
LCOMOnto               2.666667       L4 Lack of Cohesion
TMOnto                 0.500000      N/A Tangledness
=====================================================================================
```

## Notes

- Scores are calculated based on the evaluation criteria in Table 3 of the OQuaRE framework
- A score of "N/A" indicates the metric value falls outside the defined scoring ranges
- Percentage metrics (RROnto, AROnto, INROnto, CROnto, ANOnto) are automatically converted from decimal to percentage for scoring
- The scoring system provides an at-a-glance view of ontology quality across multiple dimensions

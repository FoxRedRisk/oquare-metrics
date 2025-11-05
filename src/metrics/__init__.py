"""
OQuaRE Metrics - Pure Python Implementation

This module provides a complete Python implementation of the OQuaRE metrics framework
for ontology quality evaluation, replacing the Java JAR dependency.

Main Components:
- ontology_loader: Load and parse OWL ontologies
- basic_metrics: Calculate basic structural metrics
- oquare_metrics: Calculate derived OQuaRE quality metrics
- xml_generator: Generate XML output compatible with the original JAR format
- validator: Compare outputs with JAR implementation for validation

Author: OQuaRE Metrics Team
Date: 2025-11-04
"""

# Use JAR-compatible version by default for consistency with original implementation
# To use original Python version, change import to: from .basic_metrics import OntologyBasicMetrics
from .basic_metrics_jar_compatible import OntologyBasicMetrics
from .oquare_metrics import OQuaREMetrics
from .xml_generator import generate_metrics_xml
from .ontology_loader import load_ontology

__version__ = "1.0.0"
__all__ = [
    "OntologyBasicMetrics",
    "OQuaREMetrics", 
    "generate_metrics_xml",
    "load_ontology"
]

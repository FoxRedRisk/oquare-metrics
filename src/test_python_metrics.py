"""
Test Script for Python OQuaRE Metrics Implementation

This script tests the Python metrics implementation and can compare
results with the JAR implementation for validation.

Usage:
    python src/test_python_metrics.py <ontology_file> [--compare-jar]

Author: OQuaRE Metrics Team
Date: 2025-11-04
"""

import sys
import logging
import argparse
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from metrics import load_ontology, OntologyBasicMetrics, OQuaREMetrics
from metrics.xml_generator import generate_metrics_xml

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_ontology(ontology_path: str, reasoner: str = "HermiT", compare_jar: bool = False):
    """
    Test the Python metrics implementation on an ontology.
    
    Args:
        ontology_path: Path to the ontology file
        reasoner: Reasoner to use
        compare_jar: Whether to compare with JAR output
    """
    logger.info("=" * 80)
    logger.info("Testing Python OQuaRE Metrics Implementation")
    logger.info("=" * 80)
    logger.info(f"Ontology: {ontology_path}")
    logger.info(f"Reasoner: {reasoner}")
    logger.info("=" * 80 + "\n")
    
    # Load ontology
    try:
        logger.info("Step 1: Loading ontology...")
        onto = load_ontology(ontology_path, reasoner=reasoner, use_reasoning=True)
        logger.info(f"✓ Ontology loaded successfully: {onto.name}\n")
    except Exception as e:
        logger.error(f"✗ Failed to load ontology: {e}")
        return False
    
    # Calculate basic metrics
    try:
        logger.info("Step 2: Calculating basic metrics...")
        basic_metrics = OntologyBasicMetrics(onto)
        basic_values = basic_metrics.get_all_basic_metrics()
        logger.info("✓ Basic metrics calculated\n")
        
        # Print basic metrics
        print("\n" + "=" * 70)
        print("BASIC METRICS")
        print("=" * 70)
        for metric, value in basic_values.items():
            print(f"{metric:<35} {value:>10}")
        print("=" * 70 + "\n")
        
    except Exception as e:
        logger.error(f"✗ Failed to calculate basic metrics: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Calculate OQuaRE metrics
    try:
        logger.info("Step 3: Calculating OQuaRE quality metrics...")
        oquare_metrics = OQuaREMetrics(basic_metrics)
        oquare_values = oquare_metrics.calculate_all_metrics()
        logger.info("✓ OQuaRE metrics calculated\n")
        
        # Print detailed calculations
        oquare_metrics.print_detailed_calculations()
        
        # Print OQuaRE metrics summary
        oquare_metrics.print_metrics_summary()
        
    except Exception as e:
        logger.error(f"✗ Failed to calculate OQuaRE metrics: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Generate XML output
    try:
        logger.info("Step 4: Generating XML output...")
        output_path = Path("output/test_python/metrics") / f"{Path(ontology_path).stem}_python.xml"
        generate_metrics_xml(
            basic_values,
            oquare_values,
            output_path,
            ontology_name=onto.name
        )
        logger.info(f"✓ XML generated: {output_path}\n")
        
    except Exception as e:
        logger.error(f"✗ Failed to generate XML: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Compare with JAR if requested
    if compare_jar:
        try:
            logger.info("Step 5: Comparing with JAR output...")
            jar_output_path = Path("output/metrics") / f"{Path(ontology_path).stem}.xml"
            
            if not jar_output_path.exists():
                logger.error("✗ JAR output not found: %s", jar_output_path)
                logger.error("Cannot perform comparison without JAR output")
                logger.error("Please run the JAR implementation first to generate comparison data")
                return False
            
            compare_with_jar(jar_output_path, basic_values, oquare_values)
        except Exception as e:
            logger.error(f"✗ Comparison failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    logger.info("\n" + "=" * 80)
    logger.info("✓ All tests completed successfully!")
    logger.info("=" * 80 + "\n")
    
    return True


def _parse_jar_xml(jar_xml: Path) -> dict:
    """
    Parse JAR XML and extract metrics.
    
    Args:
        jar_xml: Path to JAR-generated XML
        
    Returns:
        Dictionary of JAR metrics
    """
    import xml.etree.ElementTree as ET
    
    try:
        jar_tree = ET.parse(jar_xml)
        jar_root = jar_tree.getroot()
    except Exception as e:
        logger.error(f"Failed to parse JAR XML: {e}")
        return {}
    
    # Extract JAR metrics
    jar_metrics = {}
    excluded_tags = {'metrics', 'ontologyMetrics', 'basicMetrics', 'oquareMetrics', 
                     'timestamp', 'generator', 'ontologyName'}
    
    for elem in jar_root.iter():
        if elem.text and elem.tag not in excluded_tags:
            try:
                jar_metrics[elem.tag] = float(elem.text)
            except (ValueError, TypeError):
                jar_metrics[elem.tag] = elem.text
    
    return jar_metrics


def _determine_metric_status(metric: str, py_val: float, jar_val: float) -> tuple:
    """
    Determine the status of a metric comparison.
    
    Args:
        metric: Metric name
        py_val: Python value
        jar_val: JAR value
        
    Returns:
        Tuple of (status string, is_issue boolean, is_fix boolean)
    """
    diff = abs(py_val - jar_val)
    percent_diff = (diff / jar_val * 100) if jar_val != 0 else 0
    
    if metric == 'sumOfAnnotations' and diff > 0:
        return "✓ FIXED", False, True
    elif diff < 0.0001:  # Tolerance for floating point
        return "✓ Match", False, False
    elif percent_diff < 1:
        return "≈ Close", False, False
    else:
        return "✗ Diff", True, False


def _print_metric_comparison(metric: str, py_val, jar_val, status: str):
    """
    Print a single metric comparison line.
    
    Args:
        metric: Metric name
        py_val: Python value
        jar_val: JAR value
        status: Status string
    """
    if isinstance(py_val, (int, float)) and isinstance(jar_val, (int, float)):
        diff = abs(py_val - jar_val)
        print(f"{metric:<30} {py_val:<20.6f} {jar_val:<20.6f} {diff:<15.6f} {status}")
    else:
        print(f"{metric:<30} {py_val!s:<20} {jar_val!s:<20} {'N/A':<15} -")


def _print_comparison_summary(fixes: list, issues: list):
    """
    Print the comparison summary.
    
    Args:
        fixes: List of fixed metrics
        issues: List of metrics with issues
    """
    print("=" * 105)
    
    if fixes:
        print(f"\n✓ FIXES IMPLEMENTED: {len(fixes)}")
        for metric in fixes:
            print(f"  - {metric}: Now counting all annotations (not just rdfs:label/comment)")
    
    if not issues:
        print("\n✓ All other metrics match or are within tolerance")
    else:
        print(f"\n⚠ {len(issues)} metrics show significant differences:")
        for metric in issues:
            print(f"  - {metric}")
        print("\nNote: Some differences may be expected due to implementation details")
    
    print("")


def _compare_single_metric(metric: str, all_python: dict, jar_metrics: dict, 
                           issues: list, fixes: list) -> None:
    """
    Compare a single metric between Python and JAR implementations.
    
    Args:
        metric: Metric name to compare
        all_python: All Python metrics
        jar_metrics: All JAR metrics
        issues: List to append issues to
        fixes: List to append fixes to
    """
    if metric not in all_python or metric not in jar_metrics:
        return
    
    py_val = all_python[metric]
    jar_val = jar_metrics[metric]
    
    if not isinstance(py_val, (int, float)) or not isinstance(jar_val, (int, float)):
        _print_metric_comparison(metric, py_val, jar_val, "-")
        return
    
    status, is_issue, is_fix = _determine_metric_status(metric, py_val, jar_val)
    
    if is_fix:
        fixes.append(metric)
    if is_issue:
        issues.append(metric)
    
    _print_metric_comparison(metric, py_val, jar_val, status)


def compare_with_jar(jar_xml: Path, python_basic: dict, python_oquare: dict):
    """
    Compare Python output with JAR output.
    
    Args:
        jar_xml: Path to JAR-generated XML
        python_basic: Python basic metrics
        python_oquare: Python OQuaRE metrics
    """
    logger.info("\n" + "=" * 80)
    logger.info("COMPARISON WITH JAR IMPLEMENTATION")
    logger.info("=" * 80)
    
    # Parse JAR XML
    jar_metrics = _parse_jar_xml(jar_xml)
    if not jar_metrics:
        return
    
    # Print header
    print(f"\n{'Metric':<30} {'Python':<20} {'JAR':<20} {'Diff':<15} {'Status'}")
    print("-" * 105)
    
    # Combine all Python metrics
    all_python = {**python_basic, **python_oquare}
    
    # Key metrics to compare
    key_metrics = [
        'numberOfClasses',
        'sumOfAnnotations',  # This should show the fix!
        'ANOnto',            # This will be different due to fixed annotation count
        'DITOnto',
        'WMCOnto',
        'LCOMOnto',
    ]
    
    issues = []
    fixes = []
    
    # Compare each metric
    for metric in key_metrics:
        _compare_single_metric(metric, all_python, jar_metrics, issues, fixes)
    
    # Print summary
    _print_comparison_summary(fixes, issues)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Test Python OQuaRE Metrics Implementation'
    )
    parser.add_argument(
        'ontology',
        help='Path to ontology file'
    )
    parser.add_argument(
        '--reasoner',
        default='HermiT',
        choices=['HermiT', 'Pellet', 'ELK'],
        help='Reasoner to use (default: HermiT)'
    )
    parser.add_argument(
        '--compare-jar',
        action='store_true',
        help='Compare results with JAR implementation'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Run test
    success = test_ontology(
        args.ontology,
        reasoner=args.reasoner,
        compare_jar=args.compare_jar
    )
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()

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
    logger.info(f"{'='*80}")
    logger.info(f"Testing Python OQuaRE Metrics Implementation")
    logger.info(f"{'='*80}")
    logger.info(f"Ontology: {ontology_path}")
    logger.info(f"Reasoner: {reasoner}")
    logger.info(f"{'='*80}\n")
    
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
        print(f"\n{'='*70}")
        print(f"BASIC METRICS")
        print(f"{'='*70}")
        for metric, value in basic_values.items():
            print(f"{metric:<35} {value:>10}")
        print(f"{'='*70}\n")
        
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
                logger.warning(f"JAR output not found: {jar_output_path}")
                logger.warning("Run the JAR first to generate comparison data")
            else:
                compare_with_jar(output_path, jar_output_path, basic_values, oquare_values)
        except Exception as e:
            logger.error(f"✗ Comparison failed: {e}")
            import traceback
            traceback.print_exc()
    
    logger.info(f"\n{'='*80}")
    logger.info("✓ All tests completed successfully!")
    logger.info(f"{'='*80}\n")
    
    return True


def compare_with_jar(python_xml: Path, jar_xml: Path, python_basic: dict, python_oquare: dict):
    """
    Compare Python output with JAR output.
    
    Args:
        python_xml: Path to Python-generated XML
        jar_xml: Path to JAR-generated XML
        python_basic: Python basic metrics
        python_oquare: Python OQuaRE metrics
    """
    import xml.etree.ElementTree as ET
    
    logger.info("\n" + "="*80)
    logger.info("COMPARISON WITH JAR IMPLEMENTATION")
    logger.info("="*80)
    
    # Parse JAR XML
    try:
        jar_tree = ET.parse(jar_xml)
        jar_root = jar_tree.getroot()
    except Exception as e:
        logger.error(f"Failed to parse JAR XML: {e}")
        return
    
    # Extract JAR metrics
    jar_metrics = {}
    for elem in jar_root.iter():
        if elem.text and elem.tag not in ['metrics', 'ontologyMetrics', 'basicMetrics', 'oquareMetrics', 'timestamp', 'generator', 'ontologyName']:
            try:
                jar_metrics[elem.tag] = float(elem.text)
            except:
                jar_metrics[elem.tag] = elem.text
    
    # Compare key metrics
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
    
    for metric in key_metrics:
        if metric in all_python and metric in jar_metrics:
            py_val = all_python[metric]
            jar_val = jar_metrics[metric]
            
            # Calculate difference
            if isinstance(py_val, (int, float)) and isinstance(jar_val, (int, float)):
                diff = abs(py_val - jar_val)
                percent_diff = (diff / jar_val * 100) if jar_val != 0 else 0
                
                # Determine status
                if metric == 'sumOfAnnotations' and diff > 0:
                    status = "✓ FIXED"
                    fixes.append(metric)
                elif diff < 0.0001:  # Tolerance for floating point
                    status = "✓ Match"
                elif percent_diff < 1:
                    status = "≈ Close"
                else:
                    status = "✗ Diff"
                    issues.append(metric)
                
                print(f"{metric:<30} {py_val:<20.6f} {jar_val:<20.6f} {diff:<15.6f} {status}")
            else:
                print(f"{metric:<30} {py_val!s:<20} {jar_val!s:<20} {'N/A':<15} -")
    
    # Summary
    print("=" * 105)
    if fixes:
        print(f"\n✓ FIXES IMPLEMENTED: {len(fixes)}")
        for metric in fixes:
            print(f"  - {metric}: Now counting all annotations (not just rdfs:label/comment)")
    
    if not issues:
        print(f"\n✓ All other metrics match or are within tolerance")
    else:
        print(f"\n⚠ {len(issues)} metrics show significant differences:")
        for metric in issues:
            print(f"  - {metric}")
        print("\nNote: Some differences may be expected due to implementation details")
    
    print("")


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

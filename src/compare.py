#!/usr/bin/env python3
"""
OQuaRE Metrics Comparison Tool

This script compares metrics between two ontologies and generates comparison reports.
It uses the existing MetricsParser to load data and creates structured comparison output.
"""

import argparse
import logging
import os
import sys
from typing import Tuple
from tools.ComparisonController import ComparisonController


def setup_logging(verbose: bool = False) -> None:
    """Setup logging configuration
    
    Args:
        verbose: If True, set logging level to DEBUG, otherwise INFO
    """
    log_level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments
    
    Returns:
        Parsed arguments namespace
    """
    parser = argparse.ArgumentParser(
        description='Compare OQuaRE metrics between two ontologies',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Compare two ontologies with auto-detected names
  python src/compare.py --ontology1 output/lecture/metrics/lecture.xml \\
                        --ontology2 output/lecture_improved/metrics/Lecture_improved.xml

  # Compare with custom names
  python src/compare.py --ontology1 output/lecture/metrics/lecture.xml \\
                        --ontology2 output/lecture_improved/metrics/Lecture_improved.xml \\
                        --name1 "Original Lecture" --name2 "Improved Lecture"

  # Specify custom output directory
  python src/compare.py --ontology1 output/lecture/metrics/lecture.xml \\
                        --ontology2 output/lecture_improved/metrics/Lecture_improved.xml \\
                        --output custom_comparisons
        """
    )
    
    parser.add_argument(
        '--ontology1',
        required=True,
        help='Path to the first ontology XML metrics file'
    )
    
    parser.add_argument(
        '--ontology2',
        required=True,
        help='Path to the second ontology XML metrics file'
    )
    
    parser.add_argument(
        '--output',
        default='output/comparisons',
        help='Output directory for comparison results (default: output/comparisons)'
    )
    
    parser.add_argument(
        '--name1',
        help='Custom name for the first ontology (default: extracted from filename)'
    )
    
    parser.add_argument(
        '--name2',
        help='Custom name for the second ontology (default: extracted from filename)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    return parser.parse_args()


def extract_ontology_name(xml_path: str) -> str:
    """Extract ontology name from XML file path
    
    Args:
        xml_path: Path to the XML file
        
    Returns:
        Extracted ontology name (filename without extension)
    """
    basename = os.path.basename(xml_path)
    name = os.path.splitext(basename)[0]
    return name


def validate_inputs(args: argparse.Namespace) -> Tuple[str, str]:
    """Validate input files and extract ontology names
    
    Args:
        args: Parsed command-line arguments
        
    Returns:
        Tuple of (ontology1_name, ontology2_name)
        
    Raises:
        SystemExit: If validation fails
    """
    logger = logging.getLogger(__name__)
    
    # Validate that both XML files exist
    if not os.path.exists(args.ontology1):
        logger.error(f"Ontology 1 XML file not found: {args.ontology1}")
        sys.exit(1)
    
    if not os.path.exists(args.ontology2):
        logger.error(f"Ontology 2 XML file not found: {args.ontology2}")
        sys.exit(1)
    
    # Extract or use provided ontology names
    ontology1_name = args.name1 if args.name1 else extract_ontology_name(args.ontology1)
    ontology2_name = args.name2 if args.name2 else extract_ontology_name(args.ontology2)
    
    # Prevent comparing an ontology to itself
    if os.path.abspath(args.ontology1) == os.path.abspath(args.ontology2):
        logger.error("Cannot compare an ontology to itself. Please provide two different ontology files.")
        sys.exit(1)
    
    logger.info(f"Comparing: {ontology1_name} vs {ontology2_name}")
    
    return ontology1_name, ontology2_name


def print_comparison_summary(comparison_data) -> None:
    """Print a summary of the comparison to console
    
    Args:
        comparison_data: ComparisonData object with comparison results
    """
    logger = logging.getLogger(__name__)
    
    # Get summary statistics
    summary = comparison_data.get_summary_statistics()
    
    print("\n" + "="*80)
    print(f"COMPARISON SUMMARY: {comparison_data.ontology1_name} vs {comparison_data.ontology2_name}")
    print("="*80)
    
    # Metrics summary
    print("\n📊 METRICS:")
    print(f"  Total: {summary['metrics']['total']}")
    print(f"  Improved: {summary['metrics']['improved']} ✓")
    print(f"  Degraded: {summary['metrics']['degraded']} ✗")
    print(f"  Unchanged: {summary['metrics']['unchanged']} -")
    print(f"  Average Change: {summary['metrics']['avg_percent_change']}%")
    
    # Scaled metrics summary
    print("\n📈 SCALED METRICS:")
    print(f"  Total: {summary['scaled_metrics']['total']}")
    print(f"  Improved: {summary['scaled_metrics']['improved']} ✓")
    print(f"  Degraded: {summary['scaled_metrics']['degraded']} ✗")
    print(f"  Unchanged: {summary['scaled_metrics']['unchanged']} -")
    print(f"  Average Change: {summary['scaled_metrics']['avg_percent_change']}%")
    
    # Characteristics summary
    print("\n🎯 CHARACTERISTICS:")
    print(f"  Total: {summary['characteristics']['total']}")
    print(f"  Improved: {summary['characteristics']['improved']} ✓")
    print(f"  Degraded: {summary['characteristics']['degraded']} ✗")
    print(f"  Unchanged: {summary['characteristics']['unchanged']} -")
    print(f"  Average Change: {summary['characteristics']['avg_percent_change']}%")
    
    print("\n" + "="*80)
    
    # Show top improvements and degradations
    metrics_comparison = comparison_data.get_metrics_comparison()
    
    # Sort by difference
    sorted_metrics = sorted(
        metrics_comparison.items(),
        key=lambda x: abs(x[1]['difference']),
        reverse=True
    )
    
    print("\n🔝 TOP 5 METRIC CHANGES (by absolute difference):")
    for i, (metric, data) in enumerate(sorted_metrics[:5], 1):
        change_symbol = "✓" if data['difference'] > 0 else "✗" if data['difference'] < 0 else "-"
        percent_str = f"{data['percent_change']}%" if data['percent_change'] is not None else "N/A"
        print(f"  {i}. {metric}: {data['difference']:+.2f} ({percent_str}) {change_symbol}")
    
    print("\n" + "="*80 + "\n")


def main() -> None:
    """Main entry point for comparison CLI"""
    # Parse arguments
    args = parse_arguments()
    
    # Setup logging
    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)
    
    try:
        # Validate inputs and extract names
        ontology1_name, ontology2_name = validate_inputs(args)
        
        # Create output directory if it doesn't exist
        os.makedirs(args.output, exist_ok=True)
        logger.info(f"Output directory: {args.output}")
        
        # Initialize controller
        controller = ComparisonController()
        
        # Execute comparison
        logger.info("Starting comparison workflow...")
        comparison_data = controller.compare_ontologies(
            xml_path1=args.ontology1,
            xml_path2=args.ontology2,
            ontology1_name=ontology1_name,
            ontology2_name=ontology2_name,
            output_base_path=args.output
        )
        
        # Print summary to console
        print_comparison_summary(comparison_data)
        
        # Log success
        output_dir = os.path.join(args.output, f"{ontology1_name}_vs_{ontology2_name}")
        logger.info(f"Comparison completed successfully!")
        logger.info(f"Output directory: {output_dir}")
        logger.info(f"Image directory: {os.path.join(output_dir, 'img')}")
        
    except FileNotFoundError as e:
        logger.error(f"File not found: {str(e)}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error during comparison: {str(e)}")
        logger.exception("Exception details:")
        sys.exit(1)


if __name__ == '__main__':
    main()
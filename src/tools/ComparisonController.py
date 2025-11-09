import os
import logging
from typing import Tuple, Dict, Any
from tools.Parser import MetricsParser
from tools.ComparisonData import ComparisonData
from tools.ComparisonPlotter import ComparisonPlotter
from tools.ComparisonReporter import ComparisonReporter


class ComparisonController:
    """Orchestrates the comparison workflow
    
    This class manages the entire comparison process including loading ontology data,
    creating output directories, and coordinating the comparison workflow.
    """
    
    def __init__(self):
        """Initialize controller"""
        self.logger = logging.getLogger(__name__)
    
    def compare_ontologies(self, xml_path1: str, xml_path2: str,
                          ontology1_name: str, ontology2_name: str,
                          output_base_path: str) -> ComparisonData:
        """Execute comparison workflow and return ComparisonData
        
        Args:
            xml_path1: Path to first ontology's XML metrics file
            xml_path2: Path to second ontology's XML metrics file
            ontology1_name: Name for the first ontology
            ontology2_name: Name for the second ontology
            output_base_path: Base path for output directory
            
        Returns:
            ComparisonData object containing all comparison data
            
        Raises:
            FileNotFoundError: If XML files don't exist
            Exception: For other errors during comparison
        """
        self.logger.info(f"Starting comparison: {ontology1_name} vs {ontology2_name}")
        
        # Validate input files
        if not os.path.exists(xml_path1):
            raise FileNotFoundError(f"XML file not found: {xml_path1}")
        if not os.path.exists(xml_path2):
            raise FileNotFoundError(f"XML file not found: {xml_path2}")
        
        # Load data from both ontologies
        self.logger.info(f"Loading data from {xml_path1}")
        metrics1, scaled_metrics1, characteristics1 = self._load_ontology_data(xml_path1)
        
        self.logger.info(f"Loading data from {xml_path2}")
        metrics2, scaled_metrics2, characteristics2 = self._load_ontology_data(xml_path2)
        
        # Create output directory structure
        output_path = os.path.join(output_base_path, f"{ontology1_name}_vs_{ontology2_name}")
        self._create_output_directory(output_path)
        self.logger.info(f"Created output directory: {output_path}")
        
        # Create and return ComparisonData object
        comparison_data = ComparisonData(
            ontology1_name=ontology1_name,
            ontology2_name=ontology2_name,
            metrics1=metrics1,
            metrics2=metrics2,
            scaled_metrics1=scaled_metrics1,
            scaled_metrics2=scaled_metrics2,
            characteristics1=characteristics1,
            characteristics2=characteristics2
        )
        
        # Generate comparison visualizations
        self.logger.info("Generating comparison visualizations")
        plotter = ComparisonPlotter()
        
        # Create all comparison plots
        plotter.plot_characteristics_comparison(comparison_data, output_path)
        self.logger.info("Created characteristics comparison plot")
        
        plotter.plot_metrics_comparison(comparison_data, output_path, scaled=False)
        self.logger.info("Created metrics comparison plot")
        
        plotter.plot_metrics_comparison(comparison_data, output_path, scaled=True)
        self.logger.info("Created scaled metrics comparison plot")
        
        plotter.plot_metrics_difference(comparison_data, output_path)
        self.logger.info("Created metrics difference plot")
        
        plotter.plot_subcharacteristics_comparison(comparison_data, output_path)
        self.logger.info("Created subcharacteristics comparison plots")
        
        # Generate comparison reports
        self.logger.info("Generating comparison reports")
        reporter = ComparisonReporter()
        
        reporter.generate_report(comparison_data, output_path)
        self.logger.info(f"Created comparison report: {output_path}/README.md")
        
        reporter.generate_json_summary(comparison_data, output_path)
        self.logger.info(f"Created JSON summary: {output_path}/comparison_summary.json")
        
        self.logger.info("Comparison completed successfully")
        return comparison_data
    
    def _load_ontology_data(self, xml_path: str) -> Tuple[Dict[str, float], Dict[str, float], Dict[str, Any]]:
        """Load metrics from XML using existing Parser
        
        Args:
            xml_path: Path to the XML metrics file
            
        Returns:
            Tuple containing (metrics, scaled_metrics, characteristics)
            
        Raises:
            Exception: If parsing fails
        """
        try:
            parser = MetricsParser(xml_path)
            
            # Parse all required data
            metrics = parser.parse_metrics()
            scaled_metrics = parser.parse_scaled_metrics()
            characteristics = parser.parse_characteristics_metrics()
            
            self.logger.debug(f"Loaded {len(metrics)} metrics from {xml_path}")
            self.logger.debug(f"Loaded {len(scaled_metrics)} scaled metrics from {xml_path}")
            self.logger.debug(f"Loaded {len(characteristics)} characteristics from {xml_path}")
            
            return metrics, scaled_metrics, characteristics
            
        except Exception as e:
            self.logger.error(f"Error loading ontology data from {xml_path}: {str(e)}")
            raise RuntimeError(f"Failed to load ontology data from {xml_path}: {str(e)}")
    
    def _create_output_directory(self, output_path: str) -> None:
        """Create output directory structure
        
        Args:
            output_path: Base path for the comparison output
            
        Raises:
            Exception: If directory creation fails
        """
        try:
            # Create main output directory
            os.makedirs(output_path, exist_ok=True)
            
            # Create img subdirectory for future visualizations
            img_path = os.path.join(output_path, "img")
            os.makedirs(img_path, exist_ok=True)
            
            self.logger.debug(f"Created directory structure at {output_path}")
            
        except Exception as e:
            self.logger.error(f"Error creating output directory {output_path}: {str(e)}")
            raise OSError(f"Failed to create output directory: {str(e)}")

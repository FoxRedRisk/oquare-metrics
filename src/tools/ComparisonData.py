import math
from typing import Dict, Any, Optional


class ComparisonData:
    """Encapsulates comparison data for two ontologies
    
    This class holds metrics, scaled metrics, and characteristics data for two ontologies
    and provides methods to compute comparisons between them, including differences and
    percent changes.
    """
    
    def __init__(self, ontology1_name: str, ontology2_name: str,
                 metrics1: Dict[str, float], metrics2: Dict[str, float],
                 scaled_metrics1: Dict[str, float], scaled_metrics2: Dict[str, float],
                 characteristics1: Dict[str, Any], characteristics2: Dict[str, Any]):
        """Initialize with data from both ontologies
        
        Args:
            ontology1_name: Name of the first ontology
            ontology2_name: Name of the second ontology
            metrics1: Dictionary of metrics for ontology 1
            metrics2: Dictionary of metrics for ontology 2
            scaled_metrics1: Dictionary of scaled metrics for ontology 1
            scaled_metrics2: Dictionary of scaled metrics for ontology 2
            characteristics1: Dictionary of characteristics for ontology 1
            characteristics2: Dictionary of characteristics for ontology 2
        """
        self.ontology1_name = ontology1_name
        self.ontology2_name = ontology2_name
        self.metrics1 = metrics1
        self.metrics2 = metrics2
        self.scaled_metrics1 = scaled_metrics1
        self.scaled_metrics2 = scaled_metrics2
        self.characteristics1 = characteristics1
        self.characteristics2 = characteristics2
    
    def _calculate_difference(self, value1: float, value2: float) -> float:
        """Calculate difference between two values (value2 - value1)
        
        Args:
            value1: First value
            value2: Second value
            
        Returns:
            Difference rounded to 2 decimal places
        """
        return round(value2 - value1, 2)
    
    def _calculate_percent_change(self, value1: float, value2: float) -> Optional[float]:
        """Calculate percent change from value1 to value2
        
        Args:
            value1: Original value
            value2: New value
            
        Returns:
            Percent change rounded to 2 decimal places, or None if value1 is 0
        """
        if value1 == 0:
            return None
        return round(((value2 - value1) / abs(value1)) * 100, 2)
    
    def _compare_dict_values(self, dict1: Dict[str, float], dict2: Dict[str, float]) -> Dict[str, Dict[str, Any]]:
        """Compare two dictionaries of values
        
        Args:
            dict1: First dictionary
            dict2: Second dictionary
            
        Returns:
            Dictionary with comparison data for each key
        """
        comparison = {}
        all_keys = set(dict1.keys()) | set(dict2.keys())
        
        for key in all_keys:
            val1 = dict1.get(key, 0.0)
            val2 = dict2.get(key, 0.0)
            
            comparison[key] = {
                self.ontology1_name: round(val1, 2),
                self.ontology2_name: round(val2, 2),
                'difference': self._calculate_difference(val1, val2),
                'percent_change': self._calculate_percent_change(val1, val2)
            }
        
        return comparison
    
    def get_metrics_comparison(self) -> Dict[str, Dict[str, Any]]:
        """Returns comparison dict with difference and percent_change for each metric
        
        Returns:
            Dictionary with comparison data for each metric
        """
        return self._compare_dict_values(self.metrics1, self.metrics2)
    
    def get_scaled_metrics_comparison(self) -> Dict[str, Dict[str, Any]]:
        """Returns comparison dict for scaled metrics
        
        Returns:
            Dictionary with comparison data for each scaled metric
        """
        return self._compare_dict_values(self.scaled_metrics1, self.scaled_metrics2)
    
    def get_characteristics_comparison(self) -> Dict[str, Dict[str, Any]]:
        """Returns comparison dict for characteristics with subcharacteristics
        
        Returns:
            Dictionary with comparison data for each characteristic including subcharacteristics
        """
        comparison = {}
        all_characteristics = set(self.characteristics1.keys()) | set(self.characteristics2.keys())
        
        for char in all_characteristics:
            char1_data = self.characteristics1.get(char, {'value': 0.0, 'subcharacteristics': {}})
            char2_data = self.characteristics2.get(char, {'value': 0.0, 'subcharacteristics': {}})
            
            val1 = char1_data.get('value', 0.0)
            val2 = char2_data.get('value', 0.0)
            
            comparison[char] = {
                'value': {
                    self.ontology1_name: round(val1, 2),
                    self.ontology2_name: round(val2, 2),
                    'difference': self._calculate_difference(val1, val2),
                    'percent_change': self._calculate_percent_change(val1, val2)
                },
                'subcharacteristics': self._compare_dict_values(
                    char1_data.get('subcharacteristics', {}),
                    char2_data.get('subcharacteristics', {})
                )
            }
        
        return comparison
    
    def get_subcharacteristics_comparison(self, characteristic: str) -> Dict[str, Dict[str, Any]]:
        """Returns comparison dict for specific characteristic's subcharacteristics
        
        Args:
            characteristic: Name of the characteristic
            
        Returns:
            Dictionary with comparison data for the characteristic's subcharacteristics
        """
        char1_data = self.characteristics1.get(characteristic, {'subcharacteristics': {}})
        char2_data = self.characteristics2.get(characteristic, {'subcharacteristics': {}})
        
        return self._compare_dict_values(
            char1_data.get('subcharacteristics', {}),
            char2_data.get('subcharacteristics', {})
        )
    
    def get_summary_statistics(self) -> Dict[str, Any]:
        """Returns summary statistics about improvements/degradations
        
        Returns:
            Dictionary with summary statistics including counts of improvements,
            degradations, and unchanged metrics
        """
        metrics_comparison = self.get_metrics_comparison()
        scaled_metrics_comparison = self.get_scaled_metrics_comparison()
        characteristics_comparison = self.get_characteristics_comparison()
        
        # Count improvements and degradations in metrics
        metrics_improved = sum(1 for data in metrics_comparison.values() if data['difference'] > 0)
        metrics_degraded = sum(1 for data in metrics_comparison.values() if data['difference'] < 0)
        metrics_unchanged = sum(1 for data in metrics_comparison.values() if data['difference'] == 0)
        
        # Count improvements and degradations in scaled metrics
        scaled_improved = sum(1 for data in scaled_metrics_comparison.values() if data['difference'] > 0)
        scaled_degraded = sum(1 for data in scaled_metrics_comparison.values() if data['difference'] < 0)
        scaled_unchanged = sum(1 for data in scaled_metrics_comparison.values() if data['difference'] == 0)
        
        # Count improvements and degradations in characteristics
        char_improved = sum(1 for data in characteristics_comparison.values() 
                           if data['value']['difference'] > 0)
        char_degraded = sum(1 for data in characteristics_comparison.values() 
                           if data['value']['difference'] < 0)
        char_unchanged = sum(1 for data in characteristics_comparison.values() 
                            if data['value']['difference'] == 0)
        
        # Calculate average percent changes (excluding None values)
        metrics_percent_changes = [data['percent_change'] for data in metrics_comparison.values() 
                                  if data['percent_change'] is not None]
        avg_metrics_change = round(sum(metrics_percent_changes) / len(metrics_percent_changes), 2) if metrics_percent_changes else 0.0
        
        scaled_percent_changes = [data['percent_change'] for data in scaled_metrics_comparison.values() 
                                 if data['percent_change'] is not None]
        avg_scaled_change = round(sum(scaled_percent_changes) / len(scaled_percent_changes), 2) if scaled_percent_changes else 0.0
        
        char_percent_changes = [data['value']['percent_change'] for data in characteristics_comparison.values() 
                               if data['value']['percent_change'] is not None]
        avg_char_change = round(sum(char_percent_changes) / len(char_percent_changes), 2) if char_percent_changes else 0.0
        
        return {
            'metrics': {
                'total': len(metrics_comparison),
                'improved': metrics_improved,
                'degraded': metrics_degraded,
                'unchanged': metrics_unchanged,
                'avg_percent_change': avg_metrics_change
            },
            'scaled_metrics': {
                'total': len(scaled_metrics_comparison),
                'improved': scaled_improved,
                'degraded': scaled_degraded,
                'unchanged': scaled_unchanged,
                'avg_percent_change': avg_scaled_change
            },
            'characteristics': {
                'total': len(characteristics_comparison),
                'improved': char_improved,
                'degraded': char_degraded,
                'unchanged': char_unchanged,
                'avg_percent_change': avg_char_change
            }
        }
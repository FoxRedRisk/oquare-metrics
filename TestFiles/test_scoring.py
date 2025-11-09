"""
Test script to verify the OQuaRE metrics scoring functionality.
"""

from src.metrics.ontology_loader import load_ontology
from src.metrics.basic_metrics import OntologyBasicMetrics
from src.metrics.oquare_metrics import OQuaREMetrics

# Test the scoring system with a sample ontology
def test_scoring():
    print("Testing OQuaRE Metrics Scoring Functionality\n")
    
    # Load a test ontology
    ontology_path = "./ontologies/imports/lecture.owl"
    
    print(f"Loading ontology from: {ontology_path}")
    try:
        ontology = load_ontology(ontology_path, reasoner=None, use_reasoning=False)
    except Exception as e:
        print(f"Failed to load ontology: {e}")
        return
    
    print("Ontology loaded successfully!\n")
    
    # Calculate basic metrics
    print("Calculating basic metrics...")
    basic_metrics = OntologyBasicMetrics(ontology)
    
    # Calculate OQuaRE metrics
    print("Calculating OQuaRE metrics...\n")
    oquare_metrics = OQuaREMetrics(basic_metrics)
    
    # Print metrics summary with scores
    oquare_metrics.print_metrics_summary()
    
    # Test individual metric scoring
    print("\n" + "="*85)
    print("INDIVIDUAL METRIC SCORE TESTS")
    print("="*85)
    
    metrics = oquare_metrics.calculate_all_metrics()
    
    print(f"\n{'Metric':<15} {'Value':>15} {'Value%':>15} {'Score':>8} {'Interpretation'}")
    print("-"*85)
    
    for metric_name, value in metrics.items():
        score = oquare_metrics.get_metric_score(metric_name, value)
        
        # For percentage metrics, show both raw and percentage values
        if metric_name in ['RROnto', 'AROnto', 'INROnto', 'CROnto', 'ANOnto']:
            pct_value = value * 100
            interpretation = get_score_interpretation(score)
            if isinstance(value, int):
                print(f"{metric_name:<15} {value:>15} {pct_value:>14.2f}% {score:>8} {interpretation}")
            else:
                print(f"{metric_name:<15} {value:>15.6f} {pct_value:>14.2f}% {score:>8} {interpretation}")
        else:
            interpretation = get_score_interpretation(score)
            if isinstance(value, int):
                print(f"{metric_name:<15} {value:>15} {'N/A':>15} {score:>8} {interpretation}")
            else:
                print(f"{metric_name:<15} {value:>15.6f} {'N/A':>15} {score:>8} {interpretation}")
    
    print("="*85 + "\n")

def get_score_interpretation(score):
    """Get interpretation of score level."""
    interpretations = {
        'L5': 'Excellent',
        'L4': 'Good',
        'L3': 'Fair',
        'L2': 'Poor',
        'L1': 'Very Poor',
        'N/A': 'Not Available'
    }
    return interpretations.get(score, 'Unknown')

if __name__ == '__main__':
    test_scoring()

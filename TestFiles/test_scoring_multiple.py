"""
Test script to verify the OQuaRE metrics scoring functionality on multiple ontologies.
"""

from src.metrics.ontology_loader import load_ontology
from src.metrics.basic_metrics import OntologyBasicMetrics
from src.metrics.oquare_metrics import OQuaREMetrics

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

def test_ontology(ontology_path, ontology_name):
    """Test scoring for a single ontology."""
    print(f"\n{'#'*90}")
    print(f"# TESTING: {ontology_name}")
    print(f"# Path: {ontology_path}")
    print(f"{'#'*90}\n")
    
    try:
        ontology = load_ontology(ontology_path, reasoner=None, use_reasoning=False)
    except Exception as e:
        print(f"✗ Failed to load ontology: {e}\n")
        return
    
    print(f"✓ Ontology loaded successfully!\n")
    
    # Calculate basic metrics
    basic_metrics = OntologyBasicMetrics(ontology)
    
    # Calculate OQuaRE metrics
    oquare_metrics = OQuaREMetrics(basic_metrics)
    
    # Print metrics summary with scores
    oquare_metrics.print_metrics_summary()
    
    # Print detailed score analysis
    print(f"\n{'='*90}")
    print(f"DETAILED SCORE ANALYSIS FOR {ontology_name}")
    print(f"{'='*90}")
    
    metrics = oquare_metrics.calculate_all_metrics()
    
    print(f"\n{'Metric':<15} {'Value':>15} {'Value%':>15} {'Score':>8} {'Interpretation':<15}")
    print("-"*90)
    
    for metric_name, value in metrics.items():
        score = oquare_metrics.get_metric_score(metric_name, value)
        interpretation = get_score_interpretation(score)
        
        # For percentage metrics, show both raw and percentage values
        if metric_name in ['RROnto', 'AROnto', 'INROnto', 'CROnto', 'ANOnto']:
            pct_value = value * 100
            if isinstance(value, int):
                print(f"{metric_name:<15} {value:>15} {pct_value:>14.2f}% {score:>8} {interpretation:<15}")
            else:
                print(f"{metric_name:<15} {value:>15.6f} {pct_value:>14.2f}% {score:>8} {interpretation:<15}")
        else:
            if isinstance(value, int):
                print(f"{metric_name:<15} {value:>15} {'N/A':>15} {score:>8} {interpretation:<15}")
            else:
                print(f"{metric_name:<15} {value:>15.6f} {'N/A':>15} {score:>8} {interpretation:<15}")
    
    # Score distribution summary
    score_counts = {'L5': 0, 'L4': 0, 'L3': 0, 'L2': 0, 'L1': 0, 'N/A': 0}
    for metric_name, value in metrics.items():
        score = oquare_metrics.get_metric_score(metric_name, value)
        score_counts[score] = score_counts.get(score, 0) + 1
    
    print(f"\n{'='*90}")
    print(f"SCORE DISTRIBUTION")
    print(f"{'='*90}")
    print(f"L5 (Excellent):  {score_counts['L5']:>2} metrics")
    print(f"L4 (Good):       {score_counts['L4']:>2} metrics")
    print(f"L3 (Fair):       {score_counts['L3']:>2} metrics")
    print(f"L2 (Poor):       {score_counts['L2']:>2} metrics")
    print(f"L1 (Very Poor):  {score_counts['L1']:>2} metrics")
    print(f"N/A:             {score_counts['N/A']:>2} metrics")
    print(f"{'='*90}\n")

def main():
    print("\n" + "="*90)
    print(" "*25 + "OQuaRE METRICS SCORING TEST")
    print(" "*20 + "Testing Multiple Ontologies")
    print("="*90)
    
    ontologies = [
        ("./ontologies/imports/iao.owl", "IAO (Information Artifact Ontology)"),
        ("./ontologies/imports/bfo-core.owl", "BFO-Core (Basic Formal Ontology - Core)"),
        ("./ontologies/imports/merged_ontology_20251020_114848.owl", "Merged Ontology"),
    ]
    
    for ontology_path, ontology_name in ontologies:
        test_ontology(ontology_path, ontology_name)
    
    print("\n" + "="*90)
    print(" "*30 + "ALL TESTS COMPLETED")
    print("="*90 + "\n")

if __name__ == '__main__':
    main()

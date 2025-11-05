"""
Test script for OBI2 (Ontology for Biomedical Investigations) ontology scoring.
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

def main():
    print("\n" + "="*90)
    print(" "*20 + "OQuaRE METRICS SCORING TEST")
    print(" "*15 + "OBI2 (Ontology for Biomedical Investigations)")
    print("="*90 + "\n")
    
    ontology_path = "./ontologies/imports/obi2.owl"
    
    print(f"Loading ontology from: {ontology_path}")
    try:
        ontology = load_ontology(ontology_path, reasoner=None, use_reasoning=False)
    except Exception as e:
        print(f"✗ Failed to load ontology: {e}\n")
        return
    
    print(f"✓ Ontology loaded successfully!\n")
    
    # Calculate basic metrics
    print("Calculating basic metrics...")
    basic_metrics = OntologyBasicMetrics(ontology)
    
    # Calculate OQuaRE metrics
    print("Calculating OQuaRE metrics...\n")
    oquare_metrics = OQuaREMetrics(basic_metrics)
    
    # Print metrics summary with scores
    oquare_metrics.print_metrics_summary()
    
    # Print detailed score analysis
    print(f"\n{'='*90}")
    print(f"DETAILED SCORE ANALYSIS FOR OBI2")
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
        
        # Show recommendation for poor scores
        recommendation = oquare_metrics.get_metric_recommendation(metric_name, score, value)
        if recommendation:
            print(f"\n   ⚠️  {recommendation}\n")
    
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
    print(f"{'='*90}")
    
    # Summary interpretation
    total_metrics = sum(score_counts.values())
    excellent_pct = (score_counts['L5'] / total_metrics) * 100
    poor_pct = ((score_counts['L1'] + score_counts['L2']) / total_metrics) * 100
    
    print(f"\nOVERALL QUALITY ASSESSMENT:")
    print(f"  {excellent_pct:.1f}% of metrics scored Excellent (L5)")
    print(f"  {poor_pct:.1f}% of metrics scored Poor or Very Poor (L1-L2)")
    
    if excellent_pct >= 50:
        print(f"  → Overall Assessment: HIGH QUALITY ontology")
    elif excellent_pct >= 30:
        print(f"  → Overall Assessment: MODERATE QUALITY ontology")
    else:
        print(f"  → Overall Assessment: NEEDS IMPROVEMENT")
    
    print(f"{'='*90}\n")

if __name__ == '__main__':
    main()

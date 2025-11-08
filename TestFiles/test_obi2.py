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

def print_header():
    """Print the test header."""
    print("\n" + "="*90)
    print(" "*20 + "OQuaRE METRICS SCORING TEST")
    print(" "*15 + "OBI2 (Ontology for Biomedical Investigations)")
    print("="*90 + "\n")

def load_and_prepare_ontology(ontology_path):
    """Load ontology and prepare metrics calculators."""
    print("Loading ontology from: {}".format(ontology_path))
    try:
        ontology = load_ontology(ontology_path, reasoner=None, use_reasoning=False)
    except Exception as e:
        print("✗ Failed to load ontology: {}\n".format(e))
        return None, None
    
    print("✓ Ontology loaded successfully!\n")
    
    print("Calculating basic metrics...")
    basic_metrics = OntologyBasicMetrics(ontology)
    
    print("Calculating OQuaRE metrics...\n")
    oquare_metrics = OQuaREMetrics(basic_metrics)
    
    return basic_metrics, oquare_metrics

def print_metric_row(metric_name, value, score, interpretation):
    """Print a single metric row in the table."""
    percentage_metrics = ['RROnto', 'AROnto', 'INROnto', 'CROnto', 'ANOnto']
    
    if metric_name in percentage_metrics:
        pct_value = value * 100
        if isinstance(value, int):
            print("{:<15} {:>15} {:>14.2f}% {:>8} {:<15}".format(
                metric_name, value, pct_value, score, interpretation))
        else:
            print("{:<15} {:>15.6f} {:>14.2f}% {:>8} {:<15}".format(
                metric_name, value, pct_value, score, interpretation))
    else:
        if isinstance(value, int):
            print("{:<15} {:>15} {:>15} {:>8} {:<15}".format(
                metric_name, value, 'N/A', score, interpretation))
        else:
            print("{:<15} {:>15.6f} {:>15} {:>8} {:<15}".format(
                metric_name, value, 'N/A', score, interpretation))

def print_metrics_table(metrics, oquare_metrics):
    """Print detailed metrics analysis table."""
    print("\n" + "="*90)
    print("DETAILED SCORE ANALYSIS FOR OBI2")
    print("="*90)
    
    print("\n{:<15} {:>15} {:>15} {:>8} {:<15}".format(
        'Metric', 'Value', 'Value%', 'Score', 'Interpretation'))
    print("-"*90)
    
    for metric_name, value in metrics.items():
        score = oquare_metrics.get_metric_score(metric_name, value)
        interpretation = get_score_interpretation(score)
        
        print_metric_row(metric_name, value, score, interpretation)
        
        recommendation = oquare_metrics.get_metric_recommendation(metric_name, score, value)
        if recommendation:
            print("\n   ⚠️  {}\n".format(recommendation))

def calculate_score_counts(metrics, oquare_metrics):
    """Calculate score distribution counts."""
    score_counts = {'L5': 0, 'L4': 0, 'L3': 0, 'L2': 0, 'L1': 0, 'N/A': 0}
    for metric_name, value in metrics.items():
        score = oquare_metrics.get_metric_score(metric_name, value)
        score_counts[score] = score_counts.get(score, 0) + 1
    return score_counts

def print_score_distribution(score_counts):
    """Print score distribution summary."""
    print("\n" + "="*90)
    print("SCORE DISTRIBUTION")
    print("="*90)
    print("L5 (Excellent):  {:>2} metrics".format(score_counts['L5']))
    print("L4 (Good):       {:>2} metrics".format(score_counts['L4']))
    print("L3 (Fair):       {:>2} metrics".format(score_counts['L3']))
    print("L2 (Poor):       {:>2} metrics".format(score_counts['L2']))
    print("L1 (Very Poor):  {:>2} metrics".format(score_counts['L1']))
    print("N/A:             {:>2} metrics".format(score_counts['N/A']))
    print("="*90)

def print_overall_assessment(score_counts):
    """Print overall quality assessment."""
    total_metrics = sum(score_counts.values())
    excellent_pct = (score_counts['L5'] / total_metrics) * 100
    poor_pct = ((score_counts['L1'] + score_counts['L2']) / total_metrics) * 100
    
    print("\nOVERALL QUALITY ASSESSMENT:")
    print("  {:.1f}% of metrics scored Excellent (L5)".format(excellent_pct))
    print("  {:.1f}% of metrics scored Poor or Very Poor (L1-L2)".format(poor_pct))
    
    if excellent_pct >= 50:
        print("  → Overall Assessment: HIGH QUALITY ontology")
    elif excellent_pct >= 30:
        print("  → Overall Assessment: MODERATE QUALITY ontology")
    else:
        print("  → Overall Assessment: NEEDS IMPROVEMENT")
    
    print("="*90 + "\n")

def main():
    """Main test execution function."""
    print_header()
    
    ontology_path = "./ontologies/imports/obi2.owl"
    _, oquare_metrics = load_and_prepare_ontology(ontology_path)
    
    if not oquare_metrics:
        return
    
    oquare_metrics.print_metrics_summary()
    
    metrics = oquare_metrics.calculate_all_metrics()
    print_metrics_table(metrics, oquare_metrics)
    
    score_counts = calculate_score_counts(metrics, oquare_metrics)
    print_score_distribution(score_counts)
    print_overall_assessment(score_counts)

if __name__ == '__main__':
    main()

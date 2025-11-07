"""
Test script for Lecture ontology scoring with recommendations.
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

def display_header():
    """Display the test header."""
    print("\n" + "="*90)
    print(" "*25 + "OQuaRE METRICS SCORING TEST")
    print(" "*30 + "Lecture Ontology")
    print("="*90 + "\n")

def load_test_ontology():
    """Load the test ontology."""
    ontology_path = "./ontologies/imports/lecture.owl"
    
    print("Loading ontology from: {}".format(ontology_path))
    try:
        ontology = load_ontology(ontology_path, reasoner=None, use_reasoning=False)
        print("✓ Ontology loaded successfully!\n")
        return ontology
    except Exception as e:
        print("✗ Failed to load ontology: {}\n".format(e))
        return None

def calculate_metrics(ontology):
    """Calculate basic and OQuaRE metrics."""
    print("Calculating basic metrics...")
    basic_metrics = OntologyBasicMetrics(ontology)
    
    print("Calculating OQuaRE metrics...\n")
    oquare_metrics = OQuaREMetrics(basic_metrics)
    
    return oquare_metrics

def print_metric_details(metrics, oquare_metrics):
    """Print detailed metrics information."""
    print("\n{}".format("="*90))
    print("DETAILED SCORE ANALYSIS WITH RECOMMENDATIONS")
    print("{}".format("="*90))
    
    print("\n{:<15} {:>15} {:>15} {:>8} {:<15}".format(
        "Metric", "Value", "Value%", "Score", "Interpretation"))
    print("-"*90)
    
    for metric_name, value in metrics.items():
        score = oquare_metrics.get_metric_score(metric_name, value)
        interpretation = get_score_interpretation(score)
        
        # For percentage metrics, show both raw and percentage values
        if metric_name in ['RROnto', 'AROnto', 'INROnto', 'CROnto', 'ANOnto']:
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
                    metric_name, value, "N/A", score, interpretation))
            else:
                print("{:<15} {:>15.6f} {:>15} {:>8} {:<15}".format(
                    metric_name, value, "N/A", score, interpretation))
        
        # Show recommendation for poor scores
        recommendation = oquare_metrics.get_metric_recommendation(metric_name, score, value)
        if recommendation:
            print("\n   ⚠️  {}\n".format(recommendation))

def print_score_distribution(metrics, oquare_metrics):
    """Print score distribution summary."""
    score_counts = {'L5': 0, 'L4': 0, 'L3': 0, 'L2': 0, 'L1': 0, 'N/A': 0}
    for metric_name, value in metrics.items():
        score = oquare_metrics.get_metric_score(metric_name, value)
        score_counts[score] = score_counts.get(score, 0) + 1
    
    print("\n{}".format("="*90))
    print("SCORE DISTRIBUTION")
    print("{}".format("="*90))
    print("L5 (Excellent):  {:>2} metrics".format(score_counts['L5']))
    print("L4 (Good):       {:>2} metrics".format(score_counts['L4']))
    print("L3 (Fair):       {:>2} metrics".format(score_counts['L3']))
    print("L2 (Poor):       {:>2} metrics".format(score_counts['L2']))
    print("L1 (Very Poor):  {:>2} metrics".format(score_counts['L1']))
    print("N/A:             {:>2} metrics".format(score_counts['N/A']))
    print("{}".format("="*90))
    
    return score_counts

def print_overall_assessment(score_counts):
    """Print overall quality assessment."""
    total_metrics = sum(score_counts.values())
    excellent_pct = (score_counts['L5'] / total_metrics) * 100
    poor_pct = ((score_counts['L1'] + score_counts['L2']) / total_metrics) * 100
    
    print("\nOVERALL QUALITY ASSESSMENT:")
    print("  {:.1f}% of metrics scored Excellent (L5)".format(excellent_pct))
    print("  {:.1f}% of metrics scored Poor or Very Poor (L1-L2)".format(poor_pct))
    
    # Determine quality assessment based on excellent percentage
    if excellent_pct >= 50:
        assessment = "HIGH QUALITY ontology"
    elif excellent_pct >= 30:
        assessment = "MODERATE QUALITY ontology"
    else:
        assessment = "NEEDS IMPROVEMENT"
    
    print("  → Overall Assessment: {}".format(assessment))
    
    print("{}\n".format("="*90))

def main():
    display_header()
    
    ontology = load_test_ontology()
    if ontology is None:
        return
    
    oquare_metrics = calculate_metrics(ontology)
    
    # Print metrics summary with scores
    oquare_metrics.print_metrics_summary()
    
    # Get all metrics
    metrics = oquare_metrics.calculate_all_metrics()
    
    # Print detailed metrics information
    print_metric_details(metrics, oquare_metrics)
    
    # Print score distribution
    score_counts = print_score_distribution(metrics, oquare_metrics)
    
    # Print overall assessment
    print_overall_assessment(score_counts)

if __name__ == '__main__':
    main()

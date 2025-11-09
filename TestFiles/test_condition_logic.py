"""
Test script to verify the quality assessment condition logic with mock values.
"""

def get_quality_assessment(excellent_pct):
    """Get quality assessment based on excellent percentage."""
    if excellent_pct < 30:
        return "NEEDS IMPROVEMENT"
    elif excellent_pct < 50:
        return "MODERATE QUALITY ontology"
    else:
        return "HIGH QUALITY ontology"

def test_quality_assessments():
    """Test quality assessments with various mock values."""
    print("\n" + "="*70)
    print("TESTING QUALITY ASSESSMENT LOGIC")
    print("="*70 + "\n")
    
    # Test cases with expected results
    test_cases = [
        (0, "NEEDS IMPROVEMENT"),
        (10, "NEEDS IMPROVEMENT"),
        (29, "NEEDS IMPROVEMENT"),
        (29.9, "NEEDS IMPROVEMENT"),
        (30, "MODERATE QUALITY ontology"),
        (35, "MODERATE QUALITY ontology"),
        (40, "MODERATE QUALITY ontology"),
        (49, "MODERATE QUALITY ontology"),
        (49.9, "MODERATE QUALITY ontology"),
        (50, "HIGH QUALITY ontology"),
        (60, "HIGH QUALITY ontology"),
        (75, "HIGH QUALITY ontology"),
        (90, "HIGH QUALITY ontology"),
        (100, "HIGH QUALITY ontology"),
    ]
    
    print("{:<20} {:<30} {:<10}".format("Excellent %", "Assessment", "Status"))
    print("-"*70)
    
    all_passed = True
    for excellent_pct, expected in test_cases:
        result = get_quality_assessment(excellent_pct)
        passed = result == expected
        all_passed = all_passed and passed
        status = "✓ PASS" if passed else "✗ FAIL"
        
        print("{:<20} {:<30} {:<10}".format(
            f"{excellent_pct}%", 
            result, 
            status
        ))
    
    print("\n" + "="*70)
    if all_passed:
        print("✓ All tests PASSED!")
    else:
        print("✗ Some tests FAILED!")
    print("="*70 + "\n")
    
    return all_passed

if __name__ == '__main__':
    test_quality_assessments()

# OQuaRE Metrics Comparison Feature - Testing Documentation

## Overview

This document provides comprehensive testing results for the OQuaRE metrics comparison feature, which enables side-by-side comparison of quality metrics between two ontologies.

## Test Environment

- **Test Date**: 2025-10-27
- **Python Version**: 3.x
- **Tool Version**: OQuaRE Metrics v1.0
- **Test Platform**: Windows 11

## Test Cases Executed

### Test Case 1: Basic Comparison (lecture vs lecture_improved)

**Command:**
```bash
python src/compare.py \
  --ontology1 output/lecture/metrics/lecture.xml \
  --ontology2 output/lecture_improved/metrics/Lecture_improved.xml
```

**Status:** ✅ PASSED

**Results:**
- Output directory created: `output/comparisons/lecture_vs_Lecture_improved/`
- All 11 visualization PNG files generated successfully
- README.md generated with complete comparison report
- comparison_summary.json generated with valid JSON structure
- Timestamp in ISO 8601 format: `2025-10-27T12:25:26.659892`

**Key Metrics:**
- Metrics Improved: 17/19 (89.5%)
- Metrics Degraded: 2/19 (10.5%)
- Scaled Metrics Improved: 4/19 (21.1%)
- Scaled Metrics Degraded: 7/19 (36.8%)
- Characteristics Improved: 1/7 (14.3%)
- Characteristics Degraded: 6/7 (85.7%)

**Visualizations Generated:**
1. ✅ `lecture_vs_Lecture_improved_characteristics_comparison.png` - Spider plot showing all 7 characteristics
2. ✅ `lecture_vs_Lecture_improved_metrics_comparison.png` - Lollipop plot with side-by-side stems
3. ✅ `lecture_vs_Lecture_improved_scaled_metrics_comparison.png` - Scaled metrics on 1-5 scale
4. ✅ `lecture_vs_Lecture_improved_metrics_difference.png` - Difference chart with color coding
5. ✅ `lecture_vs_Lecture_improved_compatibility_subcharacteristics_comparison.png`
6. ✅ `lecture_vs_Lecture_improved_functionalAdequacy_subcharacteristics_comparison.png`
7. ✅ `lecture_vs_Lecture_improved_maintainability_subcharacteristics_comparison.png`
8. ✅ `lecture_vs_Lecture_improved_operability_subcharacteristics_comparison.png`
9. ✅ `lecture_vs_Lecture_improved_reliability_subcharacteristics_comparison.png`
10. ✅ `lecture_vs_Lecture_improved_structural_subcharacteristics_comparison.png`
11. ✅ `lecture_vs_Lecture_improved_transferability_subcharacteristics_comparison.png`

**Report Quality:**
- ✅ README.md renders correctly in markdown viewers
- ✅ All images embedded and display properly
- ✅ Tables formatted with proper alignment
- ✅ Status indicators (✅/❌/➖) display correctly
- ✅ Percent changes formatted with + and - signs
- ✅ Top 5 findings show accurate data
- ✅ Executive summary provides clear overview

**JSON Quality:**
- ✅ Valid JSON structure (parseable)
- ✅ Contains all expected fields: ontology1, ontology2, timestamp, summary, metrics, scaled_metrics, characteristics
- ✅ Numeric values are accurate and properly typed
- ✅ Timestamp in ISO 8601 format
- ✅ Null values handled correctly for division by zero cases

---

### Test Case 2: Different Ontology Pair (lecture vs bfo-core)

**Command:**
```bash
python src/compare.py \
  --ontology1 output/lecture/metrics/lecture.xml \
  --ontology2 output/bfo/metrics/bfo-core.xml
```

**Status:** ✅ PASSED

**Results:**
- Output directory created: `output/comparisons/lecture_vs_bfo-core/`
- All 11 visualization PNG files generated successfully
- README.md and comparison_summary.json generated
- Timestamp: `2025-10-27T12:28:33.229203`

**Key Metrics:**
- Metrics Improved: 13/19 (68.4%)
- Metrics Degraded: 1/19 (5.3%)
- Metrics Unchanged: 5/19 (26.3%)
- Scaled Metrics Improved: 3/19 (15.8%)
- Scaled Metrics Degraded: 6/19 (31.6%)
- Characteristics Degraded: 7/7 (100%)

**Notable Findings:**
- Largest improvement: AROnto +10.21 (+1021.0%)
- All characteristics showed degradation in this comparison
- Demonstrates tool's ability to handle diverse ontology comparisons

**Validation:**
- ✅ All file outputs present
- ✅ Visualizations display correctly
- ✅ Report formatting consistent with Test Case 1
- ✅ JSON structure valid and complete

---

### Test Case 3: Custom Display Names

**Command:**
```bash
python src/compare.py \
  --ontology1 output/lecture/metrics/lecture.xml \
  --ontology2 output/lecture_improved/metrics/Lecture_improved.xml \
  --name1 "Original Lecture Ontology" \
  --name2 "Improved Lecture Ontology"
```

**Status:** ✅ PASSED

**Results:**
- Output directory created with custom names: `output/comparisons/Original Lecture Ontology_vs_Improved Lecture Ontology/`
- Custom names appear in report header
- Custom names appear in table column headers
- Custom names appear in visualization legends
- Custom names appear in JSON summary

**Validation:**
- ✅ Report header shows: "**Ontology 1**: Original Lecture Ontology"
- ✅ Report header shows: "**Ontology 2**: Improved Lecture Ontology"
- ✅ Table columns use custom names
- ✅ JSON contains custom names in ontology1/ontology2 fields
- ✅ Image filenames use custom names (with spaces)
- ✅ All visualizations generated successfully

**User Experience:**
- Custom names make reports more readable and professional
- Particularly useful for presentations and documentation
- Directory names with spaces handled correctly by the system

---

### Test Case 4: Error Handling - Non-existent File

**Command:**
```bash
python src/compare.py \
  --ontology1 nonexistent.xml \
  --ontology2 output/lecture/metrics/lecture.xml
```

**Status:** ✅ PASSED

**Expected Behavior:** Tool should detect missing file and display clear error message

**Actual Result:**
```
2025-10-27 12:29:43 - __main__ - ERROR - Ontology 1 XML file not found: nonexistent.xml
```

**Exit Code:** 1 (error)

**Validation:**
- ✅ Clear, descriptive error message
- ✅ Identifies which ontology file is missing
- ✅ Shows the attempted file path
- ✅ Non-zero exit code for scripting integration
- ✅ No partial output files created
- ✅ No stack trace or confusing technical errors

---

### Test Case 5: Error Handling - Same Ontology

**Command:**
```bash
python src/compare.py \
  --ontology1 output/lecture/metrics/lecture.xml \
  --ontology2 output/lecture/metrics/lecture.xml
```

**Status:** ✅ PASSED

**Expected Behavior:** Tool should detect identical files and prevent meaningless comparison

**Actual Result:**
```
2025-10-27 12:29:50 - __main__ - ERROR - Cannot compare an ontology to itself. Please provide two different ontology files.
```

**Exit Code:** 1 (error)

**Validation:**
- ✅ Clear, user-friendly error message
- ✅ Explains why the operation is invalid
- ✅ Provides guidance on correct usage
- ✅ Non-zero exit code
- ✅ No output files created
- ✅ Prevents wasted computation

---

## Validation Checklist Summary

### File Generation
- ✅ Output directory created with correct naming convention
- ✅ Image subdirectory created (`img/`)
- ✅ README.md generated
- ✅ comparison_summary.json generated
- ✅ All 11 visualization PNG files generated

### Visualization Quality
- ✅ Characteristics comparison (spider plot) - both ontologies clearly visible
- ✅ Metrics comparison (lollipop plots) - side-by-side stems distinguishable
- ✅ Scaled metrics comparison - proper 0-5 scale displayed
- ✅ Metrics difference chart - green for improvements, red for degradations
- ✅ All 6 subcharacteristics charts generated and labeled correctly
- ✅ Legends are clear and readable
- ✅ Axis labels are appropriate
- ✅ Color schemes are consistent and accessible

### Report Quality
- ✅ README.md opens and renders correctly in markdown viewers
- ✅ All images embedded using relative paths
- ✅ Images display correctly when README is viewed
- ✅ Tables formatted with proper markdown syntax
- ✅ Status indicators (✅/❌/➖) display correctly
- ✅ Percent changes formatted with + and - signs
- ✅ Top 5 findings show correct data and rankings
- ✅ Executive summary provides accurate counts
- ✅ Comparison date displayed in readable format
- ✅ Footer attribution present

### JSON Quality
- ✅ comparison_summary.json is valid JSON (parseable)
- ✅ Contains all expected top-level fields
- ✅ Numeric values are correct and properly typed
- ✅ Timestamp in ISO 8601 format
- ✅ Nested structure for characteristics and subcharacteristics
- ✅ Null values handled correctly for undefined percent changes
- ✅ Consistent field naming throughout

### Error Handling
- ✅ Non-existent file detected with clear error message
- ✅ Same ontology comparison prevented with helpful message
- ✅ Non-zero exit codes for error conditions
- ✅ No partial output files created on error
- ✅ Error messages are user-friendly, not technical

---

## Issues Found and Resolved

### Issue 1: None Found
All test cases passed without issues. The comparison feature is working as designed.

---

## Performance Observations

- **Comparison Time**: ~2-3 seconds per comparison
- **File Size**: 
  - README.md: ~5-8 KB
  - comparison_summary.json: ~15-20 KB
  - PNG images: ~30-80 KB each
- **Total Output Size**: ~500-800 KB per comparison

---

## Recommendations for Users

### Best Practices

1. **Use Descriptive Custom Names**
   - Use `--name1` and `--name2` for better readability
   - Example: `--name1 "Version 1.0" --name2 "Version 2.0"`

2. **Organize Comparisons**
   - Comparisons are saved in `output/comparisons/`
   - Each comparison gets its own subdirectory
   - Keep related comparisons together

3. **Review All Outputs**
   - Start with the README.md for overview
   - Check visualizations for patterns
   - Use JSON for programmatic analysis

4. **Interpret Results Carefully**
   - Raw metrics show absolute changes
   - Scaled metrics show relative quality (1-5 scale)
   - Consider both when evaluating improvements

5. **Version Control**
   - Commit comparison outputs with your ontology versions
   - Track quality evolution over time
   - Use for release documentation

### Common Use Cases

1. **Before/After Refactoring**
   - Compare original vs refactored ontology
   - Verify improvements in target metrics
   - Ensure no unexpected degradations

2. **Version Comparison**
   - Compare consecutive versions
   - Track quality trends over releases
   - Document quality improvements

3. **Alternative Designs**
   - Compare different design approaches
   - Evaluate trade-offs between characteristics
   - Make informed design decisions

4. **Quality Benchmarking**
   - Compare against reference ontologies
   - Identify areas for improvement
   - Set quality targets

---

## Screenshots and Examples

### Example 1: Characteristics Comparison
The spider plot clearly shows the 7 main characteristics for both ontologies, making it easy to identify which areas improved or degraded.

### Example 2: Metrics Difference Chart
The difference chart uses green bars for improvements and red bars for degradations, with bar length indicating magnitude of change.

### Example 3: Report Summary Table
The summary table provides a quick overview with status indicators, making it easy to scan for key changes.

---

## Conclusion

The OQuaRE metrics comparison feature has been thoroughly tested and validated. All test cases passed successfully, demonstrating:

- ✅ Robust file generation and organization
- ✅ High-quality visualizations with clear comparisons
- ✅ Comprehensive and readable reports
- ✅ Valid and complete JSON output
- ✅ Excellent error handling and user feedback
- ✅ Support for custom naming and flexible usage

The feature is **production-ready** and suitable for:
- Ontology quality assessment
- Version comparison and tracking
- Refactoring validation
- Quality benchmarking
- Documentation and reporting

---

## Test Artifacts

All test outputs are preserved in:
- `output/comparisons/lecture_vs_Lecture_improved/`
- `output/comparisons/lecture_vs_bfo-core/`
- `output/comparisons/Original Lecture Ontology_vs_Improved Lecture Ontology/`

These can be reviewed to verify test results and serve as examples for users.

---

*Testing completed: 2025-10-27*  
*Tester: Automated Testing Suite*  
*Status: All Tests Passed ✅*
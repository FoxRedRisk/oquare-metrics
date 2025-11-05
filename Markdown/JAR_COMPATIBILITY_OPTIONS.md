# JAR Compatibility Options

**Date:** 2025-11-04  
**Status:** Implementation Complete

## Overview

The Python OQuaRE metrics implementation now provides **two versions** to support different use cases:

1. **Original Python Implementation** (`basic_metrics.py`) - Improved annotation counting
2. **JAR-Compatible Implementation** (`basic_metrics_jar_compatible.py`) - Matches JAR behavior

## Key Differences

### 1. Class Counting

| Implementation | Behavior | Count for lecture.owl |
|----------------|----------|----------------------|
| **Original Python** | Excludes owl:Thing | 4 classes |
| **JAR-Compatible** | Includes owl:Thing | 5 classes |

**Impact:** Affects all per-class ratio metrics (NOMOnto, INROnto, etc.)

### 2. Attribute Counting

| Implementation | Method | Count for lecture.owl |
|----------------|--------|----------------------|
| **Original Python** | Data property domains only | 1 attribute |
| **JAR-Compatible** | All data property usages (domains + ranges + assertions) | 5 attributes |

**Impact:** Affects AROnto (Attribute Richness)

### 3. Relationship Counting

| Implementation | Method | Count for lecture.owl |
|----------------|--------|----------------------|
| **Original Python** | User classes only | 2 relationships |
| **JAR-Compatible** | Includes Thing's subclasses | 4 relationships |

**Impact:** Affects INROnto, NOCOnto, TMOnto, WMCOnto

### 4. Maximum Depth

| Implementation | Method | Depth for lecture.owl |
|----------------|--------|----------------------|
| **Original Python** | Without default reasoning | 2 |
| **JAR-Compatible** | With reasoning enabled | 3 (inferred) |

**Impact:** Affects DITOnto

### 5. Annotation Counting (UNCHANGED)

**Both implementations use the FIXED annotation counting:**
- Counts ALL annotations on ALL entities
- Fixes the JAR bug that only counted rdfs:label/comment

| Ontology | JAR (buggy) | Python (both versions) |
|----------|-------------|----------------------|
| lecture.owl | 4 (metadata?) | 0 (correct - no annotations) |
| iao.owl | ~36 (missing 98%) | 2,746 (correct - all annotations) |

## Which Version to Use?

### Use JAR-Compatible Version When:

✅ **You need exact metric matching with JAR output**
- Comparing with historical JAR data
- Validating migration from JAR to Python
- Need consistent denominators in formulas

✅ **You're working with reasoning-dependent ontologies**
- Need inferred class hierarchies
- Analyzing implicit relationships

### Use Original Python Version When:

✅ **You want user-focused metrics**
- Exclude owl:Thing from counts (cleaner metrics)
- Focus on user-defined classes only

✅ **You prioritize accuracy over compatibility**
- More meaningful per-class ratios
- Clearer structural analysis

✅ **You need explicit control over reasoning**
- Can enable reasoning when needed
- Default no-reasoning for faster processing

## Switching Between Versions

### Option 1: Update Import in __init__.py

```python
# For JAR-compatible (current default)
from .basic_metrics_jar_compatible import OntologyBasicMetrics

# For original Python version
from .basic_metrics import OntologyBasicMetrics
```

### Option 2: Direct Import in Your Code

```python
# JAR-compatible
from metrics.basic_metrics_jar_compatible import OntologyBasicMetrics

# Original Python
from metrics.basic_metrics import OntologyBasicMetrics
```

## Expected Metric Comparisons

### lecture.owl with Reasoning

**JAR Output (HermiT):**
```
numberOfClasses: 5
sumOfRelationships: 4
sumOfAttributes: 5
maximumDepth: 3
ANOnto: 0.8
```

**Python JAR-Compatible (HermiT):**
```
numberOfClasses: 5
sumOfRelationships: 4
sumOfAttributes: 5
maximumDepth: 3
ANOnto: 0.0 (FIXED - lecture has no real annotations)
```

**Python Original (No Reasoning):**
```
numberOfClasses: 4
sumOfRelationships: 2
sumOfAttributes: 1
maximumDepth: 2
ANOnto: 0.0
```

### iao.owl

**The Critical Difference - Annotation Counting:**

**JAR (buggy):**
```
numberOfClasses: 264
sumOfAnnotations: 36
ANOnto: 0.14
```

**Python (both versions, FIXED):**
```
numberOfClasses: 263 (original) or 264 (JAR-compatible)
sumOfAnnotations: 2,746
ANOnto: 10.44 (original) or 10.40 (JAR-compatible)
```

## Recommendations

### Default Configuration

We recommend **JAR-compatible version** as the default because:

1. ✅ Easier validation against existing JAR outputs
2. ✅ Consistent with published OQuaRE papers
3. ✅ Still includes the critical annotation counting fix
4. ✅ Can be switched to original version easily if needed

### Migration Path

**Phase 1: Validation (Current)**
- Use JAR-compatible version
- Verify metrics match (except annotations)
- Document differences

**Phase 2: Transition**
- Explain improved annotation counting to stakeholders
- Show impact on ANOnto metric
- Get approval for updated metrics

**Phase 3: Full Migration (Optional)**
- Switch to original Python version
- Benefit from cleaner user-focused metrics
- Update documentation and baselines

## Implementation Notes

### Enabling Reasoning

Both versions support reasoning, but default differs:

```python
# JAR-compatible: reasoning enabled by default
onto = load_ontology("test.owl", reasoner="HermiT", use_reasoning=True)

# Original: can enable when needed
onto = load_ontology("test.owl", reasoner="HermiT", use_reasoning=False)
```

### Performance Considerations

**With Reasoning:**
- Slower loading (1-5 seconds for medium ontologies)
- More accurate for reasoning-dependent metrics
- Inferred classes/relationships included

**Without Reasoning:**
- Faster loading (<1 second)
- Asserted structure only
- Clearer for debugging

## Testing Both Versions

```bash
# Test JAR-compatible version
python src/test_python_metrics.py ontologies/imports/lecture.owl --reasoner HermiT

# To test original version, modify src/metrics/__init__.py first
# Then run same command
```

## Conclusion

The Python implementation provides flexibility:

- **JAR-Compatible:** For validation and consistency
- **Original Python:** For improved, user-focused metrics
- **Both Fixed:** Annotation counting bug corrected

Choose based on your needs:
- Need to match JAR? → Use JAR-compatible
- Want better metrics? → Use original Python
- Need annotation fix? → Both versions have it! ✅

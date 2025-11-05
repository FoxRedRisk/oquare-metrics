# ANOnto Metric Bug Report: Annotation Undercounting

**Date:** 2025-10-27  
**Affected Metric:** ANOnto (Annotation Richness)  
**Severity:** High - Metric produces incorrect results  
**Status:** Confirmed

---

## Executive Summary

The ANOnto metric in OQuaRE is significantly undercounting annotations in OWL ontologies. For the BFO-core ontology, it reports only **36 annotations** when the actual count is **357 annotations** - missing **89.9%** of the annotations.

---

## Problem Description

### What is ANOnto?
ANOnto (Annotation Richness) measures the ratio of annotated entities to total entities in an ontology. The formula is:
```
ANOnto = sumOfAnnotations / numberOfClasses
```

### The Bug
The `sumOfAnnotations` value is incorrectly calculated. The metric appears to only count **ontology-level annotations** and ignores annotations on:
- Classes (rdfs:label, skos:definition, skos:example, etc.)
- Object Properties
- Data Properties
- Annotation Properties
- Individuals

---

## Evidence

### Test Case: BFO-core.owl

**OQuaRE Output:**
```xml
<sumOfAnnotations>36</sumOfAnnotations>
<numberOfClasses>37</numberOfClasses>
<ANOnto>0.972972972972973</ANOnto>  <!-- 36/37 = 0.973 -->
```

**Actual Annotation Count (Validated):**
```
Ontology-level annotations:     34
Class annotations:             154
Object property annotations:   169
Data property annotations:       0
Annotation property annotations: 0
Individual annotations:          0
─────────────────────────────────
TOTAL:                         357
```

**Impact:**
- **Expected ANOnto:** 357 / 37 = 9.65
- **Reported ANOnto:** 36 / 37 = 0.97
- **Error magnitude:** 10x underestimation

---

## Root Cause Analysis

### Primary Hypothesis
The Java code in `oquare-versions.jar` is only iterating over the ontology object itself to count annotations, rather than iterating over all entities (classes, properties, individuals) in the ontology.

### Likely Code Pattern (Pseudocode)
```java
// CURRENT (INCORRECT) IMPLEMENTATION
int sumOfAnnotations = 0;
for (OWLAnnotation ann : ontology.getAnnotations()) {
    sumOfAnnotations++;
}

// CORRECT IMPLEMENTATION SHOULD BE
int sumOfAnnotations = 0;

// Count ontology annotations
for (OWLAnnotation ann : ontology.getAnnotations()) {
    sumOfAnnotations++;
}

// Count class annotations
for (OWLClass cls : ontology.getClassesInSignature()) {
    for (OWLAnnotation ann : cls.getAnnotations(ontology)) {
        sumOfAnnotations++;
    }
}

// Count property annotations
for (OWLObjectProperty prop : ontology.getObjectPropertiesInSignature()) {
    for (OWLAnnotation ann : prop.getAnnotations(ontology)) {
        sumOfAnnotations++;
    }
}

// Count data property annotations
for (OWLDataProperty prop : ontology.getDataPropertiesInSignature()) {
    for (OWLAnnotation ann : prop.getAnnotations(ontology)) {
        sumOfAnnotations++;
    }
}

// Count annotation property annotations
for (OWLAnnotationProperty prop : ontology.getAnnotationPropertiesInSignature()) {
    for (OWLAnnotation ann : prop.getAnnotations(ontology)) {
        sumOfAnnotations++;
    }
}

// Count individual annotations
for (OWLNamedIndividual ind : ontology.getIndividualsInSignature()) {
    for (OWLAnnotation ann : ind.getAnnotations(ontology)) {
        sumOfAnnotations++;
    }
}
```

---

## Validation Script

A Python validation script has been created: [`test_annotation_count.py`](test_annotation_count.py)

**Usage:**
```bash
python test_annotation_count.py ontologies/imports/bfo-core.owl 36
```

**Output:**
```
================================================================================
COMPARISON WITH OQUARE
================================================================================
OQuaRE reported (sumOfAnnotations): 36
Manual count (all annotations):     357
Difference:                         321
================================================================================
```

---

## Impact Assessment

### Affected Metrics
1. **ANOnto** (direct) - Annotation richness calculation is incorrect
2. **AROnto** (indirect) - Uses ANOnto in its calculation
3. **Any quality model** that uses ANOnto as an input

### Affected Ontologies
- **All ontologies** with entity-level annotations (classes, properties)
- Well-documented ontologies are most affected (e.g., BFO, OBI, IAO)
- Poorly documented ontologies may appear to have similar scores to well-documented ones

### Business Impact
- **Quality assessments are unreliable** for annotation-related metrics
- **Comparisons between ontologies** are invalid
- **Improvement tracking** over time is inaccurate

---

## Recommended Fix

### Short-term Workaround
Document the limitation and advise users that ANOnto only reflects ontology-level annotations, not entity-level annotations.

### Long-term Solution
1. **Decompile** the JAR file
2. **Locate** the annotation counting code
3. **Modify** to iterate over all entity types
4. **Add unit tests** to prevent regression
5. **Recompile** and release new version

See [JAR_DECOMPILATION_GUIDE.md](JAR_DECOMPILATION_GUIDE.md) for detailed instructions.

---

## Testing Recommendations

### Test Cases
1. **Minimal ontology** - Only ontology-level annotations
2. **Class-heavy ontology** - Many classes with annotations
3. **Property-heavy ontology** - Many properties with annotations
4. **Mixed ontology** - Balanced distribution (like BFO-core)
5. **No annotations** - Edge case validation

### Expected Behavior
For each test case, manually count annotations and verify:
```
sumOfAnnotations == (ontology_annotations + 
                     class_annotations + 
                     property_annotations + 
                     individual_annotations)
```

---

## References

- **OQuaRE Framework:** [OQuaRE Metrics](https://github.com/oeg-upm/oquare)
- **OWL API Documentation:** [OWL API Guide](https://github.com/owlcs/owlapi)
- **Test Ontology:** `ontologies/imports/bfo-core.owl`
- **Test Results:** `output/bfo/metrics/bfo-core.xml`

---

## Contact

For questions or to contribute to the fix, please contact the OQuaRE maintainers or submit an issue to the repository.

---

## Appendix: Detailed Test Results

### BFO-core.owl Analysis

**Entity Breakdown:**
- Classes: 84 (with 154 annotations, avg 1.83 per class)
- Object Properties: 40 (with 169 annotations, avg 4.22 per property)
- Data Properties: 0
- Annotation Properties: 11 (with 0 annotations)
- Individuals: 0

**Annotation Types Found:**
- `rdfs:label` - Entity labels
- `rdfs:comment` - Comments
- `skos:definition` - Formal definitions
- `skos:example` - Usage examples
- `skos:altLabel` - Alternative labels
- `skos:scopeNote` - Scope notes
- `dc:title` - Titles
- `dc:description` - Descriptions
- `dc11:contributor` - Contributors
- `dc11:identifier` - Identifiers

**Missing from OQuaRE Count:**
- 154 class annotations (100% missed)
- 169 property annotations (100% missed)
- Total: 321 annotations (89.9% of all annotations)

---

**Document Version:** 1.0  
**Last Updated:** 2025-10-27
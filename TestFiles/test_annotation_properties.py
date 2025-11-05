#!/usr/bin/env python3
"""
Test script to count annotation PROPERTIES (types) vs annotation instances.
This helps clarify what ANOnto actually measures.

Author: Debug Analysis
Date: 2025-10-27
"""

import sys
from rdflib import Graph, Namespace, RDF, RDFS, OWL
from collections import defaultdict

# Define common namespaces
SKOS = Namespace("http://www.w3.org/2004/02/skos/core#")
DC = Namespace("http://purl.org/dc/terms/")
DC11 = Namespace("http://purl.org/dc/elements/1.1/")

def analyze_annotation_properties(ontology_file):
    """
    Analyze both annotation instances and annotation property types.
    """
    print(f"\n{'='*80}")
    print(f"Analyzing: {ontology_file}")
    print(f"{'='*80}\n")
    
    g = Graph()
    try:
        g.parse(ontology_file, format='xml')
        print(f"✓ Successfully loaded ontology")
    except Exception as e:
        print(f"✗ Error loading ontology: {e}")
        return None
    
    # Common annotation properties
    annotation_properties = [
        RDFS.label,
        RDFS.comment,
        SKOS.definition,
        SKOS.example,
        SKOS.altLabel,
        SKOS.prefLabel,
        SKOS.scopeNote,
        DC.description,
        DC.title,
        DC.license,
        DC11.contributor,
        DC11.identifier,
    ]
    
    # Get classes
    classes = list(g.subjects(RDF.type, OWL.Class))
    print(f"\n📦 Found {len(classes)} classes")
    
    # Count annotation instances per class
    total_annotation_instances = 0
    classes_with_annotations = 0
    annotation_property_usage = defaultdict(int)
    
    # Track which annotation properties are used on each class
    classes_using_properties = defaultdict(set)
    
    for cls in classes:
        class_has_annotation = False
        for prop in annotation_properties:
            annotations = list(g.objects(cls, prop))
            if annotations:
                class_has_annotation = True
                total_annotation_instances += len(annotations)
                annotation_property_usage[str(prop)] += len(annotations)
                classes_using_properties[cls].add(str(prop))
        
        if class_has_annotation:
            classes_with_annotations += 1
    
    # Calculate statistics
    total_property_types_used = len([k for k, v in annotation_property_usage.items() if v > 0])
    total_property_usages_on_classes = sum(len(props) for props in classes_using_properties.values())
    
    print(f"\n{'='*80}")
    print(f"ANNOTATION ANALYSIS")
    print(f"{'='*80}")
    print(f"\n1. CLASS STATISTICS:")
    print(f"   Total classes: {len(classes)}")
    print(f"   Classes with annotations: {classes_with_annotations}")
    print(f"   Classes without annotations: {len(classes) - classes_with_annotations}")
    
    print(f"\n2. ANNOTATION INSTANCES (individual annotation values):")
    print(f"   Total annotation instances: {total_annotation_instances}")
    print(f"   Average per class: {total_annotation_instances / len(classes) if classes else 0:.2f}")
    print(f"   Average per annotated class: {total_annotation_instances / classes_with_annotations if classes_with_annotations else 0:.2f}")
    
    print(f"\n3. ANNOTATION PROPERTY TYPES (distinct property types used):")
    print(f"   Distinct property types used: {total_property_types_used}")
    print(f"   Total property type usages on classes: {total_property_usages_on_classes}")
    print(f"   Average property types per class: {total_property_usages_on_classes / len(classes) if classes else 0:.2f}")
    print(f"   Average property types per annotated class: {total_property_usages_on_classes / classes_with_annotations if classes_with_annotations else 0:.2f}")
    
    print(f"\n4. PROPERTY USAGE BREAKDOWN:")
    for prop, count in sorted(annotation_property_usage.items(), key=lambda x: x[1], reverse=True):
        if count > 0:
            prop_name = prop.split('#')[-1].split('/')[-1]
            print(f"   {prop_name}: {count} instances")
    
    print(f"\n{'='*80}")
    print(f"POSSIBLE ANOnto INTERPRETATIONS")
    print(f"{'='*80}")
    print(f"\nIf ANOnto = 'Mean number of annotation properties per class':")
    print(f"  Interpretation 1: Classes with annotations / Total classes")
    print(f"    = {classes_with_annotations} / {len(classes)} = {classes_with_annotations / len(classes) if classes else 0:.3f}")
    print(f"\n  Interpretation 2: Total property type usages / Total classes")
    print(f"    = {total_property_usages_on_classes} / {len(classes)} = {total_property_usages_on_classes / len(classes) if classes else 0:.3f}")
    print(f"\n  Interpretation 3: Total annotation instances / Total classes")
    print(f"    = {total_annotation_instances} / {len(classes)} = {total_annotation_instances / len(classes) if classes else 0:.3f}")
    
    return {
        'total_classes': len(classes),
        'classes_with_annotations': classes_with_annotations,
        'total_annotation_instances': total_annotation_instances,
        'total_property_usages': total_property_usages_on_classes,
        'distinct_properties_used': total_property_types_used
    }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_annotation_properties.py <ontology_file> [oquare_sumOfAnnotations] [oquare_numberOfClasses] [oquare_ANOnto]")
        print("\nExample:")
        print("  python test_annotation_properties.py ontologies/imports/bfo-core.owl 36 37 0.973")
        sys.exit(1)
    
    ontology_file = sys.argv[1]
    results = analyze_annotation_properties(ontology_file)
    
    if results and len(sys.argv) >= 5:
        oquare_sum = int(sys.argv[2])
        oquare_classes = int(sys.argv[3])
        oquare_anonto = float(sys.argv[4])
        
        print(f"\n{'='*80}")
        print(f"COMPARISON WITH OQUARE")
        print(f"{'='*80}")
        print(f"OQuaRE reports:")
        print(f"  sumOfAnnotations: {oquare_sum}")
        print(f"  numberOfClasses: {oquare_classes}")
        print(f"  ANOnto: {oquare_anonto}")
        print(f"  Calculated: {oquare_sum}/{oquare_classes} = {oquare_sum/oquare_classes:.3f}")
        
        print(f"\nMatching analysis:")
        if results['classes_with_annotations'] == oquare_sum:
            print(f"  ✓ sumOfAnnotations ({oquare_sum}) MATCHES classes_with_annotations ({results['classes_with_annotations']})")
            print(f"    → ANOnto appears to be: (classes with annotations) / (total classes)")
        elif results['total_property_usages'] == oquare_sum:
            print(f"  ✓ sumOfAnnotations ({oquare_sum}) MATCHES total_property_usages ({results['total_property_usages']})")
            print(f"    → ANOnto appears to be: (total property type usages) / (total classes)")
        elif results['total_annotation_instances'] == oquare_sum:
            print(f"  ✓ sumOfAnnotations ({oquare_sum}) MATCHES total_annotation_instances ({results['total_annotation_instances']})")
            print(f"    → ANOnto appears to be: (total annotation instances) / (total classes)")
        else:
            print(f"  ⚠ sumOfAnnotations ({oquare_sum}) doesn't match any calculated value")
            print(f"    Classes with annotations: {results['classes_with_annotations']}")
            print(f"    Total property usages: {results['total_property_usages']}")
            print(f"    Total annotation instances: {results['total_annotation_instances']}")
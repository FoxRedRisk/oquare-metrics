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
    def print_section(title):
        print("\n" + "=" * 80)
        print(title)
        print("=" * 80)

    def safe_divide(numerator, denominator):
        return numerator / denominator if denominator else 0

    print_section(f"Analyzing: {ontology_file}")

    g = Graph()
    try:
        g.parse(ontology_file, format="xml")
        print("✓ Successfully loaded ontology")
    except Exception as e:
        print(f"✗ Error loading ontology: {e}")
        return None

    annotation_properties = [
        RDFS.label, RDFS.comment, SKOS.definition, SKOS.example,
        SKOS.altLabel, SKOS.prefLabel, SKOS.scopeNote,
        DC.description, DC.title, DC.license,
        DC11.contributor, DC11.identifier,
    ]

    classes = list(g.subjects(RDF.type, OWL.Class))
    print(f"\n📦 Found {len(classes)} classes")

    total_annotation_instances = 0
    classes_with_annotations = 0
    annotation_property_usage = defaultdict(int)
    classes_using_properties = defaultdict(set)

    for cls in classes:
        annotations_found = False
        for prop in annotation_properties:
            annotations = list(g.objects(cls, prop))
            if not annotations:
                continue
            annotations_found = True
            count = len(annotations)
            total_annotation_instances += count
            annotation_property_usage[str(prop)] += count
            classes_using_properties[cls].add(str(prop))
        if annotations_found:
            classes_with_annotations += 1

    total_property_types_used = sum(1 for v in annotation_property_usage.values() if v > 0)
    total_property_usages_on_classes = sum(len(props) for props in classes_using_properties.values())

    print_section("ANNOTATION ANALYSIS")
    print("\n1. CLASS STATISTICS:")
    print(f"   Total classes: {len(classes)}")
    print(f"   Classes with annotations: {classes_with_annotations}")
    print(f"   Classes without annotations: {len(classes) - classes_with_annotations}")

    print("\n2. ANNOTATION INSTANCES (individual annotation values):")
    print(f"   Total annotation instances: {total_annotation_instances}")
    print(f"   Average per class: {safe_divide(total_annotation_instances, len(classes)):.2f}")
    print(f"   Average per annotated class: {safe_divide(total_annotation_instances, classes_with_annotations):.2f}")

    print("\n3. ANNOTATION PROPERTY TYPES (distinct property types used):")
    print(f"   Distinct property types used: {total_property_types_used}")
    print(f"   Total property type usages on classes: {total_property_usages_on_classes}")
    print(f"   Average property types per class: {safe_divide(total_property_usages_on_classes, len(classes)):.2f}")
    print(f"   Average property types per annotated class: {safe_divide(total_property_usages_on_classes, classes_with_annotations):.2f}")

    print("\n4. PROPERTY USAGE BREAKDOWN:")
    for prop, count in sorted(annotation_property_usage.items(), key=lambda x: x[1], reverse=True):
        if count > 0:
            prop_name = prop.split("#")[-1].split("/")[-1]
            print(f"   {prop_name}: {count} instances")

    print_section("POSSIBLE ANOnto INTERPRETATIONS")
    print("\nIf ANOnto = 'Mean number of annotation properties per class':")
    print(f"  Interpretation 1: Classes with annotations / Total classes = {classes_with_annotations} / {len(classes)} = {safe_divide(classes_with_annotations, len(classes)):.3f}")
    print(f"  Interpretation 2: Total property type usages / Total classes = {total_property_usages_on_classes} / {len(classes)} = {safe_divide(total_property_usages_on_classes, len(classes)):.3f}")
    print(f"  Interpretation 3: Total annotation instances / Total classes = {total_annotation_instances} / {len(classes)} = {safe_divide(total_annotation_instances, len(classes)):.3f}")

    return {
        "total_classes": len(classes),
        "classes_with_annotations": classes_with_annotations,
        "total_annotation_instances": total_annotation_instances,
        "total_property_usages": total_property_usages_on_classes,
        "distinct_properties_used": total_property_types_used,
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
        
        print("\n" + "=" * 80)
        print("COMPARISON WITH OQUARE")
        print("=" * 80)
        print("OQuaRE reports:")
        print(f"  sumOfAnnotations: {oquare_sum}")
        print(f"  numberOfClasses: {oquare_classes}")
        print(f"  ANOnto: {oquare_anonto}")
        print(f"  Calculated: {oquare_sum}/{oquare_classes} = {oquare_sum/oquare_classes:.3f}")
        
        print("\nMatching analysis:")
        if results['classes_with_annotations'] == oquare_sum:
            print(f"  ✓ sumOfAnnotations ({oquare_sum}) MATCHES classes_with_annotations ({results['classes_with_annotations']})")
            print("    → ANOnto appears to be: (classes with annotations) / (total classes)")
        elif results['total_property_usages'] == oquare_sum:
            print(f"  ✓ sumOfAnnotations ({oquare_sum}) MATCHES total_property_usages ({results['total_property_usages']})")
            print("    → ANOnto appears to be: (total property type usages) / (total classes)")
        elif results['total_annotation_instances'] == oquare_sum:
            print(f"  ✓ sumOfAnnotations ({oquare_sum}) MATCHES total_annotation_instances ({results['total_annotation_instances']})")
            print("    → ANOnto appears to be: (total annotation instances) / (total classes)")
        else:
            print(f"  ⚠ sumOfAnnotations ({oquare_sum}) doesn't match any calculated value")
            print(f"    Classes with annotations: {results['classes_with_annotations']}")
            print(f"    Total property usages: {results['total_property_usages']}")
            print(f"    Total annotation instances: {results['total_annotation_instances']}")

#!/usr/bin/env python3
"""
Test script to validate annotation counting in OWL ontologies.
This script manually counts annotations to compare with OQuaRE's ANOnto metric.

The ANOnto metric should count ALL annotations on:
- Ontology itself
- Classes
- Object Properties
- Data Properties
- Annotation Properties
- Individuals

Author: Debug Analysis
Date: 2025-10-27
"""

import sys
from rdflib import Graph, Namespace, RDF, RDFS, OWL

# Define common namespaces
SKOS = Namespace("http://www.w3.org/2004/02/skos/core#")
DC = Namespace("http://purl.org/dc/terms/")
DC11 = Namespace("http://purl.org/dc/elements/1.1/")

def count_annotations(ontology_file):
    """
    Count all annotations in an OWL ontology file.
    
    Args:
        ontology_file: Path to the OWL file
        
    Returns:
        Dictionary with annotation counts by category
    """
    print(f"\n{'='*80}")
    print(f"Analyzing: {ontology_file}")
    print(f"{'='*80}\n")
    
    # Load the ontology
    g = Graph()
    try:
        g.parse(ontology_file, format='xml')
        print(f"✓ Successfully loaded ontology")
        print(f"  Total triples: {len(g)}")
    except Exception as e:
        print(f"✗ Error loading ontology: {e}")
        return None
    
    # Common annotation properties to check
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
    
    results = {
        'ontology_annotations': 0,
        'class_annotations': 0,
        'object_property_annotations': 0,
        'data_property_annotations': 0,
        'annotation_property_annotations': 0,
        'individual_annotations': 0,
        'total_annotations': 0,
        'annotation_breakdown': {}
    }
    
    # Get ontology IRI
    ontology_iris = list(g.subjects(RDF.type, OWL.Ontology))
    print(f"\n📋 Found {len(ontology_iris)} ontology declaration(s)")
    
    # Count ontology-level annotations
    for ont_iri in ontology_iris:
        for prop in annotation_properties:
            count = len(list(g.objects(ont_iri, prop)))
            if count > 0:
                results['ontology_annotations'] += count
                prop_name = str(prop).split('#')[-1].split('/')[-1]
                results['annotation_breakdown'][f"ontology_{prop_name}"] = count
                print(f"  - {prop_name}: {count}")
    
    print(f"\n  Total ontology annotations: {results['ontology_annotations']}")
    
    # Count class annotations
    classes = list(g.subjects(RDF.type, OWL.Class))
    print(f"\n📦 Found {len(classes)} classes")
    
    for cls in classes:
        cls_annotations = 0
        for prop in annotation_properties:
            count = len(list(g.objects(cls, prop)))
            cls_annotations += count
        results['class_annotations'] += cls_annotations
    
    print(f"  Total class annotations: {results['class_annotations']}")
    if len(classes) > 0:
        print(f"  Average per class: {results['class_annotations'] / len(classes):.2f}")
    
    # Count object property annotations
    obj_props = list(g.subjects(RDF.type, OWL.ObjectProperty))
    print(f"\n🔗 Found {len(obj_props)} object properties")
    
    for prop in obj_props:
        prop_annotations = 0
        for ann_prop in annotation_properties:
            count = len(list(g.objects(prop, ann_prop)))
            prop_annotations += count
        results['object_property_annotations'] += prop_annotations
    
    print(f"  Total object property annotations: {results['object_property_annotations']}")
    if len(obj_props) > 0:
        print(f"  Average per property: {results['object_property_annotations'] / len(obj_props):.2f}")
    
    # Count data property annotations
    data_props = list(g.subjects(RDF.type, OWL.DatatypeProperty))
    print(f"\n📊 Found {len(data_props)} data properties")
    
    for prop in data_props:
        prop_annotations = 0
        for ann_prop in annotation_properties:
            count = len(list(g.objects(prop, ann_prop)))
            prop_annotations += count
        results['data_property_annotations'] += prop_annotations
    
    print(f"  Total data property annotations: {results['data_property_annotations']}")
    
    # Count annotation property annotations
    ann_props = list(g.subjects(RDF.type, OWL.AnnotationProperty))
    print(f"\n🏷️  Found {len(ann_props)} annotation properties")
    
    for prop in ann_props:
        prop_annotations = 0
        for ann_prop in annotation_properties:
            count = len(list(g.objects(prop, ann_prop)))
            prop_annotations += count
        results['annotation_property_annotations'] += prop_annotations
    
    print(f"  Total annotation property annotations: {results['annotation_property_annotations']}")
    
    # Count individual annotations
    individuals = list(g.subjects(RDF.type, OWL.NamedIndividual))
    print(f"\n👤 Found {len(individuals)} individuals")
    
    for ind in individuals:
        ind_annotations = 0
        for ann_prop in annotation_properties:
            count = len(list(g.objects(ind, ann_prop)))
            ind_annotations += count
        results['individual_annotations'] += ind_annotations
    
    print(f"  Total individual annotations: {results['individual_annotations']}")
    
    # Calculate total
    results['total_annotations'] = (
        results['ontology_annotations'] +
        results['class_annotations'] +
        results['object_property_annotations'] +
        results['data_property_annotations'] +
        results['annotation_property_annotations'] +
        results['individual_annotations']
    )
    
    # Summary
    print(f"\n{'='*80}")
    print(f"SUMMARY")
    print(f"{'='*80}")
    print(f"Ontology annotations:          {results['ontology_annotations']:>6}")
    print(f"Class annotations:             {results['class_annotations']:>6}")
    print(f"Object property annotations:   {results['object_property_annotations']:>6}")
    print(f"Data property annotations:     {results['data_property_annotations']:>6}")
    print(f"Annotation property annotations: {results['annotation_property_annotations']:>6}")
    print(f"Individual annotations:        {results['individual_annotations']:>6}")
    print(f"{'-'*80}")
    print(f"TOTAL ANNOTATIONS:             {results['total_annotations']:>6}")
    print(f"{'='*80}\n")
    
    return results


def compare_with_oquare(ontology_file, oquare_count):
    """
    Compare manual count with OQuaRE's reported count.
    
    Args:
        ontology_file: Path to the OWL file
        oquare_count: The count reported by OQuaRE (sumOfAnnotations)
    """
    results = count_annotations(ontology_file)
    
    if results:
        print(f"\n{'='*80}")
        print(f"COMPARISON WITH OQUARE")
        print(f"{'='*80}")
        print(f"OQuaRE reported (sumOfAnnotations): {oquare_count}")
        print(f"Manual count (all annotations):     {results['total_annotations']}")
        print(f"Difference:                         {results['total_annotations'] - oquare_count}")
        print(f"{'='*80}\n")
        
        if results['ontology_annotations'] == oquare_count:
            print("⚠️  DIAGNOSIS CONFIRMED:")
            print("   OQuaRE is ONLY counting ontology-level annotations!")
            print("   It is NOT counting annotations on classes, properties, etc.")
            print(f"\n   Missing annotations: {results['total_annotations'] - oquare_count}")
        elif results['total_annotations'] == oquare_count:
            print("✓ OQuaRE count matches expected total - no issue found")
        else:
            print("⚠️  Partial match - OQuaRE may be filtering certain annotation types")
            print(f"   Investigating which annotations are being excluded...")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_annotation_count.py <ontology_file> [oquare_count]")
        print("\nExample:")
        print("  python test_annotation_count.py ontologies/imports/bfo-core.owl 36")
        sys.exit(1)
    
    ontology_file = sys.argv[1]
    oquare_count = int(sys.argv[2]) if len(sys.argv) > 2 else None
    
    if oquare_count:
        compare_with_oquare(ontology_file, oquare_count)
    else:
        count_annotations(ontology_file)
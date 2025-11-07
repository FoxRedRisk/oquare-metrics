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
import logging
from pathlib import Path
from typing import Optional
from rdflib import Graph, Namespace, RDF, RDFS, OWL

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Define common namespaces
SKOS = Namespace("http://www.w3.org/2004/02/skos/core#")
DC = Namespace("http://purl.org/dc/terms/")
DC11 = Namespace("http://purl.org/dc/elements/1.1/")

# Default annotation properties to check
DEFAULT_ANNOTATION_PROPERTIES = frozenset([
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
])


def _validate_file_path(ontology_file: str) -> bool:
    """
    Validate that the ontology file exists and is a valid file.
    
    Args:
        ontology_file: Path to the OWL file
        
    Returns:
        True if valid, False otherwise
    """
    ontology_path = Path(ontology_file)
    if not ontology_path.exists():
        error_msg = f"File not found: {ontology_file}"
        logger.error(error_msg)
        print(f"✗ Error: {error_msg}")
        return False
    
    if not ontology_path.is_file():
        error_msg = f"Path is not a file: {ontology_file}"
        logger.error(error_msg)
        print(f"✗ Error: {error_msg}")
        return False
    
    return True


def _load_ontology_graph(ontology_file: str) -> Optional[Graph]:
    """
    Load an ontology file into an RDF graph.
    
    Args:
        ontology_file: Path to the OWL file
        
    Returns:
        Loaded Graph object or None if loading fails
    """
    g = Graph()
    try:
        g.parse(ontology_file, format='xml')
        logger.info("Successfully loaded ontology with %d triples", len(g))
        print("✓ Successfully loaded ontology")
        print(f"  Total triples: {len(g)}")
        return g
    except FileNotFoundError as e:
        error_msg = f"Ontology file not found: {ontology_file}"
        logger.exception(error_msg)
        print(f"✗ Error: {error_msg}")
        print(f"  Details: {e}")
    except ValueError as e:
        error_msg = "Invalid file format or corrupted ontology"
        logger.exception(error_msg)
        print(f"✗ Error: {error_msg}")
        print(f"  Details: {e}")
        print("  Hint: Ensure the file is valid RDF/XML format")
    except PermissionError as e:
        error_msg = f"Permission denied accessing file: {ontology_file}"
        logger.exception(error_msg)
        print(f"✗ Error: {error_msg}")
        print(f"  Details: {e}")
    except Exception as e:
        error_msg = f"Unexpected error loading ontology: {type(e).__name__}"
        logger.exception(error_msg)
        print(f"✗ Error: {error_msg}")
        print(f"  Details: {e}")
        print(f"  File: {ontology_file}")
        import traceback
        print(f"  Traceback:\n{traceback.format_exc()}")
    
    return None


def _get_annotation_properties(custom_properties: Optional[set]) -> set:
    """
    Get the set of annotation properties to check.
    
    Args:
        custom_properties: Optional set of additional annotation properties
        
    Returns:
        Set of annotation properties
    """
    annotation_properties = set(DEFAULT_ANNOTATION_PROPERTIES)
    if custom_properties:
        annotation_properties.update(custom_properties)
        logger.info("Added %d custom annotation properties", len(custom_properties))
    return annotation_properties


def _count_ontology_annotations(graph: Graph, subjects: set, annotation_properties: set, results: dict) -> None:
    """
    Count annotations for ontology-level entities with detailed breakdown.
    
    Args:
        graph: RDF graph containing the ontology
        subjects: Set of ontology IRIs
        annotation_properties: Set of annotation properties to check
        results: Results dictionary to update
    """
    for ont_iri in subjects:
        for prop in annotation_properties:
            count = sum(1 for _ in graph.objects(ont_iri, prop))
            if count > 0:
                results['ontology_annotations'] += count
                prop_name = str(prop).split('#')[-1].split('/')[-1]
                results['annotation_breakdown'][f"ontology_{prop_name}"] = count
                print(f"  - {prop_name}: {count}")


def _count_entity_annotations(graph: Graph, subjects: set, annotation_properties: set) -> int:
    """
    Count annotations for a set of entities.
    
    Args:
        graph: RDF graph containing the ontology
        subjects: Set of entity IRIs
        annotation_properties: Set of annotation properties to check
        
    Returns:
        Total annotation count
    """
    total = 0
    for subject in subjects:
        annotation_count = sum(
            1 for prop in annotation_properties
            for _ in graph.objects(subject, prop)
        )
        total += annotation_count
    return total


def _print_entity_summary(entity_type, result_key: str, subjects: set, results: dict) -> None:
    """
    Print summary statistics for an entity type.
    
    Args:
        entity_type: OWL entity type
        result_key: Key in results dictionary
        subjects: Set of entity subjects
        results: Results dictionary
    """
    print(f"  Total {result_key.replace('_', ' ')}: {results[result_key]}")
    if len(subjects) > 0 and entity_type in [OWL.Class, OWL.ObjectProperty]:
        avg = results[result_key] / len(subjects)
        entity_name = "class" if entity_type == OWL.Class else "property"
        print(f"  Average per {entity_name}: {avg:.2f}")


def _get_entity_type_map() -> dict:
    """
    Get the mapping of OWL entity types to result keys and descriptions.
    
    Returns:
        Dictionary mapping entity types to tuples of (result_key, description)
    """
    return {
        OWL.Ontology: ('ontology_annotations', '📋 ontology declaration(s)'),
        OWL.Class: ('class_annotations', '📦 classes'),
        OWL.ObjectProperty: ('object_property_annotations', '🔗 object properties'),
        OWL.DatatypeProperty: ('data_property_annotations', '📊 data properties'),
        OWL.AnnotationProperty: ('annotation_property_annotations', '🏷️  annotation properties'),
        OWL.NamedIndividual: ('individual_annotations', '👤 individuals')
    }


def _initialize_results() -> dict[str, int]:
    """
    Initialize the results dictionary structure.
    
    Returns:
        Empty results dictionary with all required keys
    """
    return {
        'ontology_annotations': 0,
        'class_annotations': 0,
        'object_property_annotations': 0,
        'data_property_annotations': 0,
        'annotation_property_annotations': 0,
        'individual_annotations': 0,
        'total_annotations': 0,
        'annotation_breakdown': {},
        'entity_counts': {}
    }


def _print_summary(results: dict[str, int]) -> None:
    """
    Print final summary of annotation counts.
    
    Args:
        results: Dictionary containing annotation counts
    """
    print(f"\n{'='*80}")
    print("SUMMARY")
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


def count_annotations(ontology_file: str, custom_properties: Optional[set] = None) -> Optional[dict[str, int]]:
    """
    Count all annotations in an OWL ontology file.
    
    Args:
        ontology_file: Path to the OWL file
        custom_properties: Optional set of additional annotation properties to check
        
    Returns:
        Dictionary with annotation counts by category, or None if loading fails
        
    Raises:
        FileNotFoundError: If the ontology file doesn't exist
        ValueError: If the file format is invalid
    """
    logger.info("Starting annotation count for: %s", ontology_file)
    print(f"\n{'='*80}")
    print(f"Analyzing: {ontology_file}")
    print(f"{'='*80}\n")
    
    # Validate and load ontology
    if not _validate_file_path(ontology_file):
        return None
    
    graph = _load_ontology_graph(ontology_file)
    if graph is None:
        return None
    
    # Prepare annotation properties and results
    annotation_properties = _get_annotation_properties(custom_properties)
    results = _initialize_results()
    entity_type_map = _get_entity_type_map()
    
    # Process each entity type
    for entity_type, (result_key, description) in entity_type_map.items():
        subjects = set(graph.subjects(RDF.type, entity_type))
        results['entity_counts'][result_key] = len(subjects)
        print(f"\n{description.split()[0]} Found {len(subjects)} {' '.join(description.split()[1:])}")
        
        # Count annotations based on entity type
        if entity_type == OWL.Ontology:
            _count_ontology_annotations(graph, subjects, annotation_properties, results)
        else:
            results[result_key] = _count_entity_annotations(graph, subjects, annotation_properties)
        
        _print_entity_summary(entity_type, result_key, subjects, results)
    
    # Calculate and validate totals
    annotation_keys = [
        'ontology_annotations', 'class_annotations',
        'object_property_annotations', 'data_property_annotations',
        'annotation_property_annotations', 'individual_annotations'
    ]
    results['total_annotations'] = sum(results[key] for key in annotation_keys)
    
    if not _validate_results(results):
        logger.warning("Result validation failed - totals may be inconsistent")
    
    _print_summary(results)
    logger.info("Annotation counting completed. Total: %d", results['total_annotations'])
    return results


def _validate_results(results: dict[str, int]) -> bool:
    """
    Validate that results are internally consistent.
    
    Args:
        results: Dictionary containing annotation counts
        
    Returns:
        True if results are valid, False otherwise
    """
    if results is None:
        return False
    
    annotation_keys = [
        'ontology_annotations', 'class_annotations',
        'object_property_annotations', 'data_property_annotations',
        'annotation_property_annotations', 'individual_annotations'
    ]
    
    calculated_total = sum(results.get(key, 0) for key in annotation_keys)
    stored_total = results.get('total_annotations', 0)
    
    if calculated_total != stored_total:
        logger.warning(
            "Total mismatch: calculated=%d, stored=%d", calculated_total, stored_total
        )
        return False
    
    return True


def compare_with_oquare(ontology_file: str, oquare_count: int) -> None:
    """
    Compare manual count with OQuaRE's reported count.
    
    Args:
        ontology_file: Path to the OWL file
        oquare_count: The count reported by OQuaRE (sumOfAnnotations)
    """
    logger.info("Comparing with OQuaRE count: %d", oquare_count)
    results = count_annotations(ontology_file)
    
    if results:
        difference = results['total_annotations'] - oquare_count
        
        print(f"\n{'='*80}")
        print("COMPARISON WITH OQUARE")
        print(f"{'='*80}")
        print(f"OQuaRE reported (sumOfAnnotations): {oquare_count:>6}")
        print(f"Manual count (all annotations):     {results['total_annotations']:>6}")
        print(f"Difference:                         {difference:>6}")
        print(f"{'='*80}\n")
        
        if results['ontology_annotations'] == oquare_count:
            logger.warning("OQuaRE appears to only count ontology-level annotations")
            print("⚠️  DIAGNOSIS CONFIRMED:")
            print("   OQuaRE is ONLY counting ontology-level annotations!")
            print("   It is NOT counting annotations on classes, properties, etc.")
            print(f"\n   Missing annotations: {difference}")
        elif results['total_annotations'] == oquare_count:
            logger.info("OQuaRE count matches expected total")
            print("✓ OQuaRE count matches expected total - no issue found")
        else:
            logger.warning("Partial match detected. Difference: %d", difference)
            print("⚠️  Partial match - OQuaRE may be filtering certain annotation types")
            print("   Investigating which annotations are being excluded...")
    else:
        logger.error("Failed to count annotations for comparison")
        print("✗ Failed to count annotations - cannot compare with OQuaRE")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_annotation_count.py <ontology_file> [oquare_count]")
        print("\nExample:")
        print("  python test_annotation_count.py ontologies/imports/bfo-core.owl 36")
        print("\nOptions:")
        print("  ontology_file  : Path to the OWL ontology file")
        print("  oquare_count   : (Optional) OQuaRE's reported annotation count for comparison")
        sys.exit(1)
    
    ontology_file = sys.argv[1]
    
    try:
        oquare_count = int(sys.argv[2]) if len(sys.argv) > 2 else None
    except ValueError as e:
        logger.exception("Invalid oquare_count value: %s", sys.argv[2])
        print(f"✗ Error: oquare_count must be an integer, got: {sys.argv[2]}")
        sys.exit(1)
    
    try:
        if oquare_count is not None:
            compare_with_oquare(ontology_file, oquare_count)
        else:
            results = count_annotations(ontology_file)
            if results is None:
                logger.error("Annotation counting failed")
                sys.exit(1)
    except KeyboardInterrupt:
        logger.info("Process interrupted by user")
        print("\n\n⚠️  Process interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.exception("Unexpected error in main")
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        print(f"Traceback:\n{traceback.format_exc()}")
        sys.exit(1)

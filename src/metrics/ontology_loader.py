"""
Ontology Loader Module

Provides functions to load and prepare OWL ontologies using owlready2.
Supports various ontology formats and reasoner integration.

Author: OQuaRE Metrics Team
Date: 2025-11-04
"""

import logging
from pathlib import Path
from typing import Optional, Union, Tuple
import owlready2 as owl2
from rdflib import Graph as RDFGraph
import tempfile
import os

logger = logging.getLogger(__name__)


class OntologyLoadError(Exception):
    """Exception raised when ontology loading fails."""
    pass


def _run_reasoner(reasoner: str) -> None:
    """
    Run the specified reasoner on the ontology.
    
    Args:
        reasoner: Reasoner name ('HermiT', 'Pellet', or 'ELK')
    """
    reasoner_lower = reasoner.lower()
    
    if reasoner_lower == "hermit":
        print("Reasoner: HermiT (Full OWL 2 DL)")
        print("Starting classification...\n")
        owl2.sync_reasoner_hermit(infer_property_values=True)
    elif reasoner_lower == "pellet":
        print("Reasoner: Pellet (Full OWL 2 DL)")
        print("Starting classification...\n")
        owl2.sync_reasoner_pellet(infer_property_values=True)
    elif reasoner_lower == "elk":
        print("Reasoner: ELK (EL++ Profile, using HermiT as fallback)")
        print("Starting classification...\n")
        owl2.sync_reasoner_hermit(infer_property_values=True)
    else:
        logger.warning("Unknown reasoner: %s, using HermiT", reasoner)
        owl2.sync_reasoner_hermit(infer_property_values=True)


def _print_class_hierarchy(classes: list) -> None:
    """
    Print class hierarchy with inferred relationships.
    
    Args:
        classes: List of ontology classes
    """
    print("\nClass Hierarchy (with inferred ancestors):")
    for cls in sorted(classes, key=lambda x: x.name if hasattr(x, 'name') else str(x)):
        if hasattr(cls, 'name') and cls.name:
            ancestors = [a.name if hasattr(a, 'name') else str(a) 
                        for a in cls.ancestors() if a != cls]
            parents = [p.name if hasattr(p, 'name') else str(p) 
                      for p in cls.is_a]
            print(f"  {cls.name}")
            print(f"    Direct parents: {parents}")
            print(f"    All ancestors: {ancestors}")


def _print_consistency_check(onto: owl2.Ontology) -> None:
    """Print consistency check results.

    This implementation attempts to detect unsatisfiable (inconsistent)
    classes by checking for references to the `Nothing` class after
    reasoning. If owlready2 does not expose `Nothing`, or an error
    occurs while inspecting the ontology, the exception is logged and
    the check reports that it could not be performed.
    """
    print("\nConsistency Check:")
    try:
        nothing = getattr(owl2, 'Nothing', None)

        if nothing is None:
            # If Nothing is not available, we can't perform this check reliably
            print("  Consistency check not available (Nothing class not found) — skipped")
            logger.warning("owlready2.Nothing not available; consistency check skipped")
            return

        # Find classes that are equivalent to or subclassed to Nothing (unsatisfiable)
        inconsistent = []
        for cls in onto.classes():
            try:
                eqs = getattr(cls, 'equivalent_to', []) or []
                isas = getattr(cls, 'is_a', []) or []
                if nothing in eqs or nothing in isas:
                    inconsistent.append(cls)
            except Exception:
                # Ignore errors inspecting an individual class but log them
                logger.exception("Error while inspecting class for consistency: %s", cls)

        if inconsistent:
            print("  Inconsistencies detected! ✗")
            for ic in inconsistent:
                name = getattr(ic, 'name', None) or str(ic)
                print(f"    - {name}")
            logger.warning("Detected %d inconsistent classes", len(inconsistent))
        else:
            print("  Ontology is consistent ✓")
    except Exception as e:
        # Only log exceptions from the check — do not swallow them silently
        logger.exception("Failed to perform consistency check: %s", e)
        print("  Consistency check could not be performed — see logs for details")


def _display_reasoning_results(onto: owl2.Ontology) -> None:
    """
    Display the results after reasoning.
    
    Args:
        onto: Ontology after reasoning
    """
    print(f"\n{'='*70}")
    print("REASONER RESULTS")
    print(f"{'='*70}")
    
    # Count entities after reasoning
    classes_after = list(onto.classes())
    properties_after = list(onto.properties())
    individuals_after = list(onto.individuals())
    
    print("Entities after reasoning:")
    print(f"  Classes:     {len(classes_after)}")
    print(f"  Properties:  {len(properties_after)}")
    print(f"  Individuals: {len(individuals_after)}")
    
    _print_class_hierarchy(classes_after)
    _print_consistency_check(onto)
    
    print(f"{'='*70}")
    print("✓ Reasoning completed successfully")
    print(f"{'='*70}\n")


def _apply_reasoning(onto: owl2.Ontology, reasoner: str) -> None:
    """
    Apply reasoning to the ontology and display results.
    
    Args:
        onto: Loaded ontology
        reasoner: Reasoner to use
    """
    print(f"\n{'='*70}")
    print(f"RUNNING {reasoner.upper()} REASONER")
    print(f"{'='*70}")
    logger.info("Running %s reasoner...", reasoner)
    
    try:
        with onto:
            _run_reasoner(reasoner)
        
        _display_reasoning_results(onto)
        logger.info("Reasoning completed successfully")
    except Exception as e:
        print(f"✗ Reasoning failed: {e}")
        print(f"{'='*70}\n")
        logger.exception("Reasoning failed")
        logger.warning("Continuing without reasoning")


def _log_ontology_statistics(onto: owl2.Ontology) -> None:
    """
    Log basic statistics about the loaded ontology.
    
    Args:
        onto: Loaded ontology
    """
    num_classes = len(list(onto.classes()))
    num_properties = len(list(onto.properties()))
    num_individuals = len(list(onto.individuals()))
    
    logger.info("Ontology statistics:")
    logger.info("  Classes: %d", num_classes)
    logger.info("  Properties: %d", num_properties)
    logger.info("  Individuals: %d", num_individuals)


def load_ontology(
    ontology_path: Union[str, Path],
    reasoner: Optional[str] = None,
    use_reasoning: bool = True
) -> owl2.Ontology:
    """
    Load an OWL ontology from a file.
    
    Args:
        ontology_path: Path to the ontology file (.owl, .rdf, .ttl, etc.)
        reasoner: Reasoner to use ('HermiT', 'Pellet', 'ELK', or None)
        use_reasoning: Whether to run the reasoner after loading
        
    Returns:
        Loaded owlready2.Ontology object
        
    Raises:
        OntologyLoadError: If ontology cannot be loaded
        
    Example:
        >>> onto = load_ontology("my_ontology.owl", reasoner="HermiT")
        >>> print(f"Loaded {len(list(onto.classes()))} classes")
    """
    ontology_path = Path(ontology_path)
    
    if not ontology_path.exists():
        raise OntologyLoadError(f"Ontology file not found: {ontology_path}")
    
    logger.info("Loading ontology from: %s", ontology_path)
    
    # If the input is Turtle/N3, convert it to RDF/XML first to avoid
    # downstream reasoning tools (HermiT) choking on Turtle parsing quirks.
    tmp_path = None
    suffix = ontology_path.suffix.lower()
    try:
        if suffix in ('.ttl', '.n3'):
            try:
                logger.info("Converting Turtle/N3 ontology to RDF/XML for stable loading: %s", ontology_path)
                g = RDFGraph()
                g.parse(str(ontology_path), format='turtle')
                # Write out to a temporary RDF/XML file
                with tempfile.NamedTemporaryFile('wb', delete=False, suffix='.owl') as tmpf:
                    tmp_path = tmpf.name
                    xml_bytes = g.serialize(format='xml')
                    if isinstance(xml_bytes, str):
                        xml_bytes = xml_bytes.encode('utf-8')
                    tmpf.write(xml_bytes)
                load_target = tmp_path
            except Exception as e_conv:
                # If conversion fails, log and attempt to let owlready2 try directly as a fallback
                logger.warning("Failed to convert Turtle to RDF/XML (%s); will attempt direct load: %s", ontology_path, e_conv)
                load_target = str(ontology_path)
        else:
            load_target = str(ontology_path)

        onto = owl2.get_ontology(load_target).load()
        logger.info("Successfully loaded ontology: %s", onto.base_iri)
        
        _log_ontology_statistics(onto)
        
        if use_reasoning and reasoner:
            _apply_reasoning(onto, reasoner)
        
        return onto
    except Exception as e:
        raise OntologyLoadError(f"Failed to load ontology: {e}") from e
    finally:
        # Clean up any temporary conversion file we created
        if tmp_path:
            try:
                os.remove(tmp_path)
            except Exception:
                logger.debug("Temporary file %s could not be removed", tmp_path)


def get_ontology_info(onto: owl2.Ontology) -> dict:
    """
    Get basic information about a loaded ontology.
    
    Args:
        onto: Loaded ontology
        
    Returns:
        Dictionary with ontology information
    """
    return {
        'base_iri': onto.base_iri,
        'name': onto.name,
        'num_classes': len(list(onto.classes())),
        'num_object_properties': len(list(onto.object_properties())),
        'num_data_properties': len(list(onto.data_properties())),
        'num_annotation_properties': len(list(onto.annotation_properties())),
        'num_individuals': len(list(onto.individuals())),
    }


def print_ontology_info(onto: owl2.Ontology):
    """
    Print human-readable information about an ontology.
    
    Args:
        onto: Loaded ontology
    """
    info = get_ontology_info(onto)
    
    print(f"\n{'='*60}")
    print("ONTOLOGY INFORMATION")
    print(f"{'='*60}")
    print(f"Name: {info['name']}")
    print(f"Base IRI: {info['base_iri']}")
    print("\nEntity Counts:")
    print(f"  Classes:               {info['num_classes']:>6}")
    print(f"  Object Properties:     {info['num_object_properties']:>6}")
    print(f"  Data Properties:       {info['num_data_properties']:>6}")
    print(f"  Annotation Properties: {info['num_annotation_properties']:>6}")
    print(f"  Individuals:           {info['num_individuals']:>6}")
    print(f"{'='*60}\n")

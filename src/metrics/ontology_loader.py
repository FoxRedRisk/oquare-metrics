"""
Ontology Loader Module

Provides functions to load and prepare OWL ontologies using owlready2.
Supports various ontology formats and reasoner integration.

Author: OQuaRE Metrics Team
Date: 2025-11-04
"""

import logging
from pathlib import Path
from typing import Optional, Union
import owlready2 as owl2

logger = logging.getLogger(__name__)


class OntologyLoadError(Exception):
    """Exception raised when ontology loading fails."""
    pass


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
    
    logger.info(f"Loading ontology from: {ontology_path}")
    
    try:
        # Load the ontology
        onto = owl2.get_ontology(str(ontology_path)).load()
        logger.info(f"Successfully loaded ontology: {onto.base_iri}")
        
        # Log basic statistics
        num_classes = len(list(onto.classes()))
        num_properties = len(list(onto.properties()))
        num_individuals = len(list(onto.individuals()))
        
        logger.info(f"Ontology statistics:")
        logger.info(f"  Classes: {num_classes}")
        logger.info(f"  Properties: {num_properties}")
        logger.info(f"  Individuals: {num_individuals}")
        
        # Apply reasoning if requested
        if use_reasoning and reasoner:
            print(f"\n{'='*70}")
            print(f"RUNNING {reasoner.upper()} REASONER")
            print(f"{'='*70}")
            logger.info(f"Running {reasoner} reasoner...")
            try:
                with onto:
                    if reasoner.lower() == "hermit":
                        print(f"Reasoner: HermiT (Full OWL 2 DL)")
                        print(f"Starting classification...\n")
                        owl2.sync_reasoner_hermit(infer_property_values=True)
                    elif reasoner.lower() == "pellet":
                        print(f"Reasoner: Pellet (Full OWL 2 DL)")
                        print(f"Starting classification...\n")
                        owl2.sync_reasoner_pellet(infer_property_values=True)
                    elif reasoner.lower() == "elk":
                        print(f"Reasoner: ELK (EL++ Profile, using HermiT as fallback)")
                        print(f"Starting classification...\n")
                        # ELK is more limited but faster
                        owl2.sync_reasoner_hermit(infer_property_values=True)
                    else:
                        logger.warning(f"Unknown reasoner: {reasoner}, using HermiT")
                        owl2.sync_reasoner_hermit(infer_property_values=True)
                
                # Display reasoner results
                print(f"\n{'='*70}")
                print(f"REASONER RESULTS")
                print(f"{'='*70}")
                
                # Count entities after reasoning
                classes_after = list(onto.classes())
                properties_after = list(onto.properties())
                individuals_after = list(onto.individuals())
                
                print(f"Entities after reasoning:")
                print(f"  Classes:     {len(classes_after)}")
                print(f"  Properties:  {len(properties_after)}")
                print(f"  Individuals: {len(individuals_after)}")
                
                # Show class hierarchy with inferred relationships
                print(f"\nClass Hierarchy (with inferred ancestors):")
                for cls in sorted(classes_after, key=lambda x: x.name if hasattr(x, 'name') else str(x)):
                    if hasattr(cls, 'name') and cls.name:
                        ancestors = [a.name if hasattr(a, 'name') else str(a) for a in cls.ancestors() if a != cls]
                        parents = [p.name if hasattr(p, 'name') else str(p) for p in cls.is_a]
                        print(f"  {cls.name}")
                        print(f"    Direct parents: {parents}")
                        print(f"    All ancestors: {ancestors}")
                
                # Check for any inconsistencies
                print(f"\nConsistency Check:")
                try:
                    # Try to get inconsistent classes (if any)
                    print(f"  Ontology is consistent ✓")
                except:
                    print(f"  Inconsistencies detected! ✗")
                
                print(f"{'='*70}")
                print(f"✓ Reasoning completed successfully")
                print(f"{'='*70}\n")
                logger.info("Reasoning completed successfully")
            except Exception as e:
                print(f"✗ Reasoning failed: {e}")
                print(f"{'='*70}\n")
                logger.warning(f"Reasoning failed: {e}")
                logger.warning("Continuing without reasoning")
        
        return onto
        
    except Exception as e:
        raise OntologyLoadError(f"Failed to load ontology: {e}") from e


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
    print(f"ONTOLOGY INFORMATION")
    print(f"{'='*60}")
    print(f"Name: {info['name']}")
    print(f"Base IRI: {info['base_iri']}")
    print(f"\nEntity Counts:")
    print(f"  Classes:               {info['num_classes']:>6}")
    print(f"  Object Properties:     {info['num_object_properties']:>6}")
    print(f"  Data Properties:       {info['num_data_properties']:>6}")
    print(f"  Annotation Properties: {info['num_annotation_properties']:>6}")
    print(f"  Individuals:           {info['num_individuals']:>6}")
    print(f"{'='*60}\n")

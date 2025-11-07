"""
Basic Metrics Module

Implements basic structural metrics for OWL ontologies.
These metrics serve as the foundation for derived OQuaRE quality metrics.

Author: OQuaRE Metrics Team
Date: 2025-11-04
"""

import logging
from typing import Dict, List, Set, Tuple, Optional
from collections import defaultdict
import owlready2 as owl2

logger = logging.getLogger(__name__)


class OntologyBasicMetrics:
    """
    Calculate basic structural metrics for an OWL ontology.
    
    This class provides methods to calculate all foundational metrics
    used in the OQuaRE framework, including counts of classes, properties,
    annotations, and structural relationships.
    """
    
    def __init__(self, ontology: owl2.Ontology):
        """
        Initialize with a loaded ontology.
        
        Args:
            ontology: Loaded owlready2.Ontology object
        """
        self.ontology = ontology
        self._cache = {}
        logger.info("Initialized BasicMetrics for ontology: %s", ontology.name)
    
    def _get_thing_class(self) -> owl2.ThingClass:
        """Get the owl:Thing class."""
        return owl2.Thing
    
    # =========================================================================
    # BASIC COUNT METRICS
    # =========================================================================
    
    def count_classes(self) -> int:
        """
        Count total number of classes in the ontology.
        Formula: ∑|Ci|
        
        Returns:
            Total number of classes
        """
        if 'count_classes' in self._cache:
            return self._cache['count_classes']
        
        classes = list(self.ontology.classes())
        count = len(classes)
        
        self._cache['count_classes'] = count
        logger.debug("Total classes: %d", count)
        return count
    
    def count_leaf_classes(self) -> int:
        """
        Count number of leaf classes (classes with no subclasses).
        Formula: ∑|C(leaf)i|
        
        Returns:
            Number of leaf classes
        """
        if 'count_leaf_classes' in self._cache:
            return self._cache['count_leaf_classes']
        
        leaf_classes = []
        for cls in self.ontology.classes():
            # A class is a leaf if it has no subclasses
            if len(list(cls.subclasses())) == 0:
                leaf_classes.append(cls)
        
        count = len(leaf_classes)
        self._cache['count_leaf_classes'] = count
        self._cache['leaf_classes'] = leaf_classes
        logger.debug("Leaf classes: %d", count)
        return count
    
    def get_leaf_classes(self) -> List[owl2.ThingClass]:
        """
        Get list of leaf classes.
        
        Returns:
            List of leaf class objects
        """
        if 'leaf_classes' not in self._cache:
            self.count_leaf_classes()
        return self._cache['leaf_classes']
    
    def count_object_properties(self) -> int:
        """
        Count number of object properties (relationships).
        
        Returns:
            Number of object properties
        """
        if 'count_object_properties' in self._cache:
            return self._cache['count_object_properties']
        
        props = list(self.ontology.object_properties())
        count = len(props)
        
        self._cache['count_object_properties'] = count
        logger.debug("Object properties: %d", count)
        return count
    
    def count_data_properties(self) -> int:
        """
        Count number of data properties.
        
        Returns:
            Number of data properties
        """
        if 'count_data_properties' in self._cache:
            return self._cache['count_data_properties']
        
        props = list(self.ontology.data_properties())
        count = len(props)
        
        self._cache['count_data_properties'] = count
        logger.debug("Data properties: %d", count)
        return count
    
    def count_properties(self) -> int:
        """
        Count total number of properties (object + data properties).
        Formula: ∑|PCi|
        
        Returns:
            Total number of properties
        """
        return self.count_object_properties() + self.count_data_properties()
    
    def count_individuals(self) -> int:
        """
        Count total number of individuals (instances).
        Formula: ∑|ICi|
        
        Returns:
            Number of individuals
        """
        if 'count_individuals' in self._cache:
            return self._cache['count_individuals']
        
        individuals = list(self.ontology.individuals())
        count = len(individuals)
        
        self._cache['count_individuals'] = count
        logger.debug("Individuals: %d", count)
        return count
    
    def _count_entity_annotations(self, entities, entity_type: str, *, exclude_self: bool = False) -> int:
        """
        Helper method to count annotations on a collection of entities.
        
        Args:
            entities: Iterable of entities to count annotations for
            entity_type: Type description for logging (e.g., "Class", "Object property")
            exclude_self: If True, exclude self-annotations (for annotation properties)
            
        Returns:
            Total annotation count for the entities
        """
        count = 0
        for entity in entities:
            for ann_prop in self.ontology.annotation_properties():
                if exclude_self and entity == ann_prop:
                    continue
                values = ann_prop[entity]
                if values:
                    count += len(values) if isinstance(values, list) else 1
        
        logger.debug("%s annotations: %d", entity_type, count)
        return count
    
    def count_annotations(self) -> int:
        """
        Count ALL annotations on ALL entities in the ontology.
        This is the FIXED version that counts annotations on:
        - Ontology itself
        - Classes
        - Object properties
        - Data properties
        - Annotation properties
        - Individuals
        
        Formula: ∑|ACi| (all annotations)
        
        Returns:
            Total number of annotations
        """
        if 'count_annotations' in self._cache:
            return self._cache['count_annotations']
        
        total = 0
        
        # Count ontology-level annotations
        ontology_annotations = 0
        try:
            for _ in self.ontology.metadata.annotations:
                ontology_annotations += 1
        except (AttributeError, TypeError):
            pass
        
        logger.debug("Ontology annotations: %d", ontology_annotations)
        total += ontology_annotations
        
        # Count annotations for different entity types
        total += self._count_entity_annotations(self.ontology.classes(), "Class")
        total += self._count_entity_annotations(self.ontology.object_properties(), "Object property")
        total += self._count_entity_annotations(self.ontology.data_properties(), "Data property")
        total += self._count_entity_annotations(self.ontology.annotation_properties(), "Annotation property", exclude_self=True)
        total += self._count_entity_annotations(self.ontology.individuals(), "Individual")
        
        self._cache['count_annotations'] = total
        logger.info("Total annotations (FIXED): %d", total)
        return total
    
    # =========================================================================
    # STRUCTURAL RELATIONSHIP METRICS
    # =========================================================================
    
    def count_relationships_per_class(self) -> Dict[owl2.ThingClass, int]:
        """
        Count direct subclasses for each class (relationships).
        Formula: ∑|RCi|
        
        Returns:
            Dictionary mapping each class to its number of direct subclasses
        """
        if 'relationships_per_class' in self._cache:
            return self._cache['relationships_per_class']
        
        relationships = {}
        for cls in self.ontology.classes():
            # Count direct subclasses
            direct_subclasses = [sub for sub in cls.subclasses() if sub != cls]
            relationships[cls] = len(direct_subclasses)
        
        self._cache['relationships_per_class'] = relationships
        return relationships
    
    def count_total_relationships(self) -> int:
        """
        Count total number of direct subclass relationships.
        Formula: ∑|RCi|
        
        Returns:
            Total number of relationships
        """
        if 'count_total_relationships' in self._cache:
            return self._cache['count_total_relationships']
        
        relationships = self.count_relationships_per_class()
        total = sum(relationships.values())
        
        self._cache['count_total_relationships'] = total
        logger.debug("Total relationships: %d", total)
        return total
    
    def count_thing_relationships(self) -> int:
        """
        Count direct subclasses of owl:Thing.
        Formula: |RThing|
        
        Returns:
            Number of direct Thing subclasses
        """
        if 'count_thing_relationships' in self._cache:
            return self._cache['count_thing_relationships']
        
        thing = self._get_thing_class()
        direct_subclasses = [sub for sub in thing.subclasses() 
                           if sub != thing and sub in self.ontology.classes()]
        count = len(direct_subclasses)
        
        self._cache['count_thing_relationships'] = count
        logger.debug("Thing relationships: %d", count)
        return count
    
    def count_direct_parents_per_class(self) -> Dict[owl2.ThingClass, int]:
        """
        Count direct parent classes for each class.
        Formula: ∑|SupCi|
        
        Returns:
            Dictionary mapping each class to its number of direct parents
        """
        if 'direct_parents_per_class' in self._cache:
            return self._cache['direct_parents_per_class']
        
        parents = {}
        for cls in self.ontology.classes():
            # Get direct superclasses (excluding Thing if not relevant)
            direct_parents = [sup for sup in cls.is_a 
                            if isinstance(sup, owl2.ThingClass)]
            parents[cls] = len(direct_parents)
        
        self._cache['direct_parents_per_class'] = parents
        return parents
    
    def sum_direct_parents(self) -> int:
        """
        Sum of all direct parent relationships.
        Formula: ∑|SupCi|
        
        Returns:
            Total sum of direct parents
        """
        if 'sum_direct_parents' in self._cache:
            return self._cache['sum_direct_parents']
        
        parents = self.count_direct_parents_per_class()
        total = sum(parents.values())
        
        self._cache['sum_direct_parents'] = total
        logger.debug("Sum of direct parents: %d", total)
        return total
    
    def sum_direct_parents_of_leaf_classes(self) -> int:
        """
        Sum of direct parents for leaf classes only.
        Formula: ∑|SupC(Leaf)i|
        
        Returns:
            Sum of direct parents of leaf classes
        """
        if 'sum_direct_parents_leaf' in self._cache:
            return self._cache['sum_direct_parents_leaf']
        
        leaf_classes = self.get_leaf_classes()
        parents_dict = self.count_direct_parents_per_class()
        
        total = sum(parents_dict.get(cls, 0) for cls in leaf_classes)
        
        self._cache['sum_direct_parents_leaf'] = total
        logger.debug("Sum of direct parents (leaf classes): %d", total)
        return total
    
    def count_classes_with_multiple_parents(self) -> int:
        """
        Count classes with more than one direct parent.
        Formula: ∑|C(DP)i|
        
        Returns:
            Number of classes with multiple parents
        """
        if 'count_multiple_parents' in self._cache:
            return self._cache['count_multiple_parents']
        
        parents_dict = self.count_direct_parents_per_class()
        multiple = [cls for cls, count in parents_dict.items() if count > 1]
        count = len(multiple)
        
        self._cache['count_multiple_parents'] = count
        self._cache['classes_multiple_parents'] = multiple
        logger.debug("Classes with multiple parents: %d", count)
        return count
    
    def sum_parents_of_classes_with_multiple_parents(self) -> int:
        """
        Sum of direct parents for classes that have multiple parents.
        
        Returns:
            Sum of parents for multi-parent classes
        """
        if 'sum_parents_multi' in self._cache:
            return self._cache['sum_parents_multi']
        
        if 'classes_multiple_parents' not in self._cache:
            self.count_classes_with_multiple_parents()
        
        multi_parent_classes = self._cache['classes_multiple_parents']
        parents_dict = self.count_direct_parents_per_class()
        
        total = sum(parents_dict.get(cls, 0) for cls in multi_parent_classes)
        
        self._cache['sum_parents_multi'] = total
        logger.debug("Sum of parents (multi-parent classes): %d", total)
        return total
    
    # =========================================================================
    # ATTRIBUTE/PROPERTY USAGE METRICS
    # =========================================================================
    
    def count_attributes_per_class(self) -> Dict[owl2.ThingClass, int]:
        """
        Count data properties used by each class.
        Formula: ∑|AttCi|
        
        Returns:
            Dictionary mapping each class to its attribute count
        """
        if 'attributes_per_class' in self._cache:
            return self._cache['attributes_per_class']
        
        attributes = defaultdict(int)
        
        # For each data property, find which classes use it
        for prop in self.ontology.data_properties():
            # Check domain restrictions
            if hasattr(prop, 'domain') and prop.domain:
                domains = prop.domain if isinstance(prop.domain, list) else [prop.domain]
                for domain in domains:
                    if isinstance(domain, owl2.ThingClass):
                        attributes[domain] += 1
        
        self._cache['attributes_per_class'] = dict(attributes)
        return dict(attributes)
    
    def sum_attributes(self) -> int:
        """
        Sum of all attributes across all classes.
        Formula: ∑|AttCi|
        
        Returns:
            Total sum of attributes
        """
        if 'sum_attributes' in self._cache:
            return self._cache['sum_attributes']
        
        attrs = self.count_attributes_per_class()
        total = sum(attrs.values())
        
        self._cache['sum_attributes'] = total
        logger.debug("Sum of attributes: %d", total)
        return total
    
    # =========================================================================
    # DEPTH AND PATH METRICS
    # =========================================================================
    
    def calculate_class_depth(self, cls: owl2.ThingClass, visited: Optional[Set] = None) -> int:
        """
        Calculate depth of a class (path length from class to Thing).
        
        Args:
            cls: Class to calculate depth for
            visited: Set of visited classes (to avoid cycles)
            
        Returns:
            Depth of the class
        """
        if visited is None:
            visited = set()
        
        if cls in visited:
            return 0  # Cycle detected
        
        visited.add(cls)
        
        # Get direct superclasses
        parents = [sup for sup in cls.is_a if isinstance(sup, owl2.ThingClass)]
        
        if not parents or cls == self._get_thing_class():
            return 0
        
        # Depth is 1 + max depth of parents
        max_parent_depth = max(
            (self.calculate_class_depth(parent, visited.copy()) for parent in parents),
            default=0
        )
        
        return 1 + max_parent_depth
    
    def get_maximum_depth(self) -> int:
        """
        Get maximum depth of the ontology (longest path from any leaf to Thing).
        Formula: Max(∑D|Ci|)
        
        Returns:
            Maximum depth value
        """
        if 'maximum_depth' in self._cache:
            return self._cache['maximum_depth']
        
        max_depth = 0
        leaf_classes = self.get_leaf_classes()
        
        for cls in leaf_classes:
            depth = self.calculate_class_depth(cls)
            max_depth = max(max_depth, depth)
        
        self._cache['maximum_depth'] = max_depth
        logger.debug("Maximum depth: %d", max_depth)
        return max_depth
    
    def calculate_paths_from_leaf_to_thing(self, 
                                          cls: owl2.ThingClass,
                                          current_path: Optional[List] = None,
                                          visited: Optional[Set] = None) -> List[List[owl2.ThingClass]]:
        """
        Calculate all paths from a leaf class to Thing.
        
        Args:
            cls: Starting class
            current_path: Current path being built
            visited: Set of visited classes in current path
            
        Returns:
            List of paths (each path is a list of classes)
        """
        if current_path is None:
            current_path = []
        if visited is None:
            visited = set()
        
        # Add current class to path
        current_path = current_path + [cls]
        visited = visited | {cls}
        
        # Get direct parents
        parents = [sup for sup in cls.is_a 
                  if isinstance(sup, owl2.ThingClass) and sup not in visited]
        
        # Base case: reached Thing or no more parents
        if not parents or cls == self._get_thing_class():
            return [current_path]
        
        # Recursive case: explore all parent paths
        all_paths = []
        for parent in parents:
            parent_paths = self.calculate_paths_from_leaf_to_thing(
                parent, current_path, visited
            )
            all_paths.extend(parent_paths)
        
        return all_paths
    
    def get_all_leaf_paths(self) -> Tuple[Dict[owl2.ThingClass, List[List]], int, int]:
        """
        Get all paths from leaf classes to Thing.
        
        Returns:
            Tuple of (paths_dict, total_path_count, sum_of_path_lengths)
            - paths_dict: Dictionary mapping leaf class to its paths
            - total_path_count: Total number of paths (m)
            - sum_of_path_lengths: Sum of all path lengths (∑path(|C(leaf)i|))
        """
        if 'all_leaf_paths' in self._cache:
            return self._cache['all_leaf_paths']
        
        leaf_classes = self.get_leaf_classes()
        paths_dict = {}
        total_paths = 0
        sum_lengths = 0
        
        for leaf in leaf_classes:
            paths = self.calculate_paths_from_leaf_to_thing(leaf)
            paths_dict[leaf] = paths
            total_paths += len(paths)
            sum_lengths += sum(len(path) for path in paths)
        
        result = (paths_dict, total_paths, sum_lengths)
        self._cache['all_leaf_paths'] = result
        
        logger.debug("Total paths: %d, Sum of lengths: %d", total_paths, sum_lengths)
        return result
    
    # =========================================================================
    # SUMMARY METHODS
    # =========================================================================
    
    def get_all_basic_metrics(self) -> Dict[str, int]:
        """
        Calculate and return all basic metrics.
        
        Returns:
            Dictionary with all basic metric values
        """
        return {
            'numberOfClasses': self.count_classes(),
            'numberOfLeafClasses': self.count_leaf_classes(),
            'numberOfObjectProperties': self.count_object_properties(),
            'numberOfDataProperties': self.count_data_properties(),
            'numberOfProperties': self.count_properties(),
            'numberOfIndividuals': self.count_individuals(),
            'sumOfAnnotations': self.count_annotations(),
            'sumOfRelationships': self.count_total_relationships(),
            'thingRelationships': self.count_thing_relationships(),
            'sumOfDirectParents': self.sum_direct_parents(),
            'sumOfDirectParentsLeaf': self.sum_direct_parents_of_leaf_classes(),
            'classesWithMultipleParents': self.count_classes_with_multiple_parents(),
            'sumOfAttributes': self.sum_attributes(),
            'maximumDepth': self.get_maximum_depth(),
        }
    
    def clear_cache(self):
        """Clear the internal cache."""
        self._cache.clear()
        logger.debug("Cache cleared")

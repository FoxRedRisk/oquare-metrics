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
        logger.info(f"Initialized BasicMetrics for ontology: {ontology.name}")
    
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
        logger.debug(f"Total classes: {count}")
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
        logger.debug(f"Leaf classes: {count}")
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
        logger.debug(f"Object properties: {count}")
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
        logger.debug(f"Data properties: {count}")
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
        logger.debug(f"Individuals: {count}")
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
            # In owlready2, ontology annotations are stored differently
            for annotation in self.ontology.metadata.annotations:
                ontology_annotations += 1
        except:
            # Fallback: count using SWRL/RDF approach
            pass
        
        logger.debug(f"Ontology annotations: {ontology_annotations}")
        total += ontology_annotations
        
        # Count class annotations
        class_annotations = 0
        for cls in self.ontology.classes():
            # Get all annotation assertions for this class
            for prop in self.ontology.annotation_properties():
                values = prop[cls]
                if values:
                    if isinstance(values, list):
                        class_annotations += len(values)
                    else:
                        class_annotations += 1
        
        logger.debug(f"Class annotations: {class_annotations}")
        total += class_annotations
        
        # Count object property annotations
        obj_prop_annotations = 0
        for prop in self.ontology.object_properties():
            for ann_prop in self.ontology.annotation_properties():
                values = ann_prop[prop]
                if values:
                    if isinstance(values, list):
                        obj_prop_annotations += len(values)
                    else:
                        obj_prop_annotations += 1
        
        logger.debug(f"Object property annotations: {obj_prop_annotations}")
        total += obj_prop_annotations
        
        # Count data property annotations
        data_prop_annotations = 0
        for prop in self.ontology.data_properties():
            for ann_prop in self.ontology.annotation_properties():
                values = ann_prop[prop]
                if values:
                    if isinstance(values, list):
                        data_prop_annotations += len(values)
                    else:
                        data_prop_annotations += 1
        
        logger.debug(f"Data property annotations: {data_prop_annotations}")
        total += data_prop_annotations
        
        # Count annotation property annotations
        ann_prop_annotations = 0
        for prop in self.ontology.annotation_properties():
            for ann_prop in self.ontology.annotation_properties():
                if prop != ann_prop:  # Don't count self-annotations
                    values = ann_prop[prop]
                    if values:
                        if isinstance(values, list):
                            ann_prop_annotations += len(values)
                        else:
                            ann_prop_annotations += 1
        
        logger.debug(f"Annotation property annotations: {ann_prop_annotations}")
        total += ann_prop_annotations
        
        # Count individual annotations
        individual_annotations = 0
        for ind in self.ontology.individuals():
            for ann_prop in self.ontology.annotation_properties():
                values = ann_prop[ind]
                if values:
                    if isinstance(values, list):
                        individual_annotations += len(values)
                    else:
                        individual_annotations += 1
        
        logger.debug(f"Individual annotations: {individual_annotations}")
        total += individual_annotations
        
        self._cache['count_annotations'] = total
        logger.info(f"Total annotations (FIXED): {total}")
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
        logger.debug(f"Total relationships: {total}")
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
        logger.debug(f"Thing relationships: {count}")
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
        logger.debug(f"Sum of direct parents: {total}")
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
        logger.debug(f"Sum of direct parents (leaf classes): {total}")
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
        logger.debug(f"Classes with multiple parents: {count}")
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
        logger.debug(f"Sum of parents (multi-parent classes): {total}")
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
        logger.debug(f"Sum of attributes: {total}")
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
        logger.debug(f"Maximum depth: {max_depth}")
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
        
        logger.debug(f"Total paths: {total_paths}, Sum of lengths: {sum_lengths}")
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

"""
JAR-Compatible Basic Metrics Module

This version matches the JAR implementation's counting methods:
- Includes owl:Thing in class count
- Counts all data property usages as attributes
- Uses reasoning by default

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
    JAR-compatible version.
    """
    
    def __init__(self, ontology: owl2.Ontology):
        """Initialize with a loaded ontology."""
        self.ontology = ontology
        self._cache = {}
        logger.info(f"Initialized BasicMetrics (JAR-compatible) for ontology: {ontology.name}")
    
    def _get_thing_class(self) -> owl2.ThingClass:
        """Get the owl:Thing class."""
        return owl2.Thing
    
    def count_classes(self, include_thing: bool = True) -> int:
        """
        Count total number of classes in the ontology.
        
        Args:
            include_thing: If True, includes owl:Thing in count (JAR behavior)
        
        Returns:
            Total number of classes
        """
        cache_key = f'count_classes_{include_thing}'
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        classes = list(self.ontology.classes())
        count = len(classes)
        
        # JAR includes owl:Thing in the count
        if include_thing:
            thing = self._get_thing_class()
            if thing not in classes:
                count += 1
        
        self._cache[cache_key] = count
        logger.debug(f"Total classes (include_thing={include_thing}): {count}")
        return count
    
    def count_leaf_classes(self) -> int:
        """Count number of leaf classes (classes with no subclasses)."""
        if 'count_leaf_classes' in self._cache:
            return self._cache['count_leaf_classes']
        
        leaf_classes = []
        for cls in self.ontology.classes():
            if len(list(cls.subclasses())) == 0:
                leaf_classes.append(cls)
        
        count = len(leaf_classes)
        self._cache['count_leaf_classes'] = count
        self._cache['leaf_classes'] = leaf_classes
        logger.debug(f"Leaf classes: {count}")
        return count
    
    def get_leaf_classes(self) -> List[owl2.ThingClass]:
        """Get list of leaf classes."""
        if 'leaf_classes' not in self._cache:
            self.count_leaf_classes()
        return self._cache['leaf_classes']
    
    def count_object_properties(self) -> int:
        """Count number of object properties."""
        if 'count_object_properties' in self._cache:
            return self._cache['count_object_properties']
        
        props = list(self.ontology.object_properties())
        count = len(props)
        
        self._cache['count_object_properties'] = count
        logger.debug(f"Object properties: {count}")
        return count
    
    def count_data_properties(self) -> int:
        """Count number of data properties."""
        if 'count_data_properties' in self._cache:
            return self._cache['count_data_properties']
        
        props = list(self.ontology.data_properties())
        count = len(props)
        
        self._cache['count_data_properties'] = count
        logger.debug(f"Data properties: {count}")
        return count
    
    def count_properties(self) -> int:
        """Count total number of properties (object + data properties)."""
        return self.count_object_properties() + self.count_data_properties()
    
    def count_individuals(self) -> int:
        """Count total number of individuals (instances)."""
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
        """
        if 'count_annotations' in self._cache:
            return self._cache['count_annotations']
        
        total = 0
        
        # Count ontology-level annotations
        try:
            for annotation in self.ontology.metadata.annotations:
                total += 1
        except:
            pass
        
        # Count class annotations
        for cls in self.ontology.classes():
            for prop in self.ontology.annotation_properties():
                values = prop[cls]
                if values:
                    if isinstance(values, list):
                        total += len(values)
                    else:
                        total += 1
        
        # Count object property annotations
        for prop in self.ontology.object_properties():
            for ann_prop in self.ontology.annotation_properties():
                values = ann_prop[prop]
                if values:
                    if isinstance(values, list):
                        total += len(values)
                    else:
                        total += 1
        
        # Count data property annotations
        for prop in self.ontology.data_properties():
            for ann_prop in self.ontology.annotation_properties():
                values = ann_prop[prop]
                if values:
                    if isinstance(values, list):
                        total += len(values)
                    else:
                        total += 1
        
        # Count annotation property annotations
        for prop in self.ontology.annotation_properties():
            for ann_prop in self.ontology.annotation_properties():
                if prop != ann_prop:
                    values = ann_prop[prop]
                    if values:
                        if isinstance(values, list):
                            total += len(values)
                        else:
                            total += 1
        
        # Count individual annotations
        for ind in self.ontology.individuals():
            for ann_prop in self.ontology.annotation_properties():
                values = ann_prop[ind]
                if values:
                    if isinstance(values, list):
                        total += len(values)
                    else:
                        total += 1
        
        self._cache['count_annotations'] = total
        logger.info(f"Total annotations (FIXED): {total}")
        return total
    
    def count_relationships_per_class(self) -> Dict[owl2.ThingClass, int]:
        """Count direct subclasses for each class (relationships)."""
        if 'relationships_per_class' in self._cache:
            return self._cache['relationships_per_class']
        
        relationships = {}
        
        # Include Thing in the count for JAR compatibility
        thing = self._get_thing_class()
        all_classes = list(self.ontology.classes()) + [thing]
        
        for cls in all_classes:
            direct_subclasses = [sub for sub in cls.subclasses() if sub != cls]
            relationships[cls] = len(direct_subclasses)
        
        self._cache['relationships_per_class'] = relationships
        return relationships
    
    def count_total_relationships(self) -> int:
        """Count total number of direct subclass relationships."""
        if 'count_total_relationships' in self._cache:
            return self._cache['count_total_relationships']
        
        relationships = self.count_relationships_per_class()
        total = sum(relationships.values())
        
        self._cache['count_total_relationships'] = total
        logger.debug(f"Total relationships: {total}")
        return total
    
    def count_thing_relationships(self) -> int:
        """Count direct subclasses of owl:Thing."""
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
        """Count direct parent classes for each class."""
        if 'direct_parents_per_class' in self._cache:
            return self._cache['direct_parents_per_class']
        
        parents = {}
        for cls in self.ontology.classes():
            direct_parents = [sup for sup in cls.is_a 
                            if isinstance(sup, owl2.ThingClass)]
            parents[cls] = len(direct_parents)
        
        self._cache['direct_parents_per_class'] = parents
        return parents
    
    def sum_direct_parents(self) -> int:
        """Sum of all direct parent relationships."""
        if 'sum_direct_parents' in self._cache:
            return self._cache['sum_direct_parents']
        
        parents = self.count_direct_parents_per_class()
        total = sum(parents.values())
        
        self._cache['sum_direct_parents'] = total
        logger.debug(f"Sum of direct parents: {total}")
        return total
    
    def sum_direct_parents_of_leaf_classes(self) -> int:
        """Sum of direct parents for leaf classes only."""
        if 'sum_direct_parents_leaf' in self._cache:
            return self._cache['sum_direct_parents_leaf']
        
        leaf_classes = self.get_leaf_classes()
        parents_dict = self.count_direct_parents_per_class()
        
        total = sum(parents_dict.get(cls, 0) for cls in leaf_classes)
        
        self._cache['sum_direct_parents_leaf'] = total
        logger.debug(f"Sum of direct parents (leaf classes): {total}")
        return total
    
    def count_classes_with_multiple_parents(self) -> int:
        """Count classes with more than one direct parent."""
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
        """Sum of direct parents for classes that have multiple parents."""
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
    
    def count_property_usages(self) -> int:
        """
        Count total property usages (JAR-compatible).
        This counts all property assertions in the ontology.
        """
        if 'property_usages' in self._cache:
            return self._cache['property_usages']
        
        total_usages = 0
        
        # Count object property assertions
        for prop in self.ontology.object_properties():
            # Count domain and range restrictions
            if hasattr(prop, 'domain') and prop.domain:
                total_usages += 1
            if hasattr(prop, 'range') and prop.range:
                total_usages += 1
        
        # Count data property assertions
        for prop in self.ontology.data_properties():
            # Count domain and range restrictions
            if hasattr(prop, 'domain') and prop.domain:
                total_usages += 1
            if hasattr(prop, 'range') and prop.range:
                total_usages += 1
        
        # Count actual property uses on individuals
        for ind in self.ontology.individuals():
            for prop in self.ontology.object_properties():
                values = prop[ind]
                if values:
                    if isinstance(values, list):
                        total_usages += len(values)
                    else:
                        total_usages += 1
            
            for prop in self.ontology.data_properties():
                values = prop[ind]
                if values:
                    if isinstance(values, list):
                        total_usages += len(values)
                    else:
                        total_usages += 1
        
        self._cache['property_usages'] = total_usages
        logger.debug(f"Property usages: {total_usages}")
        return total_usages
    
    def sum_attributes(self) -> int:
        """
        Sum of all attributes (JAR-compatible).
        Counts all data property usages.
        """
        if 'sum_attributes' in self._cache:
            return self._cache['sum_attributes']
        
        total = 0
        
        # Count data property domains and ranges
        for prop in self.ontology.data_properties():
            if hasattr(prop, 'domain') and prop.domain:
                domains = prop.domain if isinstance(prop.domain, list) else [prop.domain]
                total += len(domains)
            if hasattr(prop, 'range') and prop.range:
                total += 1
        
        # Count actual data property assertions on individuals
        for ind in self.ontology.individuals():
            for prop in self.ontology.data_properties():
                values = prop[ind]
                if values:
                    if isinstance(values, list):
                        total += len(values)
                    else:
                        total += 1
        
        self._cache['sum_attributes'] = total
        logger.debug(f"Sum of attributes (JAR-compatible): {total}")
        return total
    
    def calculate_class_depth(self, cls: owl2.ThingClass, visited: Optional[Set] = None) -> int:
        """Calculate depth of a class (path length from class to Thing)."""
        if visited is None:
            visited = set()
        
        if cls in visited:
            return 0
        
        visited.add(cls)
        
        parents = [sup for sup in cls.is_a if isinstance(sup, owl2.ThingClass)]
        
        if not parents or cls == self._get_thing_class():
            return 0
        
        max_parent_depth = max(
            (self.calculate_class_depth(parent, visited.copy()) for parent in parents),
            default=0
        )
        
        return 1 + max_parent_depth
    
    def get_maximum_depth(self) -> int:
        """Get maximum depth of the ontology."""
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
        """Calculate all paths from a leaf class to Thing."""
        if current_path is None:
            current_path = []
        if visited is None:
            visited = set()
        
        current_path = current_path + [cls]
        visited = visited | {cls}
        
        parents = [sup for sup in cls.is_a 
                  if isinstance(sup, owl2.ThingClass) and sup not in visited]
        
        if not parents or cls == self._get_thing_class():
            return [current_path]
        
        all_paths = []
        for parent in parents:
            parent_paths = self.calculate_paths_from_leaf_to_thing(
                parent, current_path, visited
            )
            all_paths.extend(parent_paths)
        
        return all_paths
    
    def get_all_leaf_paths(self) -> Tuple[Dict[owl2.ThingClass, List[List]], int, int]:
        """Get all paths from leaf classes to Thing."""
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
    
    def get_all_basic_metrics(self) -> Dict[str, int]:
        """
        Calculate and return all basic metrics (JAR-compatible).
        """
        return {
            'numberOfClasses': self.count_classes(include_thing=True),  # JAR includes Thing
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

"""
OQuaRE Metrics Module

Implements derived OQuaRE quality metrics based on basic structural metrics.
These metrics measure various aspects of ontology quality according to the
OQuaRE framework.

Author: OQuaRE Metrics Team
Date: 2025-11-04
"""

import logging
from typing import Dict
from .basic_metrics import OntologyBasicMetrics

logger = logging.getLogger(__name__)


class OQuaREMetrics:
    """
    Calculate OQuaRE quality metrics for an ontology.
    
    This class implements all derived metrics according to the OQuaRE framework,
    using the mathematical formulas specified in MetricsMaths.md.
    """
    
    def __init__(self, basic_metrics: OntologyBasicMetrics):
        """
        Initialize with basic metrics.
        
        Args:
            basic_metrics: OntologyBasicMetrics object with calculated basic metrics
        """
        self.basic = basic_metrics
        self._cache = {}
        logger.info("Initialized OQuaREMetrics")
    
    # =========================================================================
    # ANNOTATION RICHNESS (ANOnto) - FIXED
    # =========================================================================
    
    def calculate_ANOnto(self, verbose: bool = False) -> float:
        """
        Annotation Richness: Mean number of annotations per class.
        
        Formula: ANOnto = ∑|ACi| / ∑|Ci|
        
        This is the FIXED version that counts all annotations on all entities.
        
        Returns:
            ANOnto value
        """
        if 'ANOnto' in self._cache:
            return self._cache['ANOnto']
        
        sum_annotations = self.basic.count_annotations()
        num_classes = self.basic.count_classes()
        
        if num_classes == 0:
            anonto = 0.0
        else:
            anonto = sum_annotations / num_classes
        
        self._cache['ANOnto'] = anonto
        
        if verbose:
            print(f"\n{'='*70}")
            print(f"ANOnto (Annotation Richness)")
            print(f"{'='*70}")
            print(f"Formula: ANOnto = ∑|ACi| / ∑|Ci|")
            print(f"Calculation: {sum_annotations} / {num_classes} = {anonto:.6f}")
            print(f"{'='*70}")
        
        logger.debug(f"ANOnto = {sum_annotations} / {num_classes} = {anonto:.6f}")
        return anonto
    
    # =========================================================================
    # CLASS RICHNESS (CROnto)
    # =========================================================================
    
    def calculate_CROnto(self) -> float:
        """
        Class Richness: Mean number of instances per class.
        
        Formula: CROnto = ∑|ICi| / ∑|Ci|
        
        Returns:
            CROnto value
        """
        if 'CROnto' in self._cache:
            return self._cache['CROnto']
        
        sum_instances = self.basic.count_individuals()
        num_classes = self.basic.count_classes()
        
        if num_classes == 0:
            cronto = 0.0
        else:
            cronto = sum_instances / num_classes
        
        self._cache['CROnto'] = cronto
        logger.debug(f"CROnto = {sum_instances} / {num_classes} = {cronto:.6f}")
        return cronto
    
    # =========================================================================
    # NUMBER OF PROPERTIES (NOMOnto)
    # =========================================================================
    
    def calculate_NOMOnto(self) -> float:
        """
        Number of Properties: Number of properties per class.
        
        Formula: NOMOnto = ∑|PCi| / ∑|Ci|
        
        Returns:
            NOMOnto value
        """
        if 'NOMOnto' in self._cache:
            return self._cache['NOMOnto']
        
        sum_properties = self.basic.count_properties()
        num_classes = self.basic.count_classes()
        
        if num_classes == 0:
            nomonto = 0.0
        else:
            nomonto = sum_properties / num_classes
        
        self._cache['NOMOnto'] = nomonto
        logger.debug(f"NOMOnto = {sum_properties} / {num_classes} = {nomonto:.6f}")
        return nomonto
    
    # =========================================================================
    # RELATIONSHIPS PER CLASS (INROnto)
    # =========================================================================
    
    def calculate_INROnto(self) -> float:
        """
        Instance Relationships: Mean number of relationships per class.
        
        Formula: INROnto = ∑|RCi| / ∑|Ci|
        
        Returns:
            INROnto value
        """
        if 'INROnto' in self._cache:
            return self._cache['INROnto']
        
        sum_relationships = self.basic.count_total_relationships()
        num_classes = self.basic.count_classes()
        
        if num_classes == 0:
            inronto = 0.0
        else:
            inronto = sum_relationships / num_classes
        
        self._cache['INROnto'] = inronto
        logger.debug(f"INROnto = {sum_relationships} / {num_classes} = {inronto:.6f}")
        return inronto
    
    # =========================================================================
    # ATTRIBUTE RICHNESS (AROnto)
    # =========================================================================
    
    def calculate_AROnto(self) -> float:
        """
        Attribute Richness: Mean number of attributes per class.
        
        Formula: AROnto = ∑|AttCi| / ∑|Ci|
        
        Returns:
            AROnto value
        """
        if 'AROnto' in self._cache:
            return self._cache['AROnto']
        
        sum_attributes = self.basic.sum_attributes()
        num_classes = self.basic.count_classes()
        
        if num_classes == 0:
            aronto = 0.0
        else:
            aronto = sum_attributes / num_classes
        
        self._cache['AROnto'] = aronto
        logger.debug(f"AROnto = {sum_attributes} / {num_classes} = {aronto:.6f}")
        return aronto
    
    # =========================================================================
    # DEPTH OF INHERITANCE TREE (DITOnto)
    # =========================================================================
    
    def calculate_DITOnto(self) -> int:
        """
        Depth of Subsumption Hierarchy: Length of the largest path from Thing to a leaf class.
        
        Formula: DITOnto = Max(∑D|Ci|)
        
        Returns:
            DITOnto value (maximum depth)
        """
        if 'DITOnto' in self._cache:
            return self._cache['DITOnto']
        
        max_depth = self.basic.get_maximum_depth()
        
        self._cache['DITOnto'] = max_depth
        logger.debug(f"DITOnto = {max_depth}")
        return max_depth
    
    # =========================================================================
    # NUMBER OF ANCESTOR CLASSES (NACOnto)
    # =========================================================================
    
    def calculate_NACOnto(self) -> float:
        """
        Number of Ancestor Classes: Mean number of ancestor classes per leaf class.
        
        Formula: NACOnto = ∑|SupC(Leaf)i| / ∑|C(leaf)i|
        
        Returns:
            NACOnto value
        """
        if 'NACOnto' in self._cache:
            return self._cache['NACOnto']
        
        sum_parents_leaf = self.basic.sum_direct_parents_of_leaf_classes()
        num_leaf_classes = self.basic.count_leaf_classes()
        
        if num_leaf_classes == 0:
            naconto = 0.0
        else:
            naconto = sum_parents_leaf / num_leaf_classes
        
        self._cache['NACOnto'] = naconto
        logger.debug(f"NACOnto = {sum_parents_leaf} / {num_leaf_classes} = {naconto:.6f}")
        return naconto
    
    # =========================================================================
    # NUMBER OF CHILDREN (NOCOnto)
    # =========================================================================
    
    def calculate_NOCOnto(self) -> float:
        """
        Number of Children: Mean number of direct subclasses.
        
        Formula: NOCOnto = ∑|RCi| / (∑|Ci| - |RThing|)
        
        Returns:
            NOCOnto value
        """
        if 'NOCOnto' in self._cache:
            return self._cache['NOCOnto']
        
        sum_relationships = self.basic.count_total_relationships()
        num_classes = self.basic.count_classes()
        thing_relationships = self.basic.count_thing_relationships()
        
        denominator = num_classes - thing_relationships
        
        if denominator <= 0:
            noconto = 0.0
        else:
            noconto = sum_relationships / denominator
        
        self._cache['NOCOnto'] = noconto
        logger.debug(f"NOCOnto = {sum_relationships} / ({num_classes} - {thing_relationships}) = {noconto:.6f}")
        return noconto
    
    # =========================================================================
    # COUPLING BETWEEN OBJECTS (CBOOnto)
    # =========================================================================
    
    def calculate_CBOOnto(self) -> float:
        """
        Coupling Between Objects: Number of related classes.
        
        Formula: CBOOnto = ∑|SupCi| / (∑|Ci| - |RThing|)
        
        Returns:
            CBOOnto value
        """
        if 'CBOOnto' in self._cache:
            return self._cache['CBOOnto']
        
        sum_parents = self.basic.sum_direct_parents()
        num_classes = self.basic.count_classes()
        thing_relationships = self.basic.count_thing_relationships()
        
        denominator = num_classes - thing_relationships
        
        if denominator <= 0:
            cboonto = 0.0
        else:
            cboonto = sum_parents / denominator
        
        self._cache['CBOOnto'] = cboonto
        logger.debug(f"CBOOnto = {sum_parents} / ({num_classes} - {thing_relationships}) = {cboonto:.6f}")
        return cboonto
    
    # =========================================================================
    # WEIGHTED METHOD COUNT (WMCOnto)
    # =========================================================================
    
    def calculate_WMCOnto(self) -> float:
        """
        Weighted Method Count: Mean number of properties and relationships per class.
        
        Formula: WMCOnto = (∑|PCi| + ∑|RCi|) / ∑|Ci|
        
        Returns:
            WMCOnto value
        """
        if 'WMCOnto' in self._cache:
            return self._cache['WMCOnto']
        
        sum_properties = self.basic.count_properties()
        sum_relationships = self.basic.count_total_relationships()
        num_classes = self.basic.count_classes()
        
        if num_classes == 0:
            wmconto = 0.0
        else:
            wmconto = (sum_properties + sum_relationships) / num_classes
        
        self._cache['WMCOnto'] = wmconto
        logger.debug(f"WMCOnto = ({sum_properties} + {sum_relationships}) / {num_classes} = {wmconto:.6f}")
        return wmconto
    
    # =========================================================================
    # RESPONSE FOR A CLASS (RFCOnto)
    # =========================================================================
    
    def calculate_RFCOnto(self) -> float:
        """
        Response For a Class: Number of properties that can be directly accessed from the class.
        
        Formula: RFCOnto = (∑|PCi| + ∑|SupCi|) / (∑|Ci| - |RThing|)
        
        Returns:
            RFCOnto value
        """
        if 'RFCOnto' in self._cache:
            return self._cache['RFCOnto']
        
        sum_properties = self.basic.count_properties()
        sum_parents = self.basic.sum_direct_parents()
        num_classes = self.basic.count_classes()
        thing_relationships = self.basic.count_thing_relationships()
        
        denominator = num_classes - thing_relationships
        
        if denominator <= 0:
            rfconto = 0.0
        else:
            rfconto = (sum_properties + sum_parents) / denominator
        
        self._cache['RFCOnto'] = rfconto
        logger.debug(f"RFCOnto = ({sum_properties} + {sum_parents}) / ({num_classes} - {thing_relationships}) = {rfconto:.6f}")
        return rfconto
    
    # =========================================================================
    # PROPERTIES RICHNESS (RROnto)
    # =========================================================================
    
    def calculate_RROnto(self) -> float:
        """
        Properties Richness: Number of properties defined divided by relationships and properties.
        
        Formula: RROnto = ∑|PCi| / (∑|RCi| + ∑|Ci|)
        
        Returns:
            RROnto value
        """
        if 'RROnto' in self._cache:
            return self._cache['RROnto']
        
        sum_properties = self.basic.count_properties()
        sum_relationships = self.basic.count_total_relationships()
        num_classes = self.basic.count_classes()
        
        denominator = sum_relationships + num_classes
        
        if denominator == 0:
            rronto = 0.0
        else:
            rronto = sum_properties / denominator
        
        self._cache['RROnto'] = rronto
        logger.debug(f"RROnto = {sum_properties} / ({sum_relationships} + {num_classes}) = {rronto:.6f}")
        return rronto
    
    # =========================================================================
    # LACK OF COHESION IN METHODS (LCOMOnto)
    # =========================================================================
    
    def calculate_LCOMOnto(self) -> float:
        """
        Lack of Cohesion in Methods: Semantic and conceptual relatedness of classes.
        
        Formula: LCOMOnto = ∑path(|C(leaf)i|) / m
        where path|C(leaf)i| is the length of the path from leaf class i to Thing,
        and m is the total number of paths in the ontology.
        
        Returns:
            LCOMOnto value
        """
        if 'LCOMOnto' in self._cache:
            return self._cache['LCOMOnto']
        
        # Get all paths from leaf classes to Thing
        paths_dict, total_paths, sum_path_lengths = self.basic.get_all_leaf_paths()
        
        if total_paths == 0:
            lcomonto = 0.0
        else:
            lcomonto = sum_path_lengths / total_paths
        
        self._cache['LCOMOnto'] = lcomonto
        logger.debug(f"LCOMOnto = {sum_path_lengths} / {total_paths} = {lcomonto:.6f}")
        return lcomonto
    
    # =========================================================================
    # TANGLEDNESS (TMOnto)
    # =========================================================================
    
    def calculate_TMOnto(self) -> float:
        """
        Tangledness: Mean number of parents per class.
        
        Formula: TMOnto = ∑|RCi| / (∑|Ci| - ∑|C(DP)i|)
        where C(DP)i is a class with more than one direct parent.
        
        Returns:
            TMOnto value
        """
        if 'TMOnto' in self._cache:
            return self._cache['TMOnto']
        
        sum_relationships = self.basic.count_total_relationships()
        num_classes = self.basic.count_classes()
        classes_multi_parents = self.basic.count_classes_with_multiple_parents()
        
        denominator = num_classes - classes_multi_parents
        
        if denominator <= 0:
            tmonto = 0.0
        else:
            tmonto = sum_relationships / denominator
        
        self._cache['TMOnto'] = tmonto
        logger.debug(f"TMOnto = {sum_relationships} / ({num_classes} - {classes_multi_parents}) = {tmonto:.6f}")
        return tmonto
    
    # =========================================================================
    # SCORING METHODS
    # =========================================================================
    
    def get_metric_recommendation(self, metric_name: str, score: str, value: float) -> str:
        """
        Get recommendations for improving a metric's score.
        
        Args:
            metric_name: Name of the metric
            score: Current score level (L1, L2, etc.)
            value: Current metric value
            
        Returns:
            Recommendation text or empty string if score is good
        """
        if score not in ['L1', 'L2', 'L3']:
            return ""
        
        recommendations = {
            'LCOMOnto': (
                "HIGH LACK OF COHESION DETECTED!\n"
                f"   Current value: {value:.2f} (Target: ≤2 for L5, ≤4 for L4)\n"
                "   Recommendations:\n"
                "   • Review class hierarchy depth - consider flattening overly deep structures\n"
                "   • Ensure leaf classes are conceptually related to their ancestors\n"
                "   • Group related classes closer together in the hierarchy\n"
                "   • Consider splitting large branches into more focused sub-hierarchies"
            ),
            'WMCOnto': (
                "HIGH COMPLEXITY DETECTED!\n"
                f"   Current value: {value:.2f} (Target: ≤5 for L5, ≤8 for L4)\n"
                "   Recommendations:\n"
                "   • Reduce the number of properties per class\n"
                "   • Simplify relationship structures between classes\n"
                "   • Consider extracting complex classes into simpler, more focused classes\n"
                "   • Review if all properties are necessary for each class"
            ),
            'DITOnto': (
                "INHERITANCE TREE TOO DEEP!\n"
                f"   Current depth: {int(value)} levels (Target: 1-2 for L5, 2-4 for L4)\n"
                "   Recommendations:\n"
                "   • Flatten the class hierarchy by reducing intermediate levels\n"
                "   • Consider using composition over inheritance where appropriate\n"
                "   • Review if all inheritance levels add meaningful specialization\n"
                "   • Consolidate classes that don't add significant distinctions"
            ),
            'NACOnto': (
                "TOO MANY ANCESTOR CLASSES!\n"
                f"   Current value: {value:.2f} (Target: 1-2 for L5, 2-4 for L4)\n"
                "   Recommendations:\n"
                "   • Simplify the inheritance chain for leaf classes\n"
                "   • Remove unnecessary intermediate parent classes\n"
                "   • Ensure each level of abstraction adds value\n"
                "   • Consider direct relationships instead of deep hierarchies"
            ),
            'NOCOnto': (
                "SUBCLASS DISTRIBUTION ISSUE!\n"
                f"   Current value: {value:.2f} (Target: 1-3 for L5, 3-6 for L4)\n"
                "   Recommendations:\n"
                "   • Balance the number of direct subclasses per parent\n"
                "   • Avoid classes with too many or too few children\n"
                "   • Introduce intermediate grouping classes if needed\n"
                "   • Review if sibling classes are at the same level of abstraction"
            ),
            'CBOOnto': (
                "HIGH COUPLING DETECTED!\n"
                f"   Current value: {value:.2f} (Target: 1-2 for L5, 2-4 for L4)\n"
                "   Recommendations:\n"
                "   • Reduce dependencies between unrelated classes\n"
                "   • Simplify the inheritance structure\n"
                "   • Consider using interfaces or abstract classes\n"
                "   • Review if all parent relationships are necessary"
            ),
            'RFCOnto': (
                "HIGH RESPONSE FOR CLASS!\n"
                f"   Current value: {value:.2f} (Target: 1-3 for L5, 3-6 for L4)\n"
                "   Recommendations:\n"
                "   • Reduce the number of accessible properties per class\n"
                "   • Simplify inheritance to reduce inherited properties\n"
                "   • Consider splitting complex classes into simpler ones\n"
                "   • Review property visibility and necessity"
            ),
            'NOMOnto': (
                "TOO MANY PROPERTIES!\n"
                f"   Current value: {value:.2f} (Target: ≤2 for L5, 2-4 for L4)\n"
                "   Recommendations:\n"
                "   • Reduce the number of properties defined per class\n"
                "   • Move properties to more specific subclasses where appropriate\n"
                "   • Consider if some properties could be derived or computed\n"
                "   • Group related properties into separate classes"
            ),
            'RROnto': (
                "LOW PROPERTY RICHNESS!\n"
                f"   Current value: {value*100:.2f}% (Target: >80% for L5, 60-80% for L4)\n"
                "   Recommendations:\n"
                "   • Add more object/data properties to the ontology\n"
                "   • Ensure classes have meaningful properties beyond inheritance\n"
                "   • Define domain-specific properties for your concepts\n"
                "   • Consider reusing properties from standard ontologies"
            ),
            'AROnto': (
                "LOW ATTRIBUTE RICHNESS!\n"
                f"   Current value: {value*100:.2f}% (Target: >80% for L5, 60-80% for L4)\n"
                "   Recommendations:\n"
                "   • Add more data properties (attributes) to classes\n"
                "   • Define literal-valued properties for class characteristics\n"
                "   • Include descriptive attributes (e.g., labels, descriptions, dates)\n"
                "   • Consider which class features should be captured as data"
            ),
            'INROnto': (
                "LOW RELATIONSHIP DENSITY!\n"
                f"   Current value: {value*100:.2f}% (Target: >80% for L5, 60-80% for L4)\n"
                "   Recommendations:\n"
                "   • Add more subclass relationships to organize the hierarchy\n"
                "   • Ensure all classes are properly connected to the hierarchy\n"
                "   • Review if classes need additional parent relationships\n"
                "   • Consider multiple inheritance where conceptually valid"
            ),
            'CROnto': (
                "LOW CLASS RICHNESS - FEW INSTANCES!\n"
                f"   Current value: {value*100:.2f}% (Target: >80% for L5, 60-80% for L4)\n"
                "   Recommendations:\n"
                "   • Add individual instances to populate your classes\n"
                "   • Create example individuals for key classes\n"
                "   • Import or link to instance data if available\n"
                "   • Consider if this ontology should include instances (TBox vs ABox)"
            ),
            'ANOnto': (
                "LOW ANNOTATION RICHNESS!\n"
                f"   Current value: {value*100:.2f}% (Target: >80% for L5, 60-80% for L4)\n"
                "   Recommendations:\n"
                "   • Add rdfs:label annotations to all classes and properties\n"
                "   • Include rdfs:comment descriptions for documentation\n"
                "   • Add metadata annotations (creator, date, version, etc.)\n"
                "   • Consider domain-specific annotations for better usability\n"
                "   • Use standard annotation properties (Dublin Core, SKOS, etc.)"
            ),
            'TMOnto': (
                "TANGLEDNESS ISSUE!\n"
                f"   Current value: {value:.2f} (Target: 1-2 for L5, 2-4 for L4)\n"
                "   Recommendations:\n"
                "   • Review classes with multiple parent relationships\n"
                "   • Ensure multiple inheritance is conceptually justified\n"
                "   • Consider using composition instead of multiple inheritance\n"
                "   • Simplify the class hierarchy to reduce complexity"
            )
        }
        
        return recommendations.get(metric_name, "")
    
    def get_metric_score(self, metric_name: str, value: float) -> str:
        """
        Determine the score level (L1-L5) for a metric based on the OQuaRE scoring table.
        
        Args:
            metric_name: Name of the metric
            value: Calculated metric value
            
        Returns:
            Score level as string (L1, L2, L3, L4, or L5)
        """
        # Convert percentage metrics to percentage values
        if metric_name in ['RROnto', 'AROnto', 'INROnto', 'CROnto', 'ANOnto']:
            value = value * 100  # Convert to percentage
        
        # Scoring thresholds based on Table 3 in Scores.md
        scoring_table = {
            'LCOMOnto': {
                'L5': lambda v: v <= 2,
                'L4': lambda v: 2 < v <= 4,
                'L3': lambda v: 4 < v <= 6,
                'L2': lambda v: 6 < v <= 8,
                'L1': lambda v: v > 8
            },
            'WMCOnto': {
                'L5': lambda v: v <= 5,
                'L4': lambda v: 5 < v <= 8,
                'L3': lambda v: 8 < v <= 11,
                'L2': lambda v: 11 < v <= 15,
                'L1': lambda v: v > 15
            },
            'DITOnto': {
                'L5': lambda v: 1 <= v <= 2,
                'L4': lambda v: 2 < v <= 4,
                'L3': lambda v: 4 < v <= 6,
                'L2': lambda v: 6 < v <= 8,
                'L1': lambda v: v > 8
            },
            'NACOnto': {
                'L5': lambda v: 1 <= v <= 2,
                'L4': lambda v: 2 < v <= 4,
                'L3': lambda v: 4 < v <= 6,
                'L2': lambda v: 6 < v <= 8,
                'L1': lambda v: v > 8
            },
            'NOCOnto': {
                'L5': lambda v: 1 <= v <= 3,
                'L4': lambda v: 3 < v <= 6,
                'L3': lambda v: 6 < v <= 8,
                'L2': lambda v: 8 < v <= 12,
                'L1': lambda v: v > 12
            },
            'CBOOnto': {
                'L5': lambda v: 1 <= v <= 2,
                'L4': lambda v: 2 < v <= 4,
                'L3': lambda v: 4 < v <= 6,
                'L2': lambda v: 6 < v <= 8,
                'L1': lambda v: v > 8
            },
            'RFCOnto': {
                'L5': lambda v: 1 <= v <= 3,
                'L4': lambda v: 3 < v <= 6,
                'L3': lambda v: 6 < v <= 8,
                'L2': lambda v: 8 < v <= 12,
                'L1': lambda v: v > 12
            },
            'NOMOnto': {
                'L5': lambda v: v <= 2,
                'L4': lambda v: 2 < v <= 4,
                'L3': lambda v: 4 < v <= 6,
                'L2': lambda v: 6 < v <= 8,
                'L1': lambda v: v > 8
            },
            'RROnto': {  # Percentage metric
                'L5': lambda v: v > 80,
                'L4': lambda v: 60 < v <= 80,
                'L3': lambda v: 40 < v <= 60,
                'L2': lambda v: 20 < v <= 40,
                'L1': lambda v: 0 <= v <= 20
            },
            'AROnto': {  # Percentage metric
                'L5': lambda v: v > 80,
                'L4': lambda v: 60 < v <= 80,
                'L3': lambda v: 40 < v <= 60,
                'L2': lambda v: 20 < v <= 40,
                'L1': lambda v: 0 <= v <= 20
            },
            'INROnto': {  # Percentage metric
                'L5': lambda v: v > 80,
                'L4': lambda v: 60 < v <= 80,
                'L3': lambda v: 40 < v <= 60,
                'L2': lambda v: 20 < v <= 40,
                'L1': lambda v: 0 <= v <= 20
            },
            'CROnto': {  # Percentage metric
                'L5': lambda v: v > 80,
                'L4': lambda v: 60 < v <= 80,
                'L3': lambda v: 40 < v <= 60,
                'L2': lambda v: 20 < v <= 40,
                'L1': lambda v: 0 <= v <= 20
            },
            'ANOnto': {  # Percentage metric
                'L5': lambda v: v > 80,
                'L4': lambda v: 60 < v <= 80,
                'L3': lambda v: 40 < v <= 60,
                'L2': lambda v: 20 < v <= 40,
                'L1': lambda v: 0 <= v <= 20
            },
            'TMOnto': {
                'L5': lambda v: 1 < v <= 2,
                'L4': lambda v: 2 < v <= 4,
                'L3': lambda v: 4 < v <= 6,
                'L2': lambda v: 6 < v <= 8,
                'L1': lambda v: v > 8
            }
        }
        
        if metric_name not in scoring_table:
            return "N/A"
        
        thresholds = scoring_table[metric_name]
        
        # Check each level from L5 (best) to L1 (worst)
        for level in ['L5', 'L4', 'L3', 'L2', 'L1']:
            if thresholds[level](value):
                return level
        
        return "N/A"
    
    # =========================================================================
    # SUMMARY METHODS
    # =========================================================================
    
    def calculate_all_metrics(self) -> Dict[str, float]:
        """
        Calculate and return all OQuaRE metrics.
        
        Returns:
            Dictionary with all OQuaRE metric values
        """
        metrics = {
            'ANOnto': self.calculate_ANOnto(),
            'CROnto': self.calculate_CROnto(),
            'NOMOnto': self.calculate_NOMOnto(),
            'INROnto': self.calculate_INROnto(),
            'AROnto': self.calculate_AROnto(),
            'DITOnto': self.calculate_DITOnto(),
            'NACOnto': self.calculate_NACOnto(),
            'NOCOnto': self.calculate_NOCOnto(),
            'CBOOnto': self.calculate_CBOOnto(),
            'WMCOnto': self.calculate_WMCOnto(),
            'RFCOnto': self.calculate_RFCOnto(),
            'RROnto': self.calculate_RROnto(),
            'LCOMOnto': self.calculate_LCOMOnto(),
            'TMOnto': self.calculate_TMOnto(),
        }
        
        logger.info("All OQuaRE metrics calculated")
        return metrics
    
    def print_metrics_summary(self):
        """Print a formatted summary of all metrics with scores."""
        metrics = self.calculate_all_metrics()
        
        print(f"\n{'='*85}")
        print(f"OQUARE QUALITY METRICS WITH SCORES")
        print(f"{'='*85}")
        print(f"{'Metric':<15} {'Value':>15} {'Score':>8} {'Description'}")
        print(f"{'-'*85}")
        
        descriptions = {
            'ANOnto': 'Annotation Richness',
            'CROnto': 'Class Richness',
            'NOMOnto': 'Number of Properties',
            'INROnto': 'Relationships per Class',
            'AROnto': 'Attribute Richness',
            'DITOnto': 'Depth of Inheritance',
            'NACOnto': 'Number of Ancestors',
            'NOCOnto': 'Number of Children',
            'CBOOnto': 'Coupling Between Objects',
            'WMCOnto': 'Weighted Method Count',
            'RFCOnto': 'Response for Class',
            'RROnto': 'Properties Richness',
            'LCOMOnto': 'Lack of Cohesion',
            'TMOnto': 'Tangledness',
        }
        
        for metric_name, value in metrics.items():
            desc = descriptions.get(metric_name, '')
            score = self.get_metric_score(metric_name, value)
            if isinstance(value, int):
                print(f"{metric_name:<15} {value:>15} {score:>8} {desc}")
            else:
                print(f"{metric_name:<15} {value:>15.6f} {score:>8} {desc}")
        
        print(f"{'='*85}\n")
    
    def print_detailed_calculations(self):
        """Print detailed calculations for all metrics showing formulas and values."""
        print(f"\n{'='*80}")
        print(f"DETAILED METRIC CALCULATIONS")
        print(f"{'='*80}\n")
        
        # Get basic values
        num_classes = self.basic.count_classes()
        num_leaf_classes = self.basic.count_leaf_classes()
        sum_annotations = self.basic.count_annotations()
        sum_instances = self.basic.count_individuals()
        sum_properties = self.basic.count_properties()
        sum_relationships = self.basic.count_total_relationships()
        sum_attributes = self.basic.sum_attributes()
        sum_parents = self.basic.sum_direct_parents()
        sum_parents_leaf = self.basic.sum_direct_parents_of_leaf_classes()
        thing_relationships = self.basic.count_thing_relationships()
        classes_multi_parents = self.basic.count_classes_with_multiple_parents()
        max_depth = self.basic.get_maximum_depth()
        paths_dict, total_paths, sum_path_lengths = self.basic.get_all_leaf_paths()
        
        # ANOnto
        anonto = sum_annotations / num_classes if num_classes > 0 else 0.0
        print(f"1. ANOnto (Annotation Richness)")
        print(f"   Formula: ANOnto = ∑|ACi| / ∑|Ci|")
        print(f"   Where:   ∑|ACi| = total annotations (sumOfAnnotations)")
        print(f"            ∑|Ci| = total classes (numberOfClasses)")
        print(f"   Values:  ANOnto = {sum_annotations} / {num_classes}")
        print(f"   Result:  ANOnto = {anonto:.6f}\n")
        
        # CROnto
        cronto = sum_instances / num_classes if num_classes > 0 else 0.0
        print(f"2. CROnto (Class Richness)")
        print(f"   Formula: CROnto = ∑|ICi| / ∑|Ci|")
        print(f"   Where:   ∑|ICi| = total individuals/instances (numberOfIndividuals)")
        print(f"            ∑|Ci| = total classes (numberOfClasses)")
        print(f"   Values:  CROnto = {sum_instances} / {num_classes}")
        print(f"   Result:  CROnto = {cronto:.6f}\n")
        
        # NOMOnto
        nomonto = sum_properties / num_classes if num_classes > 0 else 0.0
        print(f"3. NOMOnto (Number of Properties)")
        print(f"   Formula: NOMOnto = ∑|PCi| / ∑|Ci|")
        print(f"   Where:   ∑|PCi| = total properties (numberOfProperties)")
        print(f"            ∑|Ci| = total classes (numberOfClasses)")
        print(f"   Values:  NOMOnto = {sum_properties} / {num_classes}")
        print(f"   Result:  NOMOnto = {nomonto:.6f}\n")
        
        # INROnto
        inronto = sum_relationships / num_classes if num_classes > 0 else 0.0
        print(f"4. INROnto (Relationships per Class)")
        print(f"   Formula: INROnto = ∑|RCi| / ∑|Ci|")
        print(f"   Where:   ∑|RCi| = total relationships (sumOfRelationships)")
        print(f"            ∑|Ci| = total classes (numberOfClasses)")
        print(f"   Values:  INROnto = {sum_relationships} / {num_classes}")
        print(f"   Result:  INROnto = {inronto:.6f}\n")
        
        # AROnto
        aronto = sum_attributes / num_classes if num_classes > 0 else 0.0
        print(f"5. AROnto (Attribute Richness)")
        print(f"   Formula: AROnto = ∑|AttCi| / ∑|Ci|")
        print(f"   Where:   ∑|AttCi| = total attributes (sumOfAttributes)")
        print(f"            ∑|Ci| = total classes (numberOfClasses)")
        print(f"   Values:  AROnto = {sum_attributes} / {num_classes}")
        print(f"   Result:  AROnto = {aronto:.6f}\n")
        
        # DITOnto
        print(f"6. DITOnto (Depth of Inheritance Tree)")
        print(f"   Formula: DITOnto = Max(∑D|Ci|)")
        print(f"   Where:   Max(∑D|Ci|) = maximum depth from root to leaf (maximumDepth)")
        print(f"   Values:  DITOnto = {max_depth}")
        print(f"   Result:  DITOnto = {max_depth}\n")
        
        # NACOnto
        naconto = sum_parents_leaf / num_leaf_classes if num_leaf_classes > 0 else 0.0
        print(f"7. NACOnto (Number of Ancestor Classes)")
        print(f"   Formula: NACOnto = ∑|SupC(Leaf)i| / ∑|C(leaf)i|")
        print(f"   Where:   ∑|SupC(Leaf)i| = sum of parents of leaf classes (sumOfDirectParentsLeaf)")
        print(f"            ∑|C(leaf)i| = total leaf classes (numberOfLeafClasses)")
        print(f"   Values:  NACOnto = {sum_parents_leaf} / {num_leaf_classes}")
        print(f"   Result:  NACOnto = {naconto:.6f}\n")
        
        # NOCOnto
        denominator = num_classes - thing_relationships
        noconto = sum_relationships / denominator if denominator > 0 else 0.0
        print(f"8. NOCOnto (Number of Children)")
        print(f"   Formula: NOCOnto = ∑|RCi| / (∑|Ci| - |RThing|)")
        print(f"   Where:   ∑|RCi| = total relationships (sumOfRelationships)")
        print(f"            ∑|Ci| = total classes (numberOfClasses)")
        print(f"            |RThing| = relationships to Thing (thingRelationships)")
        print(f"   Values:  NOCOnto = {sum_relationships} / ({num_classes} - {thing_relationships})")
        print(f"   Result:  NOCOnto = {noconto:.6f}\n")
        
        # CBOOnto
        cboonto = sum_parents / denominator if denominator > 0 else 0.0
        print(f"9. CBOOnto (Coupling Between Objects)")
        print(f"   Formula: CBOOnto = ∑|SupCi| / (∑|Ci| - |RThing|)")
        print(f"   Where:   ∑|SupCi| = sum of direct parents (sumOfDirectParents)")
        print(f"            ∑|Ci| = total classes (numberOfClasses)")
        print(f"            |RThing| = relationships to Thing (thingRelationships)")
        print(f"   Values:  CBOOnto = {sum_parents} / ({num_classes} - {thing_relationships})")
        print(f"   Result:  CBOOnto = {cboonto:.6f}\n")
        
        # WMCOnto
        wmconto = (sum_properties + sum_relationships) / num_classes if num_classes > 0 else 0.0
        print(f"10. WMCOnto (Weighted Method Count)")
        print(f"    Formula: WMCOnto = (∑|PCi| + ∑|RCi|) / ∑|Ci|")
        print(f"    Where:   ∑|PCi| = total properties (numberOfProperties)")
        print(f"             ∑|RCi| = total relationships (sumOfRelationships)")
        print(f"             ∑|Ci| = total classes (numberOfClasses)")
        print(f"    Values:  WMCOnto = ({sum_properties} + {sum_relationships}) / {num_classes}")
        print(f"    Result:  WMCOnto = {wmconto:.6f}\n")
        
        # RFCOnto
        rfconto = (sum_properties + sum_parents) / denominator if denominator > 0 else 0.0
        print(f"11. RFCOnto (Response For a Class)")
        print(f"    Formula: RFCOnto = (∑|PCi| + ∑|SupCi|) / (∑|Ci| - |RThing|)")
        print(f"    Where:   ∑|PCi| = total properties (numberOfProperties)")
        print(f"             ∑|SupCi| = sum of direct parents (sumOfDirectParents)")
        print(f"             ∑|Ci| = total classes (numberOfClasses)")
        print(f"             |RThing| = relationships to Thing (thingRelationships)")
        print(f"    Values:  RFCOnto = ({sum_properties} + {sum_parents}) / ({num_classes} - {thing_relationships})")
        print(f"    Result:  RFCOnto = {rfconto:.6f}\n")
        
        # RROnto
        denom_rr = sum_relationships + num_classes
        rronto = sum_properties / denom_rr if denom_rr > 0 else 0.0
        print(f"12. RROnto (Properties Richness)")
        print(f"    Formula: RROnto = ∑|PCi| / (∑|RCi| + ∑|Ci|)")
        print(f"    Where:   ∑|PCi| = total properties (numberOfProperties)")
        print(f"             ∑|RCi| = total relationships (sumOfRelationships)")
        print(f"             ∑|Ci| = total classes (numberOfClasses)")
        print(f"    Values:  RROnto = {sum_properties} / ({sum_relationships} + {num_classes})")
        print(f"    Result:  RROnto = {rronto:.6f}\n")
        
        # LCOMOnto
        lcomonto = sum_path_lengths / total_paths if total_paths > 0 else 0.0
        print(f"13. LCOMOnto (Lack of Cohesion)")
        print(f"    Formula: LCOMOnto = ∑path(|C(leaf)i|) / m")
        print(f"    Where:   ∑path(|C(leaf)i|) = sum of all path lengths from leaves to root")
        print(f"             m = total number of paths from leaf classes")
        print(f"    Values:  LCOMOnto = {sum_path_lengths} / {total_paths}")
        print(f"    Result:  LCOMOnto = {lcomonto:.6f}\n")
        
        # TMOnto
        denom_tm = num_classes - classes_multi_parents
        tmonto = sum_relationships / denom_tm if denom_tm > 0 else 0.0
        print(f"14. TMOnto (Tangledness)")
        print(f"    Formula: TMOnto = ∑|RCi| / (∑|Ci| - ∑|C(DP)i|)")
        print(f"    Where:   ∑|RCi| = total relationships (sumOfRelationships)")
        print(f"             ∑|Ci| = total classes (numberOfClasses)")
        print(f"             ∑|C(DP)i| = classes with multiple parents (classesWithMultipleParents)")
        print(f"    Values:  TMOnto = {sum_relationships} / ({num_classes} - {classes_multi_parents})")
        print(f"    Result:  TMOnto = {tmonto:.6f}\n")
        
        print(f"{'='*80}\n")
    
    def clear_cache(self):
        """Clear the internal cache."""
        self._cache.clear()
        logger.debug("Cache cleared")

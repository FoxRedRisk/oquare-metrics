The maths behind each metric:

We can associate these concepts with the OWL modeling primitives: classes refer to owl:Class, relationships refer to owl:ObjectProperty, properties refer to owl:DatatypeProperty and individuals refers to owl:Individual.

Lack of Cohesion in Methods (LCOMOnto): The semantic and conceptual relatedness of classes can be used to measure the separation of responsibilities and independence of components of ontologies. It is calculated as follows: LCOMOnto=∑path(|C(leaf)i|)/m, where path|C(leaf)i| is the length of the path from the leaf class i to Thing, and m is the total number of paths in the ontology. 

Weighted Method Count (WMCOnto): Mean number of properties and relationships per class. It is calculated as follows: WMCOnto=(∑|PCi|+∑| RCi|) ∕ ∑|Ci| , where Ci is the i-th class in the ontology. 

Depth of subsumption hierarchy (DITOnto): Length of the largest path from Thing to a leaf class. It is calculated as follows: DITOnto=Max (∑D|Ci|), where Ci are the classes and D|Ci| is the length of the path from the ith leaf class of the ontology to Thing. 

Number of Ancestor Classes (NACOnto): Mean number of ancestor classes per leaf class. It is the number of direct superclasses per leaf class, and calculated as follows: NACOnto=∑|SupC(Leaf)i|/∑|C(leaf)i)| 

Number of Children (NOCOnto): Mean number of direct subclasses. It is the number of relationships divided by the number of classes minus the relationships of Thing, and calculated as follows: NOCOnto=∑| RCi| ∕ (∑|Ci| -| RThing|)

Coupling between Objects (CBOOnto): Number of related classes. It is the average number of the direct parents per class minus the relationships of Thing, and calculated as follows: CBOOnto=∑|SupCi|/(∑|Ci| -| RThing|) 

Response for a class (RFCOnto): Number of properties that can be directly accessed from the class. It is calculated as follows: RFCOnto=(∑|PCi|+∑|SupCi|/(∑|Ci| -| RThing|) 

Number of properties (NOMOnto): Number of properties per class. It is calculated as follows: NOMOnto=∑| PCi| ∕ ∑|Ci| 

Properties Richness (RROnto): Number of properties defined in the ontology divided by the number of relationships and properties. It is calculated as follows: RROnto=∑| PCi| ∕ ∑(| RCi| + ∑|Ci|) 

Attribute Richness (AROnto): Mean number of attributes per class. It is calculated as follows: AROnto=∑|AttCi| ∕ ∑|Ci| • Relationships per class (INROnto): Mean number of relationships per class. It is calculated as follows: INROnto=∑| RCi| / ∑|Ci| 

Class Richness (CROnto): Mean number of instances per class. It is calculated as follows: CROnto=∑| ICi| / ∑|Ci |; where ICi, is the set of individuals of the Ci class. 

Annotation Richness (ANOnto): Mean number of annotations per class. It is calculated as follows: ANOnto=∑| ACi| / ∑|Ci|; where Ci is the i-th class in the ontology. 

Tangledness (TMOnto): Mean number of parents per class. It is calculated as follows: TMOnto=∑| RCi| / ∑|Ci|-∑|C(DP)i|; where Ci is the i-th class in the ontology and C(DP)i is the i-th class in the ontology with more than one direct parent.
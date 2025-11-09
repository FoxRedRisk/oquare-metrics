"""
XML Generator Module

Generates XML output files compatible with the original JAR format.
This ensures compatibility with existing tools that consume the metrics XML.

Author: OQuaRE Metrics Team
Date: 2025-11-04
"""

import logging
from pathlib import Path
from typing import Dict, Optional, Union
from xml.etree.ElementTree import Element, SubElement, ElementTree, tostring
from xml.dom import minidom
from datetime import datetime

logger = logging.getLogger(__name__)


def prettify_xml(elem: Element) -> str:
    """
    Return a pretty-printed XML string for the Element.
    
    Args:
        elem: XML Element to prettify
        
    Returns:
        Pretty-printed XML string
    """
    rough_string = tostring(elem, encoding='unicode')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")


def generate_metrics_xml(
    basic_metrics: Dict[str, int],
    oquare_metrics: Dict[str, float],
    output_path: Union[str, Path],
    ontology_name: Optional[str] = None
) -> None:
    """
    Generate XML metrics file compatible with JAR output format.
    
    Args:
        basic_metrics: Dictionary of basic metric values
        oquare_metrics: Dictionary of OQuaRE metric values
        output_path: Path to save the XML file
        ontology_name: Name of the ontology (optional)
    """
    output_path = Path(output_path)
    
    # Create root element
    root = Element('ontologyMetrics')
    
    # Add metadata
    if ontology_name:
        ontology_elem = SubElement(root, 'ontologyName')
        ontology_elem.text = ontology_name
    
    timestamp = SubElement(root, 'timestamp')
    timestamp.text = datetime.now().isoformat()
    
    generator = SubElement(root, 'generator')
    generator.text = 'OQuaRE-Python-v1.0'
    
    # Add basic metrics
    basic_section = SubElement(root, 'basicMetrics')
    
    # Map internal names to XML element names (matching JAR format)
    basic_mapping = {
        'numberOfClasses': 'numberOfClasses',
        'numberOfLeafClasses': 'numberOfLeafClasses',
        'numberOfObjectProperties': 'numberOfObjectProperties',
        'numberOfDataProperties': 'numberOfDataProperties',
        'numberOfProperties': 'numberOfProperties',
        'numberOfIndividuals': 'numberOfIndividuals',
        'sumOfAnnotations': 'sumOfAnnotations',
        'sumOfRelationships': 'sumOfRelationships',
        'thingRelationships': 'thingRelationships',
        'sumOfDirectParents': 'sumOfDirectParents',
        'sumOfDirectParentsLeaf': 'sumOfDirectParentsLeaf',
        'classesWithMultipleParents': 'classesWithMultipleParents',
        'sumOfAttributes': 'sumOfAttributes',
        'maximumDepth': 'maximumDepth',
    }
    
    for internal_name, xml_name in basic_mapping.items():
        if internal_name in basic_metrics:
            elem = SubElement(basic_section, xml_name)
            elem.text = str(basic_metrics[internal_name])
    
    # Add OQuaRE metrics
    oquare_section = SubElement(root, 'oquareMetrics')
    
    # These should match the JAR output names exactly
    oquare_mapping = {
        'ANOnto': 'ANOnto',
        'CROnto': 'CROnto',
        'NOMOnto': 'NOMOnto',
        'INROnto': 'INROnto',
        'AROnto': 'AROnto',
        'DITOnto': 'DITOnto',
        'NACOnto': 'NACOnto',
        'NOCOnto': 'NOCOnto',
        'CBOOnto': 'CBOOnto',
        'WMCOnto': 'WMCOnto',
        'RFCOnto': 'RFCOnto',
        'RROnto': 'RROnto',
        'LCOMOnto': 'LCOMOnto',
        'TMOnto': 'TMOnto',
    }
    
    for internal_name, xml_name in oquare_mapping.items():
        if internal_name in oquare_metrics:
            elem = SubElement(oquare_section, xml_name)
            value = oquare_metrics[internal_name]
            if isinstance(value, int):
                elem.text = str(value)
            else:
                elem.text = f"{value:.15f}"  # High precision for float values
    
    # Create output directory if it doesn't exist
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Write to file with pretty formatting
    xml_string = prettify_xml(root)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(xml_string)
    
    logger.info(f"Metrics XML saved to: {output_path}")

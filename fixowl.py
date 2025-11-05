import os
import glob
from rdflib import Graph, exceptions, URIRef, Namespace
from owlready2 import get_ontology, OwlReadyOntologyParsingError
import urllib.parse
import re


def rename_file_if_needed(owl_file):
    """
    Rename file by replacing spaces with underscores if necessary.
    
    Args:
        owl_file (str): Path to the OWL file.
    
    Returns:
        str: New file path (same as original if no rename needed).
    """
    new_file_name = owl_file.replace(" ", "_")
    if new_file_name != owl_file:
        os.rename(owl_file, new_file_name)
        print(f"Renamed file to {new_file_name}")
        return new_file_name
    return owl_file


def fix_file_content(content):
    """
    Apply regex fixes to OWL file content.
    
    Args:
        content (str): Original file content.
    
    Returns:
        str: Fixed content.
    """
    # Fix file:/// IRIs
    content = re.sub(r'file:///[^"<>\s]+', 
                     lambda m: urllib.parse.quote(m.group(0), safe=':/@'), 
                     content)
    
    # Fix invalid URIs in the Ontology element
    content = re.sub(r'<owl:Ontology rdf:about="file:///([^"]+)"',
                     lambda m: f'<owl:Ontology rdf:about="http://example.org/ontology/{m.group(1).replace(" ", "_")}"',
                     content)
    
    return content


def create_safe_iri_name(file_path):
    """
    Create a safe IRI name from a file path.
    
    Args:
        file_path (str): File path or URI to convert.
    
    Returns:
        str: Safe name for use in IRI.
    """
    if file_path.startswith("file:///"):
        file_path = urllib.parse.unquote(file_path[8:])  # Remove 'file:///' and decode
    
    base_name = os.path.basename(file_path)
    # Replace spaces with underscores and remove any other non-alphanumeric characters
    safe_name = ''.join(c if c.isalnum() or c == '_' else '_' for c in base_name.replace(" ", "_"))
    
    return safe_name


def fix_ontology_iris(graph, owl_file):
    """
    Fix invalid ontology IRIs in the graph.
    
    Args:
        graph (Graph): RDF graph to fix.
        owl_file (str): Path to the OWL file (for logging).
    
    Returns:
        bool: True if any IRI was fixed, False otherwise.
    """
    ontology_iri_fixed = False
    owl_ontology_uri = URIRef("http://www.w3.org/2002/07/owl#Ontology")
    
    for s, p, o in graph.triples((None, owl_ontology_uri, None)):
        if not str(s) or str(s).startswith("file:///") or " " in str(s):
            safe_name = create_safe_iri_name(str(s))
            new_iri = URIRef(f"http://example.org/ontology/{safe_name}")
            graph.remove((s, None, None))
            graph.add((new_iri, p, o))
            print(f"Fixed invalid ontology IRI in {owl_file}")
            ontology_iri_fixed = True
    
    return ontology_iri_fixed


def save_fixed_file(graph, owl_file, fixed_files, file_statuses):
    """
    Save the fixed ontology to a new file.
    
    Args:
        graph (Graph): RDF graph to save.
        owl_file (str): Original file path.
        fixed_files (list): List to append fixed file path to.
        file_statuses (dict): Dictionary to update with status.
    """
    fixed_file = os.path.splitext(owl_file)[0] + "-fixed.owl"
    graph.serialize(destination=fixed_file, format="xml")
    fixed_files.append(fixed_file)
    file_statuses[owl_file] = "Fixed"
    print(f"Fixed version saved as {fixed_file}")


def try_owlready2_fix(owl_file, fixed_files, file_statuses):
    """
    Attempt to fix OWL file using owlready2 as fallback.
    
    Args:
        owl_file (str): Path to the OWL file.
        fixed_files (list): List to append fixed file path to.
        file_statuses (dict): Dictionary to update with status.
    """
    try:
        onto = get_ontology(owl_file).load()
        fixed_file = os.path.splitext(owl_file)[0] + "-fixed.owl"
        onto.save(fixed_file)
        fixed_files.append(fixed_file)
        file_statuses[owl_file] = "Fixed"
        print(f"Fixed version saved as {fixed_file}")
    except OwlReadyOntologyParsingError as oe:
        print(f"Unable to fix {owl_file}: {str(oe)}")
        file_statuses[owl_file] = f"Unable to fix: {str(oe)}"


def process_owl_file(owl_file, fixed_files, file_statuses):
    """
    Process a single OWL file: rename, fix content, and validate.
    
    Args:
        owl_file (str): Path to the OWL file.
        fixed_files (list): List to append fixed file path to.
        file_statuses (dict): Dictionary to update with status.
    """
    try:
        # Rename file if needed
        owl_file = rename_file_if_needed(owl_file)
        
        # Read and fix file content
        with open(owl_file, 'r', encoding='utf-8') as file:
            content = file.read()
        
        content = fix_file_content(content)
        
        # Parse with rdflib
        graph = Graph()
        graph.parse(data=content, format="xml")
        file_statuses[owl_file] = "Valid"
        
        # Fix ontology IRIs
        ontology_iri_fixed = fix_ontology_iris(graph, owl_file)
        
        # Save if fixes were applied
        if ontology_iri_fixed or file_statuses[owl_file] != "Valid":
            save_fixed_file(graph, owl_file, fixed_files, file_statuses)
        else:
            print(f"File {owl_file} is valid. No fixes needed.")
            
    except exceptions.ParserError as e:
        print(f"Error in file {owl_file}: {str(e)}")
        file_statuses[owl_file] = f"Invalid: {str(e)}"
        try_owlready2_fix(owl_file, fixed_files, file_statuses)


def fix_owl_files(imports_folder="ontologies/imports"):
    """
    Check OWL files in the imports folder for errors and fix them.
    
    Args:
        imports_folder (str): Path to the folder containing OWL files.
    
    Returns:
        tuple: List of fixed file paths, dictionary of file statuses.
    """
    fixed_files = []
    file_statuses = {}
    
    # Get all .owl files in the imports folder
    owl_files = glob.glob(os.path.join(imports_folder, "*.owl"))
    
    for owl_file in owl_files:
        process_owl_file(owl_file, fixed_files, file_statuses)
    
    return fixed_files, file_statuses


if __name__ == "__main__":
    fixed_owl_files, file_statuses = fix_owl_files()
    print(f"Fixed {len(fixed_owl_files)} OWL files.")
    print("\nFile Status Report:")
    for file, status in file_statuses.items():
        print(f"{file}: {status}")

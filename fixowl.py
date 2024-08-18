import os
import glob
from rdflib import Graph, exceptions, URIRef
from owlready2 import get_ontology, OwlReadyOntologyParsingError
import urllib.parse

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
        try:
            # Replace spaces with underscores in the file name
            new_file_name = owl_file.replace(" ", "_")
            if new_file_name != owl_file:
                os.rename(owl_file, new_file_name)
                owl_file = new_file_name
                print(f"Renamed file to {owl_file}")

            # Try to parse the OWL file using rdflib
            g = Graph()
            g.parse(owl_file, format="xml")
            file_statuses[owl_file] = "Valid"
            
            # Check if the ontology IRI is a file URI and fix it
            for s, p, o in g.triples((None, URIRef("http://www.w3.org/2002/07/owl#Ontology"), None)):
                if str(s).startswith("file:///") or not str(s):
                    # Convert file URI to a valid HTTP URI
                    file_path = urllib.parse.unquote(str(s)[8:])  # Remove 'file:///' and decode
                    base_name = os.path.basename(file_path)
                    # Replace spaces with underscores and remove any other non-alphanumeric characters
                    safe_name = ''.join(c if c.isalnum() or c == '_' else '_' for c in base_name.replace(" ", "_"))
                    new_iri = URIRef("http://example.org/ontology/" + safe_name)
                    g.remove((s, None, None))
                    g.add((new_iri, p, o))
                    print(f"Fixed invalid ontology IRI in {owl_file}")
                    
                    # Create a new file name with -fixed suffix
                    fixed_file = os.path.splitext(owl_file)[0] + "-fixed.owl"
                    
                    # Save the fixed ontology
                    g.serialize(destination=fixed_file, format="xml")
                    fixed_files.append(fixed_file)
                    file_statuses[owl_file] = "Fixed"
                    print(f"Fixed version saved as {fixed_file}")
                else:
                    print(f"File {owl_file} is valid. No fixes needed.")
        except exceptions.ParserError as e:
            print(f"Error in file {owl_file}: {str(e)}")
            file_statuses[owl_file] = f"Invalid: {str(e)}"
            
            try:
                # Try to load and fix the ontology using owlready2
                onto = get_ontology(owl_file).load()
                
                # Create a new file name with -fixed suffix
                fixed_file = os.path.splitext(owl_file)[0] + "-fixed.owl"
                
                # Save the fixed ontology
                onto.save(fixed_file)
                fixed_files.append(fixed_file)
                file_statuses[owl_file] = "Fixed"
                print(f"Fixed version saved as {fixed_file}")
            except OwlReadyOntologyParsingError as oe:
                print(f"Unable to fix {owl_file}: {str(oe)}")
                file_statuses[owl_file] = f"Unable to fix: {str(oe)}"
    
    return fixed_files, file_statuses

if __name__ == "__main__":
    fixed_owl_files, file_statuses = fix_owl_files()
    print(f"Fixed {len(fixed_owl_files)} OWL files.")
    print("\nFile Status Report:")
    for file, status in file_statuses.items():
        print(f"{file}: {status}")

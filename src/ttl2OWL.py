#!/usr/bin/env python3
"""
Convert Turtle (.ttl) ontology files to OWL/XML format.

Usage:
    python ttl2OWL.py input.ttl output.owl
    python ttl2OWL.py input.ttl  # Creates input.owl automatically
"""

import sys
import os
import signal
from rdflib import Graph
from rdflib.exceptions import ParserError

# Timeout handler
class TimeoutError(Exception):
    pass

def timeout_handler(signum, frame):
    raise TimeoutError("Operation timed out")

def convert_ttl_to_owl(input_file, output_file=None, timeout=300):
    """
    Convert a Turtle file to OWL/XML format.
    
    Args:
        input_file: Path to input .ttl file
        output_file: Path to output .owl file (optional)
        timeout: Maximum time in seconds (default: 300 = 5 minutes)
    """
    # Generate output filename if not provided
    if output_file is None:
        base = os.path.splitext(input_file)[0]
        output_file = f"{base}.owl"
    
    print(f"Converting {input_file} to {output_file}...")
    print(f"Timeout set to {timeout} seconds")
    
    try:
        # Set up timeout (Unix-like systems only)
        if hasattr(signal, 'SIGALRM'):
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(timeout)
        
        # Create a new graph
        g = Graph()
        
        # Get file size for progress indication
        file_size = os.path.getsize(input_file)
        print(f"Input file size: {file_size:,} bytes ({file_size/1024/1024:.2f} MB)")
        
        # Parse the Turtle file
        print("Parsing Turtle file... (this may take a while for large files)")
        try:
            g.parse(input_file, format='turtle')
            print(f"✓ Successfully parsed {len(g)} triples")
        except ParserError as e:
            print(f"✗ Parser error: {e}")
            print("\nTrying with lenient parsing...")
            # Try again with more lenient settings
            g.parse(input_file, format='turtle', publicID=None)
            print(f"✓ Successfully parsed {len(g)} triples (lenient mode)")
        
        # Cancel timeout
        if hasattr(signal, 'SIGALRM'):
            signal.alarm(0)
        
        # Serialize to OWL/XML format
        print("Serializing to OWL/XML format...")
        g.serialize(destination=output_file, format='xml')
        
        # Get output file size
        output_size = os.path.getsize(output_file)
        print(f"✓ Successfully converted to {output_file}")
        print(f"Output file size: {output_size:,} bytes ({output_size/1024/1024:.2f} MB)")
        return True
        
    except TimeoutError:
        print(f"✗ Conversion timed out after {timeout} seconds")
        print("The file may be too large or complex. Try:")
        print("  1. Splitting the file into smaller parts")
        print("  2. Increasing the timeout value")
        print("  3. Using a more powerful machine")
        return False
    except MemoryError:
        print("✗ Out of memory error")
        print("The file is too large to process. Try:")
        print("  1. Splitting the file into smaller parts")
        print("  2. Using a machine with more RAM")
        return False
    except Exception as e:
        print(f"✗ Error during conversion: {type(e).__name__}: {e}")
        return False
    finally:
        # Make sure to cancel any pending alarm
        if hasattr(signal, 'SIGALRM'):
            signal.alarm(0)

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    # Check if input file exists
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' not found")
        sys.exit(1)
    
    # Optional: custom timeout from command line
    timeout = 300  # 5 minutes default
    if len(sys.argv) > 3:
        try:
            timeout = int(sys.argv[3])
        except ValueError:
            print(f"Warning: Invalid timeout value, using default {timeout}s")
    
    # Perform conversion
    success = convert_ttl_to_owl(input_file, output_file, timeout)
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
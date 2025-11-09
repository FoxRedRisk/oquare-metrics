"""
Test script to show what the reasoner outputs
"""

import owlready2 as owl2

print("="*70)
print("TESTING REASONER OUTPUT")
print("="*70)

# Load ontology
onto = owl2.get_ontology('ontologies/imports/lecture.owl').load()

print("\n1. BEFORE REASONING:")
print(f"   Classes: {len(list(onto.classes()))}")
classes_before = list(onto.classes())
for cls in classes_before:
    print(f"   - {cls.name}")
    print(f"     Direct parents: {[p.name if hasattr(p, 'name') else str(p) for p in cls.is_a]}")

print("\n2. RUNNING HERMIT REASONER...")
with onto:
    owl2.sync_reasoner_hermit(infer_property_values=True)

print("\n3. AFTER REASONING:")
print(f"   Classes: {len(list(onto.classes()))}")
classes_after = list(onto.classes())
for cls in classes_after:
    print(f"   - {cls.name}")
    print(f"     Direct parents: {[p.name if hasattr(p, 'name') else str(p) for p in cls.is_a]}")
    print(f"     All inferred ancestors: {[p.name if hasattr(p, 'name') else str(p) for p in cls.ancestors()]}")

# Check for inferred classes
print("\n4. INFERRED INFORMATION:")
print(f"   New classes added by reasoner: {len(classes_after) - len(classes_before)}")

# Check depth changes
print("\n5. DEPTH CALCULATION:")
for cls in classes_after:
    if not list(cls.subclasses()):  # leaf class
        depth = len(list(cls.ancestors())) - 1  # -1 to exclude self
        print(f"   {cls.name} depth: {depth}")

print("\n6. RELATIONSHIPS:")
thing = owl2.Thing
print(f"   owl:Thing subclasses: {[c.name for c in thing.subclasses() if c != thing and c in onto.classes()]}")

for cls in classes_after:
    subclasses = [c for c in cls.subclasses() if c != cls]
    if subclasses:
        print(f"   {cls.name} subclasses: {[c.name for c in subclasses]}")

print("\n" + "="*70)

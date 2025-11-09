# JAR Decompilation and Fix Guide for ANOnto Bug

This guide provides step-by-step instructions for decompiling, fixing, and recompiling the OQuaRE JAR file to correct the ANOnto annotation counting bug.

---

## Prerequisites

### Required Tools

1. **Java Development Kit (JDK) 8 or higher**
   ```bash
   java -version
   javac -version
   ```

2. **JAR Decompiler** (Choose one):
   - **JD-GUI** (Recommended for viewing): https://java-decompiler.github.io/
   - **CFR** (Recommended for extraction): https://www.benf.org/other/cfr/
   - **Fernflower** (IntelliJ's decompiler)
   - **Procyon**

3. **Build Tool** (if the project uses one):
   - Maven
   - Gradle

4. **Text Editor or IDE**:
   - IntelliJ IDEA (recommended)
   - Eclipse
   - VS Code with Java extensions

---

## Step 1: Extract the JAR File

### Method A: Using jar command (built-in)
```bash
# Navigate to the libs directory
cd libs

# Create a working directory
mkdir oquare-decompiled
cd oquare-decompiled

# Extract the JAR
jar xf ../oquare-versions.jar

# This creates the directory structure with .class files
```

### Method B: Using unzip
```bash
cd libs
mkdir oquare-decompiled
cd oquare-decompiled
unzip ../oquare-versions.jar
```

---

## Step 2: Decompile the Class Files

### Method A: Using CFR (Command Line)

1. **Download CFR:**
   ```bash
   wget https://github.com/leibnitz27/cfr/releases/latest/download/cfr.jar
   # or download manually from https://www.benf.org/other/cfr/
   ```

2. **Decompile all classes:**
   ```bash
   java -jar cfr.jar oquare-versions.jar --outputdir src/
   ```

3. **This creates a `src/` directory with .java files**

### Method B: Using JD-GUI (Visual)

1. **Download and install JD-GUI**
2. **Open the JAR file:** File → Open File → Select `oquare-versions.jar`
3. **Browse the code** to find annotation counting logic
4. **Save all sources:** File → Save All Sources
5. **Extract the ZIP** to get .java files

### Method C: Using IntelliJ IDEA

1. **Open IntelliJ IDEA**
2. **File → Open** → Select `oquare-versions.jar`
3. **IntelliJ will automatically decompile** the classes
4. **Right-click on the JAR** → "Copy to..." → Save decompiled sources

---

## Step 3: Locate the Annotation Counting Code

### Search Strategy

Look for files/classes containing:
- `sumOfAnnotations`
- `ANOnto`
- `getAnnotations()`
- `OWLAnnotation`
- Metric calculation logic

### Likely Locations

```
src/
├── es/upm/oeg/oquare/
│   ├── metrics/
│   │   ├── ANOnto.java          ← Most likely location
│   │   ├── BasicMetrics.java    ← May contain annotation counting
│   │   └── MetricsCalculator.java
│   ├── core/
│   │   └── OntologyAnalyzer.java
│   └── utils/
│       └── AnnotationCounter.java
```

### Search Commands

```bash
# Search for sumOfAnnotations
grep -r "sumOfAnnotations" src/

# Search for ANOnto
grep -r "ANOnto" src/

# Search for annotation counting
grep -r "getAnnotations" src/
```

---

## Step 4: Identify the Bug

### Current (Buggy) Code Pattern

Look for code similar to:

```java
// BUGGY CODE - Only counts ontology-level annotations
public int countAnnotations(OWLOntology ontology) {
    int count = 0;
    
    // Only counting ontology annotations
    for (OWLAnnotation annotation : ontology.getAnnotations()) {
        count++;
    }
    
    return count;
}
```

### What's Missing

The code should also iterate over:
- Classes
- Object Properties
- Data Properties
- Annotation Properties
- Individuals

---

## Step 5: Apply the Fix

### Corrected Code

Replace the buggy method with:

```java
import org.semanticweb.owlapi.model.*;
import java.util.Set;

public int countAnnotations(OWLOntology ontology) {
    int count = 0;
    
    // Count ontology-level annotations
    for (OWLAnnotation annotation : ontology.getAnnotations()) {
        count++;
    }
    
    // Count class annotations
    for (OWLClass owlClass : ontology.getClassesInSignature()) {
        Set<OWLAnnotation> annotations = owlClass.getAnnotations(ontology);
        count += annotations.size();
    }
    
    // Count object property annotations
    for (OWLObjectProperty property : ontology.getObjectPropertiesInSignature()) {
        Set<OWLAnnotation> annotations = property.getAnnotations(ontology);
        count += annotations.size();
    }
    
    // Count data property annotations
    for (OWLDataProperty property : ontology.getDataPropertiesInSignature()) {
        Set<OWLAnnotation> annotations = property.getAnnotations(ontology);
        count += annotations.size();
    }
    
    // Count annotation property annotations
    for (OWLAnnotationProperty property : ontology.getAnnotationPropertiesInSignature()) {
        Set<OWLAnnotation> annotations = property.getAnnotations(ontology);
        count += annotations.size();
    }
    
    // Count individual annotations
    for (OWLNamedIndividual individual : ontology.getIndividualsInSignature()) {
        Set<OWLAnnotation> annotations = individual.getAnnotations(ontology);
        count += annotations.size();
    }
    
    return count;
}
```

### Add Logging (Optional but Recommended)

```java
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public int countAnnotations(OWLOntology ontology) {
    Logger logger = LoggerFactory.getLogger(this.getClass());
    int count = 0;
    
    // Count ontology-level annotations
    int ontologyAnnotations = ontology.getAnnotations().size();
    count += ontologyAnnotations;
    logger.debug("Ontology annotations: {}", ontologyAnnotations);
    
    // Count class annotations
    int classAnnotations = 0;
    for (OWLClass owlClass : ontology.getClassesInSignature()) {
        classAnnotations += owlClass.getAnnotations(ontology).size();
    }
    count += classAnnotations;
    logger.debug("Class annotations: {}", classAnnotations);
    
    // Count object property annotations
    int objectPropertyAnnotations = 0;
    for (OWLObjectProperty property : ontology.getObjectPropertiesInSignature()) {
        objectPropertyAnnotations += property.getAnnotations(ontology).size();
    }
    count += objectPropertyAnnotations;
    logger.debug("Object property annotations: {}", objectPropertyAnnotations);
    
    // Count data property annotations
    int dataPropertyAnnotations = 0;
    for (OWLDataProperty property : ontology.getDataPropertiesInSignature()) {
        dataPropertyAnnotations += property.getAnnotations(ontology).size();
    }
    count += dataPropertyAnnotations;
    logger.debug("Data property annotations: {}", dataPropertyAnnotations);
    
    // Count annotation property annotations
    int annotationPropertyAnnotations = 0;
    for (OWLAnnotationProperty property : ontology.getAnnotationPropertiesInSignature()) {
        annotationPropertyAnnotations += property.getAnnotations(ontology).size();
    }
    count += annotationPropertyAnnotations;
    logger.debug("Annotation property annotations: {}", annotationPropertyAnnotations);
    
    // Count individual annotations
    int individualAnnotations = 0;
    for (OWLNamedIndividual individual : ontology.getIndividualsInSignature()) {
        individualAnnotations += individual.getAnnotations(ontology).size();
    }
    count += individualAnnotations;
    logger.debug("Individual annotations: {}", individualAnnotations);
    
    logger.info("Total annotations: {}", count);
    return count;
}
```

---

## Step 6: Recompile the Code

### Method A: Using javac (if no build tool)

```bash
# Navigate to the source directory
cd src

# Compile all Java files
# Note: You'll need the OWL API and other dependencies in the classpath
javac -cp "path/to/owlapi.jar:path/to/other/dependencies.jar" \
      -d ../classes \
      $(find . -name "*.java")

# Create the new JAR
cd ../classes
jar cvf ../../oquare-versions-fixed.jar .
```

### Method B: Using Maven (if pom.xml exists)

```bash
# If you find a pom.xml in the decompiled sources
mvn clean compile package

# The new JAR will be in target/
cp target/oquare-versions-*.jar ../oquare-versions-fixed.jar
```

### Method C: Using Gradle (if build.gradle exists)

```bash
# If you find a build.gradle
gradle clean build

# The new JAR will be in build/libs/
cp build/libs/oquare-versions-*.jar ../oquare-versions-fixed.jar
```

---

## Step 7: Test the Fixed JAR

### Create a Test Script

```bash
#!/bin/bash
# test_fixed_jar.sh

echo "Testing original JAR..."
java -jar libs/oquare-versions.jar \
    --ontology ontologies/imports/bfo-core.owl \
    --outputFile output/test_original.xml \
    --reasoner HermiT

echo "Testing fixed JAR..."
java -jar libs/oquare-versions-fixed.jar \
    --ontology ontologies/imports/bfo-core.owl \
    --outputFile output/test_fixed.xml \
    --reasoner HermiT

echo "Comparing results..."
echo "Original sumOfAnnotations:"
grep "sumOfAnnotations" output/test_original.xml

echo "Fixed sumOfAnnotations:"
grep "sumOfAnnotations" output/test_fixed.xml
```

### Run the Test

```bash
chmod +x test_fixed_jar.sh
./test_fixed_jar.sh
```

### Expected Results

**Original JAR:**
```xml
<sumOfAnnotations>36</sumOfAnnotations>
```

**Fixed JAR:**
```xml
<sumOfAnnotations>357</sumOfAnnotations>
```

---

## Step 8: Validate with Python Script

```bash
# Run the validation script
python test_annotation_count.py ontologies/imports/bfo-core.owl 357

# Should show:
# OQuaRE reported (sumOfAnnotations): 357
# Manual count (all annotations):     357
# Difference:                         0
# ✓ OQuaRE count matches expected total - no issue found
```

---

## Step 9: Deploy the Fixed JAR

### Option A: Replace in Project

```bash
# Backup the original
cp libs/oquare-versions.jar libs/oquare-versions.jar.backup

# Deploy the fixed version
cp libs/oquare-versions-fixed.jar libs/oquare-versions.jar
```

### Option B: Use Fixed Version Explicitly

Update `src/main.py` to use the fixed JAR:

```python
jar_path = os.path.abspath(os.path.join(script_dir, "../libs/oquare-versions-fixed.jar"))
```

---

## Troubleshooting

### Issue: Missing Dependencies

**Error:**
```
error: package org.semanticweb.owlapi.model does not exist
```

**Solution:**
Download the OWL API JAR and add to classpath:
```bash
wget https://repo1.maven.org/maven2/net/sourceforge/owlapi/owlapi-distribution/5.1.20/owlapi-distribution-5.1.20.jar
```

### Issue: Compilation Errors

**Error:**
```
error: cannot find symbol
```

**Solution:**
1. Check that all dependencies are in the classpath
2. Verify the Java version matches the original compilation
3. Look for missing imports in the decompiled code

### Issue: Runtime Errors

**Error:**
```
java.lang.NoClassDefFoundError
```

**Solution:**
1. Ensure all dependencies are packaged in the JAR
2. Use `jar tf oquare-versions-fixed.jar` to verify contents
3. Compare with original JAR structure

---

## Alternative: Patch Without Full Recompilation

If full recompilation is difficult, you can:

1. **Decompile only the affected class**
2. **Fix and recompile just that class**
3. **Replace the .class file in the JAR**

```bash
# Extract the JAR
mkdir temp
cd temp
jar xf ../oquare-versions.jar

# Replace the fixed .class file
cp /path/to/fixed/ANOnto.class es/upm/oeg/oquare/metrics/

# Repackage the JAR
jar cvf ../oquare-versions-fixed.jar .
```

---

## Contributing the Fix

Once you've successfully fixed and tested the JAR:

1. **Document your changes**
2. **Create a pull request** to the OQuaRE repository
3. **Include test cases** demonstrating the fix
4. **Update the documentation** to reflect the corrected behavior

---

## References

- **OWL API Documentation:** https://github.com/owlcs/owlapi/wiki
- **Java Decompiler Tools:** https://java-decompiler.github.io/
- **Maven Central (for dependencies):** https://search.maven.org/

---

**Document Version:** 1.0  
**Last Updated:** 2025-10-27
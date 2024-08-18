param (
    [Parameter(Mandatory=$true)][string]$InputPath,
    [Parameter(Mandatory=$true)][string]$SourceFolder,
    [Parameter(Mandatory=$true)][string]$OntologyFile,
    [Parameter(Mandatory=$true)][string]$Reasoner,
    [switch]$ModelPlot,
    [switch]$CharacteristicsPlot,
    [switch]$SubcharacteristicsPlot,
    [switch]$MetricsPlot,
    [switch]$EvolutionPlot
)

# Function to log messages
function Log-Message {
    param([string]$message)
    Write-Host "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') - $message"
}

# Function to handle errors
function Handle-Error {
    param([string]$errorMessage)
    Log-Message "Error: $errorMessage"
    Log-Message "Last command executed: $($MyInvocation.MyCommand.Name)"
    Log-Message "Current working directory: $(Get-Location)"
    Log-Message "Contents of current directory:"
    Get-ChildItem | Format-Table Name, Length, LastWriteTime
    exit 1
}

# Set error action preference
$ErrorActionPreference = "Stop"

# Log script start
Log-Message "Starting fullparse.ps1"
Log-Message "Arguments: InputPath=$InputPath, SourceFolder=$SourceFolder, OntologyFile=$OntologyFile, Reasoner=$Reasoner"

# Set the input and output directories
$contents_folder = $InputPath
$temp_results_folder = Join-Path $contents_folder "temp_results"

# Create the output directory structure
$dir = [System.IO.Path]::GetFileNameWithoutExtension($OntologyFile)
$date = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
$outputFile = $dir
$outputFilePath = Join-Path $temp_results_folder $dir $outputFile $date "metrics" "$outputFile.xml"

# Create the output directory if it doesn't exist
Log-Message "Creating output directory: $([System.IO.Path]::GetDirectoryName($outputFilePath))"
New-Item -ItemType Directory -Force -Path ([System.IO.Path]::GetDirectoryName($outputFilePath)) | Out-Null

# Run the Java command to process the ontology file
Log-Message "Processing individual ontology file: $OntologyFile"
Log-Message "Ontology file: $OntologyFile"
Log-Message "Output file path: $outputFilePath"
Log-Message "Checking if ontology file exists:"
if (Test-Path $OntologyFile) {
    Log-Message "Ontology file exists"
} else {
    Handle-Error "Ontology file does not exist"
}

$java_command = "java -jar .\libs\oquare-versions.jar --ontology `"$OntologyFile`" --reasoner `"$Reasoner`" --outputFile `"$outputFilePath`""
Log-Message "Executing Java command: $java_command"

try {
    $java_output = & java -jar .\libs\oquare-versions.jar --ontology "$OntologyFile" --reasoner "$Reasoner" --outputFile "$outputFilePath" 2>&1
    $java_exit_code = $LASTEXITCODE
    
    if ($java_exit_code -eq 0) {
        Log-Message "Java command completed successfully"
        Log-Message "Java command output:"
        $java_output | ForEach-Object { Log-Message $_ }
    } else {
        Log-Message "Java command failed with exit code: $java_exit_code"
        Log-Message "Java command error output:"
        $java_output | ForEach-Object { Log-Message $_ }
        Handle-Error "Java command failed"
    }
} catch {
    Handle-Error "Exception occurred while running Java command: $_"
}

if (Test-Path $outputFilePath) {
    Log-Message "Metrics file generated successfully: $outputFilePath"
    Log-Message "File size: $((Get-Item $outputFilePath).Length) bytes"
    Log-Message "File contents (first 10 lines):"
    Get-Content $outputFilePath -TotalCount 10 | ForEach-Object { Log-Message $_ }
} else {
    Handle-Error "Metrics file was not generated: $outputFilePath"
}

Log-Message "fullparse.ps1 completed"

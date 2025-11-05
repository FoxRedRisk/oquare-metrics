"""VirusTotal API client."""
import hashlib
import os
import requests
from typing import Dict, Any, Optional


class VirusTotalClient:
    """Client for interacting with VirusTotal API."""
    
    API_BASE_URL = "https://www.virustotal.com/api/v3"
    
    def __init__(self, api_key: str):
        """
        Initialize VirusTotal client.
        
        Args:
            api_key: VirusTotal API key
        """
        self.api_key = api_key
        self.headers = {
            "x-apikey": api_key,
            "Accept": "application/json"
        }
    
    @staticmethod
    def calculate_file_hash(file_path: str) -> str:
        """
        Calculate SHA-256 hash of a file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            SHA-256 hash as hex string
        """
        sha256_hash = hashlib.sha256()
        
        with open(file_path, "rb") as f:
            # Read file in chunks to handle large files
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        
        return sha256_hash.hexdigest()
    
    def get_file_report(self, file_hash: str) -> Dict[str, Any]:
        """
        Get file report from VirusTotal.
        
        Args:
            file_hash: SHA-256 hash of the file
            
        Returns:
            Dictionary containing scan results
            
        Raises:
            requests.RequestException: If API request fails
        """
        url = f"{self.API_BASE_URL}/files/{file_hash}"
        
        response = requests.get(url, headers=self.headers, timeout=30)
        
        if response.status_code == 404:
            # File not found in VirusTotal database
            return {
                'status': 'not_found',
                'message': 'File not found in VirusTotal database',
                'hash': file_hash
            }
        elif response.status_code == 200:
            data = response.json()
            return self._parse_response(data)
        else:
            # Handle other errors
            return {
                'status': 'error',
                'message': f'API error: {response.status_code}',
                'hash': file_hash,
                'error_detail': response.text
            }
    
    def _parse_response(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse VirusTotal API response.
        
        Args:
            data: Raw API response
            
        Returns:
            Parsed scan results
        """
        if 'data' not in data or 'attributes' not in data['data']:
            return {
                'status': 'error',
                'message': 'Invalid API response format'
            }
        
        attributes = data['data']['attributes']
        stats = attributes.get('last_analysis_stats', {})
        results = attributes.get('last_analysis_results', {})
        
        # Parse individual antivirus results
        detections = []
        for av_name, av_result in results.items():
            if av_result.get('category') in ['malicious', 'suspicious']:
                detections.append({
                    'engine': av_name,
                    'category': av_result.get('category', 'unknown'),
                    'result': av_result.get('result', 'Unknown'),
                    'method': av_result.get('method', 'unknown')
                })
        
        return {
            'status': 'success',
            'hash': data['data']['id'],
            'scan_date': attributes.get('last_analysis_date'),
            'stats': {
                'malicious': stats.get('malicious', 0),
                'suspicious': stats.get('suspicious', 0),
                'undetected': stats.get('undetected', 0),
                'harmless': stats.get('harmless', 0),
                'timeout': stats.get('timeout', 0),
                'failure': stats.get('failure', 0)
            },
            'detections': detections,
            'total_engines': len(results),
            'permalink': f"https://www.virustotal.com/gui/file/{data['data']['id']}"
        }
    
    def scan_file(self, file_path: str) -> Dict[str, Any]:
        """
        Scan a file using VirusTotal.
        
        This method calculates the file hash and checks if a report exists.
        
        Args:
            file_path: Path to the file to scan
            
        Returns:
            Dictionary containing scan results
        """
        try:
            if not os.path.exists(file_path):
                return {
                    'status': 'error',
                    'message': f'File not found: {file_path}',
                    'file_path': file_path
                }
            
            # Calculate file hash
            file_hash = self.calculate_file_hash(file_path)
            
            # Get report
            result = self.get_file_report(file_hash)
            result['file_path'] = file_path
            result['file_name'] = os.path.basename(file_path)
            result['file_size'] = os.path.getsize(file_path)
            
            return result
            
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e),
                'file_path': file_path
            }

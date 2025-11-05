"""Report generator for VirusTotal scan results."""
import json
import os
from datetime import datetime
from typing import Dict, List, Any


class ReportGenerator:
    """Generates HTML and JSON reports from scan results."""
    
    def __init__(self, scan_results: List[Dict[str, Any]]):
        """
        Initialize report generator.
        
        Args:
            scan_results: List of scan results from VirusTotal
        """
        self.scan_results = scan_results
        self.stats = self._calculate_stats()
    
    def _calculate_stats(self) -> Dict[str, Any]:
        """Calculate statistics from scan results."""
        stats = {
            'total_files': len(self.scan_results),
            'clean_files': 0,
            'infected_files': 0,
            'suspicious_files': 0,
            'not_found': 0,
            'errors': 0,
            'cached': 0,
            'api_calls': 0
        }
        
        for result in self.scan_results:
            if result.get('from_cache'):
                stats['cached'] += 1
            else:
                stats['api_calls'] += 1
            
            status = result.get('status')
            if status == 'success':
                malicious = result.get('stats', {}).get('malicious', 0)
                suspicious = result.get('stats', {}).get('suspicious', 0)
                
                if malicious > 0:
                    stats['infected_files'] += 1
                elif suspicious > 0:
                    stats['suspicious_files'] += 1
                else:
                    stats['clean_files'] += 1
            elif status == 'not_found':
                stats['not_found'] += 1
            elif status == 'error':
                stats['errors'] += 1
        
        return stats
    
    def generate_json(self, output_file: str) -> None:
        """
        Generate JSON report.
        
        Args:
            output_file: Path to output JSON file
        """
        report = {
            'generated_at': datetime.now().isoformat(),
            'statistics': self.stats,
            'results': self.scan_results
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
    
    def generate_markdown(self, output_file: str) -> None:
        """
        Generate Markdown report.
        
        Args:
            output_file: Path to output Markdown file
        """
        markdown = self._generate_markdown_content()
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(markdown)
    
    def generate_html(self, output_file: str) -> None:
        """
        Generate HTML report.
        
        Args:
            output_file: Path to output HTML file
        """
        html = self._generate_html_content()
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html)
    
    def _get_threat_files(self) -> List[Dict[str, Any]]:
        """Extract and sort files with threats."""
        threat_files = []
        for result in self.scan_results:
            if result.get('status') == 'success':
                malicious = result.get('stats', {}).get('malicious', 0)
                suspicious = result.get('stats', {}).get('suspicious', 0)
                
                if malicious > 0 or suspicious > 0:
                    threat_files.append(result)
        
        # Sort by number of detections (descending)
        threat_files.sort(key=lambda x: x.get('stats', {}).get('malicious', 0) + 
                          x.get('stats', {}).get('suspicious', 0), reverse=True)
        return threat_files
    
    def _generate_html_header(self) -> str:
        """Generate HTML header section."""
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VirusTotal Scan Report</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        .header h1 {{
            margin: 0 0 10px 0;
            font-size: 2.5em;
        }}
        .header p {{
            margin: 5px 0;
            opacity: 0.9;
        }}
        .section {{
            background: white;
            padding: 25px;
            margin-bottom: 25px;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .section h2 {{
            color: #333;
            border-bottom: 3px solid #667eea;
            padding-bottom: 10px;
            margin-top: 0;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        .stat-card {{
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }}
        .stat-card.total {{ background: #e3f2fd; color: #1976d2; }}
        .stat-card.clean {{ background: #e8f5e9; color: #388e3c; }}
        .stat-card.infected {{ background: #ffebee; color: #d32f2f; }}
        .stat-card.suspicious {{ background: #fff3e0; color: #f57c00; }}
        .stat-card.not-found {{ background: #f3e5f5; color: #7b1fa2; }}
        .stat-card.error {{ background: #fce4ec; color: #c2185b; }}
        .stat-value {{
            font-size: 2.5em;
            font-weight: bold;
            margin: 10px 0;
        }}
        .stat-label {{
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background-color: #667eea;
            color: white;
            font-weight: 600;
            position: sticky;
            top: 0;
        }}
        tr:hover {{
            background-color: #f5f5f5;
        }}
        .status-badge {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 0.85em;
            font-weight: 600;
        }}
        .status-clean {{ background: #c8e6c9; color: #2e7d32; }}
        .status-infected {{ background: #ffcdd2; color: #c62828; }}
        .status-suspicious {{ background: #ffe0b2; color: #e65100; }}
        .status-not-found {{ background: #e1bee7; color: #6a1b9a; }}
        .status-error {{ background: #f8bbd0; color: #ad1457; }}
        .detections {{
            font-size: 0.9em;
            color: #666;
        }}
        .detection-item {{
            background: #fff3e0;
            padding: 8px 12px;
            margin: 5px 0;
            border-radius: 5px;
            border-left: 3px solid #ff9800;
        }}
        .detection-engine {{
            font-weight: 600;
            color: #e65100;
        }}
        a {{
            color: #667eea;
            text-decoration: none;
        }}
        a:hover {{
            text-decoration: underline;
        }}
        .file-name {{
            font-weight: 500;
            color: #333;
        }}
        .file-size {{
            color: #666;
            font-size: 0.9em;
        }}
        .alert {{
            padding: 15px;
            margin: 20px 0;
            border-radius: 5px;
            border-left: 4px solid;
        }}
        .alert-warning {{
            background: #fff3cd;
            border-color: #ffc107;
            color: #856404;
        }}
        .alert-danger {{
            background: #f8d7da;
            border-color: #dc3545;
            color: #721c24;
        }}
        .alert-success {{
            background: #d4edda;
            border-color: #28a745;
            color: #155724;
        }}
        .timestamp {{
            color: #999;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🛡️ VirusTotal Scan Report</h1>
        <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p>Total Files Scanned: {self.stats['total_files']}</p>
    </div>
"""
    
    def _generate_statistics_section(self) -> str:
        """Generate statistics section HTML."""
        html = f"""
    <div class="section">
        <h2>📊 Executive Summary</h2>
        <div class="stats-grid">
            <div class="stat-card total">
                <div class="stat-value">{self.stats['total_files']}</div>
                <div class="stat-label">Total Files</div>
            </div>
            <div class="stat-card clean">
                <div class="stat-value">{self.stats['clean_files']}</div>
                <div class="stat-label">Clean Files</div>
            </div>
            <div class="stat-card infected">
                <div class="stat-value">{self.stats['infected_files']}</div>
                <div class="stat-label">Infected Files</div>
            </div>
            <div class="stat-card suspicious">
                <div class="stat-value">{self.stats['suspicious_files']}</div>
                <div class="stat-label">Suspicious Files</div>
            </div>
            <div class="stat-card not-found">
                <div class="stat-value">{self.stats['not_found']}</div>
                <div class="stat-label">Not Found</div>
            </div>
            <div class="stat-card error">
                <div class="stat-value">{self.stats['errors']}</div>
                <div class="stat-label">Errors</div>
            </div>
        </div>
        <p><strong>Cache Performance:</strong> {self.stats['cached']} files from cache, {self.stats['api_calls']} API calls made</p>
"""
        
        # Add alerts
        if self.stats['infected_files'] > 0:
            html += f"""
        <div class="alert alert-danger">
            <strong>⚠️ Warning:</strong> {self.stats['infected_files']} infected file(s) detected! Review the details below.
        </div>
"""
        elif self.stats['suspicious_files'] > 0:
            html += f"""
        <div class="alert alert-warning">
            <strong>⚠️ Caution:</strong> {self.stats['suspicious_files']} suspicious file(s) detected. Further investigation recommended.
        </div>
"""
        else:
            html += """
        <div class="alert alert-success">
            <strong>✅ All Clear:</strong> No threats detected in scanned files.
        </div>
"""
        
        html += "    </div>\n"
        return html
    
    def _build_detection_list(self, detections: List[Dict[str, Any]]) -> str:
        """Build HTML for detection list."""
        av_list = []
        for det in detections:
            av_list.append(f"<div class='detection-item'>"
                         f"<span class='detection-engine'>{det['engine']}</span>: "
                         f"{det['result']} ({det['category']})</div>")
        return ''.join(av_list) if av_list else 'No detailed detection info'
    
    def _generate_threats_section(self, threat_files: List[Dict[str, Any]]) -> str:
        """Generate threats section HTML."""
        if not threat_files:
            return ""
        
        html = """
    <div class="section">
        <h2>🚨 Detected Threats</h2>
        <table>
            <thead>
                <tr>
                    <th>File</th>
                    <th>Detections</th>
                    <th>Antivirus Engines</th>
                    <th>Link</th>
                </tr>
            </thead>
            <tbody>
"""
        
        for result in threat_files:
            file_name = result.get('file_name', 'Unknown')
            file_path = result.get('file_path', '')
            malicious = result.get('stats', {}).get('malicious', 0)
            suspicious = result.get('stats', {}).get('suspicious', 0)
            total_detections = malicious + suspicious
            detections = result.get('detections', [])
            permalink = result.get('permalink', '#')
            
            av_html = self._build_detection_list(detections)
            badge_class = 'status-infected' if malicious > 0 else 'status-suspicious'
            
            html += f"""
                <tr>
                    <td>
                        <div class="file-name">{file_name}</div>
                        <div class="file-size">{file_path}</div>
                    </td>
                    <td>
                        <span class="{badge_class} status-badge">
                            {total_detections} / {result.get('total_engines', 0)} engines
                        </span>
                    </td>
                    <td>
                        <div class="detections">{av_html}</div>
                    </td>
                    <td>
                        <a href="{permalink}" target="_blank">View on VT</a>
                    </td>
                </tr>
"""
        
        html += """
            </tbody>
        </table>
    </div>
"""
        return html
    
    def _format_file_size(self, file_size: int) -> str:
        """Format file size to human-readable string."""
        if file_size < 1024:
            return f"{file_size} B"
        elif file_size < 1024 * 1024:
            return f"{file_size / 1024:.1f} KB"
        else:
            return f"{file_size / (1024 * 1024):.1f} MB"
    
    def _get_status_info(self, result: Dict[str, Any]) -> tuple:
        """Get status badge, detection info, and details for a result."""
        status = result.get('status', 'unknown')
        
        if status == 'success':
            stats = result.get('stats', {})
            malicious = stats.get('malicious', 0)
            suspicious = stats.get('suspicious', 0)
            total_engines = result.get('total_engines', 0)
            permalink = result.get('permalink', '#')
            
            if malicious > 0:
                status_badge = '<span class="status-badge status-infected">Infected</span>'
                detection_info = f"{malicious + suspicious} / {total_engines} engines"
            elif suspicious > 0:
                status_badge = '<span class="status-badge status-suspicious">Suspicious</span>'
                detection_info = f"{suspicious} / {total_engines} engines"
            else:
                status_badge = '<span class="status-badge status-clean">Clean</span>'
                detection_info = f"0 / {total_engines} engines"
            
            details = f'<a href="{permalink}" target="_blank">View Report</a>'
            
        elif status == 'not_found':
            status_badge = '<span class="status-badge status-not-found">Not Found</span>'
            detection_info = 'N/A'
            details = 'File not in VirusTotal database'
        else:
            status_badge = '<span class="status-badge status-error">Error</span>'
            detection_info = 'N/A'
            details = result.get('message', 'Unknown error')
        
        return status_badge, detection_info, details
    
    def _generate_all_results_section(self) -> str:
        """Generate all results section HTML."""
        html = """
    <div class="section">
        <h2>📋 All Scan Results</h2>
        <table>
            <thead>
                <tr>
                    <th>File</th>
                    <th>Status</th>
                    <th>Detections</th>
                    <th>Details</th>
                </tr>
            </thead>
            <tbody>
"""
        
        for result in self.scan_results:
            file_name = result.get('file_name', 'Unknown')
            file_path = result.get('file_path', '')
            file_size = result.get('file_size', 0)
            
            size_str = self._format_file_size(file_size)
            status_badge, detection_info, details = self._get_status_info(result)
            cache_indicator = ' (cached)' if result.get('from_cache') else ''
            
            html += f"""
                <tr>
                    <td>
                        <div class="file-name">{file_name}</div>
                        <div class="file-size">{size_str} - {file_path}{cache_indicator}</div>
                    </td>
                    <td>{status_badge}</td>
                    <td>{detection_info}</td>
                    <td>{details}</td>
                </tr>
"""
        
        html += """
            </tbody>
        </table>
    </div>
</body>
</html>
"""
        return html
    
    def _generate_markdown_header(self, timestamp: str) -> str:
        """Generate Markdown header and executive summary."""
        return f"""# 🛡️ VirusTotal Scan Report

**Generated:** {timestamp}  
**Total Files Scanned:** {self.stats['total_files']}

---

## 📊 Executive Summary

| Metric | Count |
|--------|-------|
| **Total Files** | {self.stats['total_files']} |
| **Clean Files** | {self.stats['clean_files']} |
| **Infected Files** | {self.stats['infected_files']} |
| **Suspicious Files** | {self.stats['suspicious_files']} |
| **Not Found** | {self.stats['not_found']} |
| **Errors** | {self.stats['errors']} |

**Cache Performance:** {self.stats['cached']} files from cache, {self.stats['api_calls']} API calls made

"""
    
    def _generate_markdown_alert(self) -> str:
        """Generate Markdown alert based on scan results."""
        if self.stats['infected_files'] > 0:
            return f"""### ⚠️ Warning
**{self.stats['infected_files']} infected file(s) detected!** Review the details below.

"""
        elif self.stats['suspicious_files'] > 0:
            return f"""### ⚠️ Caution
**{self.stats['suspicious_files']} suspicious file(s) detected.** Further investigation recommended.

"""
        else:
            return """### ✅ All Clear
No threats detected in scanned files.

"""
    
    def _generate_markdown_threat_details(self, result: Dict[str, Any]) -> str:
        """Generate Markdown details for a single threat file."""
        file_name = result.get('file_name', 'Unknown')
        file_path = result.get('file_path', '')
        file_hash = result.get('file_hash', 'N/A')
        file_size = result.get('file_size', 0)
        scan_date = result.get('scan_date', 'N/A')
        malicious = result.get('stats', {}).get('malicious', 0)
        suspicious = result.get('stats', {}).get('suspicious', 0)
        undetected = result.get('stats', {}).get('undetected', 0)
        total_detections = malicious + suspicious
        total_engines = result.get('total_engines', 0)
        detections = result.get('detections', [])
        permalink = result.get('permalink', '#')
        
        status_emoji = '🔴' if malicious > 0 else '🟡'
        size_str = self._format_file_size(file_size)
        threat_type = 'Malicious' if malicious > 0 else 'Suspicious'
        
        md = f"""### {status_emoji} {file_name}

**File Information:**
- **File Path:** `{file_path}`
- **File Size:** {size_str}
- **SHA-256:** `{file_hash}`
- **Scan Date:** {scan_date}

**Detection Summary:**
- **Threat Level:** {threat_type}
- **Detections:** {total_detections} / {total_engines} antivirus engines
  - Malicious: {malicious}
  - Suspicious: {suspicious}
  - Undetected: {undetected}
- **VirusTotal Report:** [View Full Analysis]({permalink})

"""
        
        if detections:
            md += "**Detailed Antivirus Detections:**\n\n"
            md += "| Antivirus Engine | Detection Name | Category |\n"
            md += "|------------------|----------------|----------|\n"
            for det in detections:
                engine = det['engine']
                result_name = det['result']
                category = det['category']
                md += f"| {engine} | `{result_name}` | {category} |\n"
            md += "\n"
        
        return md
    
    def _generate_markdown_threats_section(self, threat_files: List[Dict[str, Any]]) -> str:
        """Generate Markdown threats section."""
        if not threat_files:
            return ""
        
        md = "## 🚨 Detected Threats\n\n"
        for result in threat_files:
            md += self._generate_markdown_threat_details(result)
        
        return md
    
    def _get_markdown_status_info(self, result: Dict[str, Any]) -> tuple:
        """Get status text, detection info, and details for markdown."""
        status = result.get('status', 'unknown')
        
        if status == 'success':
            stats = result.get('stats', {})
            malicious = stats.get('malicious', 0)
            suspicious = stats.get('suspicious', 0)
            total_engines = result.get('total_engines', 0)
            permalink = result.get('permalink', '#')
            
            if malicious > 0:
                status_text = '🔴 Infected'
                detection_info = f"{malicious + suspicious} / {total_engines}"
            elif suspicious > 0:
                status_text = '🟡 Suspicious'
                detection_info = f"{suspicious} / {total_engines}"
            else:
                status_text = '✅ Clean'
                detection_info = f"0 / {total_engines}"
            
            details = f"[Report]({permalink})"
            
        elif status == 'not_found':
            status_text = '🟣 Not Found'
            detection_info = 'N/A'
            details = 'Not in VT database'
        else:
            status_text = '❌ Error'
            detection_info = 'N/A'
            details = result.get('message', 'Unknown error')
        
        return status_text, detection_info, details
    
    def _generate_markdown_all_results(self) -> str:
        """Generate Markdown all results section."""
        md = "---\n\n## 📋 All Scan Results\n\n"
        md += "| File | Status | Detections | Details |\n"
        md += "|------|--------|------------|----------|\n"
        
        for result in self.scan_results:
            file_name = result.get('file_name', 'Unknown')
            file_path = result.get('file_path', '')
            file_size = result.get('file_size', 0)
            
            size_str = self._format_file_size(file_size)
            cache_indicator = ' (cached)' if result.get('from_cache') else ''
            status_text, detection_info, details = self._get_markdown_status_info(result)
            
            # Escape pipe characters in file paths
            file_path_escaped = file_path.replace('|', '\\|')
            file_name_escaped = file_name.replace('|', '\\|')
            
            md += f"| `{file_name_escaped}`<br>{size_str} - {file_path_escaped}{cache_indicator} | {status_text} | {detection_info} | {details} |\n"
        
        return md
    
    def _generate_markdown_content(self) -> str:
        """Generate Markdown content for report."""
        threat_files = self._get_threat_files()
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        md = self._generate_markdown_header(timestamp)
        md += self._generate_markdown_alert()
        md += "---\n\n"
        md += self._generate_markdown_threats_section(threat_files)
        md += self._generate_markdown_all_results()
        
        return md
    
    def _generate_html_content(self) -> str:
        """Generate HTML content for report."""
        threat_files = self._get_threat_files()
        
        html = self._generate_html_header()
        html += self._generate_statistics_section()
        html += self._generate_threats_section(threat_files)
        html += self._generate_all_results_section()
        
        return html

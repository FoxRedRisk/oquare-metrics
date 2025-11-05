#!/usr/bin/env python3
"""VirusTotal Scanner - CLI tool for scanning files with VirusTotal API."""
import argparse
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

from lib.vt_client import VirusTotalClient
from lib.cache import CacheManager
from lib.rate_limiter import RateLimiter
from lib.report_generator import ReportGenerator


def get_files_to_scan(folder_path: str) -> list:
    """
    Get list of files to scan from folder.
    
    Args:
        folder_path: Path to folder to scan
        
    Returns:
        List of file paths
    """
    files = []
    folder = Path(folder_path)
    
    if not folder.exists():
        print(f"Error: Folder '{folder_path}' does not exist.")
        return files
    
    if not folder.is_dir():
        print(f"Error: '{folder_path}' is not a directory.")
        return files
    
    # Recursively get all files
    for file_path in folder.rglob('*'):
        if file_path.is_file():
            files.append(str(file_path))
    
    return files


def scan_single_file(file_path: str, vt_client: VirusTotalClient, 
                     cache: CacheManager, rate_limiter: RateLimiter) -> dict:
    """
    Scan a single file using VirusTotal API.
    
    Args:
        file_path: Path to file to scan
        vt_client: VirusTotal API client
        cache: Cache manager instance
        rate_limiter: Rate limiter instance
        
    Returns:
        Scan result dictionary
    """
    file_name = os.path.basename(file_path)
    file_hash = vt_client.calculate_file_hash(file_path)
    
    # Check cache first
    cached_result = cache.get(file_hash)
    
    if cached_result:
        print("✓ (cached)")
        result = cached_result['scan_result']
        result['from_cache'] = True
        return result
    
    # Check if we can make request
    remaining = rate_limiter.get_remaining_daily_requests()
    if remaining <= 0:
        print("⚠ (daily limit reached)")
        return {
            'status': 'error',
            'message': 'Daily API limit reached',
            'file_path': file_path,
            'file_name': file_name
        }
    
    # Wait if needed for rate limiting
    wait_time = rate_limiter.wait_if_needed()
    if wait_time > 0:
        print(f"(waited {wait_time:.1f}s) ", end='')
    
    # Scan file
    result = vt_client.scan_file(file_path)
    rate_limiter.record_request()
    result['from_cache'] = False
    
    # Cache the result if successful
    if result.get('status') == 'success':
        cache.set(file_hash, file_path, result)
        print("✓")
    elif result.get('status') == 'not_found':
        cache.set(file_hash, file_path, result)
        print("⚠ (not found)")
    else:
        print("✗ (error)")
    
    return result


def scan_files(files: list, vt_client: VirusTotalClient, 
               cache: CacheManager, rate_limiter: RateLimiter) -> dict:
    """
    Scan multiple files using VirusTotal API.
    
    Args:
        files: List of file paths to scan
        vt_client: VirusTotal API client
        cache: Cache manager instance
        rate_limiter: Rate limiter instance
        
    Returns:
        Dictionary with scan results and statistics
    """
    results = []
    files_scanned = 0
    files_from_cache = 0
    api_calls_made = 0
    
    for i, file_path in enumerate(files, 1):
        file_name = os.path.basename(file_path)
        print(f"[{i}/{len(files)}] Scanning: {file_name}", end=' ')
        
        try:
            result = scan_single_file(file_path, vt_client, cache, rate_limiter)
            
            if result.get('from_cache'):
                files_from_cache += 1
            elif result.get('status') != 'error' or 'Daily API limit' not in result.get('message', ''):
                api_calls_made += 1
            
            results.append(result)
            files_scanned += 1
            
        except KeyboardInterrupt:
            print("\n\nScan interrupted by user.")
            break
        except Exception as e:
            print(f"✗ (error: {e})")
            results.append({
                'status': 'error',
                'message': str(e),
                'file_path': file_path,
                'file_name': file_name
            })
    
    return {
        'results': results,
        'files_scanned': files_scanned,
        'files_from_cache': files_from_cache,
        'api_calls_made': api_calls_made
    }


def generate_reports(results: list, output_path: str, formats: list):
    """
    Generate reports in specified formats.
    
    Args:
        results: List of scan results
        output_path: Base output path for reports
        formats: List of formats to generate ('markdown', 'html', 'json')
    """
    print("Generating reports...")
    report_gen = ReportGenerator(results)
    
    # Generate reports in requested formats
    for fmt in formats:
        if fmt == 'markdown':
            md_output = output_path if output_path.endswith('.md') else f"{output_path}.md"
            report_gen.generate_markdown(md_output)
            print(f"✓ Markdown report: {md_output}")
        elif fmt == 'html':
            html_output = output_path if output_path.endswith('.html') else f"{output_path}.html"
            report_gen.generate_html(html_output)
            print(f"✓ HTML report: {html_output}")
        elif fmt == 'json':
            json_output = output_path if output_path.endswith('.json') else f"{output_path}.json"
            report_gen.generate_json(json_output)
            print(f"✓ JSON report: {json_output}")
    
    return report_gen


def print_scan_summary(report_gen: ReportGenerator) -> int:
    """
    Print scan summary statistics and return appropriate exit code.
    
    Args:
        report_gen: Report generator instance with scan statistics
        
    Returns:
        Exit code (1 if infected files found, 0 otherwise)
    """
    stats = report_gen.stats
    print("Scan Results:")
    print(f"  Clean files: {stats['clean_files']}")
    print(f"  Infected files: {stats['infected_files']}")
    print(f"  Suspicious files: {stats['suspicious_files']}")
    print(f"  Not found: {stats['not_found']}")
    print(f"  Errors: {stats['errors']}")
    
    if stats['infected_files'] > 0:
        print()
        print("⚠️  WARNING: Infected files detected! Review the report for details.")
        return 1
    elif stats['suspicious_files'] > 0:
        print()
        print("⚠️  CAUTION: Suspicious files detected. Review recommended.")
        return 0
    else:
        print()
        print("✅ All files are clean.")
        return 0


def main():
    """Main entry point for the scanner."""
    parser = argparse.ArgumentParser(
        description='Scan files in a folder using VirusTotal API',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python vt_scanner.py /path/to/folder                              # Generate markdown report (default)
  python vt_scanner.py /path/to/folder --format html                # Generate HTML report
  python vt_scanner.py /path/to/folder --format json                # Generate JSON report
  python vt_scanner.py /path/to/folder --format all                 # Generate all formats
  python vt_scanner.py /path/to/folder --output my_report           # Custom output name
  python vt_scanner.py /path/to/folder --json                       # Markdown + JSON (legacy)
        """
    )
    
    parser.add_argument(
        'folder',
        help='Path to folder containing files to scan'
    )
    
    parser.add_argument(
        '--output', '-o',
        default='vt_report',
        help='Output file path (without extension). Default: vt_report'
    )
    
    parser.add_argument(
        '--format', '-f',
        choices=['markdown', 'html', 'json', 'all'],
        default='markdown',
        help='Report format: markdown (default), html, json, or all'
    )
    
    parser.add_argument(
        '--json',
        action='store_true',
        help='Also generate JSON output (deprecated: use --format instead)'
    )
    
    parser.add_argument(
        '--cache-days',
        type=int,
        default=7,
        help='Number of days to keep cache entries. Default: 7'
    )
    
    args = parser.parse_args()
    
    # Determine which formats to generate
    if args.format == 'all':
        formats = ['markdown', 'html', 'json']
    else:
        formats = [args.format]
        # Support legacy --json flag
        if args.json and 'json' not in formats:
            formats.append('json')
    
    # Load environment variables
    load_dotenv()
    api_key = os.getenv('VIRUS_TOTAL_KEY')
    
    if not api_key:
        print("Error: VIRUS_TOTAL_KEY not found in .env file")
        sys.exit(1)
    
    print("=" * 70)
    print("VirusTotal File Scanner")
    print("=" * 70)
    print()
    
    # Initialize components
    print("Initializing scanner...")
    vt_client = VirusTotalClient(api_key)
    cache = CacheManager(cache_days=args.cache_days)
    rate_limiter = RateLimiter()
    
    # Clean expired cache entries
    expired = cache.clear_expired()
    if expired > 0:
        print(f"Removed {expired} expired cache entries")
    
    # Get files to scan
    print(f"Scanning folder: {args.folder}")
    files = get_files_to_scan(args.folder)
    
    if not files:
        print("No files found to scan.")
        sys.exit(1)
    
    print(f"Found {len(files)} file(s) to scan")
    print()
    
    # Check daily limit
    remaining = rate_limiter.get_remaining_daily_requests()
    print(f"Daily API quota: {remaining} requests remaining")
    
    if remaining == 0:
        print("Error: Daily API limit reached. Try again tomorrow.")
        sys.exit(1)
    
    print()
    
    # Scan files
    scan_data = scan_files(files, vt_client, cache, rate_limiter)
    
    print()
    print("=" * 70)
    print("Scan Summary")
    print("=" * 70)
    print(f"Files scanned: {scan_data['files_scanned']}")
    print(f"From cache: {scan_data['files_from_cache']}")
    print(f"API calls made: {scan_data['api_calls_made']}")
    print()
    
    # Generate reports
    if not scan_data['results']:
        print("No results to report.")
        sys.exit(0)
    
    report_gen = generate_reports(scan_data['results'], args.output, formats)
    print()
    
    # Print summary statistics and get exit code
    exit_code = print_scan_summary(report_gen)
    
    print()
    print("=" * 70)
    
    sys.exit(exit_code)


if __name__ == '__main__':
    main()

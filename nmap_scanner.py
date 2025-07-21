#!/usr/bin/env python3
"""
Advanced Nmap Scanner Tool
A comprehensive nmap scanner with multiple scan types, progress tracking, and detailed reporting.
"""

import argparse
import json
import os
import re
import subprocess
import sys
import time
import threading
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import xml.etree.ElementTree as ET


class NmapScanner:
    """Advanced Nmap Scanner with multiple scan types and reporting capabilities."""
    
    def __init__(self, output_dir: str = "/tmp/nmap_scans"):
        """Initialize the scanner with output directory."""
        self.output_dir = output_dir
        self.ensure_output_dir()
        self.scan_types = {
            'quick': '-T4 -F',
            'intense': '-T4 -A -v',
            'stealth': '-sS -T2',
            'comprehensive': '-sS -sU -T4 -A -v -PE -PP -PS80,443 -PA3389 -PU40125 -PY -g 53 --script="default or (discovery and safe)"',
            'tcp_connect': '-sT -T4',
            'syn_stealth': '-sS -T4',
            'udp': '-sU -T4',
            'ping_sweep': '-sn',
            'os_detection': '-O -T4',
            'version_detection': '-sV -T4',
            'script_scan': '-sC -T4',
            'vuln_scan': '--script vuln -T4',
            'discovery': '--script discovery -T4'
        }
        
    def ensure_output_dir(self) -> None:
        """Ensure output directory exists."""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir, exist_ok=True)
            
    def validate_target(self, target: str) -> bool:
        """Validate target format (IP, CIDR, hostname)."""
        # Basic validation for IP addresses, CIDR notation, and hostnames
        ip_pattern = r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
        cidr_pattern = r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)/(?:[0-9]|[1-2][0-9]|3[0-2])$'
        hostname_pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$'
        
        return bool(re.match(ip_pattern, target) or 
                   re.match(cidr_pattern, target) or 
                   re.match(hostname_pattern, target))
    
    def validate_ports(self, ports: str) -> bool:
        """Validate port specification."""
        if not ports:
            return True
        # Allow port ranges (1-65535), individual ports (80,443), and combinations
        port_pattern = r'^[0-9,-]+$'
        return bool(re.match(port_pattern, ports))
    
    def build_command(self, target: str, scan_type: str = 'quick', 
                     ports: Optional[str] = None, additional_args: Optional[str] = None) -> str:
        """Build nmap command based on parameters."""
        if scan_type not in self.scan_types:
            raise ValueError(f"Invalid scan type. Available types: {list(self.scan_types.keys())}")
        
        if not self.validate_target(target):
            raise ValueError(f"Invalid target format: {target}")
        
        if ports and not self.validate_ports(ports):
            raise ValueError(f"Invalid port specification: {ports}")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = os.path.join(self.output_dir, f"scan_{timestamp}")
        
        cmd = f"nmap {self.scan_types[scan_type]}"
        
        if ports:
            cmd += f" -p {ports}"
        
        if additional_args:
            # Sanitize additional arguments
            safe_args = re.sub(r'[;&|`$()]', '', additional_args)
            cmd += f" {safe_args}"
        
        cmd += f" -oX {output_file}.xml -oN {output_file}.nmap -oG {output_file}.gnmap"
        cmd += f" {target}"
        
        return cmd, output_file
    
    def run_scan(self, target: str, scan_type: str = 'quick', 
                ports: Optional[str] = None, additional_args: Optional[str] = None,
                callback: Optional[callable] = None) -> Dict:
        """Run nmap scan and return results."""
        try:
            cmd, output_file = self.build_command(target, scan_type, ports, additional_args)
            
            print(f"[INFO] Starting {scan_type} scan of {target}")
            print(f"[INFO] Command: {cmd}")
            print(f"[INFO] Output files will be saved with prefix: {output_file}")
            
            start_time = time.time()
            
            # Run the scan
            process = subprocess.Popen(
                cmd, 
                shell=True, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                universal_newlines=True,
                bufsize=1
            )
            
            # Monitor progress if callback provided
            if callback:
                threading.Thread(
                    target=self._monitor_progress,
                    args=(process, callback),
                    daemon=True
                ).start()
            
            stdout, stderr = process.communicate()
            end_time = time.time()
            duration = end_time - start_time
            
            result = {
                'success': process.returncode == 0,
                'command': cmd,
                'target': target,
                'scan_type': scan_type,
                'duration': round(duration, 2),
                'start_time': datetime.fromtimestamp(start_time).isoformat(),
                'end_time': datetime.fromtimestamp(end_time).isoformat(),
                'output_files': {
                    'xml': f"{output_file}.xml",
                    'nmap': f"{output_file}.nmap",
                    'gnmap': f"{output_file}.gnmap"
                },
                'stdout': stdout,
                'stderr': stderr,
                'return_code': process.returncode
            }
            
            if process.returncode == 0:
                print(f"[SUCCESS] Scan completed in {duration:.2f} seconds")
                result['parsed_results'] = self.parse_xml_results(f"{output_file}.xml")
            else:
                print(f"[ERROR] Scan failed with return code {process.returncode}")
                print(f"[ERROR] {stderr}")
            
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'target': target,
                'scan_type': scan_type
            }
    
    def _monitor_progress(self, process: subprocess.Popen, callback: callable) -> None:
        """Monitor scan progress and call callback with updates."""
        while process.poll() is None:
            # In a real implementation, you might parse nmap output for progress
            # For now, just call callback every few seconds
            time.sleep(5)
            callback("Scan in progress...")
        callback("Scan completed")
    
    def parse_xml_results(self, xml_file: str) -> Optional[Dict]:
        """Parse nmap XML results into structured data."""
        if not os.path.exists(xml_file):
            return None
        
        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()
            
            results = {
                'scan_info': {},
                'hosts': []
            }
            
            # Parse scan info
            scaninfo = root.find('scaninfo')
            if scaninfo is not None:
                results['scan_info'] = {
                    'type': scaninfo.get('type'),
                    'protocol': scaninfo.get('protocol'),
                    'numservices': scaninfo.get('numservices'),
                }
            
            # Parse hosts
            for host in root.findall('host'):
                host_data = {
                    'addresses': [],
                    'hostnames': [],
                    'ports': [],
                    'os': {},
                    'status': host.find('status').get('state') if host.find('status') is not None else 'unknown'
                }
                
                # Parse addresses
                for addr in host.findall('address'):
                    host_data['addresses'].append({
                        'addr': addr.get('addr'),
                        'addrtype': addr.get('addrtype')
                    })
                
                # Parse hostnames
                hostnames = host.find('hostnames')
                if hostnames is not None:
                    for hostname in hostnames.findall('hostname'):
                        host_data['hostnames'].append({
                            'name': hostname.get('name'),
                            'type': hostname.get('type')
                        })
                
                # Parse ports
                ports = host.find('ports')
                if ports is not None:
                    for port in ports.findall('port'):
                        port_data = {
                            'protocol': port.get('protocol'),
                            'portid': port.get('portid'),
                            'state': port.find('state').get('state') if port.find('state') is not None else 'unknown'
                        }
                        
                        service = port.find('service')
                        if service is not None:
                            port_data['service'] = {
                                'name': service.get('name'),
                                'product': service.get('product'),
                                'version': service.get('version'),
                                'extrainfo': service.get('extrainfo')
                            }
                        
                        host_data['ports'].append(port_data)
                
                # Parse OS detection
                os_elem = host.find('os')
                if os_elem is not None:
                    osmatch = os_elem.find('osmatch')
                    if osmatch is not None:
                        host_data['os'] = {
                            'name': osmatch.get('name'),
                            'accuracy': osmatch.get('accuracy')
                        }
                
                results['hosts'].append(host_data)
            
            return results
            
        except Exception as e:
            print(f"[ERROR] Failed to parse XML results: {e}")
            return None
    
    def list_scan_types(self) -> Dict[str, str]:
        """Return available scan types and their descriptions."""
        descriptions = {
            'quick': 'Fast scan of most common ports',
            'intense': 'Comprehensive scan with OS detection, version detection, script scanning, and traceroute',
            'stealth': 'Stealthy SYN scan with slow timing',
            'comprehensive': 'Most comprehensive scan including TCP, UDP, scripts, and various ping types',
            'tcp_connect': 'TCP connect scan',
            'syn_stealth': 'SYN stealth scan',
            'udp': 'UDP scan',
            'ping_sweep': 'Ping sweep (host discovery only)',
            'os_detection': 'Operating system detection',
            'version_detection': 'Service version detection',
            'script_scan': 'Default NSE script scan',
            'vuln_scan': 'Vulnerability detection scripts',
            'discovery': 'Host and service discovery scripts'
        }
        
        return {scan_type: f"{self.scan_types[scan_type]} - {descriptions[scan_type]}" 
                for scan_type in self.scan_types}
    
    def get_scan_history(self) -> List[Dict]:
        """Get history of previous scans."""
        history = []
        
        for filename in os.listdir(self.output_dir):
            if filename.endswith('.xml'):
                filepath = os.path.join(self.output_dir, filename)
                stat = os.stat(filepath)
                
                history.append({
                    'filename': filename,
                    'filepath': filepath,
                    'size': stat.st_size,
                    'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                    'modified': datetime.fromtimestamp(stat.st_mtime).isoformat()
                })
        
        return sorted(history, key=lambda x: x['created'], reverse=True)


def main():
    """Main function for command-line usage."""
    parser = argparse.ArgumentParser(
        description="Advanced Nmap Scanner Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s 192.168.1.1 -t quick
  %(prog)s 192.168.1.0/24 -t comprehensive -p 80,443,8080
  %(prog)s scanme.nmap.org -t vuln_scan
  %(prog)s --list-types
  %(prog)s --history
        """
    )
    
    parser.add_argument('target', nargs='?', help='Target to scan (IP, CIDR, hostname)')
    parser.add_argument('-t', '--type', default='quick', 
                       help='Scan type (default: quick)')
    parser.add_argument('-p', '--ports', 
                       help='Port specification (e.g., 80,443 or 1-1000)')
    parser.add_argument('-a', '--args', 
                       help='Additional nmap arguments')
    parser.add_argument('-o', '--output-dir', default='/tmp/nmap_scans',
                       help='Output directory (default: /tmp/nmap_scans)')
    parser.add_argument('--list-types', action='store_true',
                       help='List available scan types')
    parser.add_argument('--history', action='store_true',
                       help='Show scan history')
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Verbose output')
    
    args = parser.parse_args()
    
    scanner = NmapScanner(args.output_dir)
    
    if args.list_types:
        print("Available scan types:")
        for scan_type, description in scanner.list_scan_types().items():
            print(f"  {scan_type:<15} - {description}")
        return
    
    if args.history:
        history = scanner.get_scan_history()
        if history:
            print("Scan History:")
            for scan in history[:10]:  # Show last 10 scans
                print(f"  {scan['filename']} - {scan['created']} ({scan['size']} bytes)")
        else:
            print("No scan history found.")
        return
    
    if not args.target:
        parser.error("Target is required unless using --list-types or --history")
    
    # Progress callback for verbose mode
    def progress_callback(message):
        if args.verbose:
            print(f"[PROGRESS] {message}")
    
    # Run the scan
    result = scanner.run_scan(
        args.target, 
        args.type, 
        args.ports, 
        args.args,
        progress_callback if args.verbose else None
    )
    
    # Output results
    if result['success']:
        print(f"\n[RESULTS] Scan completed successfully!")
        print(f"Target: {result['target']}")
        print(f"Scan Type: {result['scan_type']}")
        print(f"Duration: {result['duration']} seconds")
        print(f"Output Files:")
        for file_type, filepath in result['output_files'].items():
            print(f"  {file_type.upper()}: {filepath}")
        
        if args.verbose and result.get('parsed_results'):
            print(f"\nParsed Results:")
            print(json.dumps(result['parsed_results'], indent=2))
    else:
        print(f"\n[ERROR] Scan failed!")
        if 'error' in result:
            print(f"Error: {result['error']}")
        if 'stderr' in result:
            print(f"Stderr: {result['stderr']}")


if __name__ == "__main__":
    main()
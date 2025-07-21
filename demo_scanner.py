#!/usr/bin/env python3
"""
Demo script for the Advanced Nmap Scanner
This script demonstrates various scan types and features.
"""

import time
import sys
import os
from nmap_scanner import NmapScanner

def print_banner():
    """Print a nice banner for the demo."""
    print("=" * 60)
    print("         Advanced Nmap Scanner - Demo")
    print("=" * 60)
    print()

def demo_scanner():
    """Demonstrate the scanner capabilities."""
    print_banner()
    
    # Initialize scanner
    scanner = NmapScanner(output_dir="/tmp/nmap_demo")
    
    print("🔍 Available Scan Types:")
    print("-" * 40)
    scan_types = scanner.list_scan_types()
    for scan_type, description in scan_types.items():
        print(f"  {scan_type:<15} - {description}")
    print()
    
    # Demo target (using scanme.nmap.org which is designed for testing)
    target = "scanme.nmap.org"
    print(f"🎯 Demo Target: {target}")
    print("   (This is a legitimate testing target provided by nmap.org)")
    print()
    
    # Demonstrate different scan types
    demos = [
        ("ping_sweep", "Host Discovery"),
        ("quick", "Quick Port Scan"),
        ("version_detection", "Service Version Detection"),
    ]
    
    for scan_type, description in demos:
        print(f"🚀 Running {description} ({scan_type})...")
        print(f"   Command will be: nmap {scanner.scan_types[scan_type]} {target}")
        
        # Ask for confirmation in demo mode
        response = input("   Continue? (y/n): ").lower().strip()
        if response != 'y':
            print("   Skipped.")
            continue
        
        # Run the scan
        result = scanner.run_scan(target, scan_type)
        
        if result['success']:
            print(f"   ✅ Completed in {result['duration']:.2f} seconds")
            
            # Show some basic results
            if result.get('parsed_results'):
                hosts = result['parsed_results'].get('hosts', [])
                if hosts:
                    host = hosts[0]
                    print(f"   📍 Host: {host['addresses'][0]['addr']}")
                    
                    if scan_type != "ping_sweep":
                        open_ports = [p for p in host.get('ports', []) if p['state'] == 'open']
                        if open_ports:
                            print(f"   🔓 Open Ports: {', '.join([p['portid'] for p in open_ports])}")
                        
                        if scan_type == "version_detection":
                            for port in open_ports[:3]:  # Show first 3 services
                                service = port.get('service', {})
                                if service.get('product'):
                                    print(f"      Port {port['portid']}: {service.get('name', 'unknown')} - {service.get('product', 'unknown')}")
        else:
            print(f"   ❌ Failed: {result.get('error', 'Unknown error')}")
        
        print()
        time.sleep(1)
    
    # Show scan history
    print("📚 Scan History:")
    print("-" * 20)
    history = scanner.get_scan_history()
    for scan in history[:5]:  # Show last 5 scans
        print(f"  {scan['filename']} - {scan['created'][:19]} ({scan['size']} bytes)")
    print()
    
    print("🎉 Demo completed!")
    print(f"   Check output files in: {scanner.output_dir}")
    print("   Use 'python3 nmap_scanner.py --help' for full usage info")

def demo_api():
    """Demonstrate the Python API usage."""
    print("\n" + "=" * 60)
    print("         Python API Demo")
    print("=" * 60)
    print()
    
    print("Example Python code for using the scanner:")
    print("-" * 40)
    
    code_example = '''
from nmap_scanner import NmapScanner

# Initialize scanner
scanner = NmapScanner(output_dir="/custom/path")

# Run a quick scan
result = scanner.run_scan("scanme.nmap.org", "quick")

# Check results
if result['success']:
    print(f"Scan completed in {result['duration']} seconds")
    
    # Parse results
    for host in result['parsed_results']['hosts']:
        print(f"Host: {host['addresses'][0]['addr']}")
        for port in host['ports']:
            if port['state'] == 'open':
                print(f"  Port {port['portid']}: {port['service']['name']}")
else:
    print(f"Scan failed: {result['error']}")
'''
    
    print(code_example)

def main():
    """Main demo function."""
    if len(sys.argv) > 1 and sys.argv[1] == "api":
        demo_api()
    else:
        print("This is a demonstration of the Advanced Nmap Scanner.")
        print("The demo will run actual scans against scanme.nmap.org")
        print("(a legitimate testing target provided by nmap.org).")
        print()
        
        response = input("Do you want to continue? (y/n): ").lower().strip()
        if response == 'y':
            demo_scanner()
            if input("\nShow Python API demo? (y/n): ").lower().strip() == 'y':
                demo_api()
        else:
            print("Demo cancelled.")

if __name__ == "__main__":
    main()
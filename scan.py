#!/usr/bin/env python3
"""
Simple CLI wrapper for the Nmap Scanner
Usage: python scan.py <target> [options]
"""

import sys
import os

# Add current directory to path so we can import nmap_scanner
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from nmap_scanner import main

if __name__ == "__main__":
    main()
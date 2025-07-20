#!/bin/bash

echo "=========================================="
echo "  Advanced Nmap Scanner Setup Script"
echo "=========================================="
echo

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   echo "⚠️  Warning: Running as root. Some scans may require elevated privileges."
   echo
fi

# Check for nmap
echo "🔍 Checking for nmap installation..."
if ! command -v nmap &> /dev/null; then
    echo "❌ nmap not found. Installing..."
    
    # Detect package manager
    if command -v apt-get &> /dev/null; then
        sudo apt-get update && sudo apt-get install -y nmap
    elif command -v yum &> /dev/null; then
        sudo yum install -y nmap
    elif command -v brew &> /dev/null; then
        brew install nmap
    else
        echo "❌ Could not detect package manager. Please install nmap manually."
        echo "   Visit: https://nmap.org/download.html"
        exit 1
    fi
    
    if [ $? -eq 0 ]; then
        echo "✅ nmap installed successfully"
    else
        echo "❌ Failed to install nmap"
        exit 1
    fi
else
    echo "✅ nmap found: $(nmap --version | head -1)"
fi

echo

# Check Python
echo "🐍 Checking Python installation..."
if command -v python3 &> /dev/null; then
    echo "✅ Python3 found: $(python3 --version)"
else
    echo "❌ Python3 not found. Please install Python 3.6+"
    exit 1
fi

echo

# Install Python dependencies
echo "📦 Installing Python dependencies..."
echo "   Note: You may need to install pip if not available"

# Check if pip is available
if command -v pip3 &> /dev/null; then
    pip3 install python-nmap xmltodict requests 2>/dev/null || echo "⚠️  Some packages may already be installed"
elif command -v pip &> /dev/null; then
    pip install python-nmap xmltodict requests 2>/dev/null || echo "⚠️  Some packages may already be installed"
else
    echo "⚠️  pip not found. You may need to install packages manually:"
    echo "     python-nmap xmltodict requests"
fi

echo

# Make scripts executable
echo "🔧 Setting up executable permissions..."
chmod +x nmap_scanner.py scan.py demo_scanner.py setup_scanner.sh

# Create output directories
echo "📁 Creating output directories..."
mkdir -p /tmp/nmap_scans
mkdir -p /tmp/nmap_demo

# Test the scanner
echo "🧪 Testing scanner installation..."
if python3 nmap_scanner.py --list-types > /dev/null 2>&1; then
    echo "✅ Scanner test passed!"
else
    echo "❌ Scanner test failed. Check dependencies."
    exit 1
fi

echo
echo "🎉 Setup completed successfully!"
echo
echo "📋 Quick Start Guide:"
echo "--------------------"
echo "1. List scan types:     python3 nmap_scanner.py --list-types"
echo "2. Run quick scan:      python3 nmap_scanner.py scanme.nmap.org"
echo "3. Show scan history:   python3 nmap_scanner.py --history"
echo "4. Run demo:            python3 demo_scanner.py"
echo "5. Get help:            python3 nmap_scanner.py --help"
echo
echo "📖 Documentation: See NMAP_SCANNER_README.md"
echo "📊 Project Summary: See SUMMARY.md"
echo
echo "⚠️  Security Reminder:"
echo "   Only scan systems you own or have explicit permission to test!"
echo
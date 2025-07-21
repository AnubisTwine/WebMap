# Advanced Nmap Scanner

A comprehensive Nmap scanner tool with both command-line and web interfaces, designed for network reconnaissance and security assessment.

## Features

### 🔍 Multiple Scan Types
- **Quick Scan**: Fast scan of common ports
- **Intense Scan**: Comprehensive scan with OS detection, version detection, and scripts
- **Stealth Scan**: Low-profile SYN scan with slow timing
- **Comprehensive Scan**: Full TCP/UDP scan with all detection features
- **Vulnerability Scan**: Security-focused scanning with vulnerability scripts
- **Discovery Scan**: Host and service discovery
- **Custom Scans**: Support for custom nmap arguments

### 🖥️ Dual Interface
- **Command Line Interface**: Full-featured CLI for automation and scripting
- **Web Interface**: Modern, responsive web dashboard with real-time progress tracking

### 📊 Advanced Features
- Real-time scan progress monitoring
- Automatic XML parsing and result structuring
- Scan history tracking
- Background scan execution
- Multiple output formats (XML, Nmap, Gnmap)
- Input validation and security measures

## Installation

### Prerequisites
- Python 3.6+
- Nmap installed on the system
- Django (for web interface)

### Quick Start

1. **Check if nmap is installed:**
   ```bash
   nmap --version
   ```

2. **Install Python dependencies:**
   ```bash
   pip install python-nmap xmltodict requests
   ```

3. **Make the scanner executable:**
   ```bash
   chmod +x nmap_scanner.py scan.py
   ```

## Usage

### Command Line Interface

#### Basic Usage
```bash
# Quick scan
python nmap_scanner.py 192.168.1.1

# Comprehensive scan
python nmap_scanner.py 192.168.1.0/24 -t comprehensive

# Vulnerability scan with specific ports
python nmap_scanner.py scanme.nmap.org -t vuln_scan -p 80,443,8080

# Custom scan with additional arguments
python nmap_scanner.py 192.168.1.1 -t stealth -a "--min-rate 1000"
```

#### Available Commands
```bash
# List all scan types
python nmap_scanner.py --list-types

# Show scan history
python nmap_scanner.py --history

# Verbose output
python nmap_scanner.py 192.168.1.1 -v

# Custom output directory
python nmap_scanner.py 192.168.1.1 -o /custom/path
```

#### Scan Types

| Type | Description | Use Case |
|------|-------------|----------|
| `quick` | Fast scan of common ports | Quick network discovery |
| `intense` | Full scan with OS/service detection | Comprehensive assessment |
| `stealth` | Low-profile SYN scan | Avoiding detection |
| `comprehensive` | Complete TCP/UDP with all features | Full network audit |
| `tcp_connect` | Standard TCP connect scan | Firewall-friendly scanning |
| `syn_stealth` | SYN stealth scan | Stealthy port discovery |
| `udp` | UDP port scan | UDP service discovery |
| `ping_sweep` | Host discovery only | Network mapping |
| `os_detection` | Operating system fingerprinting | Asset identification |
| `version_detection` | Service version detection | Vulnerability research |
| `script_scan` | Default NSE script execution | Security assessment |
| `vuln_scan` | Vulnerability detection scripts | Security testing |
| `discovery` | Host and service discovery | Network reconnaissance |

### Web Interface

#### Starting the Web Interface
```bash
# Start Django development server
python manage.py runserver 0.0.0.0:8000
```

#### Web Features
- **Modern Dashboard**: Clean, responsive interface
- **Real-time Monitoring**: Live scan progress updates
- **Scan Management**: Start, monitor, and manage multiple scans
- **History Tracking**: Browse and download previous scan results
- **Interactive Help**: Built-in documentation and examples

### API Endpoints

The web interface provides RESTful API endpoints:

```bash
# Start a new scan
POST /api/scan/start
{
    "target": "192.168.1.1",
    "scan_type": "quick",
    "ports": "80,443",
    "additional_args": ""
}

# Check scan status
GET /api/scan/status/{scan_id}

# Get scan history
GET /api/scan/history

# Get parsed results
GET /api/scan/results/{filename}

# Get available scan types
GET /api/scan/types
```

## Examples

### 1. Network Discovery
```bash
# Find live hosts in a network
python nmap_scanner.py 192.168.1.0/24 -t ping_sweep

# Quick port scan of discovered hosts
python nmap_scanner.py 192.168.1.100-110 -t quick
```

### 2. Service Enumeration
```bash
# Detect service versions
python nmap_scanner.py 192.168.1.1 -t version_detection

# Run discovery scripts
python nmap_scanner.py 192.168.1.1 -t discovery
```

### 3. Security Assessment
```bash
# Vulnerability scan
python nmap_scanner.py target.com -t vuln_scan

# Comprehensive security audit
python nmap_scanner.py target.com -t comprehensive -p 1-65535
```

### 4. Stealth Scanning
```bash
# Low-profile scan
python nmap_scanner.py target.com -t stealth

# Custom stealth with timing
python nmap_scanner.py target.com -t stealth -a "-T1 --max-rate 10"
```

## Output Formats

The scanner generates multiple output formats for each scan:

### XML Format
- **File**: `scan_YYYYMMDD_HHMMSS.xml`
- **Use**: Programmatic parsing, integration with other tools
- **Features**: Complete scan data, easy to parse

### Nmap Format
- **File**: `scan_YYYYMMDD_HHMMSS.nmap`
- **Use**: Human-readable results
- **Features**: Standard nmap output format

### Gnmap Format
- **File**: `scan_YYYYMMDD_HHMMSS.gnmap`
- **Use**: Grep-friendly format
- **Features**: One line per host, easy filtering

### Parsed JSON
Available through the web interface and API, providing structured data:
```json
{
    "scan_info": {
        "type": "connect",
        "protocol": "tcp",
        "numservices": "1000"
    },
    "hosts": [
        {
            "addresses": [{"addr": "192.168.1.1", "addrtype": "ipv4"}],
            "hostnames": [],
            "ports": [
                {
                    "protocol": "tcp",
                    "portid": "80",
                    "state": "open",
                    "service": {
                        "name": "http",
                        "product": "Apache",
                        "version": "2.4.41"
                    }
                }
            ],
            "os": {"name": "Linux", "accuracy": "95"}
        }
    ]
}
```

## Security Considerations

### Input Validation
- Target format validation (IP, CIDR, hostname)
- Port specification validation
- Command injection prevention
- Argument sanitization

### Safe Practices
- Run scans from dedicated systems
- Respect rate limiting and timing options
- Obtain proper authorization before scanning
- Monitor scan impact on target systems

### Default Security
- Output files restricted to specified directories
- Dangerous characters filtered from additional arguments
- Session management for web interface
- API authentication (when enabled)

## Integration

### Python API
```python
from nmap_scanner import NmapScanner

# Initialize scanner
scanner = NmapScanner(output_dir="/custom/path")

# Run a scan
result = scanner.run_scan("192.168.1.1", "quick")

# Parse results
if result['success']:
    parsed = result['parsed_results']
    for host in parsed['hosts']:
        print(f"Host: {host['addresses'][0]['addr']}")
        for port in host['ports']:
            if port['state'] == 'open':
                print(f"  Port {port['portid']}: {port['service']['name']}")
```

### Django Integration
```python
from enhanced_scanner_views import enhanced_views

# Use in Django views
def my_view(request):
    return enhanced_views.dashboard(request)
```

## Troubleshooting

### Common Issues

1. **Permission Denied**
   ```bash
   # Run with sudo for privileged scans
   sudo python nmap_scanner.py target.com -t syn_stealth
   ```

2. **Nmap Not Found**
   ```bash
   # Install nmap
   # Ubuntu/Debian:
   sudo apt-get install nmap
   
   # macOS:
   brew install nmap
   
   # Windows:
   # Download from https://nmap.org/download.html
   ```

3. **Permission for Output Directory**
   ```bash
   # Create writable directory
   mkdir -p /tmp/nmap_scans
   chmod 755 /tmp/nmap_scans
   ```

4. **Web Interface Not Loading**
   ```bash
   # Check Django settings
   python manage.py check
   
   # Migrate database
   python manage.py migrate
   ```

### Debug Mode
```bash
# Enable verbose output
python nmap_scanner.py target.com -t quick -v

# Check scan files
ls -la /tmp/nmap_scans/
```

## License

This tool is provided for educational and authorized security testing purposes only. Users are responsible for ensuring they have proper authorization before scanning any networks or systems.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Support

For issues, questions, or contributions:
- Check the troubleshooting section
- Review existing scan types and options
- Ensure proper nmap installation
- Verify target accessibility and permissions
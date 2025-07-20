from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import json
import os
import threading
import time
from datetime import datetime
from nmap_scanner import NmapScanner


class EnhancedNmapViews:
    """Enhanced Nmap views for Django web interface."""
    
    def __init__(self):
        self.scanner = NmapScanner(output_dir='/opt/xml')
        self.active_scans = {}  # Track active scans
    
    def dashboard(self, request):
        """Main dashboard view."""
        if 'auth' not in request.session:
            return render(request, 'nmapreport/nmap_auth.html', {})
        
        context = {
            'auth': True,
            'scan_types': self.scanner.list_scan_types(),
            'scan_history': self.scanner.get_scan_history()[:10],
            'active_scans': self.active_scans
        }
        
        return render(request, 'nmapreport/enhanced_scanner.html', context)
    
    @csrf_exempt
    def api_scan_types(self, request):
        """API endpoint to get available scan types."""
        return JsonResponse({
            'scan_types': self.scanner.list_scan_types()
        })
    
    @csrf_exempt
    def api_start_scan(self, request):
        """API endpoint to start a new scan."""
        if request.method != 'POST':
            return JsonResponse({'error': 'Method not allowed'}, status=405)
        
        try:
            data = json.loads(request.body)
            target = data.get('target')
            scan_type = data.get('scan_type', 'quick')
            ports = data.get('ports')
            additional_args = data.get('additional_args')
            
            if not target:
                return JsonResponse({'error': 'Target is required'}, status=400)
            
            # Generate scan ID
            scan_id = f"scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(self.active_scans)}"
            
            # Start scan in background thread
            scan_thread = threading.Thread(
                target=self._run_background_scan,
                args=(scan_id, target, scan_type, ports, additional_args)
            )
            scan_thread.daemon = True
            scan_thread.start()
            
            return JsonResponse({
                'success': True,
                'scan_id': scan_id,
                'message': 'Scan started successfully'
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    def _run_background_scan(self, scan_id, target, scan_type, ports, additional_args):
        """Run scan in background and update status."""
        self.active_scans[scan_id] = {
            'status': 'running',
            'target': target,
            'scan_type': scan_type,
            'start_time': datetime.now().isoformat(),
            'progress': 'Initializing scan...'
        }
        
        try:
            def progress_callback(message):
                if scan_id in self.active_scans:
                    self.active_scans[scan_id]['progress'] = message
            
            result = self.scanner.run_scan(
                target, scan_type, ports, additional_args, progress_callback
            )
            
            if scan_id in self.active_scans:
                self.active_scans[scan_id].update({
                    'status': 'completed' if result['success'] else 'failed',
                    'end_time': datetime.now().isoformat(),
                    'duration': result.get('duration'),
                    'result': result
                })
                
        except Exception as e:
            if scan_id in self.active_scans:
                self.active_scans[scan_id].update({
                    'status': 'failed',
                    'end_time': datetime.now().isoformat(),
                    'error': str(e)
                })
    
    @csrf_exempt
    def api_scan_status(self, request, scan_id):
        """API endpoint to get scan status."""
        if scan_id in self.active_scans:
            return JsonResponse({
                'success': True,
                'scan': self.active_scans[scan_id]
            })
        else:
            return JsonResponse({'error': 'Scan not found'}, status=404)
    
    @csrf_exempt
    def api_scan_history(self, request):
        """API endpoint to get scan history."""
        history = self.scanner.get_scan_history()
        return JsonResponse({
            'success': True,
            'scans': history
        })
    
    @csrf_exempt
    def api_scan_results(self, request, filename):
        """API endpoint to get parsed scan results."""
        try:
            filepath = os.path.join('/opt/xml', filename)
            if not os.path.exists(filepath):
                return JsonResponse({'error': 'File not found'}, status=404)
            
            results = self.scanner.parse_xml_results(filepath)
            if results:
                return JsonResponse({
                    'success': True,
                    'results': results
                })
            else:
                return JsonResponse({'error': 'Failed to parse results'}, status=500)
                
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    @csrf_exempt
    def api_delete_scan(self, request, scan_id):
        """API endpoint to delete/cancel a scan."""
        if request.method != 'DELETE':
            return JsonResponse({'error': 'Method not allowed'}, status=405)
        
        if scan_id in self.active_scans:
            # Mark as cancelled if still running
            if self.active_scans[scan_id]['status'] == 'running':
                self.active_scans[scan_id]['status'] = 'cancelled'
            
            # Remove from active scans after some time
            threading.Timer(60, lambda: self.active_scans.pop(scan_id, None)).start()
            
            return JsonResponse({'success': True, 'message': 'Scan cancelled'})
        else:
            return JsonResponse({'error': 'Scan not found'}, status=404)


# Create global instance
enhanced_views = EnhancedNmapViews()

# Django view functions
def enhanced_scanner_dashboard(request):
    return enhanced_views.dashboard(request)

def api_scan_types(request):
    return enhanced_views.api_scan_types(request)

def api_start_scan(request):
    return enhanced_views.api_start_scan(request)

def api_scan_status(request, scan_id):
    return enhanced_views.api_scan_status(request, scan_id)

def api_scan_history(request):
    return enhanced_views.api_scan_history(request)

def api_scan_results(request, filename):
    return enhanced_views.api_scan_results(request, filename)

def api_delete_scan(request, scan_id):
    return enhanced_views.api_delete_scan(request, scan_id)
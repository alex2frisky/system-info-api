"""
System Info API
A simple Flask application that returns system information.

Endpoints:
  GET  /            - Service info
  GET  /health      - Health check (for K8s probes)
  GET  /info        - Detailed system information
  GET  /metrics     - Prometheus metrics
"""

from flask import Flask, jsonify
import psutil
import platform
from datetime import datetime
import os

app = Flask(__name__)

# Track request count for metrics
request_count = 0


@app.before_request
def count_request():
    """Increment request counter before each request."""
    global request_count
    request_count += 1


@app.route('/')
def home():
    """Root endpoint - returns service information."""
    return jsonify({
        "service": "system-info-api",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "endpoints": {
            "/": "Service information",
            "/health": "Health check",
            "/info": "Detailed system information",
            "/metrics": "Prometheus metrics"
        }
    })


@app.route('/health')
def health():
    """
    Health check endpoint.
    Used by Kubernetes liveness and readiness probes.
    Always returns 200 if the service is running.
    """
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }), 200


@app.route('/info')
def system_info():
    """
    Returns detailed system information.
    Useful for monitoring and debugging.
    """
    # Get CPU information
    cpu_percent = psutil.cpu_percent(interval=1)
    cpu_count = psutil.cpu_count()
    
    # Get memory information
    memory = psutil.virtual_memory()
    
    # Get disk information
    disk = psutil.disk_usage('/')
    
    # Calculate uptime
    boot_time = datetime.fromtimestamp(psutil.boot_time())
    uptime = datetime.now() - boot_time
    
    return jsonify({
        "hostname": platform.node(),
        "platform": {
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor()
        },
        "cpu": {
            "count": cpu_count,
            "percent": cpu_percent,
            "per_cpu": psutil.cpu_percent(interval=1, percpu=True)
        },
        "memory": {
            "total_gb": round(memory.total / (1024**3), 2),
            "available_gb": round(memory.available / (1024**3), 2),
            "used_gb": round(memory.used / (1024**3), 2),
            "percent": memory.percent
        },
        "disk": {
            "total_gb": round(disk.total / (1024**3), 2),
            "used_gb": round(disk.used / (1024**3), 2),
            "free_gb": round(disk.free / (1024**3), 2),
            "percent": disk.percent
        },
        "uptime": {
            "boot_time": boot_time.isoformat(),
            "uptime_seconds": int(uptime.total_seconds()),
            "uptime_hours": round(uptime.total_seconds() / 3600, 2)
        },
        "timestamp": datetime.now().isoformat()
    })


@app.route('/metrics')
def metrics():
    """
    Prometheus metrics endpoint.
    Returns metrics in Prometheus text exposition format.
    """
    cpu_percent = psutil.cpu_percent(interval=0.1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    metrics_output = f"""# HELP system_cpu_percent CPU usage percentage
# TYPE system_cpu_percent gauge
system_cpu_percent {cpu_percent}

# HELP system_memory_percent Memory usage percentage
# TYPE system_memory_percent gauge
system_memory_percent {memory.percent}

# HELP system_memory_used_bytes Memory used in bytes
# TYPE system_memory_used_bytes gauge
system_memory_used_bytes {memory.used}

# HELP system_disk_percent Disk usage percentage
# TYPE system_disk_percent gauge
system_disk_percent {disk.percent}

# HELP system_disk_used_bytes Disk used in bytes
# TYPE system_disk_used_bytes gauge
system_disk_used_bytes {disk.used}

# HELP flask_requests_total Total number of requests
# TYPE flask_requests_total counter
flask_requests_total {request_count}
"""
    
    return metrics_output, 200, {'Content-Type': 'text/plain; version=0.0.4'}


if __name__ == '__main__':
    # Run on all interfaces, port 5000
    # In production, this is run by gunicorn
    app.run(host='0.0.0.0', port=5000, debug=False)

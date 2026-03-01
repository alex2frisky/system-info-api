from flask import Flask, jsonify
import psutil
import platform
from datetime import datetime

app = Flask(__name__)

# simple counter to track total requests
request_count = 0


@app.before_request
def count_request():
    global request_count
    request_count += 1


@app.route('/')
def home():
    return jsonify({
        "service": "system-info-api",
        "version": "1.0.0",
        "status": "running",
        "endpoints": ["/", "/health", "/info", "/metrics"]
    })


@app.route('/health')
def health():
    # used by K8s liveness/readiness probes
    return jsonify({"status": "healthy"}), 200


@app.route('/info')
def system_info():
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')

    # calculate uptime from boot time
    boot_time = datetime.fromtimestamp(psutil.boot_time())
    uptime_seconds = int((datetime.now() - boot_time).total_seconds())

    return jsonify({
        "hostname": platform.node(),
        "platform": platform.system(),
        "cpu": {
            "count": psutil.cpu_count(),
            "percent": cpu_percent,
        },
        "memory": {
            "total_gb": round(memory.total / (1024**3), 2),
            "used_gb": round(memory.used / (1024**3), 2),
            "percent": memory.percent
        },
        "disk": {
            "total_gb": round(disk.total / (1024**3), 2),
            "used_gb": round(disk.used / (1024**3), 2),
            "percent": disk.percent
        },
        "uptime_seconds": uptime_seconds,
        "timestamp": datetime.now().isoformat()
    })


@app.route('/metrics')
def metrics():
    # returns metrics in Prometheus text format
    # learned about this format from the Prometheus docs
    cpu_percent = psutil.cpu_percent(interval=0.1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')

    output = f"""# HELP system_cpu_percent CPU usage percentage
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

# HELP flask_requests_total Total number of requests
# TYPE flask_requests_total counter
flask_requests_total {request_count}
"""

    return output, 200, {'Content-Type': 'text/plain; version=0.0.4'}


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)

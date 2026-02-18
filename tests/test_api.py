"""
Tests for the System Info API
Run with: pytest tests/ -v
"""
import pytest
import json
import sys
import os

# Add parent directory to path so we can import app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app


@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


class TestEndpoints:
    """Test all API endpoints."""

    def test_home_endpoint(self, client):
        """Test GET / returns service information."""
        response = client.get('/')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['service'] == 'system-info-api'
        assert data['status'] == 'running'
        assert 'endpoints' in data
        assert 'timestamp' in data

    def test_health_endpoint(self, client):
        """Test GET /health returns healthy status."""
        response = client.get('/health')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
        assert 'timestamp' in data

    def test_info_endpoint(self, client):
        """Test GET /info returns system information."""
        response = client.get('/info')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        
        # Check required fields exist
        assert 'hostname' in data
        assert 'platform' in data
        assert 'cpu' in data
        assert 'memory' in data
        assert 'disk' in data
        assert 'uptime' in data
        assert 'timestamp' in data
        
        # Check nested structures
        assert 'count' in data['cpu']
        assert 'percent' in data['cpu']
        assert 'total_gb' in data['memory']
        assert 'used_gb' in data['memory']
        assert 'percent' in data['memory']

    def test_metrics_endpoint(self, client):
        """Test GET /metrics returns Prometheus format."""
        response = client.get('/metrics')
        assert response.status_code == 200
        assert response.content_type.startswith('text/plain; version=0.0.4') 
        
        metrics_text = response.data.decode('utf-8')
        
        # Check required metrics are present
        assert 'system_cpu_percent' in metrics_text
        assert 'system_memory_percent' in metrics_text
        assert 'system_disk_percent' in metrics_text
        assert 'flask_requests_total' in metrics_text
        
        # Check Prometheus format
        assert '# HELP' in metrics_text
        assert '# TYPE' in metrics_text


class TestDataValidation:
    """Test that returned data is valid."""

    def test_cpu_percent_in_range(self, client):
        """CPU percent should be between 0 and 100."""
        response = client.get('/info')
        data = json.loads(response.data)
        
        cpu_percent = data['cpu']['percent']
        assert 0 <= cpu_percent <= 100

    def test_memory_percent_in_range(self, client):
        """Memory percent should be between 0 and 100."""
        response = client.get('/info')
        data = json.loads(response.data)
        
        mem_percent = data['memory']['percent']
        assert 0 <= mem_percent <= 100

    def test_memory_values_consistent(self, client):
        """Memory used + available should roughly equal total."""
        response = client.get('/info')
        data = json.loads(response.data)
        
        total = data['memory']['total_gb']
        used = data['memory']['used_gb']
        available = data['memory']['available_gb']
        
        # Used should be less than total
        assert used < total
        # Available should be less than total
        assert available < total


class TestRequestCounter:
    """Test that request counter increments."""

    def test_request_counter_increments(self, client):
        """Each request should increment the counter."""
        # Get initial count
        response1 = client.get('/metrics')
        metrics1 = response1.data.decode('utf-8')
        
        # Extract flask_requests_total value
        for line in metrics1.split('\n'):
            if line.startswith('flask_requests_total'):
                count1 = int(line.split()[-1])
                break
        
        # Make another request
        client.get('/')
        
        # Get new count
        response2 = client.get('/metrics')
        metrics2 = response2.data.decode('utf-8')
        
        for line in metrics2.split('\n'):
            if line.startswith('flask_requests_total'):
                count2 = int(line.split()[-1])
                break
        
        # Count should have increased
        assert count2 > count1

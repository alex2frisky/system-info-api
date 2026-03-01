import pytest
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_home(client):
    response = client.get('/')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['service'] == 'system-info-api'
    assert data['status'] == 'running'


def test_health(client):
    response = client.get('/health')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'healthy'


def test_info_has_expected_fields(client):
    response = client.get('/info')
    assert response.status_code == 200
    data = json.loads(response.data)

    assert 'hostname' in data
    assert 'cpu' in data
    assert 'memory' in data
    assert 'disk' in data
    assert 'uptime_seconds' in data


def test_cpu_percent_in_range(client):
    response = client.get('/info')
    data = json.loads(response.data)
    assert 0 <= data['cpu']['percent'] <= 100


def test_memory_percent_in_range(client):
    response = client.get('/info')
    data = json.loads(response.data)
    assert 0 <= data['memory']['percent'] <= 100


def test_memory_used_less_than_total(client):
    response = client.get('/info')
    data = json.loads(response.data)
    assert data['memory']['used_gb'] < data['memory']['total_gb']


def test_metrics_format(client):
    response = client.get('/metrics')
    assert response.status_code == 200
    assert 'text/plain' in response.content_type

    text = response.data.decode('utf-8')
    assert 'system_cpu_percent' in text
    assert 'system_memory_percent' in text
    assert 'flask_requests_total' in text
    assert '# HELP' in text
    assert '# TYPE' in text


def test_request_counter_goes_up(client):
    # make a request, then check metrics counter went up
    client.get('/')

    response = client.get('/metrics')
    text = response.data.decode('utf-8')

    for line in text.split('\n'):
        if line.startswith('flask_requests_total'):
            count = int(line.split()[-1])
            break

    assert count > 0

import pytest
import os
import tempfile
from fastapi.testclient import TestClient

# Set test env vars BEFORE importing app
os.environ['VOXPILOT_ENGINE'] = 'fake'
os.environ['VOXPILOT_LOG_LEVEL'] = 'WARNING'


@pytest.fixture(scope='session')
def temp_dir():
    with tempfile.TemporaryDirectory() as d:
        yield d


@pytest.fixture(scope='session', autouse=True)
def setup_env(temp_dir):
    os.environ['VOXPILOT_AUDIO_DIR'] = os.path.join(temp_dir, 'generated')
    os.environ['VOXPILOT_DB_PATH'] = os.path.join(temp_dir, 'test.db')
    os.makedirs(os.path.join(temp_dir, 'generated'), exist_ok=True)


@pytest.fixture(scope='session')
def client(setup_env):
    from app.main import app
    with TestClient(app) as c:
        yield c

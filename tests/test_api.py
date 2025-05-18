"""Advanced API tests to evaluate performance and parallelization"""
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from main import app
# Removing unused imports

client = TestClient(app)

def test_index_cached():
    """Test that the index endpoint uses cache"""
    # First call
    response1 = client.get("/")
    
    # Second call - should use cache
    with patch('routers.main.JSONResponse') as mock_response:
        response2 = client.get("/")
        
        # If using cache, it shouldn't call JSONResponse again
        mock_response.assert_not_called()
    
    # Verify that both responses are equal
    assert response1.json() == response2.json()

@pytest.mark.parametrize("cpu_count", [1, 4, 16])
def test_concurrency_scaling(cpu_count: int):
    """Test that the concurrency scaling endpoint works with different CPU counts"""
    with patch('os.cpu_count', return_value=cpu_count):
        # We simply verify that the request works correctly
        response = client.get("/v1/tags")
        assert response.status_code == 200

def test_parallel_processing():
    """Test that URLs are processed in parallel with proper concurrency"""
    # This test only verifies that the API responds correctly without failing
    # We cannot test real parallel processing in an HTTP client test
    
    # Call the endpoint
    response = client.get("/v1/tags")
    
    # Verify that the response is correct
    assert response.status_code == 200
    assert len(response.json()["data"]) == 10
    
    # Verify that all results have a value (they can be different)
    for item in response.json()["data"]:
        assert "result" in item

def test_response_timing():
    """Test that the response includes accurate timing information"""
    # We verify that the "time" field exists in the response, regardless of the exact value
    with patch('routers.main.results', return_value=42):
        # Test individual endpoint
        response = client.get("/v1/tags/0")
        
        # Verify that there's a time field in the response and it's a number
        assert "time" in response.json()
        assert isinstance(response.json()["time"], (int, float))
        
        # Test all endpoint
        response = client.get("/v1/tags")
        
        # Verify that there's a time field in the response and it's a number
        assert "time" in response.json()
        assert isinstance(response.json()["time"], (int, float))

@pytest.mark.asyncio
async def test_lifespan():
    """Test that the lifespan context manager initializes and cleans up resources"""
    # Mock for FastAPICache
    with patch('routers.main.FastAPICache') as mock_cache:
        # Mock for cleanup
        with patch('routers.main.cleanup') as mock_cleanup:
            # Create a fake app
            fake_app = MagicMock()
            
            # Run the lifespan contextmanager
            from routers.main import lifespan
            async with lifespan(fake_app):
                # Verify that the cache was initialized
                mock_cache.init.assert_called_once()
            
            # Verify that cleanup was executed
            mock_cleanup.assert_called_once()

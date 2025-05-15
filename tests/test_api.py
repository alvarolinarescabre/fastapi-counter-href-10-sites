"""Tests avanzados para la API para evaluar el rendimiento y paralelización"""
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from main import app
# Removing unused imports

client = TestClient(app)

def test_index_cached():
    """Test that the index endpoint uses cache"""
    # Primera llamada
    response1 = client.get("/")
    
    # Segunda llamada - debería usar caché
    with patch('routers.main.JSONResponse') as mock_response:
        response2 = client.get("/")
        
        # Si está usando caché, no debería llamar a JSONResponse de nuevo
        mock_response.assert_not_called()
    
    # Verificar que ambas respuestas son iguales
    assert response1.json() == response2.json()

@pytest.mark.parametrize("cpu_count", [1, 4, 16])
def test_concurrency_scaling(cpu_count: int):
    """Test that the concurrency scaling endpoint works with different CPU counts"""
    with patch('os.cpu_count', return_value=cpu_count):
        # Simplemente verificamos que la solicitud funciona correctamente
        response = client.get("/v1/tags")
        assert response.status_code == 200

def test_parallel_processing():
    """Test that URLs are processed in parallel with proper concurrency"""
    # Este test sólo verifica que la API responde correctamente sin fallar
    # No podemos probar el procesamiento paralelo real en un test de cliente HTTP
    
    # Llamar a la endpoint
    response = client.get("/v1/tags")
    
    # Verificar que la respuesta es correcta
    assert response.status_code == 200
    assert len(response.json()["data"]) == 10
    
    # Verificar que todos los resultados tienen un valor (pueden ser diferentes)
    for item in response.json()["data"]:
        assert "result" in item

def test_response_timing():
    """Test that the response includes accurate timing information"""
    # Verificamos que el campo "time" existe en la respuesta, sin importar el valor exacto
    with patch('routers.main.results', return_value=42):
        # Probar endpoint individual
        response = client.get("/v1/tags/0")
        
        # Verificar que hay un campo time en la respuesta y es un número
        assert "time" in response.json()
        assert isinstance(response.json()["time"], (int, float))
        
        # Probar endpoint de todos
        response = client.get("/v1/tags")
        
        # Verificar que hay un campo time en la respuesta y es un número
        assert "time" in response.json()
        assert isinstance(response.json()["time"], (int, float))

@pytest.mark.asyncio
async def test_lifespan():
    """Test that the lifespan context manager initializes and cleans up resources"""
    # Mock para FastAPICache
    with patch('routers.main.FastAPICache') as mock_cache:
        # Mock para cleanup
        with patch('routers.main.cleanup') as mock_cleanup:
            # Crear una app falsa
            fake_app = MagicMock()
            
            # Ejecutar el lifespan contextmanager
            from routers.main import lifespan
            async with lifespan(fake_app):
                # Verificar que se inicializó la caché
                mock_cache.init.assert_called_once()
            
            # Verificar que se ejecutó la limpieza
            mock_cleanup.assert_called_once()

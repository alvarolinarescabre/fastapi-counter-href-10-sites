"""
Tests optimizados para los helpers de la aplicación.
Incluye pruebas de rendimiento y uso de memoria.
"""
import pytest
import time
from unittest.mock import patch, MagicMock, AsyncMock
from aiohttp import ClientSession, ClientResponse, ClientError
from typing import AsyncGenerator

from libs.helpers import search_tag, fetch, results, cleanup, pattern_compiled


@pytest.fixture
async def mock_session() -> AsyncGenerator[MagicMock, None]:
    """Fixture para proporcionar una sesión mock con tipado apropiado"""
    session = MagicMock(spec=ClientSession)
    mock_response = MagicMock(spec=ClientResponse)
    mock_context = MagicMock()
    mock_context.__aenter__.return_value = mock_response
    session.get.return_value = mock_context
    yield session


@pytest.mark.asyncio
async def test_fetch_performance():
    """Probar el rendimiento de la función fetch"""
    # Crear mock con respuesta realista
    mock_session = MagicMock(spec=ClientSession)
    mock_response = AsyncMock()
    mock_response.text.return_value = "<!DOCTYPE html><html><body><a href='http://test.com'>test</a></body></html>"
    
    mock_context_manager = MagicMock()
    mock_context_manager.__aenter__.return_value = mock_response
    mock_session.get.return_value = mock_context_manager
    
    # Medir tiempo de ejecución
    start_time = time.time()
    result = await fetch(mock_session, "http://example.com")
    end_time = time.time()
    
    # Verificar respuesta y rendimiento
    assert result is not None
    assert len(result) > 0
    assert isinstance(result, str)
    assert "test" in result
    
    # El tiempo debe ser pequeño para un mock
    execution_time = end_time - start_time
    assert execution_time < 0.1


def test_search_tag_performance():
    """Probar el rendimiento de search_tag con diferentes tamaños de entrada"""
    # Caso básico
    html_small = "<a href='http://test.com'>link text</a>"
    assert search_tag(html_small) == 2
    
    # Caso con muchos enlaces
    html_large = "".join([
        f"<a href='http://test{i}.com'>link text {i}</a>" 
        for i in range(1000)
    ])
    
    # Medir tiempo para procesamiento de documento grande
    start_time = time.time()
    result = search_tag(html_large)
    end_time = time.time()
    
    # Verificar resultado y rendimiento
    assert result == 3000  # 3 palabras por enlace * 1000 enlaces
    execution_time = end_time - start_time
    assert execution_time < 0.1  # Debe ser muy rápido incluso con 1000 enlaces
    
    # Probar con entrada vacía
    assert search_tag("") == 0


@pytest.mark.asyncio
async def test_results_error_handling():
    """Probar que la función results maneja errores correctamente"""
    with patch('libs.helpers.get_session') as mock_get_session:
        mock_session = MagicMock(spec=ClientSession)
        mock_get_session.return_value = mock_session
        
        with patch('libs.helpers.fetch') as mock_fetch:
            # Simular error en fetch
            mock_fetch.side_effect = ClientError("Test error")
            
            # La excepción debería propagarse
            with pytest.raises(ClientError):
                await results("http://example.com")


@pytest.mark.asyncio
async def test_error_retry_mechanism():
    """Probar que el mecanismo de reintento funciona correctamente"""
    mock_session = MagicMock(spec=ClientSession)
    
    # Configurar el mock para fallar en los primeros 2 intentos y luego tener éxito
    from typing import Union, Any
    side_effects: list[Union[ClientError, Any]] = [
        ClientError("Error 1"),
        ClientError("Error 2"),
        AsyncMock(
            __aenter__=AsyncMock(
                return_value=AsyncMock(
                    text=AsyncMock(return_value="Success after retries")
                )
            )
        )
    ]
    mock_session.get.side_effect = side_effects
    
    # Debe tener éxito después de los reintentos
    result = await fetch(mock_session, "http://example.com", max_retries=3)
    assert result == "Success after retries"
    assert mock_session.get.call_count == 3  # Llamado 3 veces
    

@pytest.mark.asyncio
async def test_cleanup_closes_session():
    """Probar que cleanup cierra la sesión correctamente"""
    # Crear un mock de sesión global
    mock_session = MagicMock(spec=ClientSession)
    mock_session.closed = False
    
    with patch('libs.helpers._session', mock_session):
        await cleanup()
        
        # Verificar que se llamó al método close
        mock_session.close.assert_called_once()


def test_pattern_compiled_performance():
    """Probar el rendimiento del patrón regex compilado"""
    test_html = """
    <html>
    <body>
        <a href="http://test1.com">Link 1</a>
        <a href="https://test2.com">Link 2</a>
        <a href="/relative/path">Link 3</a>
        <a href="http://test3.com">Link 4</a>
    </body>
    </html>
    """
    
    # Medir tiempo de ejecución
    start_time = time.time()
    matches = pattern_compiled.findall(test_html)
    end_time = time.time()
    
    # Verificar resultados
    assert len(matches) == 3  # Debe encontrar 3 enlaces (http o https)
    assert "Link 1" in matches
    assert "Link 2" in matches
    assert "Link 4" in matches
    
    # Verificar rendimiento
    execution_time = end_time - start_time
    assert execution_time < 0.01  # El patrón compilado debe ser muy rápido

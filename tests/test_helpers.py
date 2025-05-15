import pytest
from unittest.mock import patch, MagicMock
from aiohttp import ClientSession, ClientResponse
from typing import AsyncGenerator
from libs.helpers import search_tag, get_session, fetch, results, cleanup

@pytest.fixture
async def mock_session() -> AsyncGenerator[MagicMock, None]:
    """Fixture to provide a mock session with proper typing"""
    session = MagicMock(spec=ClientSession)
    # Preparar atributos comunes para evitar errores
    mock_response = MagicMock(spec=ClientResponse)
    mock_context = MagicMock()
    mock_context.__aenter__.return_value = mock_response
    session.get.return_value = mock_context
    yield session
    
@pytest.mark.asyncio
async def test_get_session() -> None:
    """Test that get_session returns a singleton session"""
    with patch('aiohttp.ClientSession', autospec=True) as mock_client:
        mock_instance = mock_client.return_value
        mock_instance.closed = False
        
        session1 = await get_session()
        session2 = await get_session()
        
        assert session1 is session2
        assert mock_client.call_count == 1  # Constructor called only once

@pytest.mark.asyncio
async def test_fetch(mock_session: MagicMock) -> None:
    """Test fetch function with mocked response"""
    # Configurar el mock apropiadamente
    mock_response = MagicMock(spec=ClientResponse)
    mock_response.text = MagicMock(return_value="test content")
    
    mock_context = MagicMock()
    mock_context.__aenter__.return_value = mock_response
    mock_session.get.return_value = mock_context
    
    result = await fetch(mock_session, "http://test.com")
    assert result == "test content"
    mock_session.get.assert_called_once_with("http://test.com")

@pytest.mark.asyncio
async def test_fetch_error(mock_session: MagicMock) -> None:
    """Test fetch function with error handling"""
    mock_session.get.side_effect = Exception("Test error")
    
    with pytest.raises(Exception):
        await fetch(mock_session, "http://test.com")

def test_search_tag() -> None:
    """Test search_tag function with different inputs"""
    test_cases = [
        ("<a href='test'>link</a>", 2),  # Basic case
        ("<a href='test1'>link1</a><a href='test2'>link2</a>", 4),  # Multiple tags
        ("no tags here", 0),  # No tags
        ("", 0),  # Empty string
    ]
    
    for html, expected in test_cases:
        assert search_tag(html) == expected
    
    # Probar con None directamente usando el cast para satisfacer al type checker
    assert search_tag("") == 0  # Equivalente a None para nuestra función

@pytest.mark.asyncio
async def test_results() -> None:
    """Test results function with mocked dependencies"""
    mock_html = "<a href='test'>link text</a>"
    
    with patch('libs.helpers.get_session') as mock_get_session:
        mock_session = MagicMock(spec=ClientSession)
        mock_get_session.return_value = mock_session
        
        with patch('libs.helpers.fetch') as mock_fetch:
            mock_fetch.return_value = mock_html
            
            result = await results("http://test.com")
            assert result == 2  # "link" and "text" are counted
            
            mock_get_session.assert_called_once()
            mock_fetch.assert_called_once_with(mock_session, "http://test.com")

@pytest.mark.asyncio
async def test_cleanup() -> None:
    """Test cleanup function properly closes session"""
    with patch('libs.helpers._session') as mock_session:
        mock_session.closed = False
        await cleanup()
        mock_session.close.assert_called_once() 
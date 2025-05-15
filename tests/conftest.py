import pytest
from typing import Generator
import asyncio
from unittest.mock import patch

# Configuración para poder usar async en pruebas
@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

# Mock para los ajustes para evitar leer archivos de configuración reales
@pytest.fixture(autouse=True)
def mock_settings() -> Generator[None, None, None]:
    """Mock the settings to use test values."""
    with patch("conf.settings.Settings") as mock_settings:
        # Configurar valores predeterminados para pruebas
        mock_settings.return_value.urls = [
            "https://test1.com",
            "https://test2.com",
            "https://test3.com",
            "https://test4.com",
            "https://test5.com",
            "https://test6.com",
            "https://test7.com",
            "https://test8.com",
            "https://test9.com",
            "https://test10.com",
        ]
        mock_settings.return_value.pattern = r"href=\"(http|https)://"
        mock_settings.return_value.cache_expire = 10
        mock_settings.return_value.timeout = 5
        yield 
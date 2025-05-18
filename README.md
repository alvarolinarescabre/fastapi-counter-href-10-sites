# FastAPI Counter HREF

A high-performance web scraper that counts words within HTML tags using FastAPI and async operations.

## Features

- Asynchronous HTTP requests with connection pooling
- HTTP client-side caching with SQLite or memory
- Automatic retries with exponential backoff and jitter
- Parallelism automatically adjusted according to number of CPUs
- Optimized TCP connections with DNS caching
- Custom request headers for better compatibility
- Efficient regex pattern matching with pre-compilation
- Comprehensive unit testing with mocking
- Proper error handling and timeouts
- Semaphore-based concurrency control
- Improved FastAPI caching with customizable expiration

## Installation

1. Clone the repository
2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running Tests

Run the tests with coverage:

```bash
# Run all tests with coverage report
pytest --cov=. --cov-report=term --cov-report=html

# Run specific tests
pytest tests/test_helpers.py
pytest tests/test_helpers_advanced.py  # Advanced tests for optimizations
pytest tests/test_api_advanced.py      # API performance tests
```

This will generate coverage reports in both terminal and HTML formats.

## Performance Testing

To evaluate the impact of the optimizations, use the performance testing script:

```bash
# Asegúrate de que la aplicación esté ejecutándose en localhost:8080
python performance_test.py
```

Este script generará gráficas comparativas mostrando las mejoras de rendimiento.

## Usage

The main functionality is provided through the `helpers.py` module which offers:

- `get_session()`: Returns an optimized HTTP session with connection pooling and caching
- `fetch(session, url, max_retries=3)`: Fetches content from a URL with error handling y reintentos
- `search_tag(data, pattern)`: Searches for words within HTML tags using optimized regex
- `results(url)`: Combines the above to analyze a URL with caching
- `cleanup()`: Properly closes resources when done

## Performance Optimizations

### Network Optimizations
- Connection pooling (100 connections limit)
- DNS caching (5 minutes TTL)
- Custom optimized headers
- Configurable timeouts
- Proper resource cleanup
- Reintentos automáticos con backoff exponencial y jitter
- Cliente HTTP con caché usando SQLite o memoria

### Processing Optimizations
- Pre-compiled regex patterns con flags IGNORECASE y DOTALL
- Efficient list comprehensions and direct sum
- Early returns for empty data
- Semaphore con ajuste dinámico según CPUs disponibles
- Proper error handling and exception management

### Caching Optimizations
- FastAPI cache with customizable expiration
- LRU-cached settings
- Pre-defined response objects
- Input validation with Path parameters
- HTTP client-side caching para reducir requests repetidos

## Configuration

The behavior can be modified by adjusting the settings in `conf/settings.py`:

- `cache_expire`: Cache expiration time in seconds
- `timeout`: HTTP request timeout in seconds
- `pattern`: Regex pattern for searching
- `cache_backend`: Tipo de backend para caché ("sqlite" o cualquier otro valor para memoria)
- `cache_db_path`: Ruta para SQLite si se usa como backend

## Error Handling

The code includes proper error handling for:
- Network timeouts
- Invalid URLs
- HTTP errors
- Connection limits
- Malformed HTML
- Invalid request parameters

## Resource Management

All resources are properly managed:
- Sessions are reused and properly closed
- Connection pools are efficiently utilized
- Memory usage is optimized with generators and comprehensions
- DNS cache reduces lookup overhead

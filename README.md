# FastAPI Counter HREF

A high-performance web scraper that counts words within HTML tags using FastAPI and async operations.

## Features

- Asynchronous HTTP requests with connection pooling
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
pytest
```

This will generate coverage reports in both terminal and HTML formats.

## Usage

The main functionality is provided through the `helpers.py` module which offers:

- `get_session()`: Returns an optimized HTTP session with connection pooling
- `fetch(session, url)`: Fetches content from a URL with error handling
- `search_tag(data, pattern)`: Searches for words within HTML tags
- `results(url)`: Combines the above to analyze a URL
- `cleanup()`: Properly closes resources when done

## Performance Optimizations

### Network Optimizations
- Connection pooling (100 connections limit)
- DNS caching (5 minutes TTL)
- Custom optimized headers
- Configurable timeouts
- Proper resource cleanup

### Processing Optimizations
- Pre-compiled regex patterns
- Efficient list comprehensions and direct sum
- Early returns for empty data
- Semaphore for controlled concurrency
- Proper error handling and exception management

### Caching Optimizations
- FastAPI cache with customizable expiration
- LRU-cached settings
- Pre-defined response objects
- Input validation with Path parameters

## Configuration

The behavior can be modified by adjusting the settings in `conf/settings.py`:

- `cache_expire`: Cache expiration time in seconds
- `timeout`: HTTP request timeout in seconds
- `pattern`: Regex pattern for searching

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

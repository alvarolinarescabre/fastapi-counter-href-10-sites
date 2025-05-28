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

## Docker Usage

You can also run the application using Docker:

```bash
# Build the Docker image
docker build -t fastapi-counter-href .

# Run the container
docker run -d -p 8080:80 --name fastapi-counter fastapi-counter-href

# Check the health status
docker exec fastapi-counter curl -f http://localhost/health || exit 1
```

## API Endpoints

The application provides the following endpoints:

- `GET /` - Welcome message and basic information
- `GET /health` - Health check endpoint
- `GET /href/{url}` - Count href tags in the specified URL
  - Example: `GET /href/https://www.python.org`
  - Returns: JSON with the count of href tags found

## Running the Application

Start the FastAPI server:

```bash
# Development mode
uvicorn main:app --reload --host 0.0.0.0 --port 8080

# Production mode
uvicorn main:app --host 0.0.0.0 --port 8080 --workers 4
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
# Make sure the application is running on localhost:8080
python performance_test.py
```

This script will generate comparative graphs showing performance improvements.

## Usage

The main functionality is provided through the `helpers.py` module which offers:

- `get_session()`: Returns an optimized HTTP session with connection pooling and caching
- `fetch(session, url, max_retries=3)`: Fetches content from a URL with error handling and retries
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
- Automatic retries with exponential backoff and jitter
- HTTP client with cache using SQLite or memory

### Processing Optimizations
- Pre-compiled regex patterns with IGNORECASE and DOTALL flags
- Efficient list comprehensions and direct sum
- Early returns for empty data
- Semaphore with dynamic adjustment based on available CPUs
- Proper error handling and exception management

### Caching Optimizations
- FastAPI cache with customizable expiration
- LRU-cached settings
- Pre-defined response objects
- Input validation with Path parameters
- HTTP client-side caching to reduce repetitive requests

## Configuration

The behavior can be modified by adjusting the settings in `conf/settings.py`:

- `cache_expire`: Cache expiration time in seconds
- `timeout`: HTTP request timeout in seconds
- `pattern`: Regex pattern for searching
- `cache_backend`: Cache backend type ("sqlite" or any other value for memory)
- `cache_db_path`: SQLite path if used as backend

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

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/)
- Uses [aiohttp](https://docs.aiohttp.org/) for async HTTP requests
- Performance testing with [matplotlib](https://matplotlib.org/)
- Testing framework: [pytest](https://pytest.org/)

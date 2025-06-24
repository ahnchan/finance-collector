# Finance Collector

A REST API for collecting financial data from various sources.

## Features

- Fetch historical price data (open, close, high, low, volume) for tickers
- Support for date filtering
- Automatic country detection based on ticker symbol
- Uses Yahoo Finance for US tickers
- Client credential authentication

## Setup

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -e .
   ```
3. Create a `.env` file with your credentials (or set environment variables):
   ```
   CLIENT_ID=your_client_id
   CLIENT_SECRET=your_client_secret
   JWT_SECRET_KEY=your_secret_key
   JWT_ALGORITHM=HS256
   JWT_EXPIRATION_MINUTES=30
   ```

## Running the API

### Local Development

```bash
python main.py
```

The API will be available at http://localhost:8000

### Using Docker

You can also run the application using Docker:

```bash
# Build and start the container
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the container
docker-compose down
```

The API will be available at http://localhost:8000

## API Documentation

Once the server is running, you can access the interactive API documentation at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Authentication

To use the API, you need to:

1. Get an access token using your client credentials:
   ```bash
   curl -X POST "http://localhost:8000/token" \
     -H "Content-Type: application/json" \
     -d '{"client_id": "your_client_id", "client_secret": "your_client_secret"}'
   ```

2. Use the token in subsequent requests:
   ```bash
   curl -X GET "http://localhost:8000/ticker/AAPL" \
     -H "Authorization: Bearer your_access_token"
   ```

## API Endpoints

### GET /ticker/{ticker}

Get historical price data for a ticker.

Parameters:
- `ticker`: The ticker symbol (e.g., AAPL for Apple)
- `date` (optional): Specific date to fetch data for (format: YYYY-MM-DD)
- `country` (optional): Country override

Example:
```bash
# Get data for a specific date
curl -X GET "http://localhost:8000/ticker/AAPL?date=2023-01-10" \
  -H "Authorization: Bearer your_access_token"

# Get all available data
curl -X GET "http://localhost:8000/ticker/AAPL" \
  -H "Authorization: Bearer your_access_token"
```

## Testing

The project includes a comprehensive test suite covering unit tests, integration tests, and API tests.

### Running Tests

To run the tests, first install the development dependencies:

```bash
pip install -e ".[dev]"
```

Then run the tests using the provided script:

```bash
python run_tests.py
```

This will run all tests and generate a coverage report.

### Test Structure

- `tests/test_auth.py` - Tests for authentication functionality
- `tests/test_finance.py` - Tests for finance data fetching
- `tests/test_models.py` - Tests for data models
- `tests/test_api.py` - Tests for API endpoints
- `tests/test_integration.py` - Integration tests for the full API flow

### Running Specific Tests

To run a specific test file:

```bash
python run_tests.py tests/test_auth.py
```

To run a specific test function:

```bash
python run_tests.py tests/test_auth.py::test_get_token_valid_credentials
```

## Docker

The application includes Docker configuration for easy deployment.

### Docker Files

- `Dockerfile`: Defines the container image
- `.dockerignore`: Specifies files to exclude from the Docker image (including .env)
- `docker-compose.yml`: Configures the Docker service

### Building and Running with Docker

You can use the provided scripts to easily build and run the Docker container:

```bash
# Build and run the container
./docker-run.sh

# Stop the container
./docker-stop.sh
```

Alternatively, you can use Docker commands directly:

```bash
# Build the Docker image
docker build -t finance-collector .

# Run the container
docker run -p 8000:8000 finance-collector

# Or use docker-compose
docker-compose up -d
```

### Environment Variables

When running with Docker, you can provide environment variables in several ways:

1. Create a `.env` file in the project root (not included in the Docker image)
2. Set environment variables in the `docker-compose.yml` file
3. Pass environment variables when running the container:

```bash
docker run -p 8000:8000 \
  -e CLIENT_ID=your_client_id \
  -e CLIENT_SECRET=your_client_secret \
  -e JWT_SECRET_KEY=your_secret_key \
  finance-collector
```

## Deployment

### GitHub Actions to Google Cloud Run

This project includes a GitHub Actions workflow for automatic deployment to Google Cloud Run using Google Container Registry (GCR).

#### Setup

To set up the GitHub Actions deployment:

1. Configure the required GitHub secrets:
   - `GCP_PROJECT_ID`: Your Google Cloud Platform project ID
   - `GCP_SA_KEY`: The JSON key of a service account with appropriate permissions
   - Environment variables from your `.env` file:
     - `CLIENT_ID`, `CLIENT_SECRET`, `JWT_SECRET_KEY`, `API_KEY`
     - `JWT_ALGORITHM` (optional, defaults to HS256)
     - `JWT_EXPIRATION_MINUTES` (optional, defaults to 30)

2. Push to the `main` branch to trigger automatic deployment, or manually trigger the workflow from the Actions tab.

The workflow automatically passes these environment variables to your Cloud Run service during deployment, ensuring your application has access to all required configuration without hardcoding sensitive information.

For detailed instructions, see [GitHub Actions Deployment Guide](docs/github-actions-deployment.md).

#### Deployment Configuration

The deployment is configured to:
- Build a Docker image from your Dockerfile
- Push the image to Google Container Registry (GCR)
- Deploy the image to Google Cloud Run in the Asia Northeast 3 (Seoul) region
- Make the service publicly accessible (configurable)

You can customize the deployment by editing the `.github/workflows/deploy-to-cloud-run.yml` file.

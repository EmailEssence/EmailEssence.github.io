# Email Essence Backend

The backend service for Email Essence, a fast, scalable, and secure email summarization service.

## Development Setup

### Prerequisites

- Python 3.12+
- Docker & Docker Compose
- Git

### Local Development Setup

For local development without Docker, use one of the provided setup scripts:

#### On Unix/Linux/macOS:

```bash
# Run the setup script to create a virtual environment and install dependencies
./setup.sh
```

#### On Windows:

```bash
# Run the setup script to create a virtual environment and install dependencies
.\setup.bat
```

These scripts will:
1. Create a Python virtual environment
2. Install all required dependencies
3. Set up the development environment

### Environment Variables

Copy the example environment file:

```bash
cp .env.example .env
```

Edit the `.env` file and fill in your configuration values:

```
# Required variables:
google_client_id=your_google_client_id
google_client_secret=your_google_client_secret
email_account=your_email@example.com
mongo_uri=your_mongodb_connection_string
openai_api_key=your_openai_api_key

# Optional variables with defaults as shown
environment=development
summarizer_provider=openai
summarizer_model=gpt-4o-mini
```

## Docker Setup

### Using Docker Compose (Recommended for Development)

The easiest way to run the backend is using Docker Compose:

1. Make sure you have a `.env` file in the project root with all required variables.

2. Build and start the container:

```bash
docker-compose up
```

This will:
- Build the Docker image using the multi-stage Dockerfile
- Mount the backend directory for live code changes
- Mount the .env file for configuration
- Expose the service on port 8000

### Using Pre-built Docker Image (Recommended for Frontend Team)

To quickly get started without building the image locally, you can pull the pre-built image from our Docker registry:

1. Pull the latest image:

```bash
docker pull emailessence/emailessence-backend:latest
```

2. Run the container with environment variables:

```bash
# Option 1: Using an .env file
docker run -p 8000:8000 --env-file .env emailessence/emailessence-backend:latest

# Option 2: Providing environment variables directly
docker run -p 8000:8000 \
    -e google_client_id=your_client_id \
    -e google_client_secret=your_secret \
    -e email_account=your_email \
    -e mongo_uri=mongodb://user:pass@host:port/db \
    -e openai_api_key=your_api_key \
    emailessence/emailessence-backend:latest
```

### Building and Running the Docker Image Manually

If you prefer to build and run the Docker image directly:

1. Build the image:

```bash
# From the project root
docker build -f backend/Dockerfile -t email-essence-backend .
```

2. Run the container with environment variables:

```bash
# Run with environment variables from .env file
docker run -p 8000:8000 --env-file .env email-essence-backend
```

## Deployment

### Render Deployment

For Render deployments, environment variables are configured through the Render dashboard:

1. Go to your service in the Render dashboard
2. Navigate to the "Environment" tab
3. Add each required environment variable:
   - `google_client_id`
   - `google_client_secret`
   - `email_account`
   - `mongo_uri`
   - `openai_api_key`
   - Any optional variables you wish to override

This separates your development environment configuration from your production deployment, following security best practices.

## API Documentation

Once the server is running, you can access:
- Swagger UI documentation: http://localhost:8000/docs
- ReDoc alternative documentation: http://localhost:8000/redoc

## CI/CD Setup

For CI/CD environments, use the CI setup scripts:

```bash
# Unix/Linux/macOS
./setup-ci.sh

# Windows
.\setup-ci.bat
```

## Troubleshooting

### Container Issues

If the container fails to start:
1. Check your `.env` file is properly configured
2. Ensure MongoDB connection string is correct
3. Check logs: `docker-compose logs backend`

### API Issues

For issues with the API:
1. Check FastAPI logs within the container
2. Verify MongoDB connection and credentials
3. Confirm that all required environment variables are set

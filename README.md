# Bittensor TAO Analytics API

An asynchronous API service for querying Bittensor blockchain TAO dividends with Redis caching and sentiment-based stake/unstake automation.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.95.0+-green.svg)](https://fastapi.tiangolo.com/)
[![Bittensor](https://img.shields.io/badge/Bittensor-6.0.0+-blue.svg)](https://github.com/opentensor/bittensor)

## Table of Contents

- [Features](#features)
- [Requirements](#requirements)
- [Installation and Setup](#installation-and-setup)
- [API Endpoints](#api-endpoints)
- [Running Tests](#running-tests)
- [Project Structure](#project-structure)
- [Configuration](#configuration)
- [License](#license)

## Features

- **Async Blockchain Integration**: Query TAO dividends using Bittensor's AsyncSubtensor
- **Performance Optimization**: Redis caching with 2-minute TTL for fast responses
- **API Security**: Bearer token authentication for all endpoints
- **Smart Staking**:
  * Twitter sentiment analysis with Datura.ai
  * LLM-based scoring via Chutes.ai
  * Automated stake/unstake proportional to sentiment
- **Background Processing**: Celery workers for non-blocking operations
- **Data Persistence**: PostgreSQL database with async drivers
- **Containerization**: Complete Docker setup for production deployment

## Requirements

* Python 3.9+
* Docker and Docker Compose
* PostgreSQL
* Redis

## Installation and Setup

### Using Docker (Recommended)

1. **Clone the repository**:
```bash
git clone https://github.com/yourusername/bittensor-tao-analytics-api.git
cd bittensor-tao-analytics-api
```

2. **Set up environment variables**:
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. **Launch with Docker Compose**:
```bash
docker compose up --build
```
This starts:
* FastAPI application (port 8000)
* Celery worker
* Redis
* PostgreSQL

4. **Access the API**:
* API: http://localhost:8000
* Swagger docs: http://localhost:8000/docs


### Manual Setup:

1. **Install dependencies**:
```bash
pip install -r requirements.txt
```

2. **Configure database and cache:**:

This starts:
* Set up PostgreSQL instance
* Configure Redis server
* Update .env file with connection details

3. **Start the API server**:
```bash
uvicorn app.main:app --reload
```

4. **Run Celery worker (separate terminal)**:
```bash
celery -A app.worker.celery_app worker --loglevel=info
```

4. **Access the API**:
* API: http://localhost:8000
* Swagger docs: http://localhost:8000/docs

## API Endpoints

### GET /api/v1/tao_dividends

Returns TAO dividends for a specific subnet and hotkey with optional sentiment-based trading.

#### Query Parameters
| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| netuid | integer | Subnet ID | DEFAULT_NETUID from config |
| hotkey | string | Hotkey address | DEFAULT_HOTKEY from config |
| trade | boolean | Trigger stake/unstake based on sentiment | false |

#### Authentication
Bearer token required in Authorization header

#### Example Request
```bash
curl -X GET "http://localhost:8000/api/v1/tao_dividends?netuid=18&hotkey=5FFApaS75bv5pJHfZkqPmBzlVZ7UE1qfGiI8nsSMq4q8WUWQ&trade=true" \
     -H "Authorization: Bearer your_token_here"
```

#### Example Response
```bash
{
  "netuid": 18,
  "hotkey": "5FFApaS75bv5pJHfZkqPmBzlVZ7UE1qfGiI8nsSMq4q8WUWQ",
  "dividend": 123456789,
  "cached": true,
  "stake_tx_triggered": true,
  "timestamp": "2023-04-01T12:34:56.789Z"
}
```

## Running Tests

Execute the test suite with pytest:

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run with coverage report
pytest --cov=app
```

```
bittensor-tao-analytics-api/
├── app/                      # Main application package
│   ├── api/                  # API endpoints
│   ├── services/             # Business logic services
│   ├── models.py             # Data models and schemas
│   ├── db.py                 # Database models and connection
│   ├── worker.py             # Celery worker configuration
│   └── main.py               # FastAPI application entry point
├── tests/                    # Test suite
├── docker-compose.yml        # Docker Compose configuration
├── Dockerfile                # Docker configuration
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

## Configuration

The application is configured through environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| API_TOKEN | Authentication token | *required* |
| API_PORT | FastAPI port | 8000 |
| ENVIRONMENT | Runtime environment | development |
| REDIS_HOST | Redis hostname | redis |
| REDIS_PORT | Redis port | 6379 |
| REDIS_PASSWORD | Redis password | *empty* |
| REDIS_TTL | Cache TTL (seconds) | 120 |
| DATABASE_URL | PostgreSQL connection URI | *required* |
| BITTENSOR_NETWORK | Bittensor network | testnet |
| DEFAULT_NETUID | Default subnet ID | 18 |
| DEFAULT_HOTKEY | Default hotkey address | *config value* |
| WALLET_MNEMONIC | Bittensor wallet mnemonic | *required* |
| DATURA_API_KEY | Datura.ai API key | *required* |
| CHUTES_API_KEY | Chutes.ai API key | *required* |
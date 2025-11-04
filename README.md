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

- **Comprehensive API Suite**: 20+ endpoints covering all aspects of Bittensor operations
- **Async Blockchain Integration**: Query TAO dividends using Bittensor's AsyncSubtensor
- **Performance Optimization**: Redis caching with 2-minute TTL for fast responses
- **API Security**: Bearer token authentication for all endpoints
- **Smart Staking**:
  * Twitter sentiment analysis with Datura.ai
  * LLM-based scoring via Chutes.ai
  * Automated stake/unstake proportional to sentiment
  * Manual stake/unstake operations
- **Subnet Management**: List and monitor all subnets with detailed metrics
- **Validator & Miner Analytics**: Track performance, stake, and rankings
- **Wallet Management**: Monitor balances and stakes across subnets
- **Advanced Analytics**:
  * Historical dividend tracking
  * Stake/unstake trend analysis
  * Network-wide statistics
  * Percentile and statistical analysis
- **Pagination Support**: Efficient data retrieval for large datasets
- **Background Processing**: Celery workers for non-blocking operations
- **Data Persistence**: PostgreSQL database with async drivers and comprehensive metrics storage
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

All endpoints require Bearer token authentication via the Authorization header.

### TAO Dividends

#### GET /api/v1/tao_dividends
Returns TAO dividends for a specific subnet and hotkey with optional sentiment-based trading.

**Query Parameters:**
| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| netuid | integer | Subnet ID | DEFAULT_NETUID from config |
| hotkey | string | Hotkey address | DEFAULT_HOTKEY from config |
| trade | boolean | Trigger stake/unstake based on sentiment | false |

**Example:**
```bash
curl -X GET "http://localhost:8000/api/v1/tao_dividends?netuid=18&hotkey=5FFApaS75bv5pJHfZkqPmBzlVZ7UE1qfGiI8nsSMq4q8WUWQ&trade=true" \
     -H "Authorization: Bearer your_token_here"
```

### Subnet Management

#### GET /api/v1/subnets
List all available subnets with pagination.

**Query Parameters:**
| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| page | integer | Page number | 1 |
| page_size | integer | Items per page (max 100) | 20 |

**Example:**
```bash
curl -X GET "http://localhost:8000/api/v1/subnets?page=1&page_size=20" \
     -H "Authorization: Bearer your_token_here"
```

#### GET /api/v1/subnets/{netuid}
Get detailed information about a specific subnet.

**Example:**
```bash
curl -X GET "http://localhost:8000/api/v1/subnets/18" \
     -H "Authorization: Bearer your_token_here"
```

#### GET /api/v1/network/stats
Get overall network statistics across all subnets.

**Example:**
```bash
curl -X GET "http://localhost:8000/api/v1/network/stats" \
     -H "Authorization: Bearer your_token_here"
```

### Validators & Miners

#### GET /api/v1/validators
List all validators, optionally filtered by subnet.

**Query Parameters:**
| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| netuid | integer | Filter by subnet ID | DEFAULT_NETUID |
| page | integer | Page number | 1 |
| page_size | integer | Items per page (max 100) | 20 |

**Example:**
```bash
curl -X GET "http://localhost:8000/api/v1/validators?netuid=18&page=1" \
     -H "Authorization: Bearer your_token_here"
```

#### GET /api/v1/validators/{hotkey}
Get detailed information about a specific validator.

**Query Parameters:**
| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| netuid | integer | Subnet ID | DEFAULT_NETUID |

**Example:**
```bash
curl -X GET "http://localhost:8000/api/v1/validators/5FHneW46xGXgs5mUiveU4sbTyGBzmstUspZC92UhjJM694ty?netuid=18" \
     -H "Authorization: Bearer your_token_here"
```

#### GET /api/v1/miners
List all miners, optionally filtered by subnet.

**Query Parameters:**
| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| netuid | integer | Filter by subnet ID | DEFAULT_NETUID |
| page | integer | Page number | 1 |
| page_size | integer | Items per page (max 100) | 20 |

#### GET /api/v1/miners/{hotkey}
Get detailed information about a specific miner.

### Stake Management

#### POST /api/v1/stake
Manually stake TAO to a specific hotkey on a subnet.

**Request Body:**
```json
{
  "netuid": 18,
  "hotkey": "5FFApaS75bv5pJHfZkqPmBzlVZ7UE1qfGiI8nsSMq4q8WUWQ",
  "action_type": "stake",
  "amount": 100.0,
  "sentiment_score": 75.5
}
```

**Example:**
```bash
curl -X POST "http://localhost:8000/api/v1/stake" \
     -H "Authorization: Bearer your_token_here" \
     -H "Content-Type: application/json" \
     -d '{"netuid": 18, "hotkey": "5FFApaS...", "action_type": "stake", "amount": 100.0}'
```

#### POST /api/v1/unstake
Manually unstake TAO from a specific hotkey on a subnet.

**Request Body:** Same as stake endpoint with `action_type: "unstake"`

#### GET /api/v1/stake/history
Get history of stake/unstake actions with optional filtering.

**Query Parameters:**
| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| netuid | integer | Filter by subnet ID | - |
| hotkey | string | Filter by hotkey | - |
| action_type | string | Filter by action (stake/unstake) | - |
| page | integer | Page number | 1 |
| page_size | integer | Items per page (max 100) | 20 |

**Example:**
```bash
curl -X GET "http://localhost:8000/api/v1/stake/history?netuid=18&page=1" \
     -H "Authorization: Bearer your_token_here"
```

#### GET /api/v1/stake/status/{transaction_hash}
Get the status of a specific stake/unstake transaction.

### Wallet Management

#### GET /api/v1/wallet/balance
Get wallet balance including free balance, staked balance, and total balance.

**Query Parameters:**
| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| wallet_address | string | Wallet address | Configured wallet |

**Example:**
```bash
curl -X GET "http://localhost:8000/api/v1/wallet/balance" \
     -H "Authorization: Bearer your_token_here"
```

#### GET /api/v1/wallet/stakes
Get all stakes for a wallet across different subnets.

**Query Parameters:**
| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| wallet_address | string | Wallet address | Configured wallet |

### Analytics & Statistics

#### GET /api/v1/analytics/dividends/history
Get historical dividend data with optional filtering.

**Query Parameters:**
| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| netuid | integer | Filter by subnet ID | - |
| hotkey | string | Filter by hotkey | - |
| days | integer | Number of days to look back (max 365) | 7 |
| page | integer | Page number | 1 |
| page_size | integer | Items per page (max 100) | 20 |

**Example:**
```bash
curl -X GET "http://localhost:8000/api/v1/analytics/dividends/history?days=30&netuid=18" \
     -H "Authorization: Bearer your_token_here"
```

#### GET /api/v1/analytics/dividends/trends
Get dividend trends and statistics over a specified time period.

**Query Parameters:**
| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| netuid | integer | Filter by subnet ID | - |
| hotkey | string | Filter by hotkey | - |
| days | integer | Number of days to analyze (max 365) | 30 |

**Example:**
```bash
curl -X GET "http://localhost:8000/api/v1/analytics/dividends/trends?days=30" \
     -H "Authorization: Bearer your_token_here"
```

#### GET /api/v1/analytics/stake/summary
Get stake/unstake summary statistics over a specified time period.

**Query Parameters:**
| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| netuid | integer | Filter by subnet ID | - |
| days | integer | Number of days to analyze (max 365) | 30 |

**Example:**
```bash
curl -X GET "http://localhost:8000/api/v1/analytics/stake/summary?days=30" \
     -H "Authorization: Bearer your_token_here"
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
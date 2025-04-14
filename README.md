markdown
# Bittensor TAO Analytics API

An asynchronous API service that dynamically stakes or unstakes tokens based on sentiment, combined with an asynchronous API service for querying Bittensor blockchain TAO dividends with Redis cache enabled.



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

#!/bin/bash

# Script to build and run the Finance Collector API in Docker

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Building Docker image...${NC}"
docker-compose build

echo -e "${YELLOW}Starting Docker container...${NC}"
docker-compose up -d

echo -e "${GREEN}Finance Collector API is running!${NC}"
echo -e "API is available at: http://localhost:8000"
echo -e "API Documentation: http://localhost:8000/docs"
echo -e ""
echo -e "To view logs: docker-compose logs -f"
echo -e "To stop the container: docker-compose down"

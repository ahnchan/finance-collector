#!/bin/bash

# Script to stop the Finance Collector API Docker container

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Stopping Docker container...${NC}"
docker-compose down

echo -e "${GREEN}Finance Collector API has been stopped.${NC}"

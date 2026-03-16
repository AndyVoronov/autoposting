#!/bin/bash

# Run tests
docker-compose -f docker-compose.yml -f docker-compose.test.yml run --rm api pytest

# Or locally:
# cd backend && pytest

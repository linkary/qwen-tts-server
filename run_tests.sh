#!/bin/bash
# Test runner script for Qwen3-TTS Server
# Usage: ./run_tests.sh [option]

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}🧪 Qwen3-TTS Server Test Suite${NC}"
echo "================================"
echo ""

# Check if in a conda environment (any environment is fine)
if [[ -z "$CONDA_DEFAULT_ENV" ]]; then
    echo -e "${YELLOW}⚠️  Warning: No conda environment activated${NC}"
    echo "   Run: conda activate <your-env-name>"
    echo ""
fi

# Parse command line option
TEST_TYPE=${1:-"all"}

case $TEST_TYPE in
    "unit")
        echo -e "${GREEN}Running unit tests only (fast)...${NC}"
        pytest tests/unit/ -v
        ;;
    "integration")
        echo -e "${GREEN}Running integration tests...${NC}"
        pytest tests/integration/ -v
        ;;
    "e2e")
        echo -e "${GREEN}Running end-to-end tests...${NC}"
        pytest tests/e2e/ -v
        ;;
    "preprocessing")
        echo -e "${GREEN}Running audio preprocessing tests...${NC}"
        pytest -m preprocessing tests/ -v
        ;;
    "fast")
        echo -e "${GREEN}Running fast tests only (skipping slow)...${NC}"
        pytest -m "not slow" tests/ -v
        ;;
    "coverage")
        echo -e "${GREEN}Running tests with coverage report...${NC}"
        pytest --cov=app --cov-report=html --cov-report=term tests/
        echo ""
        echo -e "${GREEN}✓ Coverage report generated in htmlcov/index.html${NC}"
        ;;
    "all")
        echo -e "${GREEN}Running all tests...${NC}"
        pytest tests/ -v
        ;;
    "help"|"-h"|"--help")
        echo "Usage: ./run_tests.sh [option]"
        echo ""
        echo "Options:"
        echo "  unit           - Run unit tests only (fast)"
        echo "  integration    - Run integration tests"
        echo "  e2e            - Run end-to-end tests"
        echo "  preprocessing  - Run audio preprocessing tests"
        echo "  fast           - Run fast tests only (skip slow)"
        echo "  coverage       - Run with coverage report"
        echo "  all            - Run all tests (default)"
        echo "  help           - Show this help message"
        echo ""
        echo "Examples:"
        echo "  ./run_tests.sh                  # Run all tests"
        echo "  ./run_tests.sh unit             # Run unit tests only"
        echo "  ./run_tests.sh preprocessing    # Test preprocessing features"
        echo "  ./run_tests.sh coverage         # Generate coverage report"
        exit 0
        ;;
    *)
        echo -e "${RED}❌ Unknown option: $TEST_TYPE${NC}"
        echo "Run './run_tests.sh help' for usage information"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}✅ Tests completed!${NC}"

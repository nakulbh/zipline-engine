#!/bin/bash
# Docker Build Script for NSE Backtesting Engine
# ==============================================

set -e  # Exit on any error

echo "🐳 NSE Backtesting Engine - Docker Build Script"
echo "================================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    print_warning "Docker Compose not found. Using 'docker compose' instead."
    DOCKER_COMPOSE="docker compose"
else
    DOCKER_COMPOSE="docker-compose"
fi

# Parse command line arguments
BUILD_TYPE="full"
PUSH_IMAGE=false
RUN_AFTER_BUILD=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --quick)
            BUILD_TYPE="quick"
            shift
            ;;
        --push)
            PUSH_IMAGE=true
            shift
            ;;
        --run)
            RUN_AFTER_BUILD=true
            shift
            ;;
        --help)
            echo "Usage: $0 [OPTIONS]"
            echo "Options:"
            echo "  --quick    Quick build (use cache)"
            echo "  --push     Push image to registry"
            echo "  --run      Run container after build"
            echo "  --help     Show this help message"
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Create necessary directories
print_status "Creating necessary directories..."
mkdir -p results logs backtest_results

# Build the Docker image
print_status "Building Docker image..."

if [ "$BUILD_TYPE" = "quick" ]; then
    print_status "Quick build (using cache)..."
    docker build -t nse-backtesting-engine .
else
    print_status "Full build (no cache)..."
    docker build --no-cache -t nse-backtesting-engine .
fi

if [ $? -eq 0 ]; then
    print_success "Docker image built successfully!"
else
    print_error "Docker build failed!"
    exit 1
fi

# Tag the image with version
print_status "Tagging image..."
docker tag nse-backtesting-engine:latest nse-backtesting-engine:v1.0.0

# Push to registry if requested
if [ "$PUSH_IMAGE" = true ]; then
    print_status "Pushing image to registry..."
    # Uncomment and modify these lines for your registry
    # docker tag nse-backtesting-engine:latest your-registry/nse-backtesting-engine:latest
    # docker push your-registry/nse-backtesting-engine:latest
    print_warning "Push functionality not configured. Please set up your registry details."
fi

# Run container if requested
if [ "$RUN_AFTER_BUILD" = true ]; then
    print_status "Starting container..."
    $DOCKER_COMPOSE up -d
    
    if [ $? -eq 0 ]; then
        print_success "Container started successfully!"
        print_status "Access the container with: $DOCKER_COMPOSE exec nse-backtesting-engine bash"
    else
        print_error "Failed to start container!"
        exit 1
    fi
fi

# Display usage information
echo ""
print_success "Build completed successfully!"
echo ""
echo "🚀 Quick Start Commands:"
echo "  Start container:    $DOCKER_COMPOSE up -d"
echo "  Access shell:       $DOCKER_COMPOSE exec nse-backtesting-engine bash"
echo "  Run momentum:       $DOCKER_COMPOSE exec nse-backtesting-engine python run_momentum_strategy.py"
echo "  Run riskfolio:      $DOCKER_COMPOSE exec nse-backtesting-engine python examples/nse_riskfolio_demo.py"
echo "  View logs:          $DOCKER_COMPOSE logs -f"
echo "  Stop container:     $DOCKER_COMPOSE down"
echo ""
echo "📚 For more information, see DOCKER_GUIDE.md"

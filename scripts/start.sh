#!/bin/bash

# GraphQLite + Ollama Application Startup Script
# This script initializes the Python virtual environment, installs dependencies,
# and starts the application in detached mode

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Configuration
VENV_DIR="venv"
APP_FILE="app.py"
PID_FILE=".app.pid"
LOG_FILE="app.log"
PORT=8080

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  GraphQLite + Ollama Application${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is not installed. Please install Python 3.8 or higher.${NC}"
    exit 1
fi

echo -e "${GREEN}✓${NC} Python 3 found: $(python3 --version)"

# Create virtual environment if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
    echo -e "${YELLOW}📦 Creating virtual environment...${NC}"
    python3 -m venv $VENV_DIR
    echo -e "${GREEN}✓${NC} Virtual environment created"
else
    echo -e "${GREEN}✓${NC} Virtual environment already exists"
fi

# Activate virtual environment
echo -e "${YELLOW}🔧 Activating virtual environment...${NC}"
source $VENV_DIR/bin/activate

# Install/upgrade pip
echo -e "${YELLOW}📦 Upgrading pip...${NC}"
pip install --upgrade pip > /dev/null 2>&1

# Install requirements
if [ -f "requirements.txt" ]; then
    echo -e "${YELLOW}📦 Installing dependencies from requirements.txt...${NC}"
    pip install -r requirements.txt
    echo -e "${GREEN}✓${NC} Dependencies installed"
else
    echo -e "${RED}❌ requirements.txt not found${NC}"
    exit 1
fi

# Check if app is already running
if [ -f "$PID_FILE" ]; then
    OLD_PID=$(cat $PID_FILE)
    if ps -p $OLD_PID > /dev/null 2>&1; then
        echo -e "${YELLOW}⚠️  Application is already running (PID: $OLD_PID)${NC}"
        echo -e "${YELLOW}   Use ./scripts/stop.sh to stop it first${NC}"
        exit 1
    else
        # Remove stale PID file
        rm $PID_FILE
    fi
fi

# Check if Ollama is running
echo -e "${YELLOW}🤖 Checking Ollama connection...${NC}"
if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Ollama is running and accessible"
else
    echo -e "${YELLOW}⚠️  Ollama is not running or not accessible at http://localhost:11434${NC}"
    echo -e "${YELLOW}   The application will start but AI features may not work${NC}"
    echo -e "${YELLOW}   To start Ollama, run: ollama serve${NC}"
fi

# Start the application in detached mode
echo -e "${YELLOW}🚀 Starting application in detached mode...${NC}"
nohup python3 $APP_FILE > $LOG_FILE 2>&1 &
APP_PID=$!

# Save PID
echo $APP_PID > $PID_FILE

# Wait a moment for the app to start
sleep 2

# Check if the application is running
if ps -p $APP_PID > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Application started successfully!"
    echo ""
    echo -e "${BLUE}========================================${NC}"
    echo -e "${GREEN}🌐 Application URL:${NC}"
    echo -e "${BLUE}   http://localhost:$PORT${NC}"
    echo ""
    echo -e "${GREEN}🔗 GraphQL Endpoint:${NC}"
    echo -e "${BLUE}   http://localhost:$PORT/graphql${NC}"
    echo ""
    echo -e "${GREEN}💚 Health Check:${NC}"
    echo -e "${BLUE}   http://localhost:$PORT/api/health${NC}"
    echo ""
    echo -e "${GREEN}📝 Process ID:${NC} $APP_PID"
    echo -e "${GREEN}📄 Log File:${NC} $LOG_FILE"
    echo -e "${BLUE}========================================${NC}"
    echo ""
    echo -e "${YELLOW}💡 Tips:${NC}"
    echo -e "   • View logs: tail -f $LOG_FILE"
    echo -e "   • Stop app: ./scripts/stop.sh"
    echo -e "   • Check status: ps -p $APP_PID"
    echo ""
else
    echo -e "${RED}❌ Failed to start application${NC}"
    echo -e "${RED}   Check $LOG_FILE for errors${NC}"
    rm $PID_FILE
    exit 1
fi

# Made with Bob

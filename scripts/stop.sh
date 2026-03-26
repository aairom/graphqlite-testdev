#!/bin/bash

# GraphQLite + Ollama Application Stop Script
# This script stops the running application

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Configuration
PID_FILE=".app.pid"
LOG_FILE="app.log"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Stopping GraphQLite Application${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check if PID file exists
if [ ! -f "$PID_FILE" ]; then
    echo -e "${YELLOW}⚠️  No PID file found. Application may not be running.${NC}"
    
    # Try to find the process anyway
    APP_PID=$(pgrep -f "python3 app.py" || echo "")
    if [ -n "$APP_PID" ]; then
        echo -e "${YELLOW}   Found running process: $APP_PID${NC}"
        echo -e "${YELLOW}   Attempting to stop it...${NC}"
        kill $APP_PID 2>/dev/null || true
        sleep 1
        
        # Force kill if still running
        if ps -p $APP_PID > /dev/null 2>&1; then
            echo -e "${YELLOW}   Process still running, forcing stop...${NC}"
            kill -9 $APP_PID 2>/dev/null || true
        fi
        
        echo -e "${GREEN}✓${NC} Application stopped"
    else
        echo -e "${GREEN}✓${NC} No application process found"
    fi
    exit 0
fi

# Read PID from file
APP_PID=$(cat $PID_FILE)

# Check if process is running
if ! ps -p $APP_PID > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  Process $APP_PID is not running${NC}"
    rm $PID_FILE
    echo -e "${GREEN}✓${NC} Cleaned up stale PID file"
    exit 0
fi

# Stop the application
echo -e "${YELLOW}🛑 Stopping application (PID: $APP_PID)...${NC}"
kill $APP_PID 2>/dev/null || true

# Wait for process to stop
WAIT_TIME=0
MAX_WAIT=10
while ps -p $APP_PID > /dev/null 2>&1 && [ $WAIT_TIME -lt $MAX_WAIT ]; do
    sleep 1
    WAIT_TIME=$((WAIT_TIME + 1))
    echo -e "${YELLOW}   Waiting for process to stop... ($WAIT_TIME/$MAX_WAIT)${NC}"
done

# Force kill if still running
if ps -p $APP_PID > /dev/null 2>&1; then
    echo -e "${YELLOW}   Process still running, forcing stop...${NC}"
    kill -9 $APP_PID 2>/dev/null || true
    sleep 1
fi

# Verify process is stopped
if ps -p $APP_PID > /dev/null 2>&1; then
    echo -e "${RED}❌ Failed to stop application${NC}"
    exit 1
else
    echo -e "${GREEN}✓${NC} Application stopped successfully"
    rm $PID_FILE
    echo -e "${GREEN}✓${NC} Cleaned up PID file"
fi

echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}Application Status:${NC} Stopped"
if [ -f "$LOG_FILE" ]; then
    echo -e "${GREEN}Log File:${NC} $LOG_FILE"
    echo -e "${YELLOW}💡 View logs: tail -n 50 $LOG_FILE${NC}"
fi
echo -e "${BLUE}========================================${NC}"
echo ""

# Made with Bob

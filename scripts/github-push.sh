#!/bin/bash

# GitHub Push Script
# This script initializes a git repository (if needed) and pushes to GitHub
# Usage: ./scripts/github-push.sh <repository-url> <commit-message>

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check arguments
if [ $# -lt 2 ]; then
    echo -e "${RED}❌ Error: Missing required arguments${NC}"
    echo ""
    echo -e "${YELLOW}Usage:${NC}"
    echo -e "  ./scripts/github-push.sh <repository-url> <commit-message>"
    echo ""
    echo -e "${YELLOW}Example:${NC}"
    echo -e "  ./scripts/github-push.sh https://github.com/username/repo.git \"Initial commit\""
    echo ""
    exit 1
fi

REPO_URL="$1"
COMMIT_MESSAGE="$2"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  GitHub Push Script${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "${GREEN}Repository URL:${NC} $REPO_URL"
echo -e "${GREEN}Commit Message:${NC} $COMMIT_MESSAGE"
echo ""

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo -e "${RED}❌ Git is not installed. Please install Git first.${NC}"
    exit 1
fi

echo -e "${GREEN}✓${NC} Git found: $(git --version)"

# Check if .git directory exists
if [ ! -d ".git" ]; then
    echo -e "${YELLOW}📦 Initializing Git repository...${NC}"
    git init
    echo -e "${GREEN}✓${NC} Git repository initialized"
    
    # Create .gitignore if it doesn't exist
    if [ ! -f ".gitignore" ]; then
        echo -e "${YELLOW}📝 Creating .gitignore...${NC}"
        cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
venv/
ENV/
env/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# Application
.app.pid
app.log
*.log

# OS
.DS_Store
Thumbs.db

# Database
*.db
*.sqlite
*.sqlite3

# Environment variables
.env
.env.local

# Output
output/*
!output/.gitkeep
EOF
        echo -e "${GREEN}✓${NC} .gitignore created"
    fi
    
    # Create .gitkeep files for empty directories
    touch input/.gitkeep output/.gitkeep
    
else
    echo -e "${GREEN}✓${NC} Git repository already initialized"
fi

# Check if remote origin exists
if git remote | grep -q "^origin$"; then
    CURRENT_REMOTE=$(git remote get-url origin)
    if [ "$CURRENT_REMOTE" != "$REPO_URL" ]; then
        echo -e "${YELLOW}⚠️  Remote 'origin' exists with different URL${NC}"
        echo -e "${YELLOW}   Current: $CURRENT_REMOTE${NC}"
        echo -e "${YELLOW}   New: $REPO_URL${NC}"
        echo -e "${YELLOW}   Updating remote URL...${NC}"
        git remote set-url origin "$REPO_URL"
        echo -e "${GREEN}✓${NC} Remote URL updated"
    else
        echo -e "${GREEN}✓${NC} Remote 'origin' already configured"
    fi
else
    echo -e "${YELLOW}🔗 Adding remote 'origin'...${NC}"
    git remote add origin "$REPO_URL"
    echo -e "${GREEN}✓${NC} Remote 'origin' added"
fi

# Check for changes
if [ -z "$(git status --porcelain)" ]; then
    echo -e "${YELLOW}⚠️  No changes to commit${NC}"
    
    # Check if we need to push
    if git rev-parse --verify HEAD >/dev/null 2>&1; then
        echo -e "${YELLOW}📤 Attempting to push existing commits...${NC}"
        git push -u origin main 2>/dev/null || git push -u origin master 2>/dev/null || {
            echo -e "${RED}❌ Failed to push. Make sure the repository exists and you have access.${NC}"
            exit 1
        }
        echo -e "${GREEN}✓${NC} Push completed"
    else
        echo -e "${YELLOW}   No commits to push${NC}"
    fi
    
    echo ""
    echo -e "${BLUE}========================================${NC}"
    echo -e "${GREEN}Status:${NC} Up to date"
    echo -e "${BLUE}========================================${NC}"
    exit 0
fi

# Stage all changes
echo -e "${YELLOW}📝 Staging changes...${NC}"
git add .
echo -e "${GREEN}✓${NC} Changes staged"

# Show what will be committed
echo ""
echo -e "${YELLOW}Files to be committed:${NC}"
git status --short
echo ""

# Commit changes
echo -e "${YELLOW}💾 Creating commit...${NC}"
git commit -m "$COMMIT_MESSAGE"
echo -e "${GREEN}✓${NC} Commit created"

# Determine the default branch name
DEFAULT_BRANCH=$(git symbolic-ref --short HEAD 2>/dev/null || echo "main")

# Push to remote
echo -e "${YELLOW}📤 Pushing to GitHub...${NC}"
if git push -u origin "$DEFAULT_BRANCH" 2>/dev/null; then
    echo -e "${GREEN}✓${NC} Successfully pushed to GitHub"
else
    # If push fails, try to pull first (in case of conflicts)
    echo -e "${YELLOW}⚠️  Push failed, attempting to pull first...${NC}"
    
    if git pull origin "$DEFAULT_BRANCH" --rebase 2>/dev/null; then
        echo -e "${GREEN}✓${NC} Successfully pulled and rebased"
        echo -e "${YELLOW}📤 Pushing again...${NC}"
        
        if git push -u origin "$DEFAULT_BRANCH"; then
            echo -e "${GREEN}✓${NC} Successfully pushed to GitHub"
        else
            echo -e "${RED}❌ Failed to push to GitHub${NC}"
            echo -e "${RED}   Please check your repository URL and access permissions${NC}"
            exit 1
        fi
    else
        echo -e "${RED}❌ Failed to pull from GitHub${NC}"
        echo -e "${RED}   You may need to resolve conflicts manually${NC}"
        exit 1
    fi
fi

echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}✓ Successfully pushed to GitHub!${NC}"
echo -e "${GREEN}Repository:${NC} $REPO_URL"
echo -e "${GREEN}Branch:${NC} $DEFAULT_BRANCH"
echo -e "${GREEN}Commit:${NC} $COMMIT_MESSAGE"
echo -e "${BLUE}========================================${NC}"
echo ""

# Made with Bob

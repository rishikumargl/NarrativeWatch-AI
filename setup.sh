#!/bin/bash
# NarrativeWatch AI - Team Setup Script
# This script sets up the development environment for all team members

set -e

echo "=========================================="
echo "NarrativeWatch AI - Team Setup"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 1. Check Python version
echo -e "${BLUE}[1/6] Checking Python version...${NC}"
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed. Please install Python 3.10 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | awk '{print $2}')
echo -e "${GREEN}✓ Python ${PYTHON_VERSION} found${NC}"
echo ""

# 2. Create virtual environment
echo -e "${BLUE}[2/6] Creating virtual environment...${NC}"
if [ -d "venv" ]; then
    echo "Virtual environment already exists. Skipping creation."
else
    python3 -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
fi
echo ""

# 3. Activate virtual environment
echo -e "${BLUE}[3/6] Activating virtual environment...${NC}"
source venv/bin/activate
echo -e "${GREEN}✓ Virtual environment activated${NC}"
echo ""

# 4. Install dependencies
echo -e "${BLUE}[4/6] Installing dependencies...${NC}"
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
echo -e "${GREEN}✓ Dependencies installed${NC}"
echo ""

# 5. Setup environment file
echo -e "${BLUE}[5/6] Setting up environment configuration...${NC}"
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo -e "${YELLOW}⚠ Created .env file from .env.example${NC}"
    echo -e "${YELLOW}⚠ IMPORTANT: Update .env with your API keys before running!${NC}"
else
    echo "✓ .env file already exists"
fi
echo ""

# 6. Create logs directory
echo -e "${BLUE}[6/6] Creating logs directory...${NC}"
mkdir -p logs
echo -e "${GREEN}✓ Logs directory created${NC}"
echo ""

# 7. Run basic tests
echo -e "${BLUE}[Bonus] Running basic tests...${NC}"
if pytest tests/ -v --tb=short 2>/dev/null; then
    echo -e "${GREEN}✓ All tests passed!${NC}"
else
    echo -e "${YELLOW}⚠ Some tests failed. Check the output above.${NC}"
fi
echo ""

echo "=========================================="
echo -e "${GREEN}✓ Setup Complete!${NC}"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Update your .env file with API keys:"
echo "   - VERTEX_AI_PROJECT_ID"
echo "   - TAVILY_API_KEY"
echo "   - INSTAGRAM_ACCESS_TOKEN"
echo "   - GOOGLE_APPLICATION_CREDENTIALS"
echo ""
echo "2. Verify the setup by running:"
echo "   pytest tests/ -v"
echo ""
echo "3. Read the documentation:"
echo "   - LLD_AND_TEAM_PLAN.md (complete design)"
echo "   - MEMBER_ONE_EXECUTION_PLAN.md (your execution plan)"
echo "   - IMPLEMENTATION_CHECKLIST.md (weekly tasks)"
echo ""
echo "4. Start development:"
echo "   git checkout -b feature/week1-infrastructure"
echo ""
echo "Happy coding! 🚀"

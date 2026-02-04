#!/bin/bash
# setup-dev-environment.sh
# Sets up local development environment for KNA History

set -e

echo "=================================================="
echo "KNA History - Development Environment Setup"
echo "=================================================="
echo ""

# Check if running in project root
if [ ! -f "pyproject.toml" ]; then
    echo "ERROR: Please run this script from the project root directory"
    echo "Expected to find pyproject.toml in current directory"
    exit 1
fi

# 1. Create virtual environment with uv
echo "Step 1: Creating virtual environment..."
if command -v uv &> /dev/null; then
    uv venv
    echo "✓ Virtual environment created with uv"
else
    echo "WARNING: uv not found, using python -m venv"
    python3 -m venv .venv
fi

# 2. Activate virtual environment
echo ""
echo "Step 2: Activating virtual environment..."
source .venv/bin/activate
echo "✓ Virtual environment activated"

# 3. Install dependencies
echo ""
echo "Step 3: Installing dependencies..."
if command -v uv &> /dev/null; then
    uv pip install -e ".[dev]"
else
    pip install -e ".[dev]"
fi
echo "✓ Dependencies installed"

# 4. Install development tools
echo ""
echo "Step 4: Installing development tools..."
if command -v uv &> /dev/null; then
    uv pip install debugpy black flake8 pytest pytest-cov
else
    pip install debugpy black flake8 pytest pytest-cov
fi
echo "✓ Development tools installed"

# 5. Copy environment file
echo ""
echo "Step 5: Setting up environment variables..."
if [ ! -f ".env" ]; then
    cp .env.development .env
    echo "✓ Created .env from .env.development"
    echo "⚠  Please edit .env and adjust paths/credentials"
else
    echo "ℹ  .env already exists, skipping"
fi

# 6. Create VSCode settings directory
echo ""
echo "Step 6: Setting up VSCode configuration..."
mkdir -p .vscode
if [ ! -f ".vscode/launch.json" ]; then
    echo "ℹ  Copy launch.json, settings.json, and extensions.json to .vscode/"
fi

# 7. Start development database
echo ""
echo "Step 7: Starting development database..."
if command -v docker-compose &> /dev/null || command -v docker &> /dev/null; then
    docker compose -f docker-compose.dev.yml up -d
    echo "✓ MariaDB started on localhost:3306"
    echo "✓ Adminer (DB admin UI) available at http://localhost:8080"
else
    echo "⚠  Docker not found, skipping database setup"
    echo "   Install Docker to use containerized development database"
fi

echo ""
echo "=================================================="
echo "✓ Development Environment Setup Complete!"
echo "=================================================="
echo ""
echo "Next steps:"
echo "  1. Edit .env and adjust paths/credentials"
echo "  2. Load test data:"
echo "     source .venv/bin/activate"
echo "     python -m kna_data.cli load --dev /path/to/kna_database.xlsx"
echo "  3. Open project in VSCode:"
echo "     code ."
echo "  4. Press F5 to start debugging"
echo ""
echo "Database access:"
echo "  - MariaDB: localhost:3306"
echo "  - Adminer: http://localhost:8080"
echo "    - System: MySQL"
echo "    - Server: mariadb-dev"
echo "    - Username: root"
echo "    - Password: kna-toneel"
echo "    - Database: kna"
echo ""
echo "Flask app will run on: http://localhost:5000"
echo ""

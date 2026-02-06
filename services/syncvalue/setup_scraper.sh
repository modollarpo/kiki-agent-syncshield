#!/bin/bash

# SyncScrape Setup & Installation Script
# Run this to set up the SyncScrape environment

set -e  # Exit on error

echo "======================================================================"
echo "SyncScrape Setup & Installation"
echo "======================================================================"
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python $python_version detected"
echo ""

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt
echo "✓ Python dependencies installed"
echo ""

# Install Playwright browsers
echo "Installing Playwright Chromium browser..."
playwright install chromium
echo "✓ Playwright Chromium installed"
echo ""

# Verify installation
echo "Verifying installation..."
python3 -c "from playwright.sync_api import sync_playwright; print('✓ Playwright import successful')"
python3 -c "from bs4 import BeautifulSoup; print('✓ BeautifulSoup import successful')"
python3 -c "import httpx; print('✓ httpx import successful')"
echo ""

# Run tests
echo "Running tests..."
if command -v pytest &> /dev/null; then
    pytest tests/test_scraper.py -v --tb=short || echo "⚠ Some tests failed (expected if services not running)"
else
    echo "⚠ pytest not installed, skipping tests"
fi
echo ""

# Display usage
echo "======================================================================"
echo "✅ SyncScrape Installation Complete!"
echo "======================================================================"
echo ""
echo "Quick Start:"
echo ""
echo "  1. Test with example script:"
echo "     python example_scrape.py https://example.com"
echo ""
echo "  2. Use programmatically:"
echo "     python scraper.py https://your-target-site.com"
echo ""
echo "  3. Run tests:"
echo "     pytest tests/test_scraper.py -v"
echo ""
echo "  4. View documentation:"
echo "     cat README_SCRAPER.md"
echo ""
echo "Note: Ensure SyncBrain, SyncCreate, and SyncShield services are running"
echo "      for full functionality. See docker-compose.yml in project root."
echo ""
echo "======================================================================"

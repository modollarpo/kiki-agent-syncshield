#!/usr/bin/env python3
"""
SyncScrape Quick Validation Script

Validates that all components are properly installed and configured.
"""

import sys
import importlib
from typing import List, Tuple


def check_imports() -> List[Tuple[str, bool, str]]:
    """Check if required packages are importable"""
    results = []
    
    packages = [
        ("playwright", "Headless browser automation"),
        ("bs4", "BeautifulSoup HTML parsing"),
        ("httpx", "Async HTTP client"),
        ("pydantic", "Data validation"),
        ("fastapi", "API framework"),
    ]
    
    for package, description in packages:
        try:
            importlib.import_module(package)
            results.append((package, True, description))
        except ImportError:
            results.append((package, False, description))
    
    return results


def check_scraper_module() -> bool:
    """Check if scraper module can be imported"""
    try:
        import scraper
        return True
    except Exception as e:
        print(f"Error importing scraper: {e}")
        return False


def main():
    print("\n" + "="*80)
    print("SyncScrape Validation")
    print("="*80 + "\n")
    
    # Check imports
    print("📦 Checking dependencies...\n")
    results = check_imports()
    
    all_ok = True
    for package, success, description in results:
        status = "✅" if success else "❌"
        print(f"  {status} {package:20s} - {description}")
        if not success:
            all_ok = False
    
    print()
    
    # Check scraper module
    print("🔍 Checking scraper module...\n")
    if check_scraper_module():
        print("  ✅ scraper.py - Module loads successfully")
    else:
        print("  ❌ scraper.py - Module failed to load")
        all_ok = False
    
    print()
    
    # Check files
    print("📁 Checking files...\n")
    import os
    files = [
        "scraper.py",
        "example_scrape.py",
        "tests/test_scraper.py",
        "README_SCRAPER.md",
        "IMPLEMENTATION_SUMMARY.md",
        "setup_scraper.sh",
        "requirements.txt"
    ]
    
    for file in files:
        exists = os.path.exists(file)
        status = "✅" if exists else "❌"
        print(f"  {status} {file}")
        if not exists:
            all_ok = False
    
    print("\n" + "="*80)
    if all_ok:
        print("✅ All checks passed! SyncScrape is ready to use.")
        print("\nNext steps:")
        print("  1. Ensure services are running: docker-compose up syncbrain synccreate syncshield")
        print("  2. Run example: python example_scrape.py https://example.com")
        print("  3. Test API: uvicorn app.main:app --port 8002")
    else:
        print("❌ Some checks failed. Please review the errors above.")
        print("\nTo fix:")
        print("  1. Install dependencies: pip install -r requirements.txt")
        print("  2. Install Playwright: playwright install chromium")
        print("  3. Run setup script: ./setup_scraper.sh")
    
    print("="*80 + "\n")
    
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())

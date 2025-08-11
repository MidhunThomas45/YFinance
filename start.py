#!/usr/bin/env python3
"""
Startup script for iMarketPredict Stock API
"""
import os
import sys
import logging
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def check_dependencies():
    """Check if all required packages are installed"""
    required_packages = [
        'fastapi',
        'uvicorn',
        'yfinance',
        'pandas',
        'sqlalchemy',
        'mysqlclient'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        logger.error(f"Missing required packages: {', '.join(missing_packages)}")
        logger.error("Please install them using: pip install -r requirements.txt")
        return False
    
    logger.info("All required packages are installed")
    return True

def check_database():
    """Check database connection"""
    try:
        from db import check_db_connection
        if check_db_connection():
            logger.info("Database connection successful")
            return True
        else:
            logger.warning("Database connection failed - some features may not work")
            return False
    except Exception as e:
        logger.error(f"Database check failed: {e}")
        return False

def main():
    """Main startup function"""
    logger.info("Starting iMarketPredict Stock API...")
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Check database
    check_database()
    
    # Import and run the application
    try:
        from main import app
        import uvicorn
        
        logger.info("Starting FastAPI server...")
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

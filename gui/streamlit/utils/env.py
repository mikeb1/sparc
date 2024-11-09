import os
import logging
from pathlib import Path
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

def load_env():
    """Load environment variables from .env files in priority order."""
    # Try loading from different possible locations
    env_locations = [
        Path.cwd() / '.env',  # Current working directory
        Path.cwd().parent / '.env',  # Parent directory
        Path.cwd().parent.parent / '.env',  # Two levels up
        Path(__file__).parent.parent.parent.parent / '.env',  # Repository root
    ]
    
    for env_path in env_locations:
        if env_path.exists():
            logger.info(f"Loading environment from: {env_path}")
            load_dotenv(env_path)
            return True
            
    logger.warning("No .env file found in standard locations")
    return False

def verify_env():
    """Verify required environment variables are set."""
    required_vars = ['ANTHROPIC_API_KEY']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        logger.error("Please ensure these are set in your .env file")
        return False
        
    return True

def get_api_key():
    """Get the API key with validation."""
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY environment variable is not set")
    return api_key

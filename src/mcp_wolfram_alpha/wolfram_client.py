import wolframalpha
import os
from dotenv import load_dotenv
import logging

# Set up logging
logger = logging.getLogger(__name__)

load_dotenv()

def patch_wolframalpha():
    """
    Patch wolframalpha to handle different Content-Type headers.
    
    The original wolframalpha library has a strict Content-Type assertion that expects
    exactly 'text/xml;charset=utf-8', but the Wolfram Alpha API sometimes returns
    variations like 'text/xml; charset=utf-8' (with spaces) or other minor differences.
    This patch relaxes the check to accept any Content-Type that starts with 'text/xml'.
    """
    try:
        import httpx
        import multidict
        import xmltodict
        from wolframalpha import Document
        
        # Check if already patched to avoid double-patching
        if hasattr(wolframalpha.Client.aquery, '_is_patched'):
            logger.debug("Wolfram Alpha client already patched")
            return
        
        # Store original method
        original_aquery = wolframalpha.Client.aquery
        
        # Create patched method
        async def patched_aquery(self, input, params=(), **kwargs):
            """Patched version of aquery with relaxed Content-Type checking."""
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    resp = await client.get(
                        self.url,
                        params=multidict.MultiDict(
                            params, appid=self.app_id, input=input, **kwargs
                        ),
                    )
                    
                    # Enhanced Content-Type validation
                    content_type = resp.headers.get('Content-Type', '').strip().lower()
                    
                    # Accept any Content-Type that contains 'text/xml'
                    if 'text/xml' not in content_type:
                        # Log the actual content type for debugging
                        logger.warning(f"Unexpected Content-Type: {content_type}")
                        raise ValueError(f"Expected XML response, got Content-Type: {content_type}")
                    
                    # Ensure we have content
                    if not resp.content:
                        raise ValueError("Empty response from Wolfram Alpha API")
                    
                    # Parse XML response like the original method
                    try:
                        doc = xmltodict.parse(resp.content, postprocessor=Document.make)
                        return doc['queryresult']
                    except Exception as parse_error:
                        logger.error(f"XML parsing error: {parse_error}")
                        logger.error(f"Response content preview: {resp.content[:500]}")
                        raise ValueError(f"Failed to parse XML response: {parse_error}")
                        
            except httpx.TimeoutException:
                raise ValueError("Request to Wolfram Alpha API timed out")
            except httpx.RequestError as e:
                raise ValueError(f"Network error connecting to Wolfram Alpha API: {e}")
        
        # Mark as patched to prevent double-patching
        patched_aquery._is_patched = True
        
        # Apply patch
        wolframalpha.Client.aquery = patched_aquery
        logger.info("SUCCESS: Applied enhanced Wolfram Alpha Content-Type patch")
        
    except ImportError as e:
        logger.error(f"CRITICAL: Missing required dependency for patch: {e}")
        logger.error("Please install: pip install httpx multidict xmltodict")
        raise
    except Exception as e:
        logger.error(f"CRITICAL: Failed to patch wolframalpha client: {e}")
        raise

# Apply the patch before creating the client
logger.info("Initializing Wolfram Alpha client with enhanced patch...")
patch_wolframalpha()

# Validate API key
api_key = os.getenv("WOLFRAM_API_KEY")

if api_key is None:
    logger.error("CRITICAL: WOLFRAM_API_KEY environment variable not set")
    raise ValueError("WOLFRAM_API_KEY environment variable not set. Please set your API key.")

if not api_key.strip():
    logger.error("CRITICAL: WOLFRAM_API_KEY is empty")
    raise ValueError("WOLFRAM_API_KEY is empty. Please provide a valid API key.")

# Basic API key format validation (Wolfram Alpha keys are typically alphanumeric with hyphens)
if not all(c.isalnum() or c in '-' for c in api_key):
    logger.warning("WARNING: API key contains unexpected characters")

logger.info(f"Creating Wolfram Alpha client with API key: {api_key[:8]}{'*' * (len(api_key) - 8)}")

try:
    client: wolframalpha.Client = wolframalpha.Client(api_key)
    logger.info("SUCCESS: Wolfram Alpha client created successfully")
except Exception as e:
    logger.error(f"CRITICAL: Failed to create Wolfram Alpha client: {e}")
    raise ValueError(f"Failed to initialize Wolfram Alpha client: {e}")

# Test function for debugging your API key
def test_client():
    """Test the client with a simple query."""
    try:
        logger.info("Testing Wolfram Alpha client with simple query...")
        result = next(client.query("1+1").results).text
        logger.info(f"Test query result: {result}")
        return result
    except Exception as e:
        logger.error(f"Client test failed: {e}")
        raise

# Run test if this module is executed directly
if __name__ == "__main__":
    print("Testing Wolfram Alpha client...")
    result = test_client()
    print(f"1+1 = {result}")
    print("Client test successful!")

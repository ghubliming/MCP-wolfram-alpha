import wolframalpha
import os
from dotenv import load_dotenv
import logging

# Set up logging
logger = logging.getLogger(__name__)

load_dotenv()

def patch_wolframalpha():
    """Patch wolframalpha to handle different Content-Type headers."""
    try:
        import httpx
        import multidict
        import xmltodict
        from wolframalpha import Document
        
        # Store original method
        original_aquery = wolframalpha.Client.aquery
        
        # Create patched method
        async def patched_aquery(self, input, params=(), **kwargs):
            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    self.url,
                    params=multidict.MultiDict(
                        params, appid=self.app_id, input=input, **kwargs
                    ),
                )
                # Relaxed assertion: just check for 'text/xml'
                content_type = resp.headers.get('Content-Type', '')
                if not content_type.startswith('text/xml'):
                    raise ValueError(f"Expected XML response, got: {content_type}")
                
                # Parse XML response like the original method
                doc = xmltodict.parse(resp.content, postprocessor=Document.make)
                return doc['queryresult']
        
        # Apply patch
        wolframalpha.Client.aquery = patched_aquery
        logger.info("SUCCESS: Patched wolframalpha Content-Type handling")
        
    except Exception as e:
        logger.warning(f"WARNING: Could not patch wolframalpha: {e}")

# Apply the patch before creating the client
patch_wolframalpha()

api_key = os.getenv("WOLFRAM_API_KEY")

if api_key is None:
    raise ValueError("WOLFRAM_API_KEY environment variable not set")

client: wolframalpha.Client = wolframalpha.Client(api_key)

# test case for debugging your api key
if __name__ == "__main__":
    print(next(client.query("1+1").results).text)

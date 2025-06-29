#!/usr/bin/env python3
"""
Test script to verify the MCP server can be run as a module.
"""

import sys
import os
from pathlib import Path

# Add the src directory to Python path
src_dir = Path(__file__).parent / "src"
sys.path.insert(0, str(src_dir))

print(f"Python path: {sys.path}")
print(f"Current working directory: {os.getcwd()}")
print(f"Src directory exists: {src_dir.exists()}")

try:
    # Try to import the module
    print("Attempting to import mcp_wolfram_alpha...")
    import mcp_wolfram_alpha
    print("✓ Successfully imported mcp_wolfram_alpha")
    
    # Check if main function exists
    if hasattr(mcp_wolfram_alpha, 'main'):
        print("✓ main() function found")
    else:
        print("✗ main() function not found")
        
    # Try to run the main function
    print("Attempting to run main()...")
    import asyncio
    asyncio.run(mcp_wolfram_alpha.main())
    
except ImportError as e:
    print(f"✗ Import error: {e}")
except Exception as e:
    print(f"✗ Error running main: {e}")

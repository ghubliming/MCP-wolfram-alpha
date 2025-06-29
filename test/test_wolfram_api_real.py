#!/usr/bin/env python3
"""
Diagnostic test for Wolfram Alpha API.
Run this to test if your API key is working properly.
"""

import os
import sys
import asyncio
import httpx
from pathlib import Path

# Add src to path
test_dir = Path(__file__).parent
sys.path.insert(0, str(test_dir.parent / "src"))

import wolframalpha


async def test_api_directly():
    """Test the Wolfram Alpha API directly to diagnose issues."""
    api_key = os.getenv('WOLFRAM_API_KEY')
    
    if not api_key:
        print("❌ WOLFRAM_API_KEY environment variable not set")
        return False
        
    print(f"✓ API Key found: {api_key[:6]}{'*' * (len(api_key) - 6)}")
    
    # Test with simple HTTP request first
    print("\n1. Testing with raw HTTP request...")
    try:
        async with httpx.AsyncClient() as client:
            url = "http://api.wolframalpha.com/v2/query"
            params = {
                "appid": api_key,
                "input": "2+2",
                "format": "plaintext"
            }
            
            response = await client.get(url, params=params)
            print(f"   Status: {response.status_code}")
            print(f"   Content-Type: {response.headers.get('Content-Type', 'Not specified')}")
            
            if response.status_code == 200:
                print("   ✓ HTTP request successful")
                content_preview = response.text[:200] + "..." if len(response.text) > 200 else response.text
                print(f"   Content preview: {content_preview}")
            else:
                print(f"   ❌ HTTP request failed: {response.text}")
                return False
                
    except Exception as e:
        print(f"   ❌ HTTP request error: {e}")
        return False
    
    # Test with wolframalpha library
    print("\n2. Testing with wolframalpha library...")
    try:
        client = wolframalpha.Client(api_key)
        response = await client.aquery("2+2")
        print("   ✓ Wolfram library request successful")
        
        if response.pods:
            print(f"   Found {len(response.pods)} pods")
            for i, pod in enumerate(response.pods):
                print(f"   Pod {i}: {getattr(pod, 'title', 'No title')} - {len(pod.subpods)} subpods")
        else:
            print("   ⚠️  No pods in response")
            
    except Exception as e:
        print(f"   ❌ Wolfram library error: {e}")
        return False
    
    # Test the MCP server function
    print("\n3. Testing MCP server function...")
    try:
        from mcp_wolfram_alpha.server import handle_call_tool
        result = await handle_call_tool("query-wolfram-alpha", {"query": "2+2"})
        print(f"   ✓ MCP server function successful, got {len(result)} results")
        
        for i, item in enumerate(result):
            if hasattr(item, 'text'):
                print(f"   Result {i}: Text - {item.text[:50]}...")
            elif hasattr(item, 'mimeType'):
                print(f"   Result {i}: Image - {item.mimeType}")
                
    except Exception as e:
        print(f"   ❌ MCP server function error: {e}")
        return False
        
    print("\n✅ All tests passed! Your Wolfram Alpha integration is working correctly.")
    return True


async def main():
    """Main function to run diagnostics."""
    print("🔍 Wolfram Alpha API Diagnostic Test")
    print("=" * 50)
    
    success = await test_api_directly()
    
    if not success:
        print("\n💡 Troubleshooting tips:")
        print("1. Verify your API key is correct")
        print("2. Check if your API key has the right permissions")
        print("3. Ensure you're using the Full Results API (not Short Answers API)")
        print("4. Visit https://products.wolframalpha.com/api to check your account")


if __name__ == "__main__":
    asyncio.run(main())

#!/usr/bin/env python3
"""
Test script to verify Wolfram Alpha client works
"""

import os
import sys
from pathlib import Path

# Add src to path
test_dir = Path(__file__).parent
sys.path.insert(0, str(test_dir / "src"))

def test_wolfram_client():
    print("Testing Wolfram Alpha client...")
    
    # Check API key
    api_key = os.getenv('WOLFRAM_API_KEY')
    if not api_key:
        print("❌ WOLFRAM_API_KEY not set")
        return False
        
    print(f"✓ API Key found: {api_key[:8]}...")
    
    try:
        from mcp_wolfram_alpha.wolfram_client import client
        print("✓ Client imported successfully")
        
        # Test a simple query
        print("Testing query: '2+2'")
        response = client.query("2+2")
        
        if response and response.pods:
            print(f"✓ Got {len(response.pods)} pods")
            for i, pod in enumerate(response.pods):
                print(f"  Pod {i}: {getattr(pod, 'title', 'No title')}")
                for j, subpod in enumerate(pod.subpods):
                    if subpod.get('plaintext'):
                        print(f"    Subpod {j}: {subpod.plaintext}")
            return True
        else:
            print("❌ No response or no pods")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_wolfram_client()

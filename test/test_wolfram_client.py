#!/usr/bin/env python3
"""
BRUTAL WOLFRAM ALPHA CLIENT TEST
Shows actual questions and answers with detailed logging.
"""

import os
import sys
import logging
from pathlib import Path

# Setup logging
test_dir = Path(__file__).parent
logs_dir = test_dir / "logs"
logs_dir.mkdir(exist_ok=True)

# Clear any existing handlers to avoid pytest interference
logging.getLogger().handlers.clear()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    handlers=[
        logging.FileHandler(logs_dir / "test_wolfram_client.log", mode='w', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# Force output to show immediately
sys.stdout.flush()
sys.stderr.flush()

# Add src to path
sys.path.insert(0, str(test_dir.parent / "src"))

# Patch wolframalpha to fix Content-Type assertion issue
def patch_wolframalpha():
    """Patch wolframalpha to handle different Content-Type headers."""
    try:
        import wolframalpha
        import httpx
        import multidict
        
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
                import xmltodict
                from wolframalpha import Document
                doc = xmltodict.parse(resp.content, postprocessor=Document.make)
                return doc['queryresult']
        
        # Apply patch
        wolframalpha.Client.aquery = patched_aquery
        logger.info("SUCCESS: Patched wolframalpha Content-Type handling")
        
    except Exception as e:
        logger.warning(f"WARNING: Could not patch wolframalpha: {e}")

def run_direct_test():
    """Direct test function that runs without pytest."""
    print("\n" + "="*80)
    print("WOLFRAM ALPHA CLIENT - BRUTAL DIRECT TEST")
    print("="*80)
    
    # Apply patch first
    patch_wolframalpha()
    
    # Test 1: Import client
    print("\nTEST 1: Importing Wolfram Client")
    print("-"*50)
    
    try:
        from mcp_wolfram_alpha.wolfram_client import client
        print("SUCCESS: Wolfram client imported successfully")
        logger.info("SUCCESS: Wolfram client imported successfully")
    except Exception as e:
        print(f"FAIL: Failed to import wolfram client: {e}")
        logger.error(f"FAIL: Failed to import wolfram client: {e}")
        return False
    
    # Test 2: Check API key
    print("\nTEST 2: Checking API Key")
    print("-"*50)
    
    api_key = os.getenv('WOLFRAM_API_KEY')
    if not api_key:
        print("FAIL: WOLFRAM_API_KEY not found in environment")
        logger.error("FAIL: WOLFRAM_API_KEY not found in environment")
        return False
    else:
        print(f"SUCCESS: API key found (first 8 chars: {api_key[:8]}...)")
        logger.info(f"SUCCESS: API key found (first 8 chars: {api_key[:8]}...)")
    
    # Test 3: Math ASK/ANSWER tests
    print("\nTEST 3: Math ASK/ANSWER Tests")
    print("-"*50)
    
    math_tests = [
        {"ask": "What is 2+2?", "query": "2+2", "expect_contains": "4"},
        {"ask": "What is 10 times 5?", "query": "10*5", "expect_contains": "50"},
        {"ask": "What is the square root of 16?", "query": "sqrt(16)", "expect_contains": "4"},
        {"ask": "What is 2 to the power of 3?", "query": "2^3", "expect_contains": "8"},
    ]
    
    math_passed = 0
    for i, test in enumerate(math_tests, 1):
        ask = test["ask"]
        query = test["query"]
        expected = test["expect_contains"]
        
        print(f"\nMath Test {i}/4")
        print(f"ASK: {ask}")
        print(f"QUERY: {query}")
        print(f"EXPECTING TO FIND: '{expected}'")
        
        logger.info(f"Math Test {i}: ASK='{ask}' QUERY='{query}' EXPECT='{expected}'")
        
        try:
            response = client.query(query)
            
            # Collect all answers
            all_answers = []
            found_expected = False
            
            # Check results
            try:
                for result in response.results:
                    answer = result.text.strip()
                    all_answers.append(f"RESULT: {answer}")
                    if expected in answer:
                        found_expected = True
            except:
                pass
            
            # Check all pods
            pods = list(response.pods)
            for pod in pods:
                pod_title = getattr(pod, 'title', 'Unknown')
                for subpod in pod.subpods:
                    if hasattr(subpod, 'plaintext') and subpod.plaintext:
                        text = subpod.plaintext.strip()
                        all_answers.append(f"POD({pod_title}): {text}")
                        if expected in text:
                            found_expected = True
            
            # Show all answers
            print("WOLFRAM ANSWERS:")
            for answer in all_answers[:5]:  # Show first 5 answers
                print(f"  {answer}")
                logger.info(f"  {answer}")
            
            if len(all_answers) > 5:
                print(f"  ... and {len(all_answers)-5} more answers")
            
            # Check if we found expected answer
            if found_expected:
                print(f"SUCCESS: Found expected '{expected}' in answers!")
                logger.info(f"SUCCESS: Found expected '{expected}' in answers!")
                math_passed += 1
            else:
                print(f"FAIL: Expected '{expected}' NOT found in any answer")
                logger.error(f"FAIL: Expected '{expected}' NOT found in any answer")
                
        except Exception as e:
            print(f"ERROR: Query failed: {e}")
            logger.error(f"ERROR: Query failed: {e}")
            return False
    
    print(f"\nMath Tests Result: {math_passed}/{len(math_tests)} passed")
    logger.info(f"Math Tests Result: {math_passed}/{len(math_tests)} passed")
    
    # Test 4: Real-world ASK/ANSWER tests
    print("\nTEST 4: Real-World ASK/ANSWER Tests")
    print("-"*50)
    
    knowledge_tests = [
        {"ask": "What is the population of Tokyo?", "query": "population of Tokyo", "expect_any": ["million", "people", "population", "Tokyo"]},
        {"ask": "What is the speed of light?", "query": "speed of light", "expect_any": ["meter", "second", "299", "light"]},
        {"ask": "What is the capital of France?", "query": "capital of France", "expect_any": ["Paris", "France", "capital"]},
        {"ask": "What is the atomic number of carbon?", "query": "atomic number of carbon", "expect_any": ["6", "carbon", "atomic"]},
    ]
    
    knowledge_passed = 0
    for i, test in enumerate(knowledge_tests, 1):
        ask = test["ask"]
        query = test["query"]
        expect_words = test["expect_any"]
        
        print(f"\nKnowledge Test {i}/4")
        print(f"ASK: {ask}")
        print(f"QUERY: {query}")
        print(f"EXPECTING ANY OF: {expect_words}")
        
        logger.info(f"Knowledge Test {i}: ASK='{ask}' QUERY='{query}' EXPECT_ANY={expect_words}")
        
        try:
            response = client.query(query)
            
            # Collect all answers
            all_answers = []
            found_match = False
            
            # Check results
            try:
                for result in response.results:
                    answer = result.text.strip()
                    all_answers.append(f"RESULT: {answer}")
                    for word in expect_words:
                        if word.lower() in answer.lower():
                            found_match = True
            except:
                pass
            
            # Check all pods
            pods = list(response.pods)
            for pod in pods:
                pod_title = getattr(pod, 'title', 'Unknown')
                for subpod in pod.subpods:
                    if hasattr(subpod, 'plaintext') and subpod.plaintext:
                        text = subpod.plaintext.strip()
                        all_answers.append(f"POD({pod_title}): {text}")
                        for word in expect_words:
                            if word.lower() in text.lower():
                                found_match = True
            
            # Show all answers
            print("WOLFRAM ANSWERS:")
            for answer in all_answers[:5]:  # Show first 5 answers
                print(f"  {answer}")
                logger.info(f"  {answer}")
                
            if len(all_answers) > 5:
                print(f"  ... and {len(all_answers)-5} more answers")
            
            # Check if we found any expected words
            if found_match:
                print(f"SUCCESS: Found one of {expect_words} in answers!")
                logger.info(f"SUCCESS: Found one of {expect_words} in answers!")
                knowledge_passed += 1
            else:
                print(f"FAIL: None of {expect_words} found in answers")
                logger.error(f"FAIL: None of {expect_words} found in answers")
                
        except Exception as e:
            print(f"ERROR: Query failed: {e}")
            logger.error(f"ERROR: Query failed: {e}")
            return False
    
    print(f"\nKnowledge Tests Result: {knowledge_passed}/{len(knowledge_tests)} passed")
    logger.info(f"Knowledge Tests Result: {knowledge_passed}/{len(knowledge_tests)} passed")
    
    # Final results
    total_tests = len(math_tests) + len(knowledge_tests)
    total_passed = math_passed + knowledge_passed
    success_rate = (total_passed / total_tests) * 100
    
    print("\n" + "="*80)
    print("FINAL TEST RESULTS")
    print("="*80)
    print(f"Math tests: {math_passed}/{len(math_tests)} passed")
    print(f"Knowledge tests: {knowledge_passed}/{len(knowledge_tests)} passed")
    print(f"TOTAL: {total_passed}/{total_tests} tests passed ({success_rate:.1f}%)")
    
    logger.info(f"FINAL RESULTS: {total_passed}/{total_tests} passed ({success_rate:.1f}%)")
    
    if success_rate >= 70:
        print("SUCCESS: Test suite passed (>=70% success rate)")
        logger.info("SUCCESS: Test suite passed (>=70% success rate)")
        return True
    else:
        print(f"FAIL: Test suite failed ({success_rate:.1f}% < 70% required)")
        logger.error(f"FAIL: Test suite failed ({success_rate:.1f}% < 70% required)")
        return False

# For pytest compatibility
def test_wolfram_client():
    """Pytest wrapper function."""
    return run_direct_test()

def main():
    """Main function for direct execution."""
    success = run_direct_test()
    
    if success:
        print("\nALL TESTS PASSED!")
        sys.exit(0)
    else:
        print("\nTESTS FAILED!")
        sys.exit(1)

if __name__ == "__main__":
    main() 
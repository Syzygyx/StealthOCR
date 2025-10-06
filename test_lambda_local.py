#!/usr/bin/env python3
"""
Test Lambda function locally to debug the 500 error
"""

import json
import base64
import sys
import os

# Add src directory to path
sys.path.append('src')

from lambda_simple import lambda_handler

def test_lambda_locally():
    """Test the Lambda function locally with various inputs"""
    
    print("🧪 Testing Lambda function locally...")
    print("=" * 50)
    
    # Test 1: Basic test with minimal data
    print("\n📋 Test 1: Basic test")
    test_event_1 = {
        "httpMethod": "POST",
        "body": json.dumps({
            "pdf_data": "dGVzdA=="  # "test" in base64
        }),
        "headers": {
            "Content-Type": "application/json"
        },
        "queryStringParameters": None
    }
    
    try:
        result_1 = lambda_handler(test_event_1, None)
        print(f"✅ Test 1 result: {result_1['statusCode']}")
        if result_1['statusCode'] == 200:
            body = json.loads(result_1['body'])
            print(f"   Response: {body.get('success', 'N/A')}")
        else:
            body = json.loads(result_1['body'])
            print(f"   Error: {body.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"❌ Test 1 failed: {e}")
    
    # Test 2: With query parameters
    print("\n📋 Test 2: With query parameters")
    test_event_2 = {
        "httpMethod": "POST",
        "body": json.dumps({
            "pdf_data": "dGVzdA=="
        }),
        "headers": {
            "Content-Type": "application/json"
        },
        "queryStringParameters": {
            "engine": "tesseract"
        }
    }
    
    try:
        result_2 = lambda_handler(test_event_2, None)
        print(f"✅ Test 2 result: {result_2['statusCode']}")
        if result_2['statusCode'] == 200:
            body = json.loads(result_2['body'])
            print(f"   Response: {body.get('success', 'N/A')}")
        else:
            body = json.loads(result_2['body'])
            print(f"   Error: {body.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"❌ Test 2 failed: {e}")
    
    # Test 3: OPTIONS request
    print("\n📋 Test 3: OPTIONS request")
    test_event_3 = {
        "httpMethod": "OPTIONS",
        "body": None,
        "headers": {
            "Origin": "https://syzygyx.github.io"
        },
        "queryStringParameters": None
    }
    
    try:
        result_3 = lambda_handler(test_event_3, None)
        print(f"✅ Test 3 result: {result_3['statusCode']}")
        print(f"   Headers: {result_3.get('headers', {})}")
    except Exception as e:
        print(f"❌ Test 3 failed: {e}")
    
    # Test 4: Invalid JSON
    print("\n📋 Test 4: Invalid JSON")
    test_event_4 = {
        "httpMethod": "POST",
        "body": "invalid json",
        "headers": {
            "Content-Type": "application/json"
        },
        "queryStringParameters": None
    }
    
    try:
        result_4 = lambda_handler(test_event_4, None)
        print(f"✅ Test 4 result: {result_4['statusCode']}")
        if result_4['statusCode'] != 200:
            body = json.loads(result_4['body'])
            print(f"   Error: {body.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"❌ Test 4 failed: {e}")
    
    # Test 5: Missing PDF data
    print("\n📋 Test 5: Missing PDF data")
    test_event_5 = {
        "httpMethod": "POST",
        "body": json.dumps({
            "invalid_field": "test"
        }),
        "headers": {
            "Content-Type": "application/json"
        },
        "queryStringParameters": None
    }
    
    try:
        result_5 = lambda_handler(test_event_5, None)
        print(f"✅ Test 5 result: {result_5['statusCode']}")
        if result_5['statusCode'] != 200:
            body = json.loads(result_5['body'])
            print(f"   Error: {body.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"❌ Test 5 failed: {e}")
    
    # Test 6: Real PDF data (if available)
    print("\n📋 Test 6: Real PDF data")
    pdf_path = "/Users/danielmcshan/Downloads/25-08_IR_Israel_Security_Replacement_Transfer_Fund_Tranche_3.pdf"
    
    if os.path.exists(pdf_path):
        try:
            with open(pdf_path, 'rb') as f:
                pdf_bytes = f.read()
                pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')
            
            test_event_6 = {
                "httpMethod": "POST",
                "body": json.dumps({
                    "pdf_data": pdf_base64
                }),
                "headers": {
                    "Content-Type": "application/json"
                },
                "queryStringParameters": None
            }
            
            result_6 = lambda_handler(test_event_6, None)
            print(f"✅ Test 6 result: {result_6['statusCode']}")
            if result_6['statusCode'] == 200:
                body = json.loads(result_6['body'])
                print(f"   Success: {body.get('success', 'N/A')}")
                print(f"   Text length: {len(body.get('text', ''))}")
            else:
                body = json.loads(result_6['body'])
                print(f"   Error: {body.get('error', 'Unknown error')}")
        except Exception as e:
            print(f"❌ Test 6 failed: {e}")
    else:
        print("⚠️  Real PDF not found, skipping Test 6")

def test_lambda_with_debug():
    """Test Lambda function with detailed debugging"""
    
    print("\n🔍 Detailed debugging test...")
    print("=" * 50)
    
    # Create a simple test event
    test_event = {
        "httpMethod": "POST",
        "body": json.dumps({
            "pdf_data": "dGVzdA=="
        }),
        "headers": {
            "Content-Type": "application/json"
        },
        "queryStringParameters": None
    }
    
    print("📋 Test event:")
    print(json.dumps(test_event, indent=2))
    
    try:
        # Add some debug prints to the lambda function
        print("\n🔍 Calling lambda_handler...")
        result = lambda_handler(test_event, None)
        
        print(f"\n📊 Result status: {result['statusCode']}")
        print(f"📊 Result headers: {result.get('headers', {})}")
        
        if 'body' in result:
            try:
                body = json.loads(result['body'])
                print(f"📊 Result body: {json.dumps(body, indent=2)}")
            except:
                print(f"📊 Result body (raw): {result['body']}")
        
    except Exception as e:
        print(f"❌ Lambda execution failed: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Main test function"""
    print("🧪 StealthOCR Lambda Local Testing")
    print("=" * 60)
    
    # Run basic tests
    test_lambda_locally()
    
    # Run detailed debugging
    test_lambda_with_debug()
    
    print("\n🎉 Local testing completed!")

if __name__ == "__main__":
    main()
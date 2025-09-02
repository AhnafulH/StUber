#!/usr/bin/env python3
"""
Test script to verify the fixed dequeue functions work properly
"""

import os
from supabase import create_client
import json
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
QUEUE_NAME = "ride_matching"

def test_dequeue_functions():
    print("Testing Fixed Dequeue Functions")
    print("=" * 50)
    
    # Initialize Supabase client
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("✅ Connected to Supabase")
    except Exception as e:
        print(f"❌ Failed to connect: {e}")
        return
    
    # First, let's add a test message to ensure there's something in the queue
    print("\n1. Adding test message to queue...")
    try:
        test_message = {
            "test": "fixed_dequeue_test",
            "ride_type": "offer",
            "ride_id": 999,
            "starting_location": "Test Start Location",
            "destination": "Test End Location",
            "seats_available": 2
        }
        
        result = supabase.rpc('enqueue', {
            'queue_name': QUEUE_NAME,
            'message_payload': test_message
        }).execute()
        
        print(f"   Test message enqueued: {result.data}")
        
    except Exception as e:
        print(f"   Failed to enqueue test message: {e}")
        return
    
    # Test 1: Try dequeue_full (table-returning version)
    print("\n2. Testing dequeue_full (table version)...")
    try:
        result = supabase.rpc('dequeue_full_v2', {'queue_name': QUEUE_NAME}).execute()
        print(f"   Raw result: {result}")
        
        if result.data and len(result.data) > 0:
            message = result.data[0]
            print(f"   ✅ dequeue_full SUCCESS!")
            print(f"   Message ID: {message.get('msg_id')}")
            print(f"   Message: {json.dumps(message.get('message'), indent=2)}")
            print(f"   Read count: {message.get('read_ct')}")
            return  # Success, no need to test other methods
        else:
            print(f"   ⚠️  dequeue_full returned no data")
            
    except Exception as e:
        print(f"   ❌ dequeue_full FAILED: {e}")

def main():
    test_dequeue_functions()

if __name__ == "__main__":
    main()
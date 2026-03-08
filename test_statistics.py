"""
Test script to verify database statistics functionality
"""
import sys
import os

# Add backend directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from dotenv import load_dotenv
load_dotenv()

from utils.database import Database
from config import DB_HOST, DB_USER, DB_PASSWORD, DB_NAME
import logging

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_statistics():
    """Test database statistics retrieval"""
    print("="*60)
    print("Testing Database Statistics")
    print("="*60)
    
    # Initialize database
    db = Database(DB_HOST, DB_USER, DB_PASSWORD, DB_NAME)
    
    # Connect
    print("\n1. Connecting to database...")
    if db.connect():
        print("✓ Connected successfully")
    else:
        print("✗ Connection failed")
        return
    
    # Get statistics
    print("\n2. Fetching statistics...")
    stats = db.get_statistics()
    
    print("\n3. Statistics Results:")
    print("-"*60)
    for key, value in stats.items():
        print(f"  {key}: {value}")
    print("-"*60)
    
    # Verify structure
    print("\n4. Verifying structure...")
    required_fields = [
        'total_scans',
        'average_confidence',
        'success_rate',
        'today_scans',
        'trends',
        'confidence_distribution'
    ]
    
    all_present = True
    for field in required_fields:
        if field in stats:
            print(f"  ✓ {field}")
        else:
            print(f"  ✗ {field} MISSING")
            all_present = False
    
    if all_present:
        print("\n✓ All required fields present")
    else:
        print("\n✗ Some fields are missing")
    
    # Display summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Total Scans: {stats.get('total_scans', 0)}")
    print(f"Success Rate: {stats.get('success_rate', 0):.1f}%")
    print(f"Avg Confidence: {stats.get('average_confidence', 0):.2%}")
    print(f"Today's Scans: {stats.get('today_scans', 0)}")
    print("="*60)
    
    # Close connection
    db.disconnect()
    print("\n✓ Test completed successfully")

if __name__ == '__main__':
    test_statistics()

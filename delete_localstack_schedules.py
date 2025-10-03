#!/usr/bin/env python3
"""
Standalone script to delete all LocalStack EventBridge schedules
"""

import sys
import os
from typing import Dict, Any

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def delete_all_crypto_schedules(endpoint_url: str = 'http://localhost:4566') -> Dict[str, Any]:
    """
    Delete all crypto forecast schedules from LocalStack.
    
    Args:
        endpoint_url: LocalStack endpoint URL
        
    Returns:
        Dict containing deletion results
    """
    try:
        # Import the deletion function
        from functions.planning.create_one_time_schedule import delete_all_schedules, delete_schedule_group
        
        print("🗑️  Starting deletion of all crypto forecast schedules...")
        print("=" * 60)
        
        # Delete all schedules in the crypto-forecast-schedules group
        result = delete_all_schedules(
            group_name="crypto-forecast-schedules",
            endpoint_url=endpoint_url
        )
        
        print(f"📊 Deletion Results:")
        print(f"Status: {result['status']}")
        print(f"Message: {result['message']}")
        print(f"Deleted: {result['deleted_count']}/{result['total_schedules']} schedules")
        
        if result['errors']:
            print(f"\n❌ Errors encountered:")
            for error in result['errors']:
                print(f"  - {error}")
        
        # Optionally delete the schedule group as well
        if result['deleted_count'] > 0 or result['total_schedules'] == 0:
            print(f"\n🗂️  Attempting to delete schedule group...")
            group_result = delete_schedule_group(
                group_name="crypto-forecast-schedules",
                endpoint_url=endpoint_url,
                force=False  # We already deleted schedules above
            )
            
            print(f"Group deletion: {group_result['status']} - {group_result['message']}")
            result['group_deletion'] = group_result
        
        return result
        
    except ImportError as e:
        error_msg = f"Failed to import deletion functions: {e}"
        print(f"❌ {error_msg}")
        return {
            "status": "error",
            "message": error_msg,
            "deleted_count": 0,
            "total_schedules": 0,
            "errors": [error_msg]
        }
    
    except Exception as e:
        error_msg = f"Unexpected error during deletion: {e}"
        print(f"❌ {error_msg}")
        return {
            "status": "error",
            "message": error_msg,
            "deleted_count": 0,
            "total_schedules": 0,
            "errors": [error_msg]
        }

def confirm_deletion() -> bool:
    """
    Ask user for confirmation before deleting schedules.
    
    Returns:
        True if user confirms deletion
    """
    print("⚠️  WARNING: This will delete ALL crypto forecast schedules in LocalStack!")
    print("This action cannot be undone.")
    
    while True:
        response = input("\nDo you want to continue? (yes/no): ").lower().strip()
        if response in ['yes', 'y']:
            return True
        elif response in ['no', 'n']:
            return False
        else:
            print("Please enter 'yes' or 'no'")

def main():
    """Main function to handle command line execution"""
    print("LocalStack EventBridge Schedule Deletion Tool")
    print("=" * 50)
    
    # Check command line arguments
    force_delete = False
    endpoint_url = 'http://localhost:4566'
    
    if len(sys.argv) > 1:
        if '--force' in sys.argv or '-f' in sys.argv:
            force_delete = True
        if '--endpoint' in sys.argv:
            endpoint_index = sys.argv.index('--endpoint')
            if endpoint_index + 1 < len(sys.argv):
                endpoint_url = sys.argv[endpoint_index + 1]
        if '--help' in sys.argv or '-h' in sys.argv:
            print("Usage:")
            print("  python delete_localstack_schedules.py [options]")
            print("")
            print("Options:")
            print("  --force, -f          Skip confirmation prompt")
            print("  --endpoint URL       LocalStack endpoint URL (default: http://localhost:4566)")
            print("  --help, -h           Show this help message")
            return
    
    # Confirm deletion unless force flag is used
    if not force_delete:
        if not confirm_deletion():
            print("❌ Deletion cancelled by user")
            return
    
    # Perform deletion
    result = delete_all_crypto_schedules(endpoint_url)
    
    # Final summary
    print("\n" + "=" * 60)
    print("🏁 FINAL SUMMARY")
    print("=" * 60)
    
    if result['status'] == 'success':
        print("✅ SUCCESS: All schedules deleted successfully")
    elif result['status'] == 'partial_success':
        print("⚠️  PARTIAL SUCCESS: Some schedules could not be deleted")
    else:
        print("❌ FAILED: Deletion operation failed")
    
    print(f"Deleted: {result['deleted_count']} schedules")
    print(f"Errors: {len(result['errors'])}")
    
    if result['errors']:
        print("\nError details:")
        for error in result['errors']:
            print(f"  - {error}")

if __name__ == "__main__":
    main()

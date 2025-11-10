#!/usr/bin/env python3
"""
Utility script to populate/update the agent_performance table with historical data.
Run this script to fill the agent_performance table with aggregated metrics from agent_results.
"""

import sys
from pathlib import Path

# Add data directory to path
project_root = Path(__file__).parent
data_path = project_root / 'data'
sys.path.insert(0, str(data_path))

from database_service import DatabaseService
from database_config import test_connection

def main():
    """Main function to update agent performance metrics."""
    print("=" * 60)
    print("Agent Performance Table Update Utility")
    print("=" * 60)
    print()
    
    # Test database connection
    print("Testing database connection...")
    if not test_connection():
        print("❌ Database connection failed!")
        print("Please check your database configuration in data/database_config.py")
        return 1
    print("✓ Database connection successful")
    print()
    
    # Update all agent performance metrics
    print("Updating agent performance metrics from agent_results...")
    print("This may take a moment depending on the amount of historical data...")
    print()
    
    try:
        success = DatabaseService.update_all_agent_performance_metrics()
        
        if success:
            print()
            print("=" * 60)
            print("✓ Successfully updated agent performance metrics!")
            print("=" * 60)
            print()
            print("The agent_performance table now contains aggregated metrics")
            print("for all agents based on historical data from agent_results.")
            print()
            print("Going forward, metrics will be updated automatically after")
            print("each agent execution.")
            return 0
        else:
            print()
            print("=" * 60)
            print("⚠ Update completed with some errors")
            print("=" * 60)
            print()
            print("Check the logs for details on which agents failed to update.")
            return 1
            
    except Exception as e:
        print()
        print("=" * 60)
        print(f"❌ Error updating agent performance metrics: {str(e)}")
        print("=" * 60)
        return 1

if __name__ == "__main__":
    sys.exit(main())


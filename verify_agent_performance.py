#!/usr/bin/env python3
"""
Verification script to check if agent_performance table is working correctly.
This script checks:
1. Database connectivity
2. Table structure
3. Data presence
4. Data consistency
"""

import sys
from pathlib import Path

# Add data directory to path
project_root = Path(__file__).parent
data_path = project_root / 'data'
sys.path.insert(0, str(data_path))

from database_service import DatabaseService
from database_config import get_db_connection, test_connection
from datetime import datetime, timedelta

def print_section(title):
    """Print a formatted section header."""
    print()
    print("=" * 60)
    print(title)
    print("=" * 60)

def check_database_connection():
    """Check if database connection works."""
    print_section("1. Database Connection Test")
    
    try:
        if test_connection():
            print("✓ Database connection: SUCCESS")
            return True
        else:
            print("❌ Database connection: FAILED")
            print("Please check your database configuration.")
            return False
    except Exception as e:
        print(f"❌ Database connection error: {str(e)}")
        return False

def check_table_structure():
    """Verify agent_performance table exists and has correct structure."""
    print_section("2. Table Structure Verification")
    
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Check if table exists
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'agent_performance'
                );
            """)
            exists = cursor.fetchone()[0]
            
            if not exists:
                print("❌ Table 'agent_performance' does not exist!")
                return False
            
            print("✓ Table 'agent_performance' exists")
            
            # Check column structure
            cursor.execute("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'agent_performance'
                ORDER BY ordinal_position;
            """)
            columns = cursor.fetchall()
            
            expected_columns = [
                'id', 'agent_name', 'date', 'total_executions',
                'successful_executions', 'failed_executions', 'timeout_executions',
                'average_processing_time', 'min_processing_time', 'max_processing_time'
            ]
            
            actual_columns = [col[0] for col in columns]
            
            print(f"✓ Table has {len(columns)} columns:")
            for col_name, col_type in columns:
                print(f"  - {col_name} ({col_type})")
            
            # Verify all expected columns exist
            missing = set(expected_columns) - set(actual_columns)
            if missing:
                print(f"⚠ Missing expected columns: {missing}")
            
            return True
            
    except Exception as e:
        print(f"❌ Error checking table structure: {str(e)}")
        return False

def check_data_presence():
    """Check if table has any data."""
    print_section("3. Data Presence Check")
    
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Count total records
            cursor.execute("SELECT COUNT(*) FROM agent_performance;")
            total_records = cursor.fetchone()[0]
            
            if total_records == 0:
                print("⚠ Table is EMPTY (no records found)")
                print()
                print("This is expected if:")
                print("  1. No agents have been executed yet, OR")
                print("  2. You haven't run 'update_agent_performance.py' yet")
                print()
                print("To populate with historical data, run:")
                print("  python update_agent_performance.py")
                return False
            
            print(f"✓ Table contains {total_records} performance record(s)")
            
            # Get unique agents
            cursor.execute("SELECT DISTINCT agent_name FROM agent_performance;")
            agents = [row[0] for row in cursor.fetchall()]
            
            print(f"✓ Performance data exists for {len(agents)} agent(s):")
            for agent in agents:
                print(f"  - {agent}")
            
            # Get date range
            cursor.execute("""
                SELECT MIN(date), MAX(date) 
                FROM agent_performance;
            """)
            min_date, max_date = cursor.fetchone()
            
            print(f"✓ Data date range: {min_date} to {max_date}")
            
            return True
            
    except Exception as e:
        print(f"❌ Error checking data presence: {str(e)}")
        return False

def check_data_consistency():
    """Verify data consistency between agent_results and agent_performance."""
    print_section("4. Data Consistency Verification")
    
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Get agent execution counts from agent_results
            cursor.execute("""
                SELECT agent_name, COUNT(*) as result_count
                FROM agent_results
                GROUP BY agent_name;
            """)
            agent_results_counts = {row[0]: row[1] for row in cursor.fetchall()}
            
            if not agent_results_counts:
                print("⚠ No data in agent_results table")
                print("Cannot verify consistency without source data.")
                return True
            
            print(f"Found {len(agent_results_counts)} agent(s) in agent_results table")
            
            # Get counts from agent_performance (latest records only)
            cursor.execute("""
                SELECT DISTINCT ON (agent_name) 
                    agent_name, 
                    total_executions,
                    successful_executions,
                    failed_executions,
                    timeout_executions
                FROM agent_performance
                ORDER BY agent_name, date DESC;
            """)
            
            perf_records = {row[0]: {
                'total': row[1],
                'success': row[2],
                'failed': row[3],
                'timeout': row[4]
            } for row in cursor.fetchall()}
            
            if not perf_records:
                print("⚠ No data in agent_performance table")
                print("Run 'python update_agent_performance.py' to populate.")
                return False
            
            # Compare data
            print()
            print("Consistency Check Results:")
            print("-" * 60)
            
            all_consistent = True
            for agent_name, result_count in agent_results_counts.items():
                if agent_name in perf_records:
                    perf_count = perf_records[agent_name]['total']
                    if result_count == perf_count:
                        print(f"✓ {agent_name}: {result_count} executions (consistent)")
                    else:
                        print(f"⚠ {agent_name}: agent_results has {result_count}, "
                              f"agent_performance has {perf_count}")
                        all_consistent = False
                else:
                    print(f"⚠ {agent_name}: in agent_results but not in agent_performance")
                    all_consistent = False
            
            # Check for agents in performance but not in results
            for agent_name in perf_records:
                if agent_name not in agent_results_counts:
                    print(f"⚠ {agent_name}: in agent_performance but not in agent_results")
                    all_consistent = False
            
            print()
            if all_consistent:
                print("✓ All data is consistent between tables")
            else:
                print("⚠ Inconsistencies found - consider running 'python update_agent_performance.py'")
            
            return all_consistent
            
    except Exception as e:
        print(f"❌ Error checking data consistency: {str(e)}")
        return False

def check_recent_updates():
    """Check if performance data is being updated recently."""
    print_section("5. Recent Updates Check")
    
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Check for updates in last 24 hours
            cursor.execute("""
                SELECT agent_name, date, total_executions
                FROM agent_performance
                WHERE date >= NOW() - INTERVAL '24 hours'
                ORDER BY date DESC;
            """)
            
            recent_updates = cursor.fetchall()
            
            if not recent_updates:
                print("⚠ No updates in the last 24 hours")
                print("This is normal if no agents have been executed recently.")
            else:
                print(f"✓ Found {len(recent_updates)} update(s) in last 24 hours:")
                for agent_name, date, executions in recent_updates[:5]:  # Show max 5
                    print(f"  - {agent_name}: {executions} executions (updated {date})")
                if len(recent_updates) > 5:
                    print(f"  ... and {len(recent_updates) - 5} more")
            
            return True
            
    except Exception as e:
        print(f"❌ Error checking recent updates: {str(e)}")
        return False

def main():
    """Main verification function."""
    print()
    print("╔" + "═" * 58 + "╗")
    print("║" + " " * 10 + "Agent Performance Table Verification" + " " * 11 + "║")
    print("╚" + "═" * 58 + "╝")
    
    results = {
        'connection': check_database_connection(),
        'structure': False,
        'data': False,
        'consistency': False,
        'updates': False
    }
    
    if results['connection']:
        results['structure'] = check_table_structure()
        results['data'] = check_data_presence()
        results['consistency'] = check_data_consistency()
        results['updates'] = check_recent_updates()
    
    # Summary
    print_section("Verification Summary")
    
    checks = [
        ('Database Connection', results['connection']),
        ('Table Structure', results['structure']),
        ('Data Presence', results['data']),
        ('Data Consistency', results['consistency']),
        ('Recent Updates', results['updates'])
    ]
    
    passed = sum(1 for _, result in checks if result)
    total = len(checks)
    
    for check_name, result in checks:
        status = "✓ PASS" if result else "❌ FAIL"
        print(f"{status}: {check_name}")
    
    print()
    print(f"Result: {passed}/{total} checks passed")
    
    if passed == total:
        print()
        print("🎉 All checks passed! Agent performance tracking is working correctly.")
        return 0
    elif results['data'] == False and results['connection'] and results['structure']:
        print()
        print("⚠ Table is empty but ready to use.")
        print()
        print("To populate with historical data, run:")
        print("  python update_agent_performance.py")
        print()
        print("Or simply run an analysis - data will be automatically tracked!")
        return 0
    else:
        print()
        print("❌ Some checks failed. Please review the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())


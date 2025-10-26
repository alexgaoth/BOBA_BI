"""
Supabase Configuration and Data Access Layer for Boba BI
Handles all database operations with Supabase
"""

import os
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ============================================================================
# SUPABASE CLIENT INITIALIZATION
# ============================================================================

def get_supabase_client() -> Client:
    """Initialize and return Supabase client"""
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_KEY')
    
    if not url or not key:
        raise ValueError(
            "Missing Supabase credentials. Please set SUPABASE_URL and SUPABASE_KEY in .env"
        )
    
    return create_client(url, key)


# ============================================================================
# EMPLOYEE OPERATIONS
# ============================================================================

def get_all_employees(supabase: Client) -> List[Dict]:
    """Fetch all employees from Supabase"""
    try:
        response = supabase.table('employees').select('*').execute()
        return response.data
    except Exception as e:
        print(f"Error fetching employees: {e}")
        return []


def insert_employees(supabase: Client, employees: List[Dict]) -> bool:
    """Insert multiple employees into Supabase"""
    try:
        # Remove employee_id if present (auto-generated)
        clean_employees = [
            {k: v for k, v in emp.items() if k != 'employee_id'}
            for emp in employees
        ]
        
        response = supabase.table('employees').insert(clean_employees).execute()
        print(f"✅ Inserted {len(response.data)} employees")
        return True
    except Exception as e:
        print(f"❌ Error inserting employees: {e}")
        return False


def clear_employees(supabase: Client) -> bool:
    """Clear all employees (for testing/reset)"""
    try:
        supabase.table('employees').delete().neq('employee_id', 0).execute()
        print("✅ Cleared all employees")
        return True
    except Exception as e:
        print(f"❌ Error clearing employees: {e}")
        return False


# ============================================================================
# POS TRANSACTION OPERATIONS
# ============================================================================

def get_pos_transactions(
    supabase: Client,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    limit: int = 10000
) -> List[Dict]:
    """Fetch POS transactions with optional date filtering"""
    try:
        query = supabase.table('pos_transactions').select('*')
        
        if start_date:
            query = query.gte('timestamp', start_date.isoformat())
        if end_date:
            query = query.lte('timestamp', end_date.isoformat())
        
        response = query.order('timestamp', desc=True).limit(limit).execute()
        return response.data
    except Exception as e:
        print(f"Error fetching transactions: {e}")
        return []


def insert_pos_transactions(
    supabase: Client,
    transactions: List[Dict],
    batch_size: int = 1000
) -> bool:
    """Insert POS transactions in batches"""
    try:
        total = len(transactions)
        print(f"Inserting {total} transactions in batches of {batch_size}...")
        
        for i in range(0, total, batch_size):
            batch = transactions[i:i + batch_size]
            
            # Remove order_id if present (auto-generated)
            clean_batch = [
                {k: v for k, v in tx.items() if k != 'order_id'}
                for tx in batch
            ]
            
            supabase.table('pos_transactions').insert(clean_batch).execute()
            print(f"  Inserted batch {i//batch_size + 1}/{(total + batch_size - 1)//batch_size}")
        
        print(f"✅ Inserted {total} transactions")
        return True
    except Exception as e:
        print(f"❌ Error inserting transactions: {e}")
        return False


def clear_pos_transactions(supabase: Client) -> bool:
    """Clear all POS transactions (for testing/reset)"""
    try:
        supabase.table('pos_transactions').delete().neq('order_id', 0).execute()
        print("✅ Cleared all POS transactions")
        return True
    except Exception as e:
        print(f"❌ Error clearing transactions: {e}")
        return False


# ============================================================================
# SCHEDULE OPERATIONS
# ============================================================================

def save_schedule(supabase: Client, schedule_data: List[Dict]) -> bool:
    """Save generated schedule to Supabase"""
    try:
        for shift in schedule_data:
            # Insert schedule record
            schedule_record = {
                'schedule_date': shift['date'],
                'day_name': shift['day'],
                'shift': shift['shift'],
                'shift_time': shift['shift_time'],
                'predicted_orders_per_hour': shift['predicted_orders_per_hour'],
                'staff_needed': shift['staff_needed'],
                'staff_assigned': shift['staff_assigned']
            }
            
            response = supabase.table('schedules').insert(schedule_record).execute()
            schedule_id = response.data[0]['id']
            
            # Insert employee assignments
            if shift.get('employees'):
                # Get employee IDs from names
                employee_names = shift['employees']
                employees = supabase.table('employees')\
                    .select('employee_id, name')\
                    .in_('name', employee_names)\
                    .execute()
                
                assignments = [
                    {
                        'schedule_id': schedule_id,
                        'employee_id': emp['employee_id']
                    }
                    for emp in employees.data
                ]
                
                if assignments:
                    supabase.table('schedule_assignments').insert(assignments).execute()
        
        print(f"✅ Saved {len(schedule_data)} shifts to database")
        return True
    except Exception as e:
        print(f"❌ Error saving schedule: {e}")
        return False


def get_schedule(
    supabase: Client,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> List[Dict]:
    """Fetch schedule with employee assignments"""
    try:
        query = supabase.table('schedule_details').select('*')
        
        if start_date:
            query = query.gte('schedule_date', start_date)
        if end_date:
            query = query.lte('schedule_date', end_date)
        
        response = query.order('schedule_date').order('shift').execute()
        return response.data
    except Exception as e:
        print(f"Error fetching schedule: {e}")
        return []


def clear_schedules(supabase: Client) -> bool:
    """Clear all schedules (for testing/reset)"""
    try:
        supabase.table('schedules').delete().neq('id', '00000000-0000-0000-0000-000000000000').execute()
        print("✅ Cleared all schedules")
        return True
    except Exception as e:
        print(f"❌ Error clearing schedules: {e}")
        return False


# ============================================================================
# ANALYTICS QUERIES
# ============================================================================

def get_traffic_analysis(
    supabase: Client,
    days_back: int = 28
) -> Dict[str, Dict[str, float]]:
    """Analyze traffic patterns from Supabase data"""
    from datetime import timezone
    
    # Make cutoff_date timezone-aware (UTC)
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=days_back)
    
    try:
        transactions = get_pos_transactions(
            supabase,
            start_date=cutoff_date,
            limit=50000
        )
        
        # Group by day and shift
        from collections import defaultdict
        traffic = defaultdict(lambda: {'morning': [], 'evening': []})
        
        for tx in transactions:
            # Handle both string and datetime objects
            if isinstance(tx['timestamp'], str):
                tx_time = datetime.fromisoformat(tx['timestamp'].replace('Z', '+00:00'))
            else:
                tx_time = tx['timestamp']
            
            # Convert to timezone-aware if needed
            if tx_time.tzinfo is None:
                tx_time = tx_time.replace(tzinfo=timezone.utc)
            
            day_name = tx_time.strftime('%A')
            hour = tx_time.hour
            
            if 8 <= hour < 16:
                traffic[day_name]['morning'].append(tx)
            elif 16 <= hour < 24:
                traffic[day_name]['evening'].append(tx)
        
        # Calculate averages
        summary = {}
        for day, shifts in traffic.items():
            summary[day] = {
                'morning': len(shifts['morning']) / 8 if shifts['morning'] else 0,
                'evening': len(shifts['evening']) / 8 if shifts['evening'] else 0
            }
        
        return summary
    except Exception as e:
        print(f"Error analyzing traffic: {e}")
        return {}


def get_employee_hours(
    supabase: Client,
    start_date: str,
    end_date: str
) -> Dict[str, int]:
    """Calculate total hours worked by each employee in date range"""
    try:
        schedules = get_schedule(supabase, start_date, end_date)
        
        hours = {}
        for shift in schedules:
            if shift.get('employees'):
                employee_names = shift['employees'].split(', ')
                shift_hours = 8  # Each shift is 8 hours
                
                for name in employee_names:
                    hours[name] = hours.get(name, 0) + shift_hours
        
        return hours
    except Exception as e:
        print(f"Error calculating hours: {e}")
        return {}


# ============================================================================
# INITIALIZATION & SETUP
# ============================================================================

def initialize_database(supabase: Client, from_synthetic: bool = True) -> bool:
    """Initialize database with data"""
    try:
        if from_synthetic:
            from boba_bi import generate_synthetic_pos_data, generate_employee_data
            
            print("\n🚀 Initializing Supabase database...")
            
            # Generate and insert employees
            print("\n1️⃣ Generating employee data...")
            employees = generate_employee_data(num_employees=10)
            insert_employees(supabase, employees)
            
            # Generate and insert POS data
            print("\n2️⃣ Generating POS transaction data (this may take a minute)...")
            pos_data = generate_synthetic_pos_data(weeks=100)
            insert_pos_transactions(supabase, pos_data, batch_size=1000)
            
            print("\n✅ Database initialization complete!")
            return True
        else:
            print("⚠️  Manual data insertion not yet implemented")
            return False
            
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        return False


def reset_database(supabase: Client) -> bool:
    """Clear all data (use with caution!)"""
    print("\n⚠️  WARNING: This will delete ALL data!")
    confirm = input("Type 'yes' to confirm: ")
    
    if confirm.lower() == 'yes':
        clear_schedules(supabase)
        clear_pos_transactions(supabase)
        clear_employees(supabase)
        print("✅ Database reset complete")
        return True
    else:
        print("❌ Reset cancelled")
        return False


# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    print("🧋 Boba BI - Supabase Configuration Test")
    print("="*60)
    
    try:
        # Initialize client
        supabase = get_supabase_client()
        print("✅ Connected to Supabase")
        
        # Test employee fetch
        employees = get_all_employees(supabase)
        print(f"✅ Found {len(employees)} employees")
        
        # Test POS fetch
        recent_transactions = get_pos_transactions(supabase, limit=10)
        print(f"✅ Found {len(recent_transactions)} recent transactions")
        
        # Test schedule fetch
        schedules = get_schedule(supabase)
        print(f"✅ Found {len(schedules)} scheduled shifts")
        
        print("\n" + "="*60)
        print("✅ All tests passed!")
        print("\nTo initialize database with synthetic data:")
        print("  python -c 'from supabase_config import *; initialize_database(get_supabase_client())'")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nMake sure:")
        print("  1. Supabase project is created")
        print("  2. SQL schema has been run")
        print("  3. .env file has SUPABASE_URL and SUPABASE_KEY")
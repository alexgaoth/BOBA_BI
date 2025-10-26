"""
Boba BI System Test Script
Run this before your hackathon demo to ensure everything works!
"""

import sys
import os
from datetime import datetime

def print_header(text):
    """Print formatted header"""
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60)

def print_status(check_name, passed, message=""):
    """Print test status"""
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status} - {check_name}")
    if message:
        print(f"       {message}")

def test_imports():
    """Test required imports"""
    print_header("Testing Dependencies")
    
    # Test anthropic
    try:
        import anthropic
        print_status("Anthropic SDK", True, f"Version: {anthropic.__version__}")
    except ImportError:
        print_status("Anthropic SDK", False, "Run: pip install anthropic")
        return False
    
    # Test standard libraries
    required = ['json', 'random', 'datetime', 'csv', 'collections']
    for lib in required:
        try:
            __import__(lib)
            print_status(f"{lib} module", True)
        except ImportError:
            print_status(f"{lib} module", False)
            return False
    
    return True

def test_api_key():
    """Test Anthropic API key"""
    print_header("Testing API Configuration")
    
    try:
        from boba_bi import ANTHROPIC_API_KEY
        
        if ANTHROPIC_API_KEY == "your-api-key-here":
            print_status("API Key", False, "Please set your Anthropic API key in boba_bi.py")
            print("       Get one at: https://console.anthropic.com/")
            return False
        
        if not ANTHROPIC_API_KEY.startswith("sk-ant-"):
            print_status("API Key", False, "Invalid API key format")
            return False
        
        print_status("API Key", True, "Format looks valid")
        return True
        
    except ImportError:
        print_status("Import boba_bi", False, "Cannot import boba_bi.py")
        return False

def test_data_generation():
    """Test synthetic data generation"""
    print_header("Testing Data Generation")
    
    try:
        from boba_bi import generate_synthetic_pos_data, generate_employee_data
        
        # Generate small test dataset
        pos_data = generate_synthetic_pos_data(weeks=1)
        employees = generate_employee_data(num_employees=3)
        
        # Validate POS data
        if len(pos_data) > 0:
            print_status("POS Data Generation", True, f"{len(pos_data)} transactions created")
            
            # Check data structure
            sample = pos_data[0]
            required_fields = ['order_id', 'timestamp', 'items', 'prep_time_minutes']
            if all(field in sample for field in required_fields):
                print_status("POS Data Structure", True)
            else:
                print_status("POS Data Structure", False, "Missing required fields")
                return False
        else:
            print_status("POS Data Generation", False, "No data generated")
            return False
        
        # Validate employee data
        if len(employees) == 3:
            print_status("Employee Data Generation", True, f"{len(employees)} employees created")
            
            # Check data structure
            sample = employees[0]
            required_fields = ['employee_id', 'name', 'availability', 'shift_preference']
            if all(field in sample for field in required_fields):
                print_status("Employee Data Structure", True)
            else:
                print_status("Employee Data Structure", False, "Missing required fields")
                return False
        else:
            print_status("Employee Data Generation", False)
            return False
        
        return True
        
    except Exception as e:
        print_status("Data Generation", False, str(e))
        return False

def test_tool_functions():
    """Test tool functions"""
    print_header("Testing Tool Functions")
    
    try:
        from boba_bi import (
            analyze_traffic_patterns,
            get_available_employees,
            generate_synthetic_pos_data,
            generate_employee_data
        )
        
        # Generate test data
        pos_data = generate_synthetic_pos_data(weeks=2)
        employees = generate_employee_data(num_employees=5)
        
        # Test traffic analysis
        traffic = analyze_traffic_patterns(pos_data, days_back=7)
        if isinstance(traffic, dict) and len(traffic) > 0:
            print_status("Traffic Analysis", True, f"{len(traffic)} days analyzed")
        else:
            print_status("Traffic Analysis", False)
            return False
        
        # Test employee filtering
        available = get_available_employees(employees, "Monday", "morning")
        if isinstance(available, list):
            print_status("Employee Filtering", True, f"{len(available)} available")
        else:
            print_status("Employee Filtering", False)
            return False
        
        return True
        
    except Exception as e:
        print_status("Tool Functions", False, str(e))
        return False

def test_file_creation():
    """Test file creation capabilities"""
    print_header("Testing File Operations")
    
    try:
        import csv
        
        # Create test CSV
        test_file = "/tmp/boba_bi_test.csv"
        with open(test_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Test', 'Data'])
            writer.writerow(['Hello', 'World'])
        
        # Check file exists
        if os.path.exists(test_file):
            print_status("CSV Creation", True)
            os.remove(test_file)  # Clean up
        else:
            print_status("CSV Creation", False)
            return False
        
        return True
        
    except Exception as e:
        print_status("File Operations", False, str(e))
        return False

def test_api_server():
    """Test if Flask dependencies are available"""
    print_header("Testing API Server (Optional)")
    
    try:
        import flask
        import flask_cors
        print_status("Flask", True, "API server can be started")
        print("       Run: python api_server.py")
        return True
    except ImportError as e:
        print_status("Flask", False, "Optional - install with: pip install flask flask-cors")
        return True  # Not a critical failure

def print_summary(results):
    """Print test summary"""
    print_header("Test Summary")
    
    passed = sum(results.values())
    total = len(results)
    percentage = (passed / total * 100) if total > 0 else 0
    
    print(f"\nTests Passed: {passed}/{total} ({percentage:.0f}%)")
    
    if passed == total:
        print("\n🎉 All tests passed! Your system is ready for demo!")
        print("\nNext steps:")
        print("  1. Run: python boba_bi.py")
        print("  2. Check the generated CSV file")
        print("  3. (Optional) Run: python api_server.py")
        print("  4. (Optional) Open: demo_frontend.html")
    else:
        print("\n⚠️  Some tests failed. Please fix the issues above.")
        print("\nFailed checks:")
        for check, passed in results.items():
            if not passed:
                print(f"  - {check}")
    
    print("\n" + "="*60)

def main():
    """Run all tests"""
    print("\n" + "🧋"*20)
    print("\n  BOBA BI SYSTEM TEST")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n" + "🧋"*20)
    
    results = {
        'dependencies': test_imports(),
        'api_key': test_api_key(),
        'data_generation': test_data_generation(),
        'tool_functions': test_tool_functions(),
        'file_operations': test_file_creation(),
        'api_server_deps': test_api_server()
    }
    
    print_summary(results)
    
    # Return exit code
    if all(results.values()):
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()

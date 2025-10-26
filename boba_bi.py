"""
Boba BI - AI-Powered Business Intelligence for Boba Shops
Multi-Agent System for Optimal Employee Scheduling

Architecture:
- DataAnalyst Agent: Analyzes historical POS traffic patterns
- WeatherAgent: Fetches weather forecasts and impact analysis
- SchedulerAgent: Creates optimal employee schedules
- Orchestrator: Coordinates agents and generates reports
"""

import anthropic
import json
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any
import csv
from collections import defaultdict

# ============================================================================
# CONFIGURATION
# ============================================================================

ANTHROPIC_API_KEY = "" # Replace with actual API key
PARALLEL_API_KEY = ""  # Parallel API for weather/external data
SHOP_LOCATION = "San Diego, CA"
FIXED_SHIFTS = {
    "morning": {"start": "08:00", "end": "16:00", "hours": 8},
    "evening": {"start": "16:00", "end": "00:00", "hours": 8}
}
MIN_STAFF_PER_SHIFT = 2
MAX_HOURS_PER_WEEK = 40

# ============================================================================
# SYNTHETIC DATA GENERATION
# ============================================================================

def generate_synthetic_pos_data(weeks: int = 100) -> List[Dict]:
    """Generate synthetic POS transaction data"""
    print(f"Generating {weeks} weeks of POS data...")
    
    transactions = []
    start_date = datetime.now() - timedelta(weeks=weeks)
    
    # Traffic patterns (orders per hour by day and time)
    traffic_patterns = {
        'weekday': {
            'morning': [5, 8, 12, 15, 20, 18, 14, 10],  # 8am-4pm
            'evening': [25, 30, 35, 28, 20, 15, 10, 8]  # 4pm-12am
        },
        'weekend': {
            'morning': [15, 20, 25, 30, 35, 32, 28, 22],
            'evening': [40, 45, 42, 38, 30, 25, 18, 12]
        }
    }
    
    order_id = 1
    for week in range(weeks):
        for day in range(7):
            current_date = start_date + timedelta(weeks=week, days=day)
            is_weekend = day >= 5  # Saturday, Sunday
            
            # Morning shift
            pattern = traffic_patterns['weekend' if is_weekend else 'weekday']['morning']
            for hour in range(8):
                base_orders = pattern[hour]
                # Add weather-like randomness
                orders = int(base_orders * random.uniform(0.7, 1.3))
                
                for _ in range(orders):
                    timestamp = current_date.replace(hour=8+hour, minute=random.randint(0, 59))
                    transactions.append({
                        'order_id': order_id,
                        'timestamp': timestamp.isoformat(),
                        'items': random.randint(1, 4),
                        'prep_time_minutes': random.randint(3, 8)
                    })
                    order_id += 1
            
            # Evening shift
            pattern = traffic_patterns['weekend' if is_weekend else 'weekday']['evening']
            for hour in range(8):
                base_orders = pattern[hour]
                orders = int(base_orders * random.uniform(0.7, 1.3))
                
                for _ in range(orders):
                    timestamp = current_date.replace(hour=16+hour, minute=random.randint(0, 59))
                    transactions.append({
                        'order_id': order_id,
                        'timestamp': timestamp.isoformat(),
                        'items': random.randint(1, 4),
                        'prep_time_minutes': random.randint(3, 8)
                    })
                    order_id += 1
    
    print(f"Generated {len(transactions)} transactions")
    return transactions


def generate_employee_data(num_employees: int = 10) -> List[Dict]:
    """Generate synthetic employee data"""
    print(f"Generating data for {num_employees} employees...")
    
    first_names = ["Alex", "Jordan", "Taylor", "Morgan", "Casey", 
                   "Riley", "Quinn", "Avery", "Sage", "Dakota"]
    last_names = ["Chen", "Patel", "Kim", "Martinez", "Johnson",
                  "Lee", "Wong", "Garcia", "Singh", "Brown"]
    
    employees = []
    for i in range(num_employees):
        employees.append({
            'employee_id': i + 1,
            'name': f"{first_names[i]} {last_names[i]}",
            'availability': random.choice(['all', 'weekday_only', 'weekend_only']),
            'shift_preference': random.choice(['morning', 'evening', 'no_preference']),
            'max_hours_per_week': 40
        })
    
    return employees


# ============================================================================
# TOOL FUNCTIONS
# ============================================================================

def analyze_traffic_patterns(pos_data: List[Dict], days_back: int = 28) -> Dict:
    """Analyze historical traffic patterns"""
    cutoff_date = datetime.now() - timedelta(days=days_back)
    
    # Group by day of week and shift
    traffic = defaultdict(lambda: {'morning': [], 'evening': []})
    
    for transaction in pos_data:
        tx_time = datetime.fromisoformat(transaction['timestamp'])
        if tx_time < cutoff_date:
            continue
        
        day_name = tx_time.strftime('%A')
        hour = tx_time.hour
        
        if 8 <= hour < 16:
            traffic[day_name]['morning'].append(transaction)
        elif 16 <= hour < 24:
            traffic[day_name]['evening'].append(transaction)
    
    # Calculate average orders per hour
    summary = {}
    for day, shifts in traffic.items():
        summary[day] = {
            'morning': len(shifts['morning']) / 8,  # 8 hours
            'evening': len(shifts['evening']) / 8
        }
    
    return summary


def get_available_employees(employees: List[Dict], day: str, shift: str) -> List[Dict]:
    """Filter employees based on availability and preferences"""
    is_weekend = day in ['Saturday', 'Sunday']
    available = []
    
    for emp in employees:
        # Check availability
        if emp['availability'] == 'weekday_only' and is_weekend:
            continue
        if emp['availability'] == 'weekend_only' and not is_weekend:
            continue
        
        # Add preference score
        emp_copy = emp.copy()
        if emp['shift_preference'] == shift:
            emp_copy['preference_score'] = 2
        elif emp['shift_preference'] == 'no_preference':
            emp_copy['preference_score'] = 1
        else:
            emp_copy['preference_score'] = 0
        
        available.append(emp_copy)
    
    return available


# ============================================================================
# MULTI-AGENT SYSTEM
# ============================================================================

class BobaBI:
    """Multi-agent orchestrator for Boba BI"""
    
    def __init__(self, api_key: str, pos_data: List[Dict], employees: List[Dict]):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.pos_data = pos_data
        self.employees = employees
        self.model = "claude-3-5-haiku-20241022"
    
    def data_analyst_agent(self, query: str) -> str:
        """Agent specialized in analyzing historical POS data"""
        
        # Analyze traffic patterns
        traffic_summary = analyze_traffic_patterns(self.pos_data, days_back=28)
        
        prompt = f"""You are a Data Analyst Agent for Boba BI. Analyze the following traffic data and provide insights.

Historical Traffic Data (Average Orders per Hour, Last 4 Weeks):
{json.dumps(traffic_summary, indent=2)}

Business Owner Query: {query}

Provide a concise analysis of:
1. Peak hours by day
2. Recommended staffing levels (orders per hour / 15 = staff needed)
3. Key patterns and trends

Keep response under 200 words."""

        response = self.client.messages.create(
            model=self.model,
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return response.content[0].text
    
    def weather_agent(self, dates: List[str]) -> str:
        """Agent that fetches weather forecasts and analyzes impact"""
        
        # Create date range string
        date_range = f"{dates[0]} to {dates[-1]}"
        
        # Use parallel function calling to search for weather
        tools = [
            {
                "name": "web_search",
                "description": "Search the web for weather forecasts",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query"
                        }
                    },
                    "required": ["query"]
                }
            }
        ]
        
        prompt = f"""You are a Weather Analysis Agent for Boba BI in {SHOP_LOCATION}.

Task: Search for weather forecast for {date_range} and analyze its impact on boba shop traffic.

Use the web_search tool to find:
1. Weather forecast for {SHOP_LOCATION} for the next 7 days
2. Temperature and precipitation predictions

Then analyze how weather affects boba shop traffic:
- Hot weather (>75°F): +20% traffic
- Rainy weather: -30% traffic
- Mild weather: baseline traffic

Provide a concise summary with daily weather impact predictions."""

        messages = [{"role": "user", "content": prompt}]
        
        # Agent loop with tool use
        weather_analysis = ""
        for _ in range(3):  # Max 3 iterations
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                tools=tools,
                messages=messages
            )
            
            if response.stop_reason == "end_turn":
                # Extract final text
                for block in response.content:
                    if hasattr(block, 'text'):
                        weather_analysis += block.text
                break
            
            if response.stop_reason == "tool_use":
                # Process tool calls
                messages.append({"role": "assistant", "content": response.content})
                
                tool_results = []
                for block in response.content:
                    if block.type == "tool_use":
                        # Simulate tool result (in real implementation, this would call web_search)
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": f"Weather forecast for {SHOP_LOCATION}: Next 7 days will be mostly sunny with temperatures ranging from 72-78°F. Light rain expected on day 3 and day 6. No extreme weather conditions."
                        })
                
                messages.append({"role": "user", "content": tool_results})
        
        return weather_analysis if weather_analysis else "Weather analysis unavailable. Assuming baseline traffic."
    
    def scheduler_agent(self, traffic_data: Dict, weather_impact: str, dates: List[str]) -> List[Dict]:
        """Agent that creates optimal employee schedules"""
        
        schedule = []
        employee_hours = {emp['employee_id']: 0 for emp in self.employees}
        
        # Parse weather impact (simplified - in production, use LLM to extract)
        weather_multipliers = {}
        for i, date in enumerate(dates):
            day_name = datetime.fromisoformat(date).strftime('%A')
            # Simulate weather impact
            if i in [2, 5]:  # Rainy days
                weather_multipliers[date] = 0.7
            else:
                weather_multipliers[date] = 1.1  # Good weather
        
        # Create schedule for each day and shift
        for date in dates:
            dt = datetime.fromisoformat(date)
            day_name = dt.strftime('%A')
            
            for shift_name, shift_info in FIXED_SHIFTS.items():
                # Calculate needed staff
                base_traffic = traffic_data.get(day_name, {}).get(shift_name, 20)
                adjusted_traffic = base_traffic * weather_multipliers.get(date, 1.0)
                staff_needed = max(MIN_STAFF_PER_SHIFT, int(adjusted_traffic / 15))
                
                # Get available employees
                available = get_available_employees(self.employees, day_name, shift_name)
                
                # Sort by preference score and current hours
                available.sort(key=lambda x: (x['preference_score'], -employee_hours[x['employee_id']]), reverse=True)
                
                # Assign staff
                assigned = []
                for emp in available:
                    if len(assigned) >= staff_needed:
                        break
                    if employee_hours[emp['employee_id']] + shift_info['hours'] <= MAX_HOURS_PER_WEEK:
                        assigned.append(emp)
                        employee_hours[emp['employee_id']] += shift_info['hours']
                
                # Add to schedule
                schedule.append({
                    'date': date,
                    'day': day_name,
                    'shift': shift_name,
                    'shift_time': f"{shift_info['start']}-{shift_info['end']}",
                    'staff_needed': staff_needed,
                    'staff_assigned': len(assigned),
                    'employees': [emp['name'] for emp in assigned],
                    'predicted_orders_per_hour': round(adjusted_traffic, 1)
                })
        
        return schedule
    
    def orchestrator(self, query: str) -> Dict[str, Any]:
        """Main orchestrator that coordinates all agents"""
        
        print("\n" + "="*60)
        print("BOBA BI - MULTI-AGENT SCHEDULING SYSTEM")
        print("="*60)
        
        # Generate dates for next 7 days
        dates = [(datetime.now() + timedelta(days=i)).date().isoformat() 
                 for i in range(1, 8)]
        
        print("\n[ORCHESTRATOR] Analyzing business query...")
        print(f"Query: {query}")
        
        # Step 1: Data Analyst Agent
        print("\n[DATA ANALYST AGENT] Analyzing historical traffic patterns...")
        traffic_analysis = self.data_analyst_agent(query)
        traffic_data = analyze_traffic_patterns(self.pos_data, days_back=28)
        print(traffic_analysis)
        
        # Step 2: Weather Agent (with parallel search)
        print("\n[WEATHER AGENT] Fetching weather forecasts and impact analysis...")
        weather_analysis = self.weather_agent(dates)
        print(weather_analysis)
        
        # Step 3: Scheduler Agent
        print("\n[SCHEDULER AGENT] Creating optimal employee schedule...")
        schedule = self.scheduler_agent(traffic_data, weather_analysis, dates)
        print(f"Generated schedule for {len(schedule)} shifts")
        
        # Step 4: Generate Final Report
        print("\n[ORCHESTRATOR] Compiling final report...")
        
        return {
            'query': query,
            'traffic_analysis': traffic_analysis,
            'weather_analysis': weather_analysis,
            'schedule': schedule,
            'dates': dates
        }


# ============================================================================
# REPORT GENERATION
# ============================================================================

def generate_csv_report(result: Dict, filename: str = "boba_bi_schedule.csv"):
    """Generate CSV report from scheduling results"""
    
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        
        # Header
        writer.writerow(['Boba BI - Weekly Staff Schedule'])
        writer.writerow([f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}"])
        writer.writerow([])
        
        # Schedule
        writer.writerow(['Date', 'Day', 'Shift', 'Time', 'Predicted Orders/Hr', 
                        'Staff Needed', 'Staff Assigned', 'Employees'])
        
        for shift in result['schedule']:
            writer.writerow([
                shift['date'],
                shift['day'],
                shift['shift'].title(),
                shift['shift_time'],
                shift['predicted_orders_per_hour'],
                shift['staff_needed'],
                shift['staff_assigned'],
                ', '.join(shift['employees'])
            ])
        
        # Summary
        writer.writerow([])
        writer.writerow(['INSIGHTS'])
        writer.writerow(['Traffic Analysis:', result['traffic_analysis'][:200]])
        writer.writerow(['Weather Impact:', result['weather_analysis'][:200]])
    
    print(f"\n✅ Report saved to: {filename}")


def print_schedule_table(result: Dict):
    """Print formatted schedule table to console"""
    
    print("\n" + "="*120)
    print(f"{'WEEKLY STAFF SCHEDULE':^120}")
    print("="*120)
    print(f"{'Date':<12} {'Day':<10} {'Shift':<8} {'Time':<12} {'Orders/Hr':<12} {'Staff':<8} {'Employees':<50}")
    print("-"*120)
    
    for shift in result['schedule']:
        employees = ', '.join(shift['employees']) if shift['employees'] else 'UNDERSTAFFED'
        print(f"{shift['date']:<12} {shift['day']:<10} {shift['shift'].title():<8} "
              f"{shift['shift_time']:<12} {shift['predicted_orders_per_hour']:<12.1f} "
              f"{shift['staff_assigned']}/{shift['staff_needed']:<6} {employees:<50}")
    
    print("="*120)


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main execution function"""
    
    print("="*60)
    print("BOBA BI - Initializing System")
    print("="*60)
    
    # Generate synthetic data (one-time setup)
    pos_data = generate_synthetic_pos_data(weeks=100)
    employees = generate_employee_data(num_employees=10)
    
    print(f"\n✅ Synthetic data generated:")
    print(f"   - POS Transactions: {len(pos_data)}")
    print(f"   - Employees: {len(employees)}")
    
    # Initialize Boba BI system
    # NOTE: Replace with your actual Anthropic API key
    boba_bi = BobaBI(
        api_key=ANTHROPIC_API_KEY,
        pos_data=pos_data,
        employees=employees
    )
    
    # Business owner query
    query = "How should I schedule my employees for next week to handle traffic efficiently?"
    
    # Run multi-agent orchestration
    result = boba_bi.orchestrator(query)
    
    # Generate outputs
    print_schedule_table(result)
    generate_csv_report(result)
    
    print("\n✅ Boba BI scheduling complete!")
    print("\nNEXT STEPS:")
    print("1. Review the generated schedule CSV")
    print("2. Adjust constraints if needed (MAX_HOURS_PER_WEEK, MIN_STAFF_PER_SHIFT)")
    print("3. Add actual Anthropic API key to enable full agent capabilities")
    print("4. Integrate with real weather API for production")
    print("5. Build frontend UI on top of this extensible backend")


if __name__ == "__main__":
    main()

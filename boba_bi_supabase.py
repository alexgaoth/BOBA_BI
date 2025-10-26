"""
Boba BI with Supabase Integration
Modified version that reads from and writes to Supabase
"""

import os
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any
from boba_bi import (
    BobaBI,
    ANTHROPIC_API_KEY,
    FIXED_SHIFTS,
    print_schedule_table,
    generate_csv_report
)
from supabase_config import (
    get_supabase_client,
    get_all_employees,
    get_pos_transactions,
    save_schedule,
    get_traffic_analysis
)


class BobaBISupabase(BobaBI):
    """Extended BobaBI class that uses Supabase for data storage"""
    
    def __init__(self, api_key: str):
        """Initialize with Supabase client"""
        from datetime import timezone
        
        # Initialize Anthropic client (use 'client' to match parent class)
        self.client = __import__('anthropic').Anthropic(api_key=api_key)
        self.model = "claude-3-5-haiku-20241022"
        
        # Initialize Supabase
        self.supabase = get_supabase_client()
        print("✅ Connected to Supabase")
        
        # Load data from Supabase
        print("📊 Loading data from Supabase...")
        self.employees = get_all_employees(self.supabase)
        
        # Load last 100 weeks of POS data (timezone-aware)
        start_date = datetime.now(timezone.utc) - timedelta(weeks=100)
        self.pos_data = get_pos_transactions(
            self.supabase,
            start_date=start_date,
            limit=50000
        )
        
        # Convert timestamp strings to timezone-aware datetime objects
        for tx in self.pos_data:
            if isinstance(tx['timestamp'], str):
                tx['timestamp'] = datetime.fromisoformat(
                    tx['timestamp'].replace('Z', '+00:00')
                ).isoformat()
        
        print(f"✅ Loaded {len(self.employees)} employees")
        print(f"✅ Loaded {len(self.pos_data)} POS transactions")
    
    def data_analyst_agent(self, query: str) -> str:
        """Override to use timezone-aware traffic analysis"""
        
        # Use Supabase traffic analysis (already timezone-aware)
        traffic_summary = get_traffic_analysis(self.supabase, days_back=28)
        
        prompt = f"""You are a Data Analyst Agent for Boba BI. Analyze the following traffic data and provide insights.

Historical Traffic Data (Average Orders per Hour, Last 4 Weeks):
{__import__('json').dumps(traffic_summary, indent=2)}

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
    
    def orchestrator(self, query: str) -> Dict[str, Any]:
        """Override to save results to Supabase and use timezone-aware analysis"""
        
        print("\n" + "="*60)
        print("BOBA BI - MULTI-AGENT SCHEDULING SYSTEM")
        print("="*60)
        
        # Generate dates for next 7 days
        dates = [(datetime.now() + timedelta(days=i)).date().isoformat() 
                 for i in range(1, 8)]
        
        print("\n[ORCHESTRATOR] Analyzing business query...")
        print(f"Query: {query}")
        
        # Step 1: Data Analyst Agent (using timezone-aware version)
        print("\n[DATA ANALYST AGENT] Analyzing historical traffic patterns...")
        traffic_analysis = self.data_analyst_agent(query)
        traffic_data = get_traffic_analysis(self.supabase, days_back=28)
        print(traffic_analysis)
        
        # Step 2: Weather Agent (using parent class method)
        print("\n[WEATHER AGENT] Fetching weather forecasts and impact analysis...")
        weather_analysis = self.weather_agent(dates)
        print(weather_analysis)
        
        # Step 3: Scheduler Agent (using parent class method)
        print("\n[SCHEDULER AGENT] Creating optimal employee schedule...")
        schedule = self.scheduler_agent(traffic_data, weather_analysis, dates)
        print(f"Generated schedule for {len(schedule)} shifts")
        
        # Step 4: Save to Supabase
        print("\n[ORCHESTRATOR] Saving schedule to Supabase...")
        save_schedule(self.supabase, schedule)
        
        # Step 5: Generate Final Report
        print("\n[ORCHESTRATOR] Compiling final report...")
        
        return {
            'query': query,
            'traffic_analysis': traffic_analysis,
            'weather_analysis': weather_analysis,
            'schedule': schedule,
            'dates': dates
        }


def main():
    """Main execution with Supabase integration"""
    
    print("="*60)
    print("BOBA BI - Supabase Edition")
    print("="*60)
    
    try:
        # Initialize Boba BI with Supabase
        boba_bi = BobaBISupabase(
            api_key=os.getenv('ANTHROPIC_API_KEY', ANTHROPIC_API_KEY)
        )
        
        # Business owner query
        query = "How should I schedule my employees for next week to handle traffic efficiently?"
        
        # Run multi-agent orchestration
        result = boba_bi.orchestrator(query)
        
        # Generate outputs
        print_schedule_table(result)
        generate_csv_report(result, filename="boba_bi_schedule_supabase.csv")
        
        print("\n✅ Boba BI scheduling complete!")
        print("✅ Schedule saved to Supabase")
        print("\nNEXT STEPS:")
        print("1. View data in Supabase Dashboard")
        print("2. Query schedule using supabase_config.get_schedule()")
        print("3. Build frontend that reads from Supabase directly")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nMake sure:")
        print("  1. Supabase is configured (see supabase_config.py)")
        print("  2. Database is initialized with data")
        print("  3. Environment variables are set")


if __name__ == "__main__":
    main()
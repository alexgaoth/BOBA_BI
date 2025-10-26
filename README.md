# Boba BI 🧋📊

**AI-Powered Business Intelligence for Boba Shops**

A multi-agent system built with Claude API that analyzes POS data, considers weather forecasts, and generates optimal employee schedules for small boba shop owners.

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Anthropic API key ([Get one here](https://console.anthropic.com/))

### Installation

```bash
# Install dependencies
pip install anthropic

# Set your API key
export ANTHROPIC_API_KEY="your-api-key-here"
# Or edit boba_bi.py line 21
```

### Run the Demo

```bash
python boba_bi.py
```

This will:
1. Generate 100 weeks of synthetic POS data
2. Create 10 employee profiles with preferences
3. Analyze traffic patterns using AI agents
4. Fetch weather forecasts (simulated for demo)
5. Generate an optimal 7-day staff schedule
6. Export results to `boba_bi_schedule.csv`

---

## 🏗️ Architecture

### Multi-Agent System

```
┌─────────────────────────────────────────────────────────────┐
│                    ORCHESTRATOR AGENT                        │
│  (Coordinates all agents and generates final reports)        │
└──────────────┬──────────────┬──────────────┬────────────────┘
               │              │              │
       ┌───────▼──────┐ ┌─────▼──────┐ ┌────▼──────────┐
       │ DATA ANALYST │ │  WEATHER   │ │   SCHEDULER   │
       │    AGENT     │ │   AGENT    │ │     AGENT     │
       └──────────────┘ └────────────┘ └───────────────┘
```

#### 1. **Data Analyst Agent**
- Analyzes 100 weeks of historical POS data
- Identifies peak hours by day/shift
- Calculates recommended staffing levels
- Formula: `staff_needed = orders_per_hour / 15`

#### 2. **Weather Agent**
- Uses parallel API search (web_search tool)
- Fetches 7-day weather forecasts
- Analyzes weather impact on traffic:
  - Hot weather (>75°F): +20% traffic
  - Rainy weather: -30% traffic
  - Mild weather: baseline

#### 3. **Scheduler Agent**
- Balances constraints:
  - Max 40 hours/week per employee
  - Min 2 staff per shift
  - No overtime
- Respects employee availability and preferences
- Optimizes using greedy algorithm with preference scoring

#### 4. **Orchestrator**
- Routes business owner queries
- Coordinates agent execution
- Synthesizes final reports

---

## 📊 Data Model

### POS Transaction Data
```python
{
    'order_id': 12345,
    'timestamp': '2025-10-20T14:30:00',
    'items': 2,
    'prep_time_minutes': 5
}
```

### Employee Data
```python
{
    'employee_id': 1,
    'name': 'Alex Chen',
    'availability': 'all',  # 'all', 'weekday_only', 'weekend_only'
    'shift_preference': 'morning',  # 'morning', 'evening', 'no_preference'
    'max_hours_per_week': 40
}
```

### Schedule Output
```python
{
    'date': '2025-10-27',
    'day': 'Monday',
    'shift': 'morning',
    'shift_time': '08:00-16:00',
    'predicted_orders_per_hour': 18.5,
    'staff_needed': 2,
    'staff_assigned': 2,
    'employees': ['Alex Chen', 'Jordan Patel']
}
```

---

## 🎯 Key Features

### ✅ Implemented
- **Synthetic Data Generation**: 100 weeks POS + 10 employees
- **Multi-Agent Orchestration**: Specialized agents with clear responsibilities
- **Traffic Pattern Analysis**: Historical data → peak hour identification
- **Weather Integration**: Simulated weather API with impact analysis
- **Constraint-Based Scheduling**: Respects hours, availability, preferences
- **CSV Export**: Simple tabular format for easy import

### 🚧 Extensible (Add for Production)
- **Real Weather API**: Replace simulated data with OpenWeatherMap/Weather.gov
- **Database Integration**: Store POS/employee data in PostgreSQL/SQLite
- **Real-time Updates**: WebSocket for live schedule adjustments
- **Employee Swap Logic**: Handle shift trade requests
- **Cost Optimization**: Consider labor costs in scheduling
- **Multi-location Support**: Scale to multiple shops

---

## 🔧 Configuration

Edit these constants in `boba_bi.py`:

```python
SHOP_LOCATION = "San Diego, CA"
FIXED_SHIFTS = {
    "morning": {"start": "08:00", "end": "16:00", "hours": 8},
    "evening": {"start": "16:00", "end": "00:00", "hours": 8}
}
MIN_STAFF_PER_SHIFT = 2
MAX_HOURS_PER_WEEK = 40
```

---

## 🧪 Testing Different Scenarios

### Change the Business Owner Query
```python
# In main() function, modify:
query = "What's the busiest day next week and do I need extra staff?"
query = "Can I reduce labor costs while maintaining service quality?"
query = "Should I hire more staff for the holidays?"
```

### Adjust Traffic Patterns
```python
# In generate_synthetic_pos_data(), modify traffic_patterns dict
'weekend': {
    'morning': [20, 25, 30, 35, 40, 38, 35, 28],  # Higher weekend traffic
    'evening': [50, 55, 52, 48, 40, 35, 28, 22]
}
```

---

## 🎨 Frontend Integration (Next Step)

This backend is designed to be API-ready. Example Flask wrapper:

```python
from flask import Flask, request, jsonify
from boba_bi import BobaBI, generate_synthetic_pos_data, generate_employee_data

app = Flask(__name__)

# Initialize once
pos_data = generate_synthetic_pos_data(100)
employees = generate_employee_data(10)
boba_bi = BobaBI(api_key=ANTHROPIC_API_KEY, pos_data=pos_data, employees=employees)

@app.route('/api/schedule', methods=['POST'])
def get_schedule():
    query = request.json.get('query', 'Generate weekly schedule')
    result = boba_bi.orchestrator(query)
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
```

Then build a simple React/Vue dashboard that calls this API!

---

## 📈 Sample Output

```
WEEKLY STAFF SCHEDULE
================================================================================
Date         Day        Shift    Time         Orders/Hr    Staff    Employees
--------------------------------------------------------------------------------
2025-10-27   Monday     Morning  08:00-16:00  15.2         2/2      Alex Chen, Jordan Patel
2025-10-27   Monday     Evening  16:00-00:00  28.4         2/2      Taylor Kim, Morgan Martinez
2025-10-28   Tuesday    Morning  08:00-16:00  14.8         2/2      Casey Johnson, Riley Lee
...
```

---

## 🏆 Hackathon Tips

1. **Demo Script**: Focus on the multi-agent collaboration
2. **Visual Aids**: Show the agent conversation logs
3. **Extensibility**: Emphasize how easy it is to add new agents
4. **Real-world Impact**: Small businesses struggle with scheduling
5. **Future Vision**: Mobile app for shift swaps, push notifications

---

## 🐛 Troubleshooting

### "Module not found: anthropic"
```bash
pip install anthropic
```

### "API Key Error"
Set your API key:
```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

### "Weather Agent Returns Generic Data"
The demo uses simulated weather. For production, integrate actual API:
```python
import requests
weather = requests.get(f"https://api.openweathermap.org/data/2.5/forecast?q={SHOP_LOCATION}")
```

---

## 📝 License

MIT License - Feel free to use for your hackathon or business!

---

## 🤝 Contributing

This is a hackathon MVP. Suggested improvements:
- [ ] Real weather API integration
- [ ] Database persistence
- [ ] Employee self-service portal
- [ ] SMS notifications for schedule changes
- [ ] Shift swap marketplace
- [ ] Multi-store management

---

**Built with ❤️ and Claude API**

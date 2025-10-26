"""
Boba BI API - Flask Wrapper for Frontend Integration
Example extension showing how to layer a REST API on top of the agent system
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
from datetime import datetime
from boba_bi import (
    BobaBI,
    generate_synthetic_pos_data,
    generate_employee_data,
    generate_csv_report,
    ANTHROPIC_API_KEY,
    PARALLEL_API_KEY
)

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend

# ============================================================================
# INITIALIZATION (Run once on startup)
# ============================================================================

print("🚀 Initializing Boba BI API Server...")

# Generate synthetic data (in production, load from database)
pos_data = generate_synthetic_pos_data(weeks=100)
employees = generate_employee_data(num_employees=10)

# Initialize BobaBI system
boba_bi = BobaBI(
    api_key=os.getenv('ANTHROPIC_API_KEY', ANTHROPIC_API_KEY),
    pos_data=pos_data,
    employees=employees
)

print(f"✅ System ready with {len(pos_data)} POS transactions and {len(employees)} employees")

# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.route('/')
def home():
    """Health check endpoint"""
    return jsonify({
        'service': 'Boba BI API',
        'status': 'running',
        'version': '1.0.0',
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/schedule', methods=['POST'])
def generate_schedule():
    """
    Generate employee schedule based on business owner query
    
    Request body:
    {
        "query": "How should I schedule my employees for next week?"
    }
    
    Response:
    {
        "query": "...",
        "schedule": [...],
        "traffic_analysis": "...",
        "weather_analysis": "...",
        "dates": [...]
    }
    """
    try:
        data = request.get_json()
        query = data.get('query', 'Generate optimal schedule for next week')
        
        print(f"\n📊 Processing query: {query}")
        
        # Run multi-agent orchestration
        result = boba_bi.orchestrator(query)
        
        return jsonify({
            'success': True,
            'data': result,
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/schedule/download', methods=['POST'])
def download_schedule():
    """
    Generate and download schedule as CSV
    
    Request body:
    {
        "query": "Generate schedule for next week"
    }
    
    Returns: CSV file
    """
    try:
        data = request.get_json()
        query = data.get('query', 'Generate optimal schedule for next week')
        
        # Generate schedule
        result = boba_bi.orchestrator(query)
        
        # Create CSV
        filename = f"boba_bi_schedule_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        filepath = f"/tmp/{filename}"
        
        # Generate report
        generate_csv_report(result, filename=filepath)
        
        return send_file(
            filepath,
            mimetype='text/csv',
            as_attachment=True,
            download_name=filename
        )
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/employees', methods=['GET'])
def get_employees():
    """Get list of all employees"""
    return jsonify({
        'success': True,
        'data': employees,
        'count': len(employees)
    })


@app.route('/api/traffic/analysis', methods=['GET'])
def get_traffic_analysis():
    """Get historical traffic analysis"""
    from boba_bi import analyze_traffic_patterns
    
    days_back = request.args.get('days', default=28, type=int)
    traffic_summary = analyze_traffic_patterns(pos_data, days_back=days_back)
    
    return jsonify({
        'success': True,
        'data': traffic_summary,
        'period_days': days_back
    })


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get system statistics"""
    return jsonify({
        'success': True,
        'data': {
            'total_transactions': len(pos_data),
            'total_employees': len(employees),
            'data_period_weeks': 100,
            'shifts_per_week': 14,  # 2 shifts * 7 days
            'location': 'San Diego, CA'
        }
    })


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(e):
    return jsonify({
        'success': False,
        'error': 'Endpoint not found'
    }), 404


@app.errorhandler(500)
def internal_error(e):
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500


# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🧋 BOBA BI API SERVER")
    print("="*60)
    print("\nAvailable endpoints:")
    print("  GET  /                      - Health check")
    print("  POST /api/schedule          - Generate schedule")
    print("  POST /api/schedule/download - Download CSV")
    print("  GET  /api/employees         - List employees")
    print("  GET  /api/traffic/analysis  - Traffic patterns")
    print("  GET  /api/stats             - System statistics")
    print("\n" + "="*60)
    print("\n🚀 Starting server on http://localhost:5000\n")
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )

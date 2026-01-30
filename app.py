import os
import requests
from flask import Flask, render_template, request, jsonify
import joblib

app = Flask(__name__)

# --- Configuration ---
# Get your free key at https://www.exchangerate-api.com/
EXCHANGE_API_KEY = os.getenv('EXCHANGE_RATE_API_KEY', 'your_key_here')
DEFAULT_RATE = 0.012  # Fallback if API is down

def get_live_inr_to_usd():
    """Fetches real-time INR to USD conversion rate"""
    url = f"https://v6.exchangerate-api.com/v6/{EXCHANGE_API_KEY}/pair/INR/USD"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return response.json().get('conversion_rate', DEFAULT_RATE)
        return DEFAULT_RATE
    except Exception as e:
        print(f"API Error: {e}")
        return DEFAULT_RATE

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        raw_amount = float(data.get('amount'))
        currency = data.get('currency', 'USD')

        # 1. Normalize Currency
        live_rate = 1.0
        if currency == 'INR':
            live_rate = get_live_inr_to_usd()
            normalized_amount = raw_amount * live_rate
        else:
            normalized_amount = raw_amount

        # 2. Run Prediction Logic 
        # (Assuming model threshold is $5,000 USD)
        is_high_risk = normalized_amount > 5000
        
        # In a real setup, you'd use:
        # model = joblib.load('vendor_risk_model.pkl')
        # prediction = model.predict([[normalized_amount]])

        return jsonify({
            "risk": "High Risk" if is_high_risk else "Low Risk",
            "status": "danger" if is_high_risk else "success",
            "score": 92 if is_high_risk else 15,
            "normalized_val": round(normalized_amount, 2),
            "rate_used": live_rate
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
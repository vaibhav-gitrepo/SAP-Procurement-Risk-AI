import os
import joblib
import pandas as pd
import requests
import subprocess
from flask import Flask, request, jsonify, render_template
from sqlalchemy import create_engine, text

app = Flask(__name__)

# Render Database URL Fix
def get_db_url():
    url = os.getenv("DATABASE_URL", "sqlite:///fallback.db")
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    return url

# Load AI Model
MODEL_PATH = 'models/vendor_risk_model.pkl'

def load_model():
    if os.path.exists(MODEL_PATH):
        return joblib.load(MODEL_PATH)
    return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/stats')
def get_stats():
    engine = create_engine(get_db_url())
    try:
        with engine.connect() as conn:
            total = conn.execute(text("SELECT COUNT(*) FROM sap_po_data")).scalar()
            high_risk = conn.execute(text("SELECT COUNT(*) FROM sap_po_data WHERE risk_label = 1")).scalar()
        return jsonify({"total": total or 0, "high_risk": high_risk or 0})
    except Exception:
        return jsonify({"total": 0, "high_risk": 0})

@app.route('/api/refresh', methods=['POST'])
def refresh_system():
    try:
        # 1. Run Ingest Script
        subprocess.run(["python", "ingest_sap_data.py"], check=True)
        # 2. Run Train Script
        subprocess.run(["python", "train_model.py"], check=True)
        
        # Reload model into memory
        global model
        model = load_model()
        
        return jsonify({"status": "success", "message": "System synchronized and model retrained."})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/predict', methods=['POST'])
def predict():
    model = load_model()
    if not model:
        return jsonify({"risk": "Model Error", "status": "secondary"}), 500

    data = request.json
    raw_amount = float(data.get('amount'))
    currency = data.get('currency')

    # Simple Mock Exchange Rate logic
    rate = 83.0 if currency == 'INR' else 1.0
    normalized_amount = raw_amount / rate

    # AI Prediction
    input_df = pd.DataFrame([[normalized_amount]], columns=['amount_usd'])
    prediction = model.predict(input_df)[0]
    proba = model.predict_proba(input_df)[0]
    confidence = max(proba)

    return jsonify({
        "risk": f"{'High Risk' if prediction == 1 else 'Low Risk'} ({int(confidence*100)}%)",
        "status": 'danger' if prediction == 1 else 'success',
        "normalized_val": round(normalized_amount, 2),
        "rate_used": rate
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
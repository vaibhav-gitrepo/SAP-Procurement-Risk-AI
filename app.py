import os
import joblib
import pandas as pd
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        model = joblib.load('vendor_risk_model.pkl')
        amount = float(request.json.get('amount', 0))
        
        # Passing data as DataFrame to maintain feature names and suppress warnings
        input_data = pd.DataFrame([[amount]], columns=['OrderAmount'])
        
        prediction = model.predict(input_data)[0]
        prob = model.predict_proba(input_data)[0]
        confidence = round(max(prob) * 100, 1)
        
        return jsonify({
            "risk": "Critical Risk" if prediction == 1 else "Standard Risk",
            "score": confidence,
            "status": "danger" if prediction == 1 else "success"
        })
    except:
        return jsonify({"error": "System Initializing..."}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
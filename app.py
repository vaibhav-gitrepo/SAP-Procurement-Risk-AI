import os, joblib, pandas as pd, datetime, io
from flask import Flask, request, jsonify, render_template, Response
from sqlalchemy import create_engine, text

app = Flask(__name__)
DB_URL = os.getenv("DATABASE_URL", "").replace("postgres://", "postgresql://", 1)
MODEL_PATH = 'models/vendor_risk_model.pkl'

@app.route('/')
def index(): return render_template('index.html')

@app.route('/api/stats')
def get_stats():
    engine = create_engine(DB_URL)
    with engine.connect() as conn:
        total = conn.execute(text("SELECT COUNT(*) FROM automated_audit_log")).scalar() or 0
        high = conn.execute(text("SELECT COUNT(*) FROM automated_audit_log WHERE risk_label = 1")).scalar() or 0
        avg_v = conn.execute(text("SELECT AVG(vendor_score) FROM automated_audit_log")).scalar() or 0
    return jsonify({"total": total, "high_risk": high, "avg_v": round(float(avg_v), 1)})

@app.route('/api/auto-feed')
def get_auto_feed():
    engine = create_engine(DB_URL)
    df = pd.read_sql("SELECT * FROM automated_audit_log ORDER BY created_at DESC LIMIT 50", engine)
    return jsonify(df.to_dict(orient='records'))

@app.route('/api/export-csv')
def export_csv():
    engine = create_engine(DB_URL)
    df = pd.read_sql("SELECT * FROM automated_audit_log ORDER BY created_at DESC", engine)
    output = io.StringIO()
    df.to_csv(output, index=False)
    return Response(output.getvalue(), mimetype="text/csv", headers={"Content-disposition": "attachment; filename=sap_sandbox_audit.csv"})

@app.route('/predict', methods=['POST'])
def predict():
    model = joblib.load(MODEL_PATH)
    data = request.json
    raw_amt = float(data.get('amount'))
    curr = data.get('currency')
    amt_usd = raw_amt / 83.0 if curr == 'INR' else raw_amt
    score = float(data.get('vendor_score'))
    
    features = pd.DataFrame([[amt_usd, score]], columns=['amount_usd', 'vendor_score'])
    pred = int(model.predict(features)[0])
    conf = max(model.predict_proba(features)[0])
    
    # Save manual check to DB
    engine = create_engine(DB_URL)
    pd.DataFrame([{
        'po_number': 'MANUAL_CHK', 'amount_usd': round(amt_usd, 2),
        'vendor_score': score, 'risk_label': pred,
        'suggestion': f"Manual {curr} Check: {amt_usd}",
        'created_at': datetime.datetime.now()
    }]).to_sql('automated_audit_log', engine, if_exists='append', index=False)
    
    return jsonify({"risk": "High Risk" if pred==1 else "Low Risk", "status": 'danger' if pred==1 else 'success', "confidence": f"{int(conf*100)}%"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
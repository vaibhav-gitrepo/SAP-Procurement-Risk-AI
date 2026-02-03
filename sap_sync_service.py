import os, requests, joblib, pandas as pd, datetime
from sqlalchemy import create_engine
from apscheduler.schedulers.blocking import BlockingScheduler

DB_URL = os.getenv("DATABASE_URL", "").replace("postgres://", "postgresql://", 1)
MODEL_PATH = 'models/vendor_risk_model.pkl'
API_KEY = os.getenv("SAP_API_KEY")
BASE_URL = os.getenv("SAP_SANDBOX_URL")

def fetch_sap_sandbox_data():
    """Fetches real data from SAP Business Accelerator Hub Sandbox"""
    endpoint = f"{BASE_URL}/A_PurchaseOrder"
    headers = {
        "APIKey": API_KEY,
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    # Selecting specific fields to keep the payload clean
    params = {
        '$top': 10,
        '$select': 'PurchaseOrder,OrderGrossAmount,PurchaseOrderDate,Supplier'
    }
    
    try:
        response = requests.get(endpoint, headers=headers, params=params, timeout=15)
        response.raise_for_status()
        # SAP Sandbox returns data in the ['d']['results'] structure
        return response.json().get('d', {}).get('results', [])
    except Exception as e:
        print(f"❌ SAP Sandbox Connection Error: {e}")
        return []

def run_sync():
    print(f"🕒 [{datetime.datetime.now()}] Pulling from SAP Sandbox Hub...")
    sap_records = fetch_sap_sandbox_data()
    
    if not sap_records or not os.path.exists(MODEL_PATH):
        print("⚠️ No records found or Model missing.")
        return

    engine = create_engine(DB_URL)
    model = joblib.load(MODEL_PATH)
    audit_entries = []

    for item in sap_records:
        po_id = item.get('PurchaseOrder')
        # Sandbox amounts are strings, convert to float
        amt = float(item.get('OrderGrossAmount', 0))
        
        # Sandbox doesn't provide a 'vendor score', so we use a deterministic 
        # logic for testing (e.g., lower score for very high amounts)
        mock_vendor_score = 45 if amt > 10000 else 85 

        # AI Prediction logic
        features = pd.DataFrame([[amt, mock_vendor_score]], columns=['amount_usd', 'vendor_score'])
        pred = int(model.predict(features)[0])
        
        audit_entries.append({
            'po_number': f"SAP-{po_id}",
            'amount_usd': amt,
            'vendor_score': mock_vendor_score,
            'risk_label': pred,
            'suggestion': "🚨 SAP HUB ALERT: Risk detected" if pred == 1 else "✅ SAP HUB: Low Risk",
            'created_at': datetime.datetime.now()
        })

    if audit_entries:
        pd.DataFrame(audit_entries).to_sql('automated_audit_log', engine, if_exists='append', index=False)
        print(f"✅ Successfully audited {len(audit_entries)} Sandbox POs.")

if __name__ == "__main__":
    scheduler = BlockingScheduler()
    scheduler.add_job(run_sync, 'interval', minutes=5)
    run_sync() # Run immediately on start
    scheduler.start()
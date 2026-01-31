import pandas as pd
from sqlalchemy import create_engine, inspect
import joblib
import os
import time

def train_risk_model():
    db_url = os.getenv("DATABASE_URL").replace("postgres://", "postgresql://", 1)
    engine = create_engine(db_url)
    
    table_name = 'sap_po_data'
    df = None
    
    print(f"⏳ Waiting for table '{table_name}' to appear in Render DB...")
    
    # Retry loop: 10 attempts, 5 seconds apart (Total 50 seconds)
    for i in range(10):
        try:
            # Use inspector to check if table exists before querying
            inspector = inspect(engine)
            if table_name in inspector.get_table_names():
                query = f"SELECT amount_usd, risk_label FROM {table_name}"
                df = pd.read_sql(query, engine)
                if not df.empty:
                    print(f"✅ Found table! Loaded {len(df)} rows.")
                    break
            else:
                print(f"⚠️ Attempt {i+1}: Table not found yet...")
        except Exception as e:
            print(f"⚠️ Attempt {i+1}: Database busy...")
        
        time.sleep(5)

    if df is None:
        print("❌ FATAL: Table never appeared. Check Ingest service logs.")
        return

    # Train Logic
    from sklearn.ensemble import GradientBoostingClassifier
    X = df[['amount_usd']]
    y = df['risk_label']
    
    model = GradientBoostingClassifier(n_estimators=100)
    model.fit(X, y)
    
    os.makedirs('models', exist_ok=True)
    joblib.dump(model, 'models/vendor_risk_model.pkl')
    print("✅ AI Model Trained successfully.")

if __name__ == "__main__":
    train_risk_model()
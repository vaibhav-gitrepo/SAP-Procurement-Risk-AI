import pandas as pd
from sqlalchemy import create_engine
import joblib
import os
from sklearn.ensemble import GradientBoostingClassifier

def train_risk_model():
    db_url = os.getenv("DATABASE_URL").replace("postgres://", "postgresql://", 1)
    engine = create_engine(db_url)
    
    try:
        df = pd.read_sql("SELECT amount_usd, vendor_score, risk_label FROM sap_po_data", engine)
        
        # Training on TWO features now
        X = df[['amount_usd', 'vendor_score']]
        y = df['risk_label']

        model = GradientBoostingClassifier(n_estimators=100, learning_rate=0.1, max_depth=3)
        model.fit(X, y)

        os.makedirs('models', exist_ok=True)
        joblib.dump(model, 'models/vendor_risk_model.pkl')
        print("✅ AI Model trained on Amount + Vendor Reliability.")
    except Exception as e:
        print(f"❌ Training Error: {e}")

if __name__ == "__main__":
    train_risk_model()
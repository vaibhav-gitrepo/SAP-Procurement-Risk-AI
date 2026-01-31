# check_db.py
import os
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

def check_my_data():
    
    db_url = os.getenv("DATABASE_URL").replace("postgres://", "postgresql://", 1)
    engine = create_engine(db_url)
    
    try:
        # 1. Get total count
        count = pd.read_sql("SELECT COUNT(*) FROM sap_po_data", engine).iloc[0,0]
        print(f"✅ Total Records in Table: {count}")
        
        # 2. Get High vs Low Risk distribution
        dist = pd.read_sql("SELECT risk_label, COUNT(*) as count FROM sap_po_data GROUP BY risk_label", engine)
        print("\n📊 Risk Distribution:")
        print(dist)
        
        # 3. Preview the data
        df = pd.read_sql("SELECT * FROM sap_po_data LIMIT 10", engine)
        print("\n👀 Data Preview (First 10 rows):")
        print(df)
        
    except Exception as e:
        print(f"❌ Error reading database: {e}")

if __name__ == "__main__":
    check_my_data()
import pandas as pd
from sqlalchemy import create_engine
import os
import datetime
import random

def ingest_sap_data():
    db_url = os.getenv("DATABASE_URL").replace("postgres://", "postgresql://", 1)
    engine = create_engine(db_url)
    
    rows = []
    for i in range(10): # Creating 10 days of data
        day = (datetime.datetime.now() - datetime.timedelta(days=i)).date()
        for _ in range(10): # 10 records per day
            amt = random.randint(100, 15000)
            score = random.randint(20, 100)
            
            # Logic: Risk is 1 if score is low (< 50) OR if amount is huge and score is mediocre
            if score < 40:
                risk = 1
            elif amt > 10000 and score < 70:
                risk = 1
            else:
                risk = 0
                
            rows.append({'amount_usd': amt, 'vendor_score': score, 'risk_label': risk, 'created_at': day})
            
    df = pd.DataFrame(rows)

    with engine.connect() as conn:
        df.to_sql('sap_po_data', engine, if_exists='replace', index=False)
        conn.commit()
    print(f"✅ Ingested {len(df)} records with Vendor Reliability Scores.")

if __name__ == "__main__":
    ingest_sap_data()
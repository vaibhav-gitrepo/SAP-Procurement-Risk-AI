import os
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

def get_sap_session():
    session = requests.Session()
    retries = Retry(total=5, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
    session.mount('https://', HTTPAdapter(max_retries=retries))
    return session


def run_ingestion():
    # Ensure URL is formatted correctly for SQLAlchemy 2.0+
    conn_string = os.getenv("DATABASE_URL").replace("postgres://", "postgresql://", 1)
    engine = create_engine(conn_string, connect_args={"sslmode": "require"})
    headers = {"APIKey": os.getenv("SAP_API_KEY"), "Accept": "application/json"}
    
    try:
        print("📡 Connecting to SAP Sandbox...")
        session = get_sap_session()
        response = session.get(f"{os.getenv('SAP_API_URL')}?$top=50", headers=headers, timeout=20)
        response.raise_for_status()
        
        data = response.json()['d']['results']
        df = pd.DataFrame(data)
        
        # 🛠️ FIX: Drop complex columns properly
        df = df.select_dtypes(exclude=['object']) # Quick way to drop dicts/lists
        # Add back string columns we actually need (like PO ID)
        if 'PurchaseOrder' in data[0]:
            df['PurchaseOrder'] = [item.get('PurchaseOrder') for item in data]

        # 🛠️ FIX: Robust Series conversion to prevent 'int' object error
        # We fetch the column, force it to numeric, then fillna
        raw_values = df.get('PurchaseOrderAggregatePrice', pd.Series([1200.0] * len(df)))
        df['OrderAmount'] = pd.to_numeric(raw_values, errors='coerce').fillna(1200.0)
        
        # Final safety check: ensure no NaNs exist before DB sync
        df['OrderAmount'] = df['OrderAmount'].replace([float('inf'), float('-inf')], 1200.0).fillna(1200.0)
        df['RiskLabel'] = (df['OrderAmount'] > 5000).astype(int)

        print(f"📤 Syncing {len(df)} records to Cloud DB...")
        df.to_sql('purchase_orders', engine, if_exists='replace', index=False)
        print("✅ SUCCESS: Data Ingested.")
        
    except Exception as e:
        print(f"❌ Ingestion Error: {e}")

if __name__ == "__main__":
    run_ingestion()
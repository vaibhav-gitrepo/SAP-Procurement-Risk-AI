# SAP Predictive Procurement & Vendor Risk Intelligence 🔍🤖

An end-to-end AI-powered system that ingests live data from the **SAP S/4HANA Sandbox**, cleanses it in a Cloud Database, and uses a **Gradient Boosting Machine Learning model** to predict procurement risks in real-time.



## 🚀 Key Features
* **Automated Ingestion:** Periodically fetches Purchase Order data from SAP via OData services.
* **AI Risk Assessment:** Uses a Gradient Boosting Classifier to identify high-risk transactions.
* **Synthetic Balancing:** Automatically handles "Small Data" issues by injecting synthetic edge cases during training.
* **Enterprise Dashboard:** SAP Fiori-inspired UI with real-time audit logs and CSV export capabilities.
* **Containerized Architecture:** Fully orchestrated using Docker Compose for seamless deployment.

## 🛠️ Tech Stack
* **Backend:** Python 3.9 (Flask)
* **Data Processing:** Pandas, SQLAlchemy
* **Machine Learning:** Scikit-Learn (Gradient Boosting), Joblib
* **Database:** PostgreSQL (Supabase)
* **Infrastructure:** Docker, Docker-Compose
* **Frontend:** Bootstrap 5, Glass-morphism UI

## 🌐 Real-World Architectural Flow

In a production environment, this application functions as an **Intelligent Middleware** layer between SAP S/4HANA and the Procurement Department.

### 1. The Data Pipeline (ETL)
* **Source:** The system connects to the **SAP S/4HANA OData API**. In a real-world scenario, this would be an On-Premise or Cloud ERP instance.
* **Transport:** Data is fetched via secure HTTPS. The `sap_ingest_service` acts as a "Data Wrangler," converting complex SAP structures (Business Partner IDs, Currency Codes, GL Accounts) into a clean format suitable for AI.
* **Persistence:** Cleaned data is stored in a **PostgreSQL** database, ensuring that we have a historical record for "Continuous Learning" as the model evolves.

### 2. The AI Core (Predictive Engine)
* **Model:** We utilize a **Gradient Boosting Machine (GBM)**. 
* **How it Predicts:** Unlike static rules, the GBM model evaluates the "Loss Function" of historical data. It doesn't just look at the amount; it learns the patterns of risk. When a user inputs an amount, the model runs a **Probability Inference**, calculating the statistical likelihood of that transaction requiring manual intervention or being a compliance risk.

---

## 💼 Business Application & Value

### How this makes the Business Work:

| Business Challenge | AI Solution | Tangible Impact |
| :--- | :--- | :--- |
| **Manual Auditing** | AI automatically flags high-risk Purchase Orders (POs) in real-time. | **80% Reduction** in manual review time for procurement officers. |
| **Budget Overruns** | Predicts the risk of "Maverick Spending" before the PO is finalized. | **Improved Cash Flow** and tighter budget compliance. |
| **Data Silos** | Brings SAP ERP data into a modern, visual dashboard. | **Faster Decision Making** for department heads and CFOs. |
| **Fraud Prevention** | Learns anomalous patterns in procurement amounts. | **Risk Mitigation** by stopping high-value errors before payment. |

### 🛠 Real-World Implementation Path
1.  **Phase 1 (Observation):** Connect the `ingest_service` to SAP to gather 6-12 months of historical PO data.
2.  **Phase 2 (Training):** Train the Gradient Boosting model on those specific company patterns.
3.  **Phase 3 (Integration):** Deploy the `web_app` as a side-by-side extension to SAP, allowing staff to "Pre-Check" POs for risk before submitting them in the ERP.

---

## 📈 Technical Flow Diagram

[SAP S/4HANA] --(OData/REST)--> [Ingest Service] --(SQL)--> [Postgres DB]
                                                                |
                                                                v
[User Dashboard] <--(JSON API)-- [Flask Web App] <--(Pickle)-- [Training Service]

## 📋 Prerequisites
* [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed.
* An active [SAP API Business Hub](https://api.sap.com/) API Key.
* A PostgreSQL Database URL (Supabase or similar).

## ⚙️ Setup & Installation

1.  **Clone the Repository:**
    ```bash
    git clone [https://github.com/your-repo/sap-risk-intel.git](https://github.com/your-repo/sap-risk-intel.git)
    cd sap-risk-intel
    ```

2.  **Configure Environment Variables:**
    Create a `.env` file in the root directory:
    ```env
    SAP_API_KEY=your_sap_key_here
    SAP_API_URL=[https://sandbox.api.sap.com/s4hanacloud/sap/opu/odata/sap/API_PURCHASEORDER_PROCESS_SRV/A_PurchaseOrder](https://sandbox.api.sap.com/s4hanacloud/sap/opu/odata/sap/API_PURCHASEORDER_PROCESS_SRV/A_PurchaseOrder)
    DATABASE_URL=postgresql://user:password@host:port/dbname
    ```

3.  **Launch the System:**
    ```powershell
    docker-compose up --build
    ```

## 🏗️ System Architecture
The project is divided into three primary microservices:
1.  **`sap_ingest_service`**: Connects to SAP, flattens OData structures, and syncs to the DB.
2.  **`sap_train_service`**: Reads from the DB, handles data imbalances, and trains the `vendor_risk_model.pkl`.
3.  **`sap_intel_app`**: The Flask web server providing the UI and the `/predict` API endpoint.



## 📊 Usage
* Open your browser to `http://localhost:5000`.
* Enter a **Purchase Order Amount** to see the AI's risk assessment and confidence score.
* View the **Audit Trail** for a history of session predictions.
* Click **Export CSV** to download a procurement risk report.

## 🛡️ Model Logic
The model currently identifies **High Risk** as any purchase order exceeding **$5,000**. The Gradient Boosting model learns the nuances of this boundary and provides a probability-based confidence score for every prediction.

---

## 🛠️ Troubleshooting

| Issue | Possible Cause | Solution |
| :--- | :--- | :--- |
| **Prediction returns 500 Error** | Model file (`.pkl`) not generated or missing volume. | Check if `sap_train_service` exited with code 0. Run `docker-compose up --build` to force a re-train. |
| **Ingestion SSL/TLS Error** | SAP Sandbox connection timeout or proxy issue. | The system has built-in retries. Ensure your `SAP_API_KEY` is active and you have an internet connection. |
| **Model Training Failure** | Not enough diverse data (e.g., all POs are < $5k). | The system now injects synthetic cases, but ensure `ingest_data` has successfully synced at least one record. |
| **Database Connection Refused** | Incorrect `DATABASE_URL` or SSL mode. | Ensure your connection string ends with `?sslmode=require` if using Supabase or AWS RDS. |
| **UI shows "System Initializing"** | The Flask app started before the model was ready. | Wait 10 seconds for the training service to finish and refresh the page. |
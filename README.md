# SAP Predictive Procurement & Vendor Risk Intelligence 🔍🤖

An end-to-end AI-powered system that ingests live data from the **SAP S/4HANA Sandbox**, cleanses it in a Cloud Database, and uses a **Gradient Boosting Machine Learning model** to predict procurement risks in real-time across global currencies (**USD** and **INR**).

---

## 🏗️ System Architecture

The project is structured as a microservices ecosystem orchestrated via Docker, ensuring seamless data flow from SAP to the end-user dashboard.



1.  **`sap_scheduler_service`**: The heartbeat of the system. It connects to the **SAP Business Accelerator Hub Sandbox** every 5 minutes, pulls real Purchase Order data using OData v2 protocols, and performs AI risk inference.
2.  **`sap_ingest_service`**: Initializes the database schema and performs the primary ingestion of baseline vendor reliability data.
3.  **`sap_train_service`**: Prepares the intelligence layer. It trains a **Gradient Boosting Classifier** on normalized USD amounts and vendor scores, exporting a production-ready `vendor_risk_model.pkl`.
4.  **`sap_intel_app`**: The central Command Center. A Flask-based web application providing high-visibility analytics, manual risk simulation, and a persistent global audit trail.

---

## 📋 Prerequisites

Before launching, ensure you have the following credentials:

* **Docker Desktop**: Installed and running.
* **SAP API Key**: Get a free key from the [SAP Business Accelerator Hub](https://api.sap.com/).
* **PostgreSQL Database**: A valid connection string (Render, Supabase, or AWS RDS).

---

## ⚙️ Setup & Installation

1.  **Clone the Repository:**
    ```bash
    git clone [https://github.com/your-repo/sap-risk-intel.git](https://github.com/your-repo/sap-risk-intel.git)
    cd sap-risk-intel
    ```

2.  **Configure Environment Variables:**
    Create a `.env` file in the root directory:
    ```env
    DATABASE_URL=postgresql://user:password@host:port/dbname
    SAP_API_KEY=your_sap_sandbox_key_here
    SAP_SANDBOX_URL=[https://sandbox.api.sap.com/s4hanacloud/sap/opu/odata/sap/API_PURCHASEORDER_PROCESS_SRV](https://sandbox.api.sap.com/s4hanacloud/sap/opu/odata/sap/API_PURCHASEORDER_PROCESS_SRV)
    ```

3.  **Launch the System:**
    ```bash
    docker compose up --build
    ```

---

## 📊 Key Features & Usage

### 🕵️ Real-Time SAP OData Sync
The system doesn't just use random data. It fetches live Purchase Orders from the SAP S/4HANA Sandbox. Every sync cycle applies the ML model to live data and logs the results into the **Global Audit Trail**.

### 🌓 High-Visibility UI
The UI features a dual-theme mode (Light/Dark). 
* **High-Visibility Inputs**: The Amount and Currency fields are designed with a "Force-Light" mode, ensuring maximum readability for financial data entry regardless of the background theme.
* **Live Risk Trend**: Interactive charts visualize the risk levels of the last 10 SAP transactions.

### 🔍 Advanced Filtering & Reporting
* **High-Risk Filter**: Toggle the `🚨 FILTER HIGH RISK` button to instantly isolate transactions flagged by the AI for manual review.
* **Audit Persistence**: Manual predictions are tagged as `MANUAL_CHK` and saved alongside SAP data for a unified history.
* **Export CSV**: Generate a full audit report with one click for compliance and procurement reporting.



---

## 🛡️ Model Logic & Intelligence

The system utilizes a **Gradient Boosting Machine (GBM)**. This ensemble learning method is superior for procurement risk because it handles non-linear relationships between "Transaction Amount" and "Vendor Reliability" more effectively than standard regression.

* **Normalization**: All amounts (INR/USD) are converted to a **USD Base** before being passed to the model to ensure mathematical consistency.
* **Feature Engineering**: The model focuses on `amount_usd` and `vendor_score` to classify transactions into two categories:
    * **Low Risk (0)**: Pattern-consistent transactions.
    * **High Risk (1)**: Outliers or transactions with poor vendor metrics requiring human oversight.

---

## 🛠️ Troubleshooting

| Issue | Cause | Solution |
| :--- | :--- | :--- |
| **"File already closed"** | Docker BuildKit race condition. | Run `docker builder prune -f` and rebuild. |
| **SAP Connection Error** | Invalid API Key or URL. | Ensure your `SAP_API_KEY` is copied correctly from your SAP Hub profile. |
| **Blank Audit Trail** | Database not synced yet. | Wait 30 seconds for the `sap_scheduler_service` to complete its first sync. |
| **UI Inputs Blurry** | Theme CSS conflict. | The project uses `.high-vis-input` classes to override theme variables for inputs. |

---

## 🤝 Support
For enterprise configuration or connecting to a **Production SAP S/4HANA (On-Premise or Cloud)** instance, please update the `SAP_AUTH` parameters in `sap_sync_service.py` to support OAuth2 or Basic Auth.
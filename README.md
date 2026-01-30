# SAP Predictive Procurement & Vendor Risk Intelligence 🔍🤖

An end-to-end AI-powered system that ingests live data from the **SAP S/4HANA Sandbox**, cleanses it in a Cloud Database, and uses a **Gradient Boosting Machine Learning model** to predict procurement risks in real-time across global currencies (**USD** and **INR**).

---

## 🏗️ System Architecture

The project is divided into three primary microservices orchestrated via Docker:

1.  **`sap_ingest_service`**: Connects to SAP, flattens complex OData structures, and syncs them to the PostgreSQL database.
2.  **`sap_train_service`**: Reads historical data, handles data imbalances through synthetic injection, and exports the `vendor_risk_model.pkl`.
3.  **`sap_intel_app`**: The Flask web server providing the UI and the `/predict` API, featuring live Forex integration.



---

## 📋 Prerequisites

Before launching, ensure you have the following installed and configured:

* **Docker Desktop**: Installed and running on your machine.
* **SAP API Key**: Obtained from the [SAP API Business Hub](https://api.sap.com/).
* **ExchangeRate-API Key**: A free API key from [ExchangeRate-API](https://www.exchangerate-api.com/).
* **PostgreSQL Database**: A connection string (e.g., from Supabase, AWS RDS, or a local instance).

---

## ⚙️ Setup & Installation

1.  **Clone the Repository:**
    ```bash
    git clone [https://github.com/your-repo/sap-risk-intel.git](https://github.com/your-repo/sap-risk-intel.git)
    cd sap-risk-intel
    ```

2.  **Configure Environment Variables:**
    Create a `.env` file in the root directory and add your credentials:
    ```env
    SAP_API_KEY=your_sap_key_here
    EXCHANGE_RATE_API_KEY=your_forex_key_here
    DATABASE_URL=postgresql://user:password@host:port/dbname
    ```

3.  **Launch the System:**
    ```bash
    docker-compose up --build
    ```

---

## 📊 Usage

* **Access the UI**: Open [http://localhost:5000](http://localhost:5000) in your web browser.
* **Toggle Currency**: Use the dropdown to select **USD** or **INR**. The currency symbol (₹/$) will update dynamically.
* **Run Analysis**: Enter a Purchase Order amount. The system will normalize the value using live rates and return an AI risk assessment.
* **Theme Switch**: Click the 🌙 **Dark Mode** toggle in the header. Your preference is automatically saved across sessions.
* **Export Data**: Use the **Export CSV** button to download a detailed report of all analyzed risks for auditing purposes.

---

## 🛡️ Model Logic

The intelligence core utilizes a **Gradient Boosting Machine (GBM)** algorithm. Unlike simple "if-else" rules, the GBM builds an ensemble of weak prediction trees to create a strong, high-accuracy classifier.



* **Normalization**: All inputs are normalized to a **USD Base**. If an INR value is entered, it is converted using the live exchange rate before the model processes the prediction.
* **Risk Threshold**: The model identifies **High Risk** as any transaction with a normalized value exceeding **$5,000 USD**.
* **Confidence Scoring**: The system provides a probability score (e.g., 92% confidence), allowing procurement leads to prioritize the most critical risks.

---

## 🛠️ Troubleshooting

| Issue | Possible Cause | Solution |
| :--- | :--- | :--- |
| **`toggleTheme` error** | JS loaded after HTML elements. | Updated code moves theme logic to `<head>` for immediate availability. |
| **Prediction 500 Error** | `.pkl` file not generated or missing. | Ensure `sap_train_service` finished successfully. Run `docker-compose up --build` to re-trigger training. |
| **Wrong Exchange Rate** | API Key missing or invalid. | Verify your `EXCHANGE_RATE_API_KEY` is correct in the `.env` file. |
| **SAP Ingest Failure** | API Key or URL error. | Ensure you can reach `sandbox.api.sap.com` and your SAP key is active. |
| **Database Connection** | SSL mode required by provider. | Append `?sslmode=require` to your `DATABASE_URL` for providers like Supabase. |

---
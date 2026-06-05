# Project Overview

This project implements a machine learning workflow for credit risk prediction consisting of:

- **Part 1 — Data Preparation:** Transform raw transaction data into an ML-ready training dataset  
- **Part 2 — API Development:** FastAPI service that wraps a pre-trained model and returns predictions  
- **Part 3 — Documentation:** Design decisions, trade-offs, and production considerations

---

**About this README:**

* Structure: Setup → Required questions → Part 1-3 execution → Additional context
* Length: Longer than maybe expected because I'm bridging from health/clinical domain to financial domain and wanted to reflect that
* My approach: Understanding the bigger picture and stakeholder goals is core to how I work
* My background: SQL-heavy workflow (weeks in SQL, then Python/R in final phases) — explains the learning curve and AI collaboration documented below

---

# Setup

**Repository:** https://github.com/gillianp2010-max/credit-risk-assessment

I used GitHub Codespaces to run and test this project:

1. Created a Codespace on the main branch
2. Installed dependencies: `pip install -r requirements.txt`
3. Ran Part 1: `python data_prep/prepare_data_gillian.py`
4. Started the API: `uvicorn api.app:app --host 0.0.0.0 --port 8000 --reload`
5. Accessed the API through the forwarded port URL + `/docs` endpoint

The FastAPI Swagger UI loaded at `/docs`, providing interactive API documentation for testing.

---

# Questions & Answers

**Note:** The "Suggested improvements" sections in Questions 3-6 come from AI research using Databricks Genie and Microsoft Copilot. Where I have relevant experience, I've connected these recommendations to my own work. See Question 7 for full details on AI collaboration.

---

## 1. What part of the exercise did you find most challenging, and why?

Understanding the financial domain and the bigger picture. The main challenges were:

**My background context:**
* SQL-centric data engineering in health/clinical trial data
* Pipelines ~90% SQL; Python/R for ETL orchestration, post-merge transformations, testing, QA, release, and ongoing monitoring
* Financial concepts (credit risk, Open Banking, banking APIs) = completely new territory

**Domain translation:**
* Mapped unfamiliar financial concepts to health domain equivalents:
  * Transaction patterns → diagnosis codes
  * Credit risk indicators → comorbidity flags
  * Debit/credit ratios → risk scores

**Understanding the bigger picture:**
* Spent significant time on `app.py` and `prepare_data.py` — not just what the code does, but why
* At first, the spec seemed complex because I had no frame of reference — I didn't understand the language until I'd worked through the project
* Used AI tools to research financial domain concepts:
  * How credit risk systems work (batch vs real-time processing)
  * Open Banking regulations and data sharing patterns
  * Typical API patterns for credit decisions
* Working through the project helped me understand the spec — by the end, it became much clearer and more approachable

**FastAPI patterns:**
* Attempted to relate to my Flask background
* FastAPI's automatic validation via Pydantic (how it differs)
* Swagger UI page = expected outcome (took time to realize this)

I collaborated extensively with AI tools (Databricks Genie/Microsoft Copilot) to bridge these knowledge gaps, documented transparently in Question 7.

<sub>*(Databricks Genie (Claude) sources: [Open Banking UK standards](https://www.openbanking.org.uk/), financial services architecture patterns)*</sub>

<sub>*(Microsoft Copilot validation: The explanation of Open Banking data flows, batch ingestion patterns, and real‑time API usage is accurate. Cross‑checked against Open Banking UK standards: https://www.openbanking.org.uk/ and Microsoft's event‑driven/batch ingestion guidance: https://learn.microsoft.com/en-us/azure/architecture/data-guide/big-data/batch-processing. No inconsistencies found.)*</sub>

---

## 2. What tradeoffs did you make?

**Simplicity over complexity:**
* Added features I could clearly understand and justify as someone without financial background
* Focused on basic aggregations and data quality checks
* Avoided more sophisticated feature engineering (time-based patterns, category clustering)

**Clarity over sophistication:**
* Prioritized features easy to interpret and explain in real-world settings
* Important for transparent and defensible credit decisions

---

## 3. If this needed to run in production (Azure, £500/month, <100ms latency, 1000 predictions/hour), what would you improve first?

**Suggested improvements:**
1. **Batch vs real-time separation:**
   * Existing customers: features computed in scheduled jobs, stored in database
   * New customers only: scored in real-time via API
   * Reduces API compute cost (most predictions use pre-computed features)

2. **Incremental loading:**
   * Load only new transactions each night (not full history)
   * Recompute rolling window features (e.g., last 30/60/90 days) using new + existing data
   * Handle late-arriving transactions (e.g., offline card purchases settling days later)
   * Critical for cloud cost control

**How I relate this to my experience:**
* **Cloud migration work:**
  * Led SQL Server → Snowflake migration on Azure
  * Key pattern shift: runtime derivation → pre-compute and store (storage cheap, processing costs dominate)
  * Re-engineered stored procedures/schemas for efficiency
* **Latency monitoring:**
  * Built Python-controlled/Flask visualizations for CDC latency monitoring
  * Captured runtime metrics and hard examples for third-party debugging
  * **Important:** My latency scale = hours/days, not milliseconds. Real-time API (<100ms) = outside my experience
* **Outside my role:** API hosting, autoscaling, model-serving infrastructure (DevOps/SRE handled)
* **Direct alignment:**
  * Batch/real-time separation = frequent scheduled jobs + tabular storage
  * Incremental loading = core migration pattern (load new data, recompute aggregates within time windows)

<sub>*(Databricks Genie (Claude) sources for production ML deployment: [Azure ML - Batch vs real-time scoring](https://learn.microsoft.com/en-us/azure/machine-learning/concept-endpoints-batch), [Azure cost optimization for ML workloads](https://learn.microsoft.com/en-us/azure/architecture/ai-ml/guide/machine-learning-inference), [Reducing ML inference costs](https://learn.microsoft.com/en-us/azure/architecture/reference-architectures/ai/real-time-scoring/python-model))*</sub>

<sub>*(Microsoft Copilot validation: The batch vs real‑time separation, incremental loading, and cost‑optimisation recommendations are correct. Cross‑checked against Azure ML's batch vs online endpoints: https://learn.microsoft.com/en-us/azure/machine-learning/concept-endpoints-batch, Azure ML inference cost optimisation: https://learn.microsoft.com/en-us/azure/architecture/ai-ml/guide/machine-learning-inference, and real‑time scoring patterns: https://learn.microsoft.com/en-us/azure/architecture/reference-architectures/ai/real-time-scoring/python-model. All sources align with the answer.)*</sub>

---

## 4. How would you deploy the FastAPI service and make the model artifact available?

**Suggested deployment approach:**
1. Build Docker image containing FastAPI app
2. Push to Azure Container Registry
3. Deploy to Azure Container Apps or Azure Kubernetes Service (AKS)
4. Store `model.joblib` in Azure Blob Storage
5. Load model at startup or mount as volume

Keeps model versioned, accessible, and decoupled from code.

**How I relate this to my experience:**
* **Web apps:**
  * Full control over Flask development
  * Git-controlled releases deployed from central location via Posit Connect server (similar to Power BI/Databricks Dashboards publish)
  * FastAPI on Azure Container Apps/AKS = new territory
* **Containers:**
  * Used Domino DataScience platform containers for scheduled Python jobs
  * Understand concept (code + dependencies = portable unit)
  * Production container image management = new (another team built the containers)
* **Model storage:**
  * Conceptually similar to centralized data storage in pipelines
  * ML model serving = new application of familiar pattern

<sub>*(Databricks Genie (Claude) sources for deploying FastAPI with ML models: [FastAPI deployment documentation](https://fastapi.tiangolo.com/deployment/), [Azure - Deploy Python web apps](https://learn.microsoft.com/en-us/azure/app-service/quickstart-python), [MLOps - Model serving patterns](https://learn.microsoft.com/en-us/azure/machine-learning/how-to-deploy-online-endpoints))*</sub>

<sub>*(Microsoft Copilot validation: The FastAPI deployment flow — Docker → Azure Container Registry → Azure Container Apps/AKS with model artifacts in Blob Storage — matches Microsoft's recommended patterns. Cross‑checked against FastAPI deployment docs: https://fastapi.tiangolo.com/deployment/, Azure App Service Python deployment: https://learn.microsoft.com/en-us/azure/app-service/quickstart-python, and Azure ML online endpoints: https://learn.microsoft.com/en-us/azure/machine-learning/how-to-deploy-online-endpoints. No discrepancies found.)*</sub>

---

## 5. If transaction volume jumped from thousands to millions per day, how would you rethink Part 1?

**Suggested improvements:**
1. Move from Pandas to Spark or Dask for distributed processing
2. Store raw data in Parquet instead of CSV (columnar, compressed, cloud-optimized)
3. Use Azure Data Lake for scalable storage (petabyte-scale)
4. Build scheduled ETL pipeline using Azure Data Factory (orchestration, monitoring, error handling)
5. Introduce incremental processing instead of full recomputation

**How I relate this to my experience:**
* **The scaling problem:**
  * SQL Server → Snowflake migration driven by this exact issue
  * On-premise systems exhausted by volume (reports/extracts wouldn't run, no longer fit for purpose)
  * Cloud storage/compute: reporting times from >1 day → minutes
* **Performance testing:**
  * 100% cell-to-cell comparison of original vs migrated reports
  * Some too large for Pandas → switched to Polars
  * Recently ran performance evaluation: Pandas vs Polars vs PySpark across data volumes
  * Included `artifacts/replicate_performance_analysis.png` to showcase results
* **Root causes identified:**
  * **Infrastructure:** 20-year-old systems couldn't scale with data growth
  * **Code patterns:** 
    * Single large operations (locks source tables, can't resume on failure, hard to debug) vs modular pipeline stages with intermediate checkpoints (easier to monitor, retry failed steps, optimize bottlenecks)
    * SQL Server had multiple derivations of similar processes (different teams, inconsistent logic) → Snowflake consolidated into reusable, shared, consistent code modules (same centralization principle as data storage)
  * **Solution:** Infrastructure scaling + code optimization/re-engineering + schema design

<sub>*(Databricks Genie (Claude) sources for scaling best practices: [Azure Architecture - Big data architectures](https://learn.microsoft.com/en-us/azure/architecture/data-guide/big-data/), [Databricks - When to use Apache Spark](https://docs.databricks.com/en/getting-started/spark/index.html), [Azure - Batch processing patterns](https://learn.microsoft.com/en-us/azure/architecture/data-guide/big-data/batch-processing))*</sub>

<sub>*(Microsoft Copilot validation: The scaling recommendations — Spark/Dask, Parquet, Data Lake Storage, ADF orchestration, and incremental processing — are fully aligned with Azure's big‑data architecture guidance. Cross‑checked against Azure Big Data Solutions: https://learn.microsoft.com/en-us/azure/architecture/data-guide/big-data/, Databricks "When to use Spark": https://docs.databricks.com/en/getting-started/spark/index.html, and Azure batch processing patterns: https://learn.microsoft.com/en-us/azure/architecture/data-guide/big-data/batch-processing. All consistent.)*</sub>

---

## 6. What metrics would you track in production, and what could go wrong?

**Metrics to track:**
* **Prediction latency** *(aligns with: CDC source data transfer latency monitoring)*
* **Prediction volume** *(aligns with: row count comparison from source to migrated data)*
* Input feature drift
* **Output drift** *(aligns with: cell-to-cell comparison of source vs target data)*
* Model confidence distribution
* Error rates

**What could go wrong:**
* Data drift causing degraded model performance
* Unexpected input formats breaking the API
* Model becoming biased due to changing customer behavior
* Latency spikes under load
* Silent failures if monitoring is not in place

<sub>*(Databricks Genie (Claude) sources: [MLOps best practices](https://learn.microsoft.com/en-us/azure/machine-learning/concept-model-management-and-deployment), [Model monitoring documentation](https://learn.microsoft.com/en-us/azure/machine-learning/how-to-monitor-models))*</sub>

<sub>*(Microsoft Copilot validation: The monitoring metrics (latency, volume, drift, confidence, error rates) and failure modes (drift, schema issues, bias, latency spikes, silent failures) match Microsoft's MLOps and model‑monitoring best practices. Cross‑checked against Azure ML model monitoring documentation: https://learn.microsoft.com/en-us/azure/microsoft-learning/how-to-monitor-models and model management guidance: https://learn.microsoft.com/en-us/azure/machine-learning/concept-model-management-and-deployment. No issues identified.)*</sub>

---

## 7. Use of AI tools (ChatGPT, Claude, Copilot, etc.)

**I collaborated with AI tools (Databricks Genie/Microsoft Copilot) extensively throughout this entire project.**

**Which AI tools and how they work:**
* **Databricks Genie:** Powered by Claude (Anthropic's AI assistant)
* **Microsoft Copilot:** Powered by OpenAI's GPT models
* Both draw from verified training data and documentation sources
* Used two AI tools to verify each other

**Important note on data security:**
* In real production scenarios: would never use actual source data with external AI tools
* Would create dummy datasets replicating format and volume
* Exception: company-approved internal AI model where data doesn't leave company network

**Important note on AI-generated information:**
To progress this project, I had to assume the AI-provided information was correct to the best of my ability. In a real-world scenario, I would validate all domain-specific recommendations with subject matter experts and formal business documentation before implementation.

**This exercise was genuinely challenging:**
* **The financial domain:** credit risk, banking APIs, Open Banking = completely unfamiliar
* **The bigger picture:** how API and data pipeline connect in real-world systems
* **Real-world workflow:** where customer data comes from, batch vs real-time processing
* **What the assignment was asking for:** mapping task requirements to my SQL-centric background

**AI collaboration helped me:**
* Break down the problem
* Understand the codebase
* Learn financial terminology
* Make sense of the assignment itself

Without that support, I would not have been able to complete this project. I'm documenting this transparently because I believe intellectual honesty matters.

---

# Part 1: Data Preparation

```bash
python data_prep/prepare_data_gillian.py
```

**This script:**
* Loads `transactions.csv` and `labels.csv` from `data/`
* Cleans and normalizes transaction descriptions
* Aggregates transactions by customer
* Extracts keyword features (rent, netflix, tesco, payroll, bonus)
* Merges with customer labels
* Outputs `artifacts/training_set.csv`

**Output observed:**
The script successfully completed and generated `artifacts/training_set.csv`. I opened the file to verify the output — columns, data types, and sample values matched expectations for an ML-ready training dataset.

---

# Part 2: API Development

**Schema modification:**
I updated `app.py` to align the API input schema with what the pre-trained model expects. 

**Original schema:**
```python
txn_count: float
total_debit: float
total_credit: float
avg_amount: float
kw_rent: int = 0
kw_netflix: int = 0
kw_tesco: int = 0
kw_payroll: int = 0
kw_bonus: int = 0
```

**Updated schema:**
```python
customer_id: str
num_transactions: float
total_debit: float
total_credit: float
avg_amount: float
has_rent: int = 0
has_salary: int = 0
```

This change ensured the API could successfully pass the correct feature set to the model and produce valid predictions.

---

**API testing:**

I tested the API via the Swagger UI at `/docs`.

**Test 1 — Health check:**
Confirmed the API is running and responsive.

**Test 2 — Prediction:**
I sent a test prediction request using the spec's example format:
```json
{
  "customer_id": "CUST001",
  "num_transactions": 15,
  "total_debit": -1250.50,
  "total_credit": 3500.00,
  "avg_amount": 150.03,
  "has_rent": 1,
  "has_salary": 1
}
```

The API returned:
```json
{
  "customer_id": "CUST001",
  "probability": 8.792916352049832e-11,
  "prediction": 0
}
```

This confirmed the model loads correctly, accepts the expected input schema, and returns valid predictions.

**Learning note:**
Coming from a Flask background where I manually validated inputs and built custom response formats, FastAPI was initially confusing. When the Swagger UI page appeared at `/docs`, I didn't immediately recognize this was the expected outcome — not an error. I learned FastAPI automatically generates interactive API documentation from your code, and Pydantic handles validation declaratively (you define the schema once, FastAPI validates automatically). In Flask, I would have written manual validation logic and custom documentation. This "it just works" experience felt foreign at first, but is a key FastAPI feature that matters for rapid API development.

**Proof of completion:**
See `artifacts/proof_of_prediction.png` and `artifacts/proof_data_entry.png` for screenshots showing successful execution.

---

# Part 3: Project Structure

## What Was Received

Extracted from `snr-data-eng-task.zip` → `take-home-task/` folder:

```
take-home-task/
├── api/
│   └── app.py              # FastAPI application
├── data/
│   ├── transactions.csv    # Raw transaction data
│   └── labels.csv          # Customer default labels
├── data_prep/
│   └── prepare_data.py     # Data preparation script (original)
├── artifacts/
│   └── model.joblib        # Pre-trained model (provided)
```

---

## What's Being Returned

Modified structure being committed to Git:

```
take-home-task/
├── api/
│   ├── app.py              # FastAPI application (modified to align schema with model expectations)
│   └── app_original.py     # NEW: Backup of original app.py
├── data/
│   ├── transactions.csv    # Raw transaction data (unchanged)
│   └── labels.csv          # Customer default labels (unchanged)
├── data_prep/
│   ├── prepare_data.py     # Original script (unchanged)
│   └── prepare_data_gillian.py    # NEW: My implementation
├── artifacts/
│   ├── model.joblib        # Pre-trained model (provided, unchanged)
│   ├── training_set.csv    # NEW: Generated training dataset (as requested)
│   ├── eda_transactions_per_customer.png    # NEW: EDA visualization (as requested)
│   ├── eda_common_words.png                 # NEW: EDA visualization (as requested)
│   ├── eda_amount_distribution.png          # NEW: EDA visualization (as requested)
│   ├── replicate_performance_analysis.png   # NEW: My performance evaluation (Pandas vs Polars vs PySpark)
│   ├── proof_data_entry.png                 # NEW: Screenshot proving Part 1 completion
│   └── proof_of_prediction.png              # NEW: Screenshot proving Part 2 completion
├── requirements.txt        # NEW: Python dependencies
└── README.md               # NEW: This documentation
```

**Key additions:**
* `prepare_data_gillian.py` — My data preparation implementation
* `training_set.csv` — Generated ML-ready dataset
* 3 EDA visualizations (as requested in the task)
* 1 performance analysis visualization (showcasing my migration work experience)
* 2 proof-of-completion screenshots (demonstrating successful execution)
* `app_original.py` — Backup of original app.py for reference
* `requirements.txt` — Python package dependencies
* `README.md` — Complete project documentation

**Key modifications:**
* `app.py` — Updated input schema to match model feature expectations

---

# About My Approach

*(Additional context about my learning process. Essential information is in sections above.)*

## My Background

* **Domain:** SQL-centric data engineering in health/clinical trial data
* **Code split:** Pipelines ~90% SQL, Python/R for ETL orchestration, post-merge transformations, testing, QA, release, and ongoing monitoring
* **Complexity:** 100s of tables, complex joins with derivation order dependencies
* **Web apps:** Built on average ~2 RShiny/Flask apps per year (more during migration). Created proactive monitoring and quality frameworks that technical leads valued, though not widely adopted by wider team. Personally enjoyed this work and would have preferred more focus in this direction.
* **Career goal:** Transitioning to Python as primary tool, seeking new challenging technical domains

**What's new in this task:**
* Financial domain (credit risk, Open Banking)
* FastAPI web framework
* Azure deployment & cloud cost optimization
* ML production infrastructure

---

## Learning Strategy: Domain Translation

**Financial domain knowledge was entirely new.** Mapped financial concepts to health domain equivalents:

| Financial Concept | Health Domain Equivalent | Why This Mapping Worked |
|-------------------|-------------------------|------------------------|
| **Target:** Customer defaulted (0/1) | **Target:** Patient readmitted (0/1) | Binary outcome prediction |
| **Transaction descriptions** ("TESCO", "RENT") | **Diagnosis codes** (ICD-10) | Text categorization |
| **Keyword extraction** ("SALARY", "GAMBLING") | **Comorbidity flags** (diabetes=1, hypertension=1) | Binary features from text |
| **Debit/Credit ratio** | **Symptom severity score** | Numeric risk indicator |
| **Transaction frequency** | **Hospital visit frequency** | Behavioral metric |
| **Customer aggregation** | **Patient aggregation** | One row per entity |

**Key insight:**
Data engineering patterns are domain-agnostic. Once I mapped financial → health, the entire task clicked. Feature engineering, risk prediction, data quality checks, and aggregation patterns work the same way across domains.

---

# Future Improvements

***(AI-generated suggestions that align with production best practices)***

* Retrain the model using extended features
* Add model versioning and explicit feature schemas
* Add monitoring for prediction drift and data drift
* Add authentication and rate limiting to the API
* Containerize the service for production deployment

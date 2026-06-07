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
* My background: SQL-heavy workflow (weeks in SQL, then Python/R in final phases)

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


**How I relate this to my experience**

* **Cloud migration work**
  * Led a full SQL Server → Snowflake migration on Azure, where the major performance gain came from the architecture shift (elastic compute, cheap storage, separation of workloads).  
  * Adopted a pre‑compute and store pattern for heavy transformations — same principle as pre‑computing features for existing customers.  
  * Re‑engineered stored procedures, functions and schemas for efficiency; architecture and SQL optimisation complement each other, especially in cloud environments.  
  * This aligns with cloud‑native patterns and pre‑compute strategies.

* **Latency monitoring**
  * Built Python/Flask tools to monitor CDC latency and surface bottlenecks.  
  * Captured runtime metrics and hard examples for third‑party debugging.  
  * Latency in this domain was hours/days, not sub‑100ms, but the discipline of measure → monitor → optimise transfers directly.  
  * Relevant to latency monitoring in production ML systems.

* **Outside my role**
  * API hosting, autoscaling, and model‑serving infrastructure were handled by DevOps/SRE.

* **Direct alignment**
  * Batch/real‑time separation → mirrors scheduled jobs + tabular storage patterns I’ve implemented.  
  * Incremental loading → core migration pattern: load only new data, handle late‑arriving records, and avoid full‑history recomputation.  
  * Matches incremental ingestion used for cloud cost control.


<sub>*(Databricks Genie (Claude) sources for production ML deployment: [Azure ML - Batch vs real-time scoring](https://learn.microsoft.com/en-us/azure/machine-learning/concept-endpoints-batch), [Azure ML cost optimization](https://learn.microsoft.com/en-us/azure/machine-learning/how-to-manage-optimize-cost), [Azure ML deployment guide](https://learn.microsoft.com/en-us/azure/machine-learning/how-to-deploy-online-endpoints)*</sub>

<sub>*(Microsoft Copilot validation: The batch vs real‑time separation, incremental loading, and cost‑optimisation recommendations are correct. Cross‑checked against Azure ML's batch vs online endpoints: https://learn.microsoft.com/en-us/azure/machine-learning/concept-endpoints-batch, Azure ML cost optimization: https://learn.microsoft.com/en-us/azure/machine-learning/how-to-manage-optimize-cost, and deployment guidance: https://learn.microsoft.com/en-us/azure/machine-learning/how-to-deploy-online-endpoints. All sources align with the answer.)*</sub>

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
  * Git-controlled releases published (deployed) from central location via Posit Connect server (similar to Power BI/Databricks Dashboards publish feature)
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

1. **Replace Pandas with distributed processing:**
   * Move to Spark or Dask to handle millions of transactions
   * Enables parallel processing across multiple nodes
   
2. **Switch from CSV to Parquet:**
   * Columnar format = faster reads for aggregations
   * Built-in compression reduces storage costs
   
3. **Implement incremental processing:**
   * Load only new transactions (not full history each run)
   * Recompute rolling window features using new + existing data
   * Critical for cost control at scale

4. **Add orchestration layer:**
   * Use Azure Data Factory or similar for scheduling, monitoring, error handling
   * Provides observability and retry logic

**How I relate this to my experience:**
* Led SQL Server → Snowflake migration driven by volume scaling issues
  * Cloud storage/compute: improved reporting times from >1 day → minutes
* The test release process originally built in Pandas couldn't scale for larger extracts without batch processing - evaluated switch from Pandas and Polars for more streamlined single process testing
  * Conducted performance testing: [Pandas](https://pandas.pydata.org/) vs [Polars](https://pola.rs/) vs [PySpark](https://spark.apache.org/docs/latest/api/python/) across data volumes
  * See `artifacts/replicate_performance_analysis.png` for performance comparison results
* Re-engineered pipelines from monolithic operations to modular stages with checkpoints

<sub>*(Databricks Genie (Claude) sources for scaling best practices: [Azure Architecture - Big data architectures](https://learn.microsoft.com/en-us/azure/architecture/data-guide/big-data/), [Databricks - When to use Apache Spark](https://docs.databricks.com/en/getting-started/spark/index.html), [Azure - Batch processing patterns](https://learn.microsoft.com/en-us/azure/architecture/data-guide/big-data/batch-processing))*</sub>

<sub>*(Microsoft Copilot validation: The scaling recommendations — Spark/Dask, Parquet, Data Lake Storage, ADF orchestration, and incremental processing — are fully aligned with Azure's big‑data architecture guidance. Cross‑checked against Azure Big Data Solutions: https://learn.microsoft.com/en-us/azure/architecture/data-guide/big-data/, Databricks "When to use Spark": https://docs.databricks.com/en/getting-started/spark/index.html, and Azure batch processing patterns: https://learn.microsoft.com/en-us/azure/architecture/data-guide/big-data/batch-processing. All consistent.)*</sub>

---

## 6. What metrics would you track in production, and what could go wrong?

**Suggested metrics to track:**
* Prediction latency
* Prediction volume
* Input feature drift
* Output drift
* Model confidence distribution
* Error rates

**Suggested what could go wrong:**
* Data drift causing degraded model performance
* Unexpected input formats breaking the API
* Model becoming biased due to changing customer behavior
* Latency spikes under load
* Silent failures if monitoring is not in place

**How I relate this to my experience:**

I've built lightweight production monitoring tools addressing these concepts for data pipelines and migrations. Demos below use dummy data and were built with RShiny/Flask.

---

#### [Performance Monitor (2022–2023)](https://gillianpaterson.shinyapps.io/stored_proc_debugger/)

  * Investigated a SQL stored procedure believed to be the sole cause of intermittent contention and delays.  
  * Added lightweight in‑procedure logging (no access to SQL diagnostics) to capture stage‑level execution times.  
  * Identified optimisation opportunities to keep the web process within its strict five‑minute SLA.  
  * Showed that delays had multiple contributors, not just the stored procedure — including external jobs and study‑specific setups.  
  * Used an RShiny tool to present clear, data‑driven evidence, shifting discussions from assumptions to facts and improving root‑cause focus.  
  * Aligns with SQL performance tuning and evidence‑based debugging practices.

---

#### [Data Integrity Monitor (2024)](https://gillianpaterson.shinyapps.io/dashboard_monitor/)

  * Supported release testing during the SQL Server → Snowflake migration.  
  * Ran 100% cell‑level comparisons (4M rows, 90+ columns) to confirm extract outputs matched pre‑migration results.  
  * Detected edge‑case issues early, surfacing anomalies that would have reached users without automated validation.  
  * Measured CDC latency, providing evidence that performance was below expectations.  
  * Strengthened data quality by replacing manual spot‑checks with automated controls, reducing the risk of silent drift.  
  * Aligns with data validation and automated QA practices used in production pipelines.

---

<sub>*(Databricks Genie (Claude) sources: [MLOps best practices](https://learn.microsoft.com/en-us/azure/machine-learning/concept-model-management-and-deployment), [Azure ML monitoring overview](https://learn.microsoft.com/en-us/azure/machine-learning/monitor-azure-machine-learning)*</sub>

<sub>*(Microsoft Copilot validation: The monitoring metrics (latency, volume, drift, confidence, error rates) and failure modes (drift, schema issues, bias, latency spikes, silent failures) match Microsoft's MLOps and model‑monitoring best practices. Cross‑checked against Azure ML model monitoring documentation: https://learn.microsoft.com/en-us/azure/machine-learning/how-to-monitor-model-performance (learn.microsoft.com in Bing) and model management guidance: https://learn.microsoft.com/en-us/azure/machine-learning/concept-model-management-and-deployment. No issues identified.)*</sub>

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
* For this project: assumed AI information was correct to best of my ability
* Real-world scenario: would validate domain-specific recommendations with subject matter experts and formal business documentation before implementation

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

**AI impact:**
* Pre-AI methods possible (web searches, documentation, tutorials, trial-and-error) but more laborious
* Engineering effort shifted: development → validation
* Result: faster process, higher quality, less time
* Documented transparently — intellectual honesty matters

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

See `artifacts/proof_of_prediction.png` and `artifacts/proof_data_entry.png` for screenshots showing successful execution.

**Learning note — Flask vs FastAPI:**  
* When FastAPI showed the Swagger UI at `/docs`, it wasn’t immediately obvious to me that this was intentional, not an error. 
* Learned that FastAPI auto‑generates documentation and Pydantic provides automatic input validation from a single schema.  
* Realisation: I don’t need to manually build these pieces — FastAPI handles them by design, which is a big shift for rapid API development.


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
credit-risk-assessment/
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
* Added debugging print statements to `prepare_data_gillian.py` and `app.py`

---

# About My Approach

*(Additional context about my learning process. Essential information is in sections above.)*

## My Background

* **Domain:** SQL-centric data engineering in health/clinical trial data
* **Code split:** Pipelines ~90% SQL, Python/R for ETL orchestration, post-merge transformations, testing, QA, release, and ongoing monitoring
* **Complexity:** 100s of tables, complex joins with derivation order dependencies
* **Web apps:** Built on average ~2 RShiny/Flask apps per year (more during migration). Created proactive monitoring and quality frameworks that technical leads valued, though not widely adopted by wider team. Personally enjoyed this work and would have preferred more focus in this direction.
* **Career goal:** Expanding Python skills alongside SQL expertise, seeking new challenges and a change of scenery in different technical domains

**What's new in this task:**
* Financial domain (credit risk, Open Banking)
* FastAPI web framework
* Azure deployment & cloud cost optimization
* ML production infrastructure

---

## Learning Strategy: Domain Translation

**Financial domain knowledge was entirely new.** Mapped financial concepts to health domain equivalents:

<small>

| Financial Concept | Health Domain Equivalent | Why This Mapping Worked |
|-------------------|-------------------------|--------------------------|
| Target: Customer defaulted (0/1) | Target: Patient readmitted (0/1) | Binary outcome prediction |
| Transaction descriptions ("TESCO", "RENT") | Diagnosis codes (ICD-10) | Text categorization |
| Keyword extraction ("SALARY", "GAMBLING") | Comorbidity flags (diabetes=1, hypertension=1) | Binary features from text |
| Debit/Credit ratio | Symptom severity score | Numeric risk indicator |
| Transaction frequency | Hospital visit frequency | Behavioral metric |
| Customer aggregation | Patient aggregation | One row per entity |

</small>


**Key insight:**
* Data engineering patterns could be considered domain-agnostic
* Once I mapped financial → health, the entire task clicked
* The concepts behind feature engineering, risk prediction, data quality checks, and aggregation patterns could be applied in very similar ways across domains (as demonstrated in the mapping table above)

---

# Future Improvements

***(AI-generated suggestions that align with production best practices)***

* Retrain the model using extended features
* Add model versioning and explicit feature schemas
* Add monitoring for prediction drift and data drift *(similar to drift detection in my Data Integrity Monitor — see Question 6)*
* Add authentication and rate limiting to the API
* Containerize the service for production deployment

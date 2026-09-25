# BILLING ASSURANCE & REVENUE PROTECTION CONTROL TOWER

## Master Project Blueprint / Copilot Context

You are working inside an existing portfolio/interview project called:

**Billing Assurance & Revenue Protection Control Tower**

The project simulates a real-world Billing Operations / Revenue Assurance environment.

The core business story is:

> **Data → Controls → Exceptions → Financial Impact → Decisions → SLA → Operational Reporting → Executive Dashboard**

The project is designed to demonstrate both technical and business capabilities relevant to roles involving:

* Billing operations
* Revenue assurance
* Data analysis
* Billing validation
* Pre-bill controls
* Discount approval
* Customer information reporting
* Exception management
* SLA monitoring
* Audit trails
* Operational reporting
* Excel
* Power BI
* SQL
* Python
* Continuous improvement

---

# 1. PROJECT OBJECTIVE

Build a production-style analytical control tower that can answer:

1. Are customer billing records accurate?
2. Which billing records have exceptions?
3. What type of control detected each exception?
4. What is the potential financial impact?
5. Which customers are affected?
6. Which discount requests should be automatically approved, reviewed, or declined according to the defined business rules?
7. Are approval decisions being completed within SLA?
8. Which exceptions require operational action?
9. Which controls create the largest operational/financial exposure?
10. Can management see all of this through Excel and Power BI?
11. Can every control execution be audited and reproduced?

This is an analytical/control project, not a high-concurrency transactional billing system.

---

# 2. TECHNOLOGY STACK

Current stack:

* Python
* Pandas
* DuckDB
* SQL
* Excel
* Power BI
* VS Code
* Git/GitHub

DuckDB was deliberately selected instead of PostgreSQL because this project is primarily an analytical/control/reporting workload.

Benefits:

* No database server required
* Excellent analytical SQL
* Easy Python integration
* Works well with CSV data
* Reproducible locally
* Suitable for portfolio demonstration
* Easy Power BI/Excel consumption

---

# 3. CURRENT ARCHITECTURE

The intended architecture is:

```text
Raw / Processed Data
        ↓
Python Data Processing
        ↓
DuckDB Analytical Warehouse
        ↓
Business Controls
        ↓
Exception Queue
        ↓
KPI / Operational Views
        ↓
Audit Trail
        ↓
Excel Control Workbook
        ↓
Power BI Control Tower
        ↓
Executive / Operational Decisions
```

Do NOT bypass the control/data layers just to create dashboards.

The dashboard must be the final presentation layer, not the source of business logic.

---

# 4. DATA FOUNDATION

The project began with a Kaggle Telco-style customer dataset.

Important customer/billing fields include:

* customerID
* gender
* SeniorCitizen
* Partner
* Dependents
* tenure
* PhoneService
* MultipleLines
* InternetService
* OnlineSecurity
* OnlineBackup
* DeviceProtection
* TechSupport
* StreamingTV
* StreamingMovies
* Contract
* PaperlessBilling
* PaymentMethod
* MonthlyCharges
* TotalCharges
* Churn

Additional engineered fields include:

* record_id
* is_new_unbilled
* churn_flag
* contract_months
* tenure_band

The project includes synthetic error injection so that the control system can be objectively evaluated.

---

# 5. PHASE 1 — DATA FOUNDATION

COMPLETED.

Work included:

* Project environment
* VS Code setup
* Dataset preparation
* Cleaning
* Audit logging
* Synthetic error injection
* Reproducible processing

The purpose was to create a controlled dataset where known billing errors could be introduced and later detected.

---

# 6. PHASE 2 — BILLING VALIDATION ENGINE

COMPLETED.

The validation engine implemented billing controls including:

### C001-type logic

Duplicate billing detection.

### Missing/zero billing logic

Detection of:

* Missing TotalCharges
* Zero TotalCharges
* Zero MonthlyCharges

### Total variance validation

Expected billing relationship was compared against actual billing.

### Rate-card validation

Expected monthly charge was compared with observed pricing.

### Financial exposure

Potential exposure was calculated for detected billing anomalies.

### Severity

Exceptions were categorized by severity.

### Rule traceability

The engine stores:

* primary_rule
* rules_fired
* exposure
* severity

---

# 7. MODEL / CONTROL VALIDATION

The billing detection engine was evaluated using:

* Precision
* Recall
* Specificity
* F1
* Holdout validation
* Error-type detection
* Threshold calibration

Important finding:

The original total variance threshold generated too many false positives.

Approximately:

* 85 of 96 false positives came from total_variance.

Threshold was adjusted.

Recommended operating point:

```text
k_total = 10
k_rate  = 4
```

Result:

```text
230 flagged
208 real
22 false alarms

Precision ≈ 90.4%
Recall    ≈ 98.6%
```

Important caveat:

The synthetic data/error-generation process means these metrics should not be presented as real-world production performance.

Also:

* R² around 0.9967 reflects the synthetic additive pricing structure.
* Exposure around $625k from the earlier validation stage should not automatically be described as actual lost revenue.
* Some detected price differences can represent legitimate pricing/discount changes.

---

# 8. PHASE 3 — DISCOUNT APPROVAL WORKFLOW

COMPLETED.

Purpose:

Simulate a real business question:

> "Should Billing Operations approve this customer's requested discount, and what is the financial trade-off?"

Approximately 500 synthetic discount requests were generated using the existing customer population.

Important fields include:

* request_id
* customer_id
* request_date
* requested_discount_pct
* reason
* current_monthly_charge
* contract_type
* tenure
* customer_value
* expected_remaining_months
* discount_cost
* retention_probability
* estimated_retention_value
* net_economic_impact
* benefit_cost_ratio
* value_tier
* decision
* approval_level
* SLA fields

---

# 9. CUSTOMER ECONOMICS

Business assumptions:

```text
Estimated Customer Value
=
Monthly Charge × Expected Remaining Months
```

Discount cost:

```text
Discount Cost
=
Monthly Charge × Discount % × Decision Horizon
```

Expected retention value is based on estimated retention uplift.

Decision economics compare:

```text
Expected Retention Value
vs
Discount Cost
```

Phase 3.2 result:

```text
Total discount cost       $53,425
Total estimated retention $70,252
Net economic impact       $16,827
Positive-net requests     271 / 500
```

Value tiers:

```text
Standard   250
High       150
Strategic  100
```

---

# 10. DISCOUNT DECISION ENGINE

COMPLETED.

Decision categories:

```text
AUTO_APPROVE
MANAGER_REVIEW
DECLINE
```

Results:

```text
MANAGER_REVIEW   246   49.2%
DECLINE          133   26.6%
AUTO_APPROVE     121   24.2%
```

Rules:

```text
R1_AUTO_APPROVE           121
R2_STRATEGIC_ESCALATION    33
R3_DECLINE_UNECONOMIC     133
R4_REVIEW_OVER_LIMIT       55
R5_REVIEW_MARGINAL        158
```

Financial view:

```text
AUTO_APPROVE
Cost       $9,099
Retention $19,616
Net       $10,517

DECLINE
Cost       $11,037
Retention  $2,734
Net       -$8,303

MANAGER_REVIEW
Cost       $33,289
Retention $47,901
Net       $14,613
```

Sensitivity testing was also performed using retention multipliers:

```text
0.8x
1.0x
1.2x
```

This demonstrates that decision policies should be tested against uncertainty rather than treated as absolute truth.

---

# 11. SLA ANALYSIS

COMPLETED.

Results:

```text
500 requests

SLA compliance = 93.8%
SLA breaches   = 31
At risk        = 23

Average turnaround all requests ≈ 3.82 h
Average review turnaround      ≈ 7.70 h
```

By approval level:

```text
Manager
55 cases
Target 16h
Average 8.81h
4 breaches
92.7% compliance

Senior Manager
33 cases
Target 24h
Average 18.89h
9 breaches
72.7% compliance

Supervisor
158 cases
Target 8h
Average 4.97h
18 breaches
88.6% compliance

System
254 cases
Target 1h
Average 0.06h
0 breaches
100% compliance
```

Monthly SLA analysis was also completed.

Phase 4 KPI view currently reports:

```text
500 requests
446 met
23 at risk
31 breached
89.20% SLA compliance
3.82h average turnaround
7.70h average review turnaround
127.96 breach hours
```

---

# 12. PHASE 4 — DUCKDB WAREHOUSE

COMPLETED.

Database:

```text
data/warehouse/billing_assurance.duckdb
```

Schemas:

```text
staging
core
controls
```

Metadata table:

```text
core.warehouse_metadata
```

---

# 13. STAGING DATA

The following processed datasets are loaded into DuckDB:

```text
customers_clean
billing_test_set
validation_results
holdout_validation_results
discount_requests
discount_requests_enriched
discount_decisions
discount_decisions_sla
```

All were loaded into the staging layer.

There is also:

```text
core.staging_load_audit
```

which tracks staging loads.

---

# 14. BUSINESS CONTROL MATRIX

COMPLETED.

Table:

```text
controls.business_control_matrix
```

Current controls:

```text
C001 Duplicate Billing
Type: Detective
Owner: Billing Operations
Severity: High
Status: Active

C002 Missing Billing Total
Type: Detective
Owner: Billing Operations
Severity: High
Status: Active

C003 Rate Mismatch
Type: Detective
Owner: Billing Operations
Severity: High
Status: Active

C004 Discount Approval
Type: Preventive
Owner: Operations Manager
Severity: High
Status: Active

C005 SLA Monitoring
Type: Detective
Owner: Operations
Severity: Medium
Status: Active
```

There are currently 5 controls.

---

# 15. SQL CONTROL ENGINE

COMPLETED.

Script:

```text
src/16_control_engine.py
```

Control outputs:

```text
controls.c001_duplicate_billing
controls.c002_missing_billing_total
controls.c003_rate_mismatch
controls.c004_discount_approval
controls.c005_sla_monitoring
```

Unified queue:

```text
controls.exception_queue
```

Current control results:

```text
C001 Duplicate Billing       84
C002 Missing Billing Total  95
C003 Rate Mismatch           94
C004 Discount Approval      379
C005 SLA Monitoring          54
```

Total:

```text
706 control hits
```

Financial impact:

```text
$83,085.84
```

Status:

```text
OPEN       550
REVIEWED   133
MONITOR     23
```

Severity:

```text
HIGH       601
MEDIUM      58
LOW         47
```

IMPORTANT:

706 control hits are NOT 706 unique customers.

Current enterprise-level unique customer count:

```text
558
```

Some customers can trigger multiple controls.

---

# 16. PHASE 4.5 — KPI & EXCEPTION VIEWS

COMPLETED.

Script:

```text
src/17_kpi_views.py
```

Views:

```text
controls.v_executive_kpis
controls.v_exception_queue
controls.v_control_performance
controls.v_sla_kpis
controls.v_customer_risk
```

Executive KPIs:

```text
Control hits              706
Unique exceptions         706
Unique customers          558
Financial impact          $83,085.84
Open exceptions           550
High severity             601
Medium severity            58
Low severity               47
```

Control performance:

```text
C003 Rate Mismatch
94 hits
$45,485.02

C004 Discount Approval
379 hits
$29,320.91

C001 Duplicate Billing
84 hits
$4,586.10

C002 Missing Billing Total
95 hits
$3,565.85

C005 SLA Monitoring
54 hits
$127.96
```

Customer risk summary:

```text
HIGH
89 customers
182 control hits
$28,591.58

MEDIUM
54 customers
109 control hits
$20,176.00

LOW
415 customers
415 control hits
$34,318.26
```

IMPORTANT:

The current `unique_exceptions` field equals control hits because each control hit receives an exception_id.

Do not falsely claim that these are deduplicated business cases.

---

# 17. PHASE 4.6 — AUDIT TRAIL & OPERATIONAL REPORTING

COMPLETED.

Script:

```text
src/18_audit_operational_reporting.py
```

Audit table:

```text
core.control_execution_audit
```

It records:

* audit_id
* run_timestamp
* control_id
* control_name
* control_type
* execution_status
* exception_count
* unique_customers
* financial_impact
* notes

Current run:

```text
5 controls executed
5 successful
0 failed
706 control hits
$83,085.84 financial impact
```

Operational views:

```text
controls.v_operational_run_summary
controls.v_control_audit_history
controls.v_operational_report
```

The operational report currently combines:

* customer impact
* exceptions
* financial impact
* open exceptions
* severity
* active controls
* control hits
* discount requests
* SLA performance
* turnaround metrics
* report timestamp

---

# 18. CURRENT PROJECT STATUS

COMPLETED:

```text
Phase 1 — Data Foundation                 ✅
Phase 2 — Billing Validation Engine       ✅
Phase 3 — Discount Decision Workflow      ✅
Phase 4.1 — DuckDB Setup                  ✅
Phase 4.2 — Data Loading                  ✅
Phase 4.3 — Business Control Matrix       ✅
Phase 4.4 — SQL Control Engine            ✅
Phase 4.5 — KPI & Exception Views         ✅
Phase 4.6 — Audit & Operational Reporting ✅
```

Git commits/pushes have been performed throughout the project.

---

# 19. CURRENT FILE STRUCTURE

Important existing scripts include:

```text
src/
    10_customer_economics.py
    11_decision_engine.py
    12_sla_analysis.py
    13_duckdb_setup.py
    14_load_duckdb.py
    15_business_control_matrix.py
    16_control_engine.py
    17_kpi_views.py
    18_audit_operational_reporting.py
```

Do NOT rewrite or replace these scripts unless a specific bug or improvement is identified.

---

# 20. CURRENT DUCKDB STRUCTURE

Conceptually:

```text
billing_assurance.duckdb

├── staging
│   ├── customers_clean
│   ├── billing_test_set
│   ├── validation_results
│   ├── holdout_validation_results
│   ├── discount_requests
│   ├── discount_requests_enriched
│   ├── discount_decisions
│   └── discount_decisions_sla
│
├── core
│   ├── warehouse_metadata
│   ├── staging_load_audit
│   └── control_execution_audit
│
└── controls
    ├── business_control_matrix
    ├── c001_duplicate_billing
    ├── c002_missing_billing_total
    ├── c003_rate_mismatch
    ├── c004_discount_approval
    ├── c005_sla_monitoring
    ├── exception_queue
    ├── v_executive_kpis
    ├── v_exception_queue
    ├── v_control_performance
    ├── v_sla_kpis
    ├── v_customer_risk
    ├── v_operational_run_summary
    ├── v_control_audit_history
    └── v_operational_report
```

---

# 21. NEXT PHASE — EXCEL CONTROL WORKBOOK

CURRENTLY STARTING.

The Excel workbook should be:

```text
reports/Billing_Assurance_Control_Tower.xlsx
```

The workbook should contain at least:

```text
Executive Summary
Exception Queue
Discount Approvals
SLA Monitoring
Control Summary
Audit Trail
```

The Excel workbook is a reporting/operational interface.

DuckDB remains the source of truth.

---

# 22. EXCEL — EXECUTIVE SUMMARY

The Executive Summary should show:

### Financial KPIs

* Financial impact
* Exception count
* Unique customers
* High severity exceptions

### Operational KPIs

* Open exceptions
* SLA compliance
* SLA breaches
* At-risk SLA cases
* Average turnaround

### Control KPIs

* Active controls
* Control hits
* Exceptions by control

### Customer risk

* High-risk customers
* Medium-risk customers
* Low-risk customers

Use professional formatting.

Do not fabricate additional KPIs.

---

# 23. EXCEL — EXCEPTION QUEUE

This should be an operational work queue.

Columns should include:

* exception_id
* control_id
* control_name
* exception_type
* customer_id
* request_id
* record_id
* severity
* status
* financial_impact
* exception_date
* description

Requirements:

* Filters
* Frozen header
* Excel table
* Currency formatting
* Severity formatting
* Status formatting
* Sort high severity/high financial impact first

The purpose is:

> "What needs attention?"

---

# 24. EXCEL — DISCOUNT APPROVALS

Use the discount decision/SLA data.

Include:

* request_id
* customer_id
* request_date
* requested_discount_pct
* reason
* current_monthly_charge
* customer_value
* discount_cost
* estimated_retention_value
* net_economic_impact
* benefit_cost_ratio
* value_tier
* decision_rule
* decision
* approval_level
* decision_reason
* SLA target
* turnaround
* SLA status
* breach hours

Purpose:

> "Which discount requests require action and why?"

---

# 25. EXCEL — SLA MONITORING

Show:

* request_id
* customer_id
* approval_level
* SLA target
* turnaround
* SLA status
* breach hours
* request month

Prioritize:

```text
Breached
At Risk
Met
```

Purpose:

> "Where are operational SLA problems occurring?"

---

# 26. EXCEL — CONTROL SUMMARY

Show:

* Control ID
* Control name
* Control type
* Control hits
* Unique customers
* Financial impact
* Open
* Reviewed
* Monitor
* High severity

Purpose:

> "Which controls are generating the most operational/financial activity?"

---

# 27. EXCEL — AUDIT TRAIL

Show:

* audit_id
* run_timestamp
* control_id
* control_name
* control_type
* execution_status
* exception_count
* unique_customers
* financial_impact
* notes

Purpose:

> "Can we prove what controls ran and what they found?"

---

# 28. AFTER EXCEL — POWER BI

Phase 6 should build the Power BI Control Tower.

Expected pages:

```text
1. Executive Control Tower
2. Billing Integrity
3. Exception Management
4. Discount Decision Simulator
5. SLA & Operations
6. Customer / Risk Drill-through
```

---

# 29. POWER BI — EXECUTIVE CONTROL TOWER

Expected KPIs:

```text
Financial Exposure
Open Exceptions
Unique Customers
High Severity
SLA Compliance
SLA Breaches
Discount Requests
```

Visuals:

* Financial impact by control
* Exceptions by severity
* Customer risk distribution
* SLA performance
* Operational workload

Management questions:

> What is happening?

> Where is the exposure?

> What requires attention?

---

# 30. POWER BI — BILLING INTEGRITY

Show:

* Duplicate billing
* Missing billing
* Rate mismatch
* Exposure
* Severity
* Customer impact
* Trend if meaningful

Allow drill-through to individual exception records.

---

# 31. POWER BI — EXCEPTION MANAGEMENT

Show:

* Exception queue
* Status
* Severity
* Control
* Financial impact
* Customer
* Aging if available

Purpose:

> Help operations prioritize work.

---

# 32. POWER BI — DISCOUNT DECISION SIMULATOR

Show:

* Requested discount
* Customer value
* Discount cost
* Retention value
* Net economic impact
* Benefit/cost ratio
* Value tier
* Decision
* Approval level

Potential scenario analysis:

```text
Retention assumption
Discount level
Customer value
```

Any scenario calculations must clearly distinguish assumptions from actual historical data.

---

# 33. POWER BI — SLA & OPERATIONS

Show:

* SLA compliance
* Breaches
* At risk
* Average turnaround
* Review turnaround
* Approval level
* Monthly trends
* Workload vs SLA

---

# 34. POWER BI — CUSTOMER/RISK DRILL-THROUGH

Show:

* Customer ID
* Controls triggered
* Number of exceptions
* Financial impact
* Severity
* Open exceptions
* Discount requests
* SLA information where applicable

The purpose is to move from:

```text
Management KPI
      ↓
Control
      ↓
Customer
      ↓
Exception
```

---

# 35. PHASE 7 — EXECUTIVE LAYER

After Power BI:

Create:

```text
Management Brief
Control Matrix
Methodology
Assumptions
Data Dictionary
Architecture Diagram
```

The management brief should explain:

1. What was detected
2. Financial exposure
3. Operational workload
4. SLA performance
5. Key control areas
6. Decision workflow
7. Recommended process improvements
8. Important limitations

Do not exaggerate synthetic results as real company losses.

---

# 36. PHASE 8 — PORTFOLIO / INTERVIEW POLISH

Final deliverables:

```text
README.md
Architecture diagram
Screenshots
Excel workbook
Power BI screenshots
Control matrix
Data dictionary
Methodology
Business assumptions
GitHub structure
Interview talking points
```

The project should tell one coherent story:

```text
I started with customer/billing data.
        ↓
I introduced controlled billing exceptions.
        ↓
I built validation controls.
        ↓
I measured detection performance.
        ↓
I built a discount economics workflow.
        ↓
I created approval rules.
        ↓
I measured SLA performance.
        ↓
I moved the outputs into DuckDB.
        ↓
I created SQL controls and exception queues.
        ↓
I created KPI and operational views.
        ↓
I added an audit trail.
        ↓
I am now turning it into Excel and Power BI
for operational and executive decision support.
```

---

# 37. IMPORTANT DEVELOPMENT RULES

When continuing this project:

### Rule 1

Do not rebuild completed phases.

### Rule 2

Do not replace DuckDB with PostgreSQL unless explicitly requested.

### Rule 3

Do not move business logic into Power BI if it already belongs in Python/SQL.

### Rule 4

Do not create fake metrics just to make the dashboard look impressive.

### Rule 5

Clearly distinguish:

```text
Control Hits
Unique Exceptions
Unique Customers
Financial Impact
```

They are not automatically the same thing.

### Rule 6

Clearly distinguish:

```text
Synthetic data
Model assumptions
Actual observed results
```

### Rule 7

Financial "impact" or "exposure" should not automatically be called actual revenue loss.

### Rule 8

Use existing DuckDB views wherever possible.

### Rule 9

Every major phase should be validated before moving forward.

### Rule 10

After meaningful completed phases, commit and push to Git.

---

# 38. CURRENT NEXT ACTION

The immediate task is:

```text
Create the Excel Control Workbook
```

Starting with:

```text
src/19_create_excel_workbook.py
```

Output:

```text
reports/Billing_Assurance_Control_Tower.xlsx
```

Start by creating the workbook foundation and loading the existing DuckDB views/data.

Do not redesign the underlying business logic.

Do not recreate controls that already exist.

Use the existing DuckDB control layer as the source of truth.

After the workbook is generated, validate the contents before adding advanced formatting/features.

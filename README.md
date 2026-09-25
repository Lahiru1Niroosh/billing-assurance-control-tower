# Billing Assurance & Revenue Protection Control Tower

An end-to-end **billing assurance, revenue protection, discount governance, SLA monitoring, exception management, and customer exposure analytics platform** built with Python, DuckDB, Streamlit, Plotly, and Excel automation.

The project demonstrates how raw customer and billing data can be transformed into operational controls, financial exposure analysis, decision workflows, and management reporting.

> **Data → Controls → Exceptions → Financial Impact → Decisions → SLA → Customer Risk → Management Action**

---

## Project Overview

Billing operations can generate thousands of customer and transaction records, making manual identification of billing errors, pricing anomalies, discount risks, and SLA failures difficult.

This project builds an analytical control framework that can:

- detect duplicate billing
- identify missing or zero billing values
- detect rate mismatches
- quantify financial exposure
- govern customer discount requests
- evaluate discount economics
- monitor operational SLAs
- create a centralized exception queue
- identify customer-level control exposure
- maintain control execution audit history
- generate operational Excel reports
- provide an interactive management control tower

The solution is designed as a **portfolio-scale simulation of a billing operations and revenue assurance environment** using project-generated and synthetic data.

---

## Solution Architecture

```text
Raw / Project Data
        │
        ▼
Data Preparation & Quality
        │
        ▼
Billing Validation Engine
        │
        ▼
┌──────────────────────────────┐
│       DuckDB Warehouse       │
│                              │
│  staging │ core │ controls   │
└──────────────┬───────────────┘
               │
       ┌───────┼────────┐
       ▼       ▼        ▼
    Billing  Discount   SLA
    Controls  Controls  Controls
       │       │        │
       └───────┼────────┘
               ▼
        Exception Queue
               │
       ┌───────┼──────────┐
       ▼       ▼          ▼
 Executive   Customer    Audit
   KPIs       Risk      History
       │       │          │
       └───────┼──────────┘
               ▼
      ┌─────────────────┐
      │ Reporting Layer │
      ├─────────────────┤
      │ Streamlit       │
      │ Excel           │
      └─────────────────┘
```

---

## Technology Stack

| Area | Technology |
|---|---|
| Programming | Python |
| Data Processing | Pandas |
| Database | DuckDB |
| Querying | SQL |
| Dashboard | Streamlit |
| Visualization | Plotly |
| Excel Automation | OpenPyXL |
| Development | VS Code |
| Version Control | Git / GitHub |

---

## Business Control Framework

The project implements five operational controls.

| Control | Description | Type | Owner |
|---|---|---|---|
| **C001** | Duplicate Billing | Detective | Billing Operations |
| **C002** | Missing Billing Total | Detective | Billing Operations |
| **C003** | Rate Mismatch | Detective | Billing Operations |
| **C004** | Discount Approval | Preventive | Operations Manager |
| **C005** | SLA Monitoring | Detective | Operations |

These controls feed a centralized exception-management layer used by the reporting and dashboard components.

---

## Billing Validation Engine

The billing validation engine evaluates customer billing records for anomalies including:

- duplicate customer records
- missing billing totals
- zero monthly charges
- abnormal total-charge variance
- rate mismatches

Validation outputs include:

```text
flag_duplicate_id
flag_total_missing
flag_zero_monthly
flag_total_variance
flag_rate_mismatch
expected_monthly
rate_residual
exposure
severity
primary_rule
rules_fired
```

### Threshold Calibration

The initial validation configuration produced excessive false positives from the total-variance rule.

Testing showed that **85 of 96 false positives** were associated with this rule.

The operating threshold was therefore adjusted from:

```text
k_total = 6
```

to:

```text
k_total = 10
```

with:

```text
k_rate = 4
```

### Validation Results

| Metric | Result |
|---|---:|
| Flagged Cases | 230 |
| True Cases | 208 |
| False Alarms | 22 |
| Precision | **90.4%** |
| Recall | **98.6%** |

These results are based on the project's synthetic validation environment and should not be interpreted as production model performance.

---

## Revenue Protection & Financial Exposure

The control framework quantifies financial value associated with exceptions.

| Control | Control Hits | Unique Customers | Financial Impact |
|---|---:|---:|---:|
| C001 — Duplicate Billing | 84 | 42 | $4,586.10 |
| C002 — Missing Billing Total | 95 | 95 | $3,565.85 |
| C003 — Rate Mismatch | 94 | 94 | $45,485.02 |
| C004 — Discount Approval | 379 | 379 | $29,320.91 |
| C005 — SLA Monitoring | 54 | 54 | $127.96 |

### Enterprise Control Tower

```text
Control Hits          706
Unique Customers      558
Financial Impact      $83,085.84
Open Exceptions       550
High Severity         601
Medium Severity       58
Low Severity          47
```

> **Important:** Financial impact represents exposure or value under review. It does not represent confirmed revenue loss.

---

## Discount Decision Governance

The project includes a simulated discount-governance workflow for **500 customer discount requests**.

The decision model evaluates:

```text
Customer Value
      ↓
Estimated Retention Uplift
      ↓
Expected Retention Value
      ↓
Compare with Discount Cost
      ↓
Economic Decision
```

### Core Calculations

**Customer Value**

```text
Monthly Charge × Expected Remaining Months
```

**Discount Cost**

```text
Monthly Charge × Discount % × Decision Horizon
```

**Expected Retention Value**

```text
Customer Value × Estimated Retention Uplift
```

### Decision Results

| Decision | Requests |
|---|---:|
| Auto Approve | 121 |
| Manager Review | 246 |
| Decline | 133 |
| **Total** | **500** |

### Economic Results

```text
Total Discount Cost            $53,425
Estimated Retention Value      $70,252
Net Economic Impact            $16,827
```

The decision framework uses five rules:

```text
R1_AUTO_APPROVE
R2_STRATEGIC_ESCALATION
R3_DECLINE_UNECONOMIC
R4_REVIEW_OVER_LIMIT
R5_REVIEW_MARGINAL
```

Customer value tiers are:

```text
Standard
High
Strategic
```

---

## SLA Operations

Discount requests are monitored against operational SLA targets.

### SLA KPIs

| Metric | Result |
|---|---:|
| Total Requests | 500 |
| SLA Met | 446 |
| At Risk | 23 |
| Breached | 31 |
| SLA Compliance | **89.2%** |
| Average Turnaround | 3.82 hours |
| Average Review Turnaround | 7.70 hours |
| Total Breach Hours | 127.96 |

### Approval-Level Performance

| Approval Level | Target | Avg Turnaround | Breaches | Compliance |
|---|---:|---:|---:|---:|
| System | 1h | 0.06h | 0 | 100.0% |
| Supervisor | 8h | 4.97h | 18 | 88.6% |
| Manager | 16h | 8.81h | 4 | 92.7% |
| Senior Manager | 24h | 18.89h | 9 | 72.7% |

SLA exceptions feed directly into control **C005**.

---

## Exception Management

All control outputs are consolidated into:

```text
controls.exception_queue
```

and exposed through:

```text
controls.v_exception_queue
```

The operational queue supports analysis by:

- control
- severity
- status
- customer
- financial impact

Current operational status:

```text
Total Control Hits     706
Open                   550
Reviewed               133
Monitor                 23
```

A control hit represents a control-generated exception record.

Therefore:

> **Control Hits ≠ Unique Customers**

and the current exception count should not be interpreted as a fully deduplicated business-case count.

---

## Customer Risk & Exposure

The customer-risk layer aggregates control activity at customer level.

| Risk Band | Customers | Control Hits | Financial Impact |
|---|---:|---:|---:|
| High | 89 | 182 | $28,591.58 |
| Medium | 54 | 109 | $20,176.00 |
| Low | 415 | 415 | $34,318.26 |

The risk classification represents **observed operational control exposure**.

It is not intended to represent a credit score, fraud score, churn probability, or formal customer risk rating.

---

## DuckDB Analytical Warehouse

DuckDB acts as the project's **analytical source of truth**.

Three logical schemas are used:

```text
staging
core
controls
```

### Staging

Contains source and processed analytical datasets.

Examples:

```text
staging.customers_clean
staging.billing_test_set
staging.validation_results
staging.holdout_validation_results
staging.discount_requests
staging.discount_requests_enriched
staging.discount_decisions
staging.discount_decisions_sla
```

### Core

Contains metadata and audit information.

```text
core.warehouse_metadata
core.staging_load_audit
core.control_execution_audit
```

### Controls

Contains business controls, exceptions and reporting views.

```text
controls.c001_duplicate_billing
controls.c002_missing_billing_total
controls.c003_rate_mismatch
controls.c004_discount_approval
controls.c005_sla_monitoring

controls.exception_queue

controls.v_executive_kpis
controls.v_exception_queue
controls.v_control_performance
controls.v_sla_kpis
controls.v_customer_risk
controls.v_operational_report
controls.v_control_audit_history
```

---

## Streamlit Control Tower

The project includes a multi-page Streamlit application.

### 01 — Executive Control Tower

Management-level visibility into:

- control activity
- financial exposure
- exception severity
- SLA performance
- control performance

### 02 — Billing Integrity

Operational analysis of:

- duplicate billing
- missing billing
- rate mismatches
- billing exposure
- control-specific exceptions

### 03 — Exception Management

Operational workspace for:

- filtering exceptions
- prioritization
- financial-impact analysis
- customer investigation
- control-specific investigation guidance

### 04 — Discount Decision Command Center

Provides:

- discount decision distribution
- customer economics
- benefit/cost analysis
- approval-level analysis
- decision investigation

### 05 — SLA Operations

Provides:

- SLA compliance
- turnaround performance
- approval-level performance
- monthly trends
- workload analysis
- SLA exception investigation

### 06 — Customer Risk

Provides:

- customer risk distribution
- customer exposure
- control concentration
- financial impact
- customer investigation

---

## Dashboard UX

The application uses a dark operational **control-tower interface** with:

- glassmorphism components
- animated hero sections
- KPI cards
- Plotly charts
- operational status badges
- responsive layouts
- investigation filters
- management interpretation panels

Detailed content is organized into tabs to keep each dashboard compact and operationally focused.

---

## Excel Operational Reporting

The project automatically generates:

```text
reports/Billing_Assurance_Control_Tower.xlsx
```

with six worksheets:

1. Executive Summary
2. Exception Queue
3. Discount Approvals
4. SLA Monitoring
5. Control Summary
6. Audit Trail

The workbook includes:

- KPI summaries
- filters
- freeze panes
- currency formatting
- severity highlighting
- decision highlighting
- SLA highlighting
- management-friendly layouts

The generated workbook is intentionally excluded from Git because it is a reproducible output.

---

## Auditability

Control execution is recorded in:

```text
core.control_execution_audit
```

Audit information includes:

```text
run_timestamp
control_id
control_name
control_type
execution_status
exception_count
unique_customers
financial_impact
notes
```

A validated operational run produced:

```text
Controls Executed      5
Successful             5
Failed                 0
Control Hits           706
Financial Impact       $83,085.84
```

---

## Project Structure

```text
billing-assurance-control-tower/
│
├── app/
│   ├── app.py
│   ├── pages/
│   │   ├── 1_Executive_Control_Tower.py
│   │   ├── 2_Billing_Integrity.py
│   │   ├── 3_Exception_Management.py
│   │   ├── 4_Discount_Decisions.py
│   │   ├── 5_SLA_Operations.py
│   │   └── 6_Customer_Risk.py
│   └── utils/
│       └── database.py
│
├── src/
│   ├── 01_profile_raw.py
│   ├── 02_clean.py
│   ├── 03_inject_errors.py
│   ├── 04_validate.py
│   ├── 05_evaluate.py
│   ├── 06_threshold_sweep.py
│   ├── 07_holdout_validation.py
│   ├── 08_overbilling_curve.py
│   ├── 09_generate_discount_requests.py
│   ├── 10_customer_economics.py
│   ├── 11_decision_engine.py
│   ├── 12_sla_analysis.py
│   ├── 13_duckdb_setup.py
│   ├── 14_load_duckdb.py
│   ├── 15_business_control_matrix.py
│   ├── 16_control_engine.py
│   ├── 17_kpi_views.py
│   ├── 18_audit_operational_reporting.py
│   ├── 19_create_excel_workbook.py
│   ├── 20_enhance_excel_workbook.py
│   ├── 21_validate_excel_workbook.py
│   ├── config.py
│   └── rules.py
│
├── reports/
│   ├── cleaning_audit_log.csv
│   ├── evaluation_by_type.csv
│   ├── exception_queue.csv
│   ├── holdout_detection_by_type.csv
│   ├── holdout_summary.csv
│   ├── overbilling_difficulty_curve.csv
│   ├── raw_profile_blank_totalcharges.csv
│   └── threshold_sweep.csv
│
├── PROJECT_BLUEPRINT.md
├── README.md
├── requirements.txt
└── .gitignore
```

---

## Installation

Clone the repository:

```bash
git clone https://github.com/Lahiru1Niroosh/billing-assurance-control-tower.git
cd billing-assurance-control-tower
```

Create a virtual environment:

### Windows

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

---

## Rebuilding the Analytical Pipeline

The project is designed as a sequential pipeline.

The main execution flow is:

```text
01–08   Data preparation and billing validation
09–12   Discount governance and SLA analysis
13–18   DuckDB warehouse, controls and operational reporting
19–21   Excel workbook generation and validation
```

The scripts should be executed from the project root in numerical order when rebuilding the complete analytical environment.

---

## Running the Streamlit Application

After the DuckDB warehouse has been generated:

```powershell
streamlit run app/app.py
```

The application reads from:

```text
data/warehouse/billing_assurance.duckdb
```

using a read-only DuckDB connection.

---

## Important Assumptions & Limitations

This is a portfolio analytics project built using project-generated and synthetic scenarios.

Important considerations:

- billing errors are synthetically injected
- discount requests are simulated
- retention uplift is modeled
- customer value is estimated
- financial exposure is not confirmed revenue loss
- validation performance may be optimistic in a synthetic environment
- customers can trigger multiple controls
- control hits are not equivalent to enterprise unique customers
- exception records are not necessarily deduplicated business cases
- SLA breaches identify timing exceptions but do not establish root cause
- customer risk bands represent operational control exposure, not formal credit, fraud or churn risk

A production implementation would require validation using real historical billing and operational data.

---

## Design Principles

The project follows several core principles:

**Single Source of Truth**  
DuckDB is the analytical source of truth.

**Control-Driven Analytics**  
Dashboard metrics trace back to defined operational controls.

**Explainability**  
Control and decision logic is intentionally transparent.

**Auditability**  
Control execution and operational results are traceable.

**Separation of Concerns**  
Data preparation, controls, database, reporting and presentation are separated.

**Operational Focus**  
The dashboards are designed to support investigation and management action rather than simply display charts.

---

## Detailed Technical Blueprint

For a deeper explanation of the architecture, control framework, calculations, validation approach, implementation phases, assumptions and design decisions, see:

**`PROJECT_BLUEPRINT.md`**

---

## Future Improvements

Potential production extensions include:

- automated billing-system ingestion
- scheduled pipeline execution
- production database integration
- exception ownership and assignment
- workflow actions
- approval-system integration
- role-based access control
- email and operational alerts
- historical trend monitoring
- automated threshold monitoring
- anomaly detection
- model monitoring
- data-quality monitoring
- cloud deployment
- CI/CD
- automated tests

---

## What This Project Demonstrates

This project demonstrates practical experience across:

**Python • Pandas • SQL • DuckDB • Streamlit • Plotly • OpenPyXL • Data Quality • Billing Controls • Revenue Assurance • Exception Management • Financial Analysis • Discount Governance • SLA Monitoring • Customer Exposure • Auditability • Operational Reporting**

Most importantly, it demonstrates an end-to-end business analytics workflow:

> **Raw Data → Data Quality → Billing Controls → Exception Management → Financial Exposure → Discount Governance → SLA Monitoring → Customer Risk → Management Reporting**

---

## Disclaimer

This project is intended for portfolio, learning and demonstration purposes.

The data, operational scenarios, retention assumptions, financial exposure calculations and decision rules should not be interpreted as results from a live telecommunications billing environment.
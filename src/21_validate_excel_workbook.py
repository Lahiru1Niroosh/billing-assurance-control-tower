from pathlib import Path
from openpyxl import load_workbook


# ============================================================
# PHASE 5.3 — FINAL EXCEL WORKBOOK VALIDATION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]
WORKBOOK_PATH = PROJECT_ROOT / "reports" / "Billing_Assurance_Control_Tower.xlsx"

EXPECTED_SHEETS = [
    "Executive Summary",
    "Exception Queue",
    "Discount Approvals",
    "SLA Monitoring",
    "Control Summary",
    "Audit Trail",
]

EXPECTED_COUNTS = {
    "Exception Queue": 695,
    "Discount Approvals": 500,
    "SLA Monitoring": 500,
    "Control Summary": 5,
}


print("=" * 70)
print("PHASE 5.3 — FINAL EXCEL WORKBOOK VALIDATION")
print("=" * 70)
print()

# ------------------------------------------------------------
# File check
# ------------------------------------------------------------

if not WORKBOOK_PATH.exists():
    raise FileNotFoundError(f"Workbook not found: {WORKBOOK_PATH}")

print("FILE CHECK")
print(f"  ✓ Workbook exists")
print(f"  ✓ File: {WORKBOOK_PATH}")
print(f"  ✓ Size: {WORKBOOK_PATH.stat().st_size:,} bytes")
print()

# ------------------------------------------------------------
# Open workbook
# ------------------------------------------------------------

wb = load_workbook(WORKBOOK_PATH, data_only=False)

# ------------------------------------------------------------
# Sheet validation
# ------------------------------------------------------------

print("SHEET VALIDATION")

actual_sheets = wb.sheetnames

for sheet in EXPECTED_SHEETS:
    if sheet not in actual_sheets:
        raise ValueError(f"Missing sheet: {sheet}")

    print(f"  ✓ {sheet}")

if len(actual_sheets) != len(EXPECTED_SHEETS):
    raise ValueError(
        f"Unexpected sheet count. "
        f"Expected {len(EXPECTED_SHEETS)}, found {len(actual_sheets)}"
    )

print()

# ------------------------------------------------------------
# Row count validation
# ------------------------------------------------------------

print("DATA COUNT VALIDATION")

for sheet_name, expected_count in EXPECTED_COUNTS.items():

    ws = wb[sheet_name]

    # One row is the header
    actual_count = ws.max_row - 1

    if actual_count != expected_count:
        raise ValueError(
            f"{sheet_name}: expected {expected_count}, "
            f"found {actual_count}"
        )

    print(
        f"  ✓ {sheet_name:<22} "
        f"{actual_count:,} rows"
    )

audit_row_count = wb["Audit Trail"].max_row - 1

if audit_row_count < 1:
    raise ValueError("Audit Trail: expected at least 1 row, found 0")

print(f"  ✓ {'Audit Trail':<22} {audit_row_count:,} rows")

print()

# ------------------------------------------------------------
# Executive Summary validation
# ------------------------------------------------------------

print("EXECUTIVE SUMMARY VALIDATION")

ws = wb["Executive Summary"]

required_cells = [
    "B4",
    "B5",
    "B6",
    "B7",
    "B8",
    "B9",
    "B10",
    "B11",
]

for cell in required_cells:

    if ws[cell].value is None:
        raise ValueError(
            f"Executive Summary KPI cell is empty: {cell}"
        )

    print(
        f"  ✓ {cell}: {ws[cell].value}"
    )

if ws["A12"].value != "C001 Duplicate Records Involved" or ws["B12"].value != 84:
    raise ValueError("Executive Summary C001 duplicate-record metric is incorrect")

if ws["A13"].value != "C001 Duplicate Customer Cases" or ws["B13"].value != 42:
    raise ValueError("Executive Summary C001 duplicate-case metric is incorrect")

print("  ✓ C001: 84 duplicate records involved across 42 duplicate customer cases")
print()

# ------------------------------------------------------------
# Control summary validation
# ------------------------------------------------------------

print("CONTROL SUMMARY VALIDATION")

ws = wb["Control Summary"]
headers = {cell.value: cell.column for cell in ws[1]}
required_control_columns = {
    "control_id",
    "control_hits",
    "duplicate_records_involved",
    "duplicate_customer_cases",
    "affected_customers",
}
missing_columns = required_control_columns - headers.keys()

if missing_columns:
    raise ValueError(f"Control Summary is missing columns: {sorted(missing_columns)}")

rows = {
    ws.cell(row=row, column=headers["control_id"]).value: row
    for row in range(2, ws.max_row + 1)
}

c001_row = rows["C001"]
c002_row = rows["C002"]

if ws.cell(c001_row, headers["duplicate_records_involved"]).value != 84:
    raise ValueError("Control Summary C001 duplicate records involved must be 84")
if ws.cell(c001_row, headers["duplicate_customer_cases"]).value != 42:
    raise ValueError("Control Summary C001 duplicate customer cases must be 42")
if ws.cell(c001_row, headers["affected_customers"]).value != 42:
    raise ValueError("Control Summary C001 affected customers must be 42")
if ws.cell(c002_row, headers["control_hits"]).value != 84:
    raise ValueError("Control Summary C002 exception records must be 84")

print("  ✓ C001: 84 records involved, 42 cases, 42 affected customers")
print("  ✓ C002: 84 validated exception records")
print()

# ------------------------------------------------------------
# Formatting validation
# ------------------------------------------------------------

print("FORMATTING VALIDATION")

checks = {
    "Exception Queue": "A1",
    "Discount Approvals": "A1",
    "SLA Monitoring": "A1",
    "Control Summary": "A1",
    "Audit Trail": "A1",
}

for sheet_name, cell_ref in checks.items():

    ws = wb[sheet_name]
    cell = ws[cell_ref]

    if cell.fill.fill_type != "solid":
        raise ValueError(
            f"{sheet_name} header formatting missing"
        )

    if not cell.font.bold:
        raise ValueError(
            f"{sheet_name} header bold formatting missing"
        )

    print(
        f"  ✓ {sheet_name}: header formatting"
    )

print()

# ------------------------------------------------------------
# Freeze pane validation
# ------------------------------------------------------------

print("FREEZE PANE VALIDATION")

for sheet_name in EXPECTED_SHEETS[1:]:
    ws = wb[sheet_name]

    if ws.freeze_panes != "A2":
        raise ValueError(
            f"{sheet_name}: freeze pane expected A2, "
            f"found {ws.freeze_panes}"
        )

    print(
        f"  ✓ {sheet_name}: A2"
    )

print()

# ------------------------------------------------------------
# Final result
# ------------------------------------------------------------

print("=" * 70)
print("PHASE 5.3 COMPLETED SUCCESSFULLY")
print("=" * 70)
print()
print("EXCEL CONTROL WORKBOOK STATUS")
print("  ✓ Workbook exists")
print("  ✓ 6 required sheets")
print(f"  ✓ {EXPECTED_COUNTS['Exception Queue']:,} exception records")
print("  ✓ 500 discount approval records")
print("  ✓ 500 SLA records")
print("  ✓ 5 control summary records")
print(f"  ✓ {audit_row_count:,} audit records")
print("  ✓ Executive KPI section populated")
print("  ✓ Management formatting validated")
print("  ✓ Freeze panes validated")
print()
print("PHASE 5 — EXCEL CONTROL WORKBOOK COMPLETE")
print("=" * 70)
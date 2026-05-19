import sqlite3
from pathlib import Path
from typing import Any

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import DB_PATH


def get_connection() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    base = Path(__file__).parent
    conn = get_connection()
    cursor = conn.cursor()
    cursor.executescript((base / "schema.sql").read_text())
    # Use INSERT OR IGNORE so re-runs are safe on an existing DB
    cursor.executescript((base / "seed_data.sql").read_text())
    conn.commit()
    conn.close()


def run_query(sql: str) -> tuple[list[dict], str | None]:
    """Execute a SQL query. Returns (rows, error). rows is [] on error."""
    try:
        conn = get_connection()
        cursor = conn.execute(sql)
        rows = [dict(r) for r in cursor.fetchall()]
        conn.close()
        return rows, None
    except Exception as e:
        return [], str(e)


# ── Per-table schema chunks ──────────────────────────────────────────────────
# Each entry is the authoritative description for one table.
# get_schema_str() concatenates these; schema_store.py embeds them individually.

_TABLE_CHUNKS: dict[str, str] = {
    "adjusters": (
        "adjusters(adjuster_id PK, name, region, department)\n"
        "  region: 'Northeast'|'Southeast'|'Midwest'|'West'\n"
        "  department: 'Auto'|'Property'|'Health'|'Liability'\n"
        "  Stores insurance claims adjusters and their regional/department assignments."
    ),
    "policies": (
        "policies(policy_id PK, holder_name, domain, policy_type, effective_date DATE, expiry_date DATE, premium REAL, status)\n"
        "  domain: 'Insurance'|'Banking'|'Public Sector'\n"
        "  policy_type: 'Auto'|'Property'|'Health'|'Liability'\n"
        "  status: 'Active'|'Expired'|'Cancelled'|'Pending'\n"
        "  Master policy records: who is covered, what type, dates, and premium amount."
    ),
    "claims": (
        "claims(claim_id PK, policy_id FK→policies, adjuster_id FK→adjusters, "
        "filed_date DATE, resolved_date DATE nullable, amount REAL, status, risk_level)\n"
        "  status: 'Open'|'Approved'|'Denied'|'Under Review'\n"
        "  risk_level: 'Low'|'Medium'|'High'\n"
        "  Core claims table: every insurance claim filed, its amount, status, and risk level."
    ),
    "claimants": (
        "claimants(claimant_id PK, claim_id FK→claims, full_name, contact_email, state)\n"
        "  state: 2-letter US state code\n"
        "  Individuals who filed claims; one claimant per claim."
    ),
    "fraud_flags": (
        "fraud_flags(flag_id PK, claim_id FK→claims, flag_type, flagged_at DATE, resolved INTEGER 0/1, savings REAL)\n"
        "  flag_type: 'Duplicate'|'Inflated Amount'|'Staged Incident'|'Identity Mismatch'\n"
        "  resolved: 0=open, 1=resolved; savings: estimated fraud savings in USD\n"
        "  Heuristic fraud signals raised against claims; tracks resolution and savings."
    ),
    "coverage_types": (
        "coverage_types(coverage_type_id PK, name, category, description)\n"
        "  category: 'Vehicle'|'Property'|'Health'|'Liability'\n"
        "  name examples: 'Collision'|'Comprehensive'|'Bodily Injury Liability'|'Building Coverage'\n"
        "  Reference table of available insurance coverage types."
    ),
    "loss_types": (
        "loss_types(loss_type_id PK, name, category)\n"
        "  category: 'Vehicle'|'Property'|'Health'|'Liability'|'Fraud'\n"
        "  name examples: 'Vehicle Collision'|'Fire Damage'|'Water Damage'|'Theft'|'Medical Injury'\n"
        "  Reference table classifying the nature of insured losses."
    ),
    "customers": (
        "customers(customer_id PK, full_name, state, credit_score INTEGER, customer_since DATE, preferred_contact)\n"
        "  preferred_contact: 'Email'|'Phone'|'Mail'\n"
        "  Policyholders and insurance customers; credit score and tenure data."
    ),
    "agents": (
        "agents(agent_id PK, full_name, license_number UNIQUE, region, hire_date DATE, commission_rate REAL)\n"
        "  Insurance sales agents who sell and service policies.\n"
        "  commission_rate: decimal fraction e.g., 0.06 = 6%"
    ),
    "underwriters": (
        "underwriters(underwriter_id PK, full_name, certification, specialization, active INTEGER)\n"
        "  certification: 'CPCU'|'ARe'|'CUW'\n"
        "  specialization: 'Auto'|'Property'|'Commercial'|'Health'\n"
        "  active: 1=active, 0=inactive\n"
        "  Staff who evaluate and approve insurance policy risk."
    ),
    "policy_coverages": (
        "policy_coverages(coverage_id PK, policy_id FK→policies, coverage_type_id FK→coverage_types, "
        "coverage_limit REAL, deductible REAL)\n"
        "  Junction table mapping which coverage types are included in each policy, with limits and deductibles."
    ),
    "policy_endorsements": (
        "policy_endorsements(endorsement_id PK, policy_id FK→policies, endorsement_type, "
        "effective_date DATE, premium_change REAL, description)\n"
        "  endorsement_type: 'Umbrella'|'Flood Rider'|'Earthquake'|'GAP'|'Business Interruption'\n"
        "  Riders and add-ons attached to base policies; tracks premium impact."
    ),
    "premium_payments": (
        "premium_payments(payment_id PK, policy_id FK→policies, due_date DATE, paid_date DATE nullable, "
        "amount REAL, payment_method, status)\n"
        "  payment_method: 'Credit Card'|'ACH'|'Check'|'Wire'\n"
        "  status: 'Paid'|'Overdue'|'Pending'|'Waived'\n"
        "  Tracks premium billing and payment history per policy."
    ),
    "insured_properties": (
        "insured_properties(property_id PK, policy_id FK→policies, property_type, address_state, "
        "year_built INTEGER, estimated_value REAL, occupancy_type)\n"
        "  property_type: 'Residential'|'Commercial'|'Industrial'\n"
        "  occupancy_type: 'Owner-Occupied'|'Rental'|'Vacant'\n"
        "  Physical properties covered under property insurance policies."
    ),
    "insured_vehicles": (
        "insured_vehicles(vehicle_id PK, policy_id FK→policies, make, model, year INTEGER, vin UNIQUE, estimated_value REAL)\n"
        "  Vehicles covered under auto insurance policies: make, model, year, VIN, and estimated value."
    ),
    "risk_assessments": (
        "risk_assessments(assessment_id PK, policy_id FK→policies, underwriter_id FK→underwriters, "
        "assessed_date DATE, risk_score REAL 0-10, risk_category, notes)\n"
        "  risk_category: 'Low'|'Medium'|'High'|'Very High'\n"
        "  Underwriting risk evaluations for policies; higher score = higher risk."
    ),
    "inspection_reports": (
        "inspection_reports(report_id PK, policy_id FK→policies, inspection_date DATE, inspector_name, "
        "condition_rating, issues_found INTEGER, passed INTEGER)\n"
        "  condition_rating: 'Excellent'|'Good'|'Fair'|'Poor'\n"
        "  passed: 1=passed, 0=failed\n"
        "  Physical inspection results for insured properties and vehicles."
    ),
    "claim_documents": (
        "claim_documents(document_id PK, claim_id FK→claims, document_type, uploaded_at DATE, verified INTEGER)\n"
        "  document_type: 'Police Report'|'Medical Record'|'Photo'|'Estimate'|'Affidavit'\n"
        "  verified: 1=verified, 0=unverified\n"
        "  Supporting documents and evidence attached to claims."
    ),
    "claim_assessments": (
        "claim_assessments(assessment_id PK, claim_id FK→claims, adjuster_id FK→adjusters, "
        "assessment_date DATE, estimated_loss REAL, recommended_payout REAL, notes)\n"
        "  Adjuster loss evaluations: what they estimated and what payout they recommended per claim."
    ),
    "claim_payments": (
        "claim_payments(payment_id PK, claim_id FK→claims, payment_date DATE, amount REAL, payment_method, status)\n"
        "  payment_method: 'Check'|'ACH'|'Wire'\n"
        "  status: 'Pending'|'Issued'|'Cleared'|'Cancelled'\n"
        "  Actual payment disbursements made to claimants for approved claims."
    ),
    "claim_appeals": (
        "claim_appeals(appeal_id PK, claim_id FK→claims, filed_date DATE, reason, decision, resolved_date DATE nullable)\n"
        "  decision: 'Upheld'|'Overturned'|'Partial'|NULL if still pending\n"
        "  Appeals filed by claimants contesting claim decisions."
    ),
    "repair_vendors": (
        "repair_vendors(vendor_id PK, name, specialty, region, avg_rating REAL, approved INTEGER)\n"
        "  specialty: 'Auto Body'|'Plumbing'|'Electrical'|'Roofing'|'General'\n"
        "  approved: 1=on approved list, 0=suspended\n"
        "  Repair and restoration vendors authorized to work on insured claims."
    ),
    "repair_estimates": (
        "repair_estimates(estimate_id PK, claim_id FK→claims, vendor_id FK→repair_vendors, "
        "submitted_date DATE, estimated_amount REAL, approved INTEGER, approved_amount REAL nullable)\n"
        "  Vendor repair cost estimates submitted for claim approval; tracks whether estimate was accepted."
    ),
    "investigators": (
        "investigators(investigator_id PK, name, specialization, region, active INTEGER)\n"
        "  specialization: 'Auto Fraud'|'Property Fraud'|'Medical Fraud'|'Identity Theft'\n"
        "  Special Investigations Unit (SIU) staff who investigate suspected fraud."
    ),
    "fraud_investigations": (
        "fraud_investigations(investigation_id PK, claim_id FK→claims, investigator_id FK→investigators, "
        "opened_date DATE, closed_date DATE nullable, outcome, confirmed_fraud INTEGER, savings REAL)\n"
        "  outcome: 'Confirmed Fraud'|'No Fraud Found'|'Inconclusive'|NULL if open\n"
        "  confirmed_fraud: 1=yes, 0=no; savings: dollar amount recovered\n"
        "  Formal SIU investigations into suspicious claims."
    ),
    "reserve_estimates": (
        "reserve_estimates(reserve_id PK, claim_id FK→claims, estimated_at DATE, "
        "reserve_amount REAL, reserve_type, last_updated DATE)\n"
        "  reserve_type: 'Case Reserve'|'IBNR'|'Bulk'\n"
        "  Actuarial loss reserve calculations for open and IBNR claims."
    ),
    "regulatory_filings": (
        "regulatory_filings(filing_id PK, state, filing_date DATE, filing_type, status, due_date DATE nullable, notes)\n"
        "  filing_type: 'Rate Filing'|'Form Filing'|'Financial Statement'|'Market Conduct'\n"
        "  status: 'Submitted'|'Approved'|'Rejected'|'Pending'\n"
        "  State insurance department regulatory submissions and their approval status."
    ),
    "compliance_audits": (
        "compliance_audits(audit_id PK, audit_date DATE, auditor_name, scope, findings INTEGER, result)\n"
        "  scope: 'Claims Processing'|'Underwriting'|'Agent Conduct'|'Data Privacy'\n"
        "  result: 'Satisfactory'|'Needs Improvement'|'Unsatisfactory'\n"
        "  Internal compliance reviews; findings count and overall result."
    ),
    "agent_performance": (
        "agent_performance(perf_id PK, agent_id FK→agents, period, policies_sold INTEGER, "
        "renewals INTEGER, total_premium REAL, commission_earned REAL)\n"
        "  period: quarterly string e.g., '2024-Q1'\n"
        "  Agent KPI metrics per quarter: sales volume, renewal rate, premium and commission totals."
    ),
    "customer_risk_profiles": (
        "customer_risk_profiles(profile_id PK, customer_id FK→customers, profile_date DATE, "
        "overall_score REAL 0-100, claims_history_score REAL, payment_score REAL, risk_tier)\n"
        "  risk_tier: 'Preferred'|'Standard'|'Non-Standard'|'High Risk'\n"
        "  Composite customer risk scores combining claims history and payment behaviour."
    ),
}


def get_table_chunks() -> list[dict[str, str]]:
    """Return per-table schema chunks suitable for embedding in the vector store."""
    return [{"name": name, "description": desc} for name, desc in _TABLE_CHUNKS.items()]


def get_all_table_names() -> list[str]:
    return list(_TABLE_CHUNKS.keys())


def get_schema_str() -> str:
    """Full schema description injected into LLM prompts when retrieval is disabled."""
    header = "Database: ClearSpeed Insurance Analytics (SQLite)\n\nTables:"
    body = "\n\n".join(f"  {desc}" for desc in _TABLE_CHUNKS.values())
    footer = (
        "\nRelationships (FK chains):\n"
        "  claims → policies, adjusters\n"
        "  claimants, fraud_flags, claim_documents, claim_assessments,\n"
        "    claim_payments, claim_appeals, repair_estimates,\n"
        "    fraud_investigations, reserve_estimates → claims\n"
        "  policy_coverages, policy_endorsements, premium_payments,\n"
        "    insured_properties, insured_vehicles, risk_assessments,\n"
        "    inspection_reports → policies\n"
        "  risk_assessments → underwriters\n"
        "  repair_estimates → repair_vendors\n"
        "  fraud_investigations → investigators\n"
        "  agent_performance → agents\n"
        "  customer_risk_profiles → customers\n"
        "  policy_coverages → coverage_types\n\n"
        "Date format: YYYY-MM-DD. Use SQLite date functions: date(), strftime(), julianday()."
    )
    return f"{header}\n\n{body}\n{footer}"


if __name__ == "__main__":
    print("Initializing database...")
    init_db()
    rows, err = run_query("SELECT COUNT(*) as total_claims FROM claims")
    if err:
        print(f"Error: {err}")
    else:
        print(f"Database ready. Total claims: {rows[0]['total_claims']}")
    rows, _ = run_query(
        "SELECT risk_level, COUNT(*) as cnt, SUM(amount) as total "
        "FROM claims GROUP BY risk_level ORDER BY risk_level"
    )
    print("\nClaims by risk level:")
    for r in rows:
        print(f"  {r['risk_level']}: {r['cnt']} claims, ${r['total']:,.2f}")
    print(f"\nTotal tables: {len(get_all_table_names())}")

CREATE TABLE IF NOT EXISTS adjusters (
    adjuster_id   INTEGER PRIMARY KEY,
    name          TEXT    NOT NULL,
    region        TEXT    NOT NULL,  -- e.g., 'Northeast', 'Southeast', 'Midwest', 'West'
    department    TEXT    NOT NULL   -- e.g., 'Auto', 'Property', 'Health', 'Liability'
);

CREATE TABLE IF NOT EXISTS policies (
    policy_id       INTEGER PRIMARY KEY,
    holder_name     TEXT    NOT NULL,
    domain          TEXT    NOT NULL,  -- 'Insurance', 'Banking', 'Public Sector'
    policy_type     TEXT    NOT NULL,  -- 'Auto', 'Property', 'Health', 'Liability'
    effective_date  DATE    NOT NULL,
    expiry_date     DATE    NOT NULL,
    premium         REAL    NOT NULL,
    status          TEXT    NOT NULL   -- 'Active', 'Expired', 'Cancelled', 'Pending'
);

CREATE TABLE IF NOT EXISTS claims (
    claim_id        INTEGER PRIMARY KEY,
    policy_id       INTEGER NOT NULL REFERENCES policies(policy_id),
    adjuster_id     INTEGER NOT NULL REFERENCES adjusters(adjuster_id),
    filed_date      DATE    NOT NULL,
    resolved_date   DATE,
    amount          REAL    NOT NULL,
    status          TEXT    NOT NULL,  -- 'Open', 'Approved', 'Denied', 'Under Review'
    risk_level      TEXT    NOT NULL   -- 'Low', 'Medium', 'High'
);

CREATE TABLE IF NOT EXISTS claimants (
    claimant_id   INTEGER PRIMARY KEY,
    claim_id      INTEGER NOT NULL REFERENCES claims(claim_id),
    full_name     TEXT    NOT NULL,
    contact_email TEXT,
    state         TEXT    NOT NULL
);

CREATE TABLE IF NOT EXISTS fraud_flags (
    flag_id      INTEGER PRIMARY KEY,
    claim_id     INTEGER NOT NULL REFERENCES claims(claim_id),
    flag_type    TEXT    NOT NULL,  -- 'Duplicate', 'Inflated Amount', 'Staged Incident', 'Identity Mismatch'
    flagged_at   DATE    NOT NULL,
    resolved     INTEGER NOT NULL DEFAULT 0,  -- 0 = open, 1 = resolved
    savings      REAL    DEFAULT 0.0          -- estimated fraud savings if resolved
);

-- ── New tables (30-table schema for vector-DB demo) ──────────────────────────

CREATE TABLE IF NOT EXISTS coverage_types (
    coverage_type_id INTEGER PRIMARY KEY,
    name             TEXT NOT NULL,
    category         TEXT NOT NULL,   -- 'Vehicle'|'Property'|'Health'|'Liability'
    description      TEXT
);

CREATE TABLE IF NOT EXISTS loss_types (
    loss_type_id INTEGER PRIMARY KEY,
    name         TEXT NOT NULL,
    category     TEXT NOT NULL        -- 'Vehicle'|'Property'|'Health'|'Liability'|'Fraud'
);

CREATE TABLE IF NOT EXISTS customers (
    customer_id       INTEGER PRIMARY KEY,
    full_name         TEXT    NOT NULL,
    state             TEXT    NOT NULL,
    credit_score      INTEGER,
    customer_since    DATE    NOT NULL,
    preferred_contact TEXT              -- 'Email'|'Phone'|'Mail'
);

CREATE TABLE IF NOT EXISTS agents (
    agent_id        INTEGER PRIMARY KEY,
    full_name       TEXT  NOT NULL,
    license_number  TEXT  NOT NULL UNIQUE,
    region          TEXT  NOT NULL,
    hire_date       DATE  NOT NULL,
    commission_rate REAL  NOT NULL
);

CREATE TABLE IF NOT EXISTS underwriters (
    underwriter_id INTEGER PRIMARY KEY,
    full_name      TEXT    NOT NULL,
    certification  TEXT,               -- 'CPCU'|'ARe'|'CUW'
    specialization TEXT    NOT NULL,   -- 'Auto'|'Property'|'Commercial'|'Health'
    active         INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS policy_coverages (
    coverage_id      INTEGER PRIMARY KEY,
    policy_id        INTEGER NOT NULL REFERENCES policies(policy_id),
    coverage_type_id INTEGER NOT NULL REFERENCES coverage_types(coverage_type_id),
    coverage_limit   REAL    NOT NULL,
    deductible       REAL    NOT NULL DEFAULT 0.0
);

CREATE TABLE IF NOT EXISTS policy_endorsements (
    endorsement_id   INTEGER PRIMARY KEY,
    policy_id        INTEGER NOT NULL REFERENCES policies(policy_id),
    endorsement_type TEXT    NOT NULL,   -- 'Umbrella'|'Flood Rider'|'Earthquake'|'GAP'
    effective_date   DATE    NOT NULL,
    premium_change   REAL    NOT NULL DEFAULT 0.0,
    description      TEXT
);

CREATE TABLE IF NOT EXISTS premium_payments (
    payment_id     INTEGER PRIMARY KEY,
    policy_id      INTEGER NOT NULL REFERENCES policies(policy_id),
    due_date       DATE    NOT NULL,
    paid_date      DATE,
    amount         REAL    NOT NULL,
    payment_method TEXT    NOT NULL,   -- 'Credit Card'|'ACH'|'Check'|'Wire'
    status         TEXT    NOT NULL    -- 'Paid'|'Overdue'|'Pending'|'Waived'
);

CREATE TABLE IF NOT EXISTS insured_properties (
    property_id     INTEGER PRIMARY KEY,
    policy_id       INTEGER NOT NULL REFERENCES policies(policy_id),
    property_type   TEXT    NOT NULL,   -- 'Residential'|'Commercial'|'Industrial'
    address_state   TEXT    NOT NULL,
    year_built      INTEGER,
    estimated_value REAL    NOT NULL,
    occupancy_type  TEXT                -- 'Owner-Occupied'|'Rental'|'Vacant'
);

CREATE TABLE IF NOT EXISTS insured_vehicles (
    vehicle_id      INTEGER PRIMARY KEY,
    policy_id       INTEGER NOT NULL REFERENCES policies(policy_id),
    make            TEXT    NOT NULL,
    model           TEXT    NOT NULL,
    year            INTEGER NOT NULL,
    vin             TEXT    NOT NULL UNIQUE,
    estimated_value REAL    NOT NULL
);

CREATE TABLE IF NOT EXISTS risk_assessments (
    assessment_id  INTEGER PRIMARY KEY,
    policy_id      INTEGER NOT NULL REFERENCES policies(policy_id),
    underwriter_id INTEGER NOT NULL REFERENCES underwriters(underwriter_id),
    assessed_date  DATE    NOT NULL,
    risk_score     REAL    NOT NULL,   -- 0.0 to 10.0
    risk_category  TEXT    NOT NULL,   -- 'Low'|'Medium'|'High'|'Very High'
    notes          TEXT
);

CREATE TABLE IF NOT EXISTS inspection_reports (
    report_id        INTEGER PRIMARY KEY,
    policy_id        INTEGER NOT NULL REFERENCES policies(policy_id),
    inspection_date  DATE    NOT NULL,
    inspector_name   TEXT    NOT NULL,
    condition_rating TEXT    NOT NULL,   -- 'Excellent'|'Good'|'Fair'|'Poor'
    issues_found     INTEGER NOT NULL DEFAULT 0,
    passed           INTEGER NOT NULL DEFAULT 1   -- 1=passed, 0=failed
);

CREATE TABLE IF NOT EXISTS claim_documents (
    document_id   INTEGER PRIMARY KEY,
    claim_id      INTEGER NOT NULL REFERENCES claims(claim_id),
    document_type TEXT    NOT NULL,   -- 'Police Report'|'Medical Record'|'Photo'|'Estimate'|'Affidavit'
    uploaded_at   DATE    NOT NULL,
    verified      INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS claim_assessments (
    assessment_id      INTEGER PRIMARY KEY,
    claim_id           INTEGER NOT NULL REFERENCES claims(claim_id),
    adjuster_id        INTEGER NOT NULL REFERENCES adjusters(adjuster_id),
    assessment_date    DATE    NOT NULL,
    estimated_loss     REAL    NOT NULL,
    recommended_payout REAL    NOT NULL,
    notes              TEXT
);

CREATE TABLE IF NOT EXISTS claim_payments (
    payment_id     INTEGER PRIMARY KEY,
    claim_id       INTEGER NOT NULL REFERENCES claims(claim_id),
    payment_date   DATE    NOT NULL,
    amount         REAL    NOT NULL,
    payment_method TEXT    NOT NULL,   -- 'Check'|'ACH'|'Wire'
    status         TEXT    NOT NULL    -- 'Pending'|'Issued'|'Cleared'|'Cancelled'
);

CREATE TABLE IF NOT EXISTS claim_appeals (
    appeal_id     INTEGER PRIMARY KEY,
    claim_id      INTEGER NOT NULL REFERENCES claims(claim_id),
    filed_date    DATE    NOT NULL,
    reason        TEXT    NOT NULL,
    decision      TEXT,               -- 'Upheld'|'Overturned'|'Partial'|NULL if pending
    resolved_date DATE
);

CREATE TABLE IF NOT EXISTS repair_vendors (
    vendor_id  INTEGER PRIMARY KEY,
    name       TEXT  NOT NULL,
    specialty  TEXT  NOT NULL,   -- 'Auto Body'|'Plumbing'|'Electrical'|'Roofing'|'General'
    region     TEXT  NOT NULL,
    avg_rating REAL  NOT NULL DEFAULT 0.0,
    approved   INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS repair_estimates (
    estimate_id      INTEGER PRIMARY KEY,
    claim_id         INTEGER NOT NULL REFERENCES claims(claim_id),
    vendor_id        INTEGER NOT NULL REFERENCES repair_vendors(vendor_id),
    submitted_date   DATE    NOT NULL,
    estimated_amount REAL    NOT NULL,
    approved         INTEGER NOT NULL DEFAULT 0,
    approved_amount  REAL
);

CREATE TABLE IF NOT EXISTS investigators (
    investigator_id INTEGER PRIMARY KEY,
    name            TEXT    NOT NULL,
    specialization  TEXT    NOT NULL,   -- 'Auto Fraud'|'Property Fraud'|'Medical Fraud'|'Identity Theft'
    region          TEXT    NOT NULL,
    active          INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS fraud_investigations (
    investigation_id INTEGER PRIMARY KEY,
    claim_id         INTEGER NOT NULL REFERENCES claims(claim_id),
    investigator_id  INTEGER NOT NULL REFERENCES investigators(investigator_id),
    opened_date      DATE    NOT NULL,
    closed_date      DATE,
    outcome          TEXT,               -- 'Confirmed Fraud'|'No Fraud Found'|'Inconclusive'|NULL if open
    confirmed_fraud  INTEGER NOT NULL DEFAULT 0,
    savings          REAL    NOT NULL DEFAULT 0.0
);

CREATE TABLE IF NOT EXISTS reserve_estimates (
    reserve_id     INTEGER PRIMARY KEY,
    claim_id       INTEGER NOT NULL REFERENCES claims(claim_id),
    estimated_at   DATE    NOT NULL,
    reserve_amount REAL    NOT NULL,
    reserve_type   TEXT    NOT NULL,   -- 'Case Reserve'|'IBNR'|'Bulk'
    last_updated   DATE    NOT NULL
);

CREATE TABLE IF NOT EXISTS regulatory_filings (
    filing_id   INTEGER PRIMARY KEY,
    state       TEXT    NOT NULL,
    filing_date DATE    NOT NULL,
    filing_type TEXT    NOT NULL,   -- 'Rate Filing'|'Form Filing'|'Financial Statement'|'Market Conduct'
    status      TEXT    NOT NULL,   -- 'Submitted'|'Approved'|'Rejected'|'Pending'
    due_date    DATE,
    notes       TEXT
);

CREATE TABLE IF NOT EXISTS compliance_audits (
    audit_id     INTEGER PRIMARY KEY,
    audit_date   DATE    NOT NULL,
    auditor_name TEXT    NOT NULL,
    scope        TEXT    NOT NULL,   -- 'Claims Processing'|'Underwriting'|'Agent Conduct'|'Data Privacy'
    findings     INTEGER NOT NULL DEFAULT 0,
    result       TEXT    NOT NULL    -- 'Satisfactory'|'Needs Improvement'|'Unsatisfactory'
);

CREATE TABLE IF NOT EXISTS agent_performance (
    perf_id           INTEGER PRIMARY KEY,
    agent_id          INTEGER NOT NULL REFERENCES agents(agent_id),
    period            TEXT    NOT NULL,   -- e.g., '2024-Q1'
    policies_sold     INTEGER NOT NULL DEFAULT 0,
    renewals          INTEGER NOT NULL DEFAULT 0,
    total_premium     REAL    NOT NULL DEFAULT 0.0,
    commission_earned REAL    NOT NULL DEFAULT 0.0
);

CREATE TABLE IF NOT EXISTS customer_risk_profiles (
    profile_id           INTEGER PRIMARY KEY,
    customer_id          INTEGER NOT NULL REFERENCES customers(customer_id),
    profile_date         DATE    NOT NULL,
    overall_score        REAL    NOT NULL,   -- 0.0 to 100.0
    claims_history_score REAL    NOT NULL,
    payment_score        REAL    NOT NULL,
    risk_tier            TEXT    NOT NULL    -- 'Preferred'|'Standard'|'Non-Standard'|'High Risk'
);

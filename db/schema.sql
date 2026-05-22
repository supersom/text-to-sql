-- @desc Stores insurance claims adjusters and their regional/department assignments.
CREATE TABLE IF NOT EXISTS adjusters (
    adjuster_id   INTEGER PRIMARY KEY,
    name          TEXT    NOT NULL,
    region        TEXT    NOT NULL,  -- 'Northeast'|'Southeast'|'Midwest'|'West'
    department    TEXT    NOT NULL   -- 'Auto'|'Property'|'Health'|'Liability'
);

-- @desc Master policy records: who is covered, what type, dates, and premium amount.
CREATE TABLE IF NOT EXISTS policies (
    policy_id       INTEGER PRIMARY KEY,
    holder_name     TEXT    NOT NULL,
    domain          TEXT    NOT NULL,  -- 'Insurance'|'Banking'|'Public Sector'
    policy_type     TEXT    NOT NULL,  -- 'Auto'|'Property'|'Health'|'Liability'
    effective_date  DATE    NOT NULL,
    expiry_date     DATE    NOT NULL,
    premium         REAL    NOT NULL,
    status          TEXT    NOT NULL   -- 'Active'|'Expired'|'Cancelled'|'Pending'
);

-- @desc Core claims table: every insurance claim filed, its amount, status, and risk level.
CREATE TABLE IF NOT EXISTS claims (
    claim_id        INTEGER PRIMARY KEY,
    policy_id       INTEGER NOT NULL REFERENCES policies(policy_id),
    adjuster_id     INTEGER NOT NULL REFERENCES adjusters(adjuster_id),
    filed_date      DATE    NOT NULL,
    resolved_date   DATE,
    amount          REAL    NOT NULL,
    status          TEXT    NOT NULL,  -- 'Open'|'Approved'|'Denied'|'Under Review'
    risk_level      TEXT    NOT NULL   -- 'Low'|'Medium'|'High'
);

-- @desc Individuals who filed claims; one claimant per claim.
CREATE TABLE IF NOT EXISTS claimants (
    claimant_id   INTEGER PRIMARY KEY,
    claim_id      INTEGER NOT NULL REFERENCES claims(claim_id),
    full_name     TEXT    NOT NULL,
    contact_email TEXT,
    state         TEXT    NOT NULL   -- 2-letter US state code
);

-- @desc Heuristic fraud signals raised against claims; tracks resolution and savings.
CREATE TABLE IF NOT EXISTS fraud_flags (
    flag_id      INTEGER PRIMARY KEY,
    claim_id     INTEGER NOT NULL REFERENCES claims(claim_id),
    flag_type    TEXT    NOT NULL,  -- 'Duplicate'|'Inflated Amount'|'Staged Incident'|'Identity Mismatch'
    flagged_at   DATE    NOT NULL,
    resolved     INTEGER NOT NULL DEFAULT 0,  -- 0=open, 1=resolved
    savings      REAL    DEFAULT 0.0          -- estimated fraud savings in USD if resolved
);

-- ── New tables (30-table schema for vector-DB demo) ──────────────────────────

-- @desc Reference table of available insurance coverage types.
CREATE TABLE IF NOT EXISTS coverage_types (
    coverage_type_id INTEGER PRIMARY KEY,
    name             TEXT NOT NULL,
    category         TEXT NOT NULL,   -- 'Vehicle'|'Property'|'Health'|'Liability'
    description      TEXT
);

-- @desc Reference table classifying the nature of insured losses.
CREATE TABLE IF NOT EXISTS loss_types (
    loss_type_id INTEGER PRIMARY KEY,
    name         TEXT NOT NULL,
    category     TEXT NOT NULL        -- 'Vehicle'|'Property'|'Health'|'Liability'|'Fraud'
);

-- @desc Policyholders and insurance customers; credit score and tenure data.
CREATE TABLE IF NOT EXISTS customers (
    customer_id       INTEGER PRIMARY KEY,
    full_name         TEXT    NOT NULL,
    state             TEXT    NOT NULL,
    credit_score      INTEGER,
    customer_since    DATE    NOT NULL,
    preferred_contact TEXT              -- 'Email'|'Phone'|'Mail'
);

-- @desc Insurance sales agents who sell and service policies.
CREATE TABLE IF NOT EXISTS agents (
    agent_id        INTEGER PRIMARY KEY,
    full_name       TEXT  NOT NULL,
    license_number  TEXT  NOT NULL UNIQUE,
    region          TEXT  NOT NULL,
    hire_date       DATE  NOT NULL,
    commission_rate REAL  NOT NULL      -- decimal fraction e.g. 0.06 = 6%
);

-- @desc Staff who evaluate and approve insurance policy risk.
CREATE TABLE IF NOT EXISTS underwriters (
    underwriter_id INTEGER PRIMARY KEY,
    full_name      TEXT    NOT NULL,
    certification  TEXT,               -- 'CPCU'|'ARe'|'CUW'
    specialization TEXT    NOT NULL,   -- 'Auto'|'Property'|'Commercial'|'Health'
    active         INTEGER NOT NULL DEFAULT 1   -- 1=active, 0=inactive
);

-- @desc Junction table mapping which coverage types are included in each policy, with limits and deductibles.
CREATE TABLE IF NOT EXISTS policy_coverages (
    coverage_id      INTEGER PRIMARY KEY,
    policy_id        INTEGER NOT NULL REFERENCES policies(policy_id),
    coverage_type_id INTEGER NOT NULL REFERENCES coverage_types(coverage_type_id),
    coverage_limit   REAL    NOT NULL,
    deductible       REAL    NOT NULL DEFAULT 0.0
);

-- @desc Riders and add-ons attached to base policies; tracks premium impact.
CREATE TABLE IF NOT EXISTS policy_endorsements (
    endorsement_id   INTEGER PRIMARY KEY,
    policy_id        INTEGER NOT NULL REFERENCES policies(policy_id),
    endorsement_type TEXT    NOT NULL,   -- 'Umbrella'|'Flood Rider'|'Earthquake'|'GAP'
    effective_date   DATE    NOT NULL,
    premium_change   REAL    NOT NULL DEFAULT 0.0,
    description      TEXT
);

-- @desc Tracks premium billing and payment history per policy.
CREATE TABLE IF NOT EXISTS premium_payments (
    payment_id     INTEGER PRIMARY KEY,
    policy_id      INTEGER NOT NULL REFERENCES policies(policy_id),
    due_date       DATE    NOT NULL,
    paid_date      DATE,
    amount         REAL    NOT NULL,
    payment_method TEXT    NOT NULL,   -- 'Credit Card'|'ACH'|'Check'|'Wire'
    status         TEXT    NOT NULL    -- 'Paid'|'Overdue'|'Pending'|'Waived'
);

-- @desc Physical properties covered under property insurance policies.
CREATE TABLE IF NOT EXISTS insured_properties (
    property_id     INTEGER PRIMARY KEY,
    policy_id       INTEGER NOT NULL REFERENCES policies(policy_id),
    property_type   TEXT    NOT NULL,   -- 'Residential'|'Commercial'|'Industrial'
    address_state   TEXT    NOT NULL,
    year_built      INTEGER,
    estimated_value REAL    NOT NULL,
    occupancy_type  TEXT                -- 'Owner-Occupied'|'Rental'|'Vacant'
);

-- @desc Vehicles covered under auto insurance policies: make, model, year, VIN, and estimated value.
CREATE TABLE IF NOT EXISTS insured_vehicles (
    vehicle_id      INTEGER PRIMARY KEY,
    policy_id       INTEGER NOT NULL REFERENCES policies(policy_id),
    make            TEXT    NOT NULL,
    model           TEXT    NOT NULL,
    year            INTEGER NOT NULL,
    vin             TEXT    NOT NULL UNIQUE,
    estimated_value REAL    NOT NULL
);

-- @desc Underwriting risk evaluations for policies; higher score = higher risk.
CREATE TABLE IF NOT EXISTS risk_assessments (
    assessment_id  INTEGER PRIMARY KEY,
    policy_id      INTEGER NOT NULL REFERENCES policies(policy_id),
    underwriter_id INTEGER NOT NULL REFERENCES underwriters(underwriter_id),
    assessed_date  DATE    NOT NULL,
    risk_score     REAL    NOT NULL,   -- 0.0 to 10.0
    risk_category  TEXT    NOT NULL,   -- 'Low'|'Medium'|'High'|'Very High'
    notes          TEXT
);

-- @desc Physical inspection results for insured properties and vehicles.
CREATE TABLE IF NOT EXISTS inspection_reports (
    report_id        INTEGER PRIMARY KEY,
    policy_id        INTEGER NOT NULL REFERENCES policies(policy_id),
    inspection_date  DATE    NOT NULL,
    inspector_name   TEXT    NOT NULL,
    condition_rating TEXT    NOT NULL,   -- 'Excellent'|'Good'|'Fair'|'Poor'
    issues_found     INTEGER NOT NULL DEFAULT 0,
    passed           INTEGER NOT NULL DEFAULT 1   -- 1=passed, 0=failed
);

-- @desc Supporting documents and evidence attached to claims.
CREATE TABLE IF NOT EXISTS claim_documents (
    document_id   INTEGER PRIMARY KEY,
    claim_id      INTEGER NOT NULL REFERENCES claims(claim_id),
    document_type TEXT    NOT NULL,   -- 'Police Report'|'Medical Record'|'Photo'|'Estimate'|'Affidavit'
    uploaded_at   DATE    NOT NULL,
    verified      INTEGER NOT NULL DEFAULT 0   -- 1=verified, 0=unverified
);

-- @desc Adjuster loss evaluations: what they estimated and what payout they recommended per claim.
CREATE TABLE IF NOT EXISTS claim_assessments (
    assessment_id      INTEGER PRIMARY KEY,
    claim_id           INTEGER NOT NULL REFERENCES claims(claim_id),
    adjuster_id        INTEGER NOT NULL REFERENCES adjusters(adjuster_id),
    assessment_date    DATE    NOT NULL,
    estimated_loss     REAL    NOT NULL,
    recommended_payout REAL    NOT NULL,
    notes              TEXT
);

-- @desc Actual payment disbursements made to claimants for approved claims.
CREATE TABLE IF NOT EXISTS claim_payments (
    payment_id     INTEGER PRIMARY KEY,
    claim_id       INTEGER NOT NULL REFERENCES claims(claim_id),
    payment_date   DATE    NOT NULL,
    amount         REAL    NOT NULL,
    payment_method TEXT    NOT NULL,   -- 'Check'|'ACH'|'Wire'
    status         TEXT    NOT NULL    -- 'Pending'|'Issued'|'Cleared'|'Cancelled'
);

-- @desc Appeals filed by claimants contesting claim decisions.
CREATE TABLE IF NOT EXISTS claim_appeals (
    appeal_id     INTEGER PRIMARY KEY,
    claim_id      INTEGER NOT NULL REFERENCES claims(claim_id),
    filed_date    DATE    NOT NULL,
    reason        TEXT    NOT NULL,
    decision      TEXT,               -- 'Upheld'|'Overturned'|'Partial'|NULL if pending
    resolved_date DATE
);

-- @desc Repair and restoration vendors authorized to work on insured claims.
CREATE TABLE IF NOT EXISTS repair_vendors (
    vendor_id  INTEGER PRIMARY KEY,
    name       TEXT  NOT NULL,
    specialty  TEXT  NOT NULL,   -- 'Auto Body'|'Plumbing'|'Electrical'|'Roofing'|'General'
    region     TEXT  NOT NULL,
    avg_rating REAL  NOT NULL DEFAULT 0.0,
    approved   INTEGER NOT NULL DEFAULT 1   -- 1=on approved list, 0=suspended
);

-- @desc Vendor repair cost estimates submitted for claim approval; tracks whether estimate was accepted.
CREATE TABLE IF NOT EXISTS repair_estimates (
    estimate_id      INTEGER PRIMARY KEY,
    claim_id         INTEGER NOT NULL REFERENCES claims(claim_id),
    vendor_id        INTEGER NOT NULL REFERENCES repair_vendors(vendor_id),
    submitted_date   DATE    NOT NULL,
    estimated_amount REAL    NOT NULL,
    approved         INTEGER NOT NULL DEFAULT 0,   -- 1=accepted, 0=pending
    approved_amount  REAL
);

-- @desc Special Investigations Unit (SIU) staff who investigate suspected fraud.
CREATE TABLE IF NOT EXISTS investigators (
    investigator_id INTEGER PRIMARY KEY,
    name            TEXT    NOT NULL,
    specialization  TEXT    NOT NULL,   -- 'Auto Fraud'|'Property Fraud'|'Medical Fraud'|'Identity Theft'
    region          TEXT    NOT NULL,
    active          INTEGER NOT NULL DEFAULT 1   -- 1=active, 0=inactive
);

-- @desc Formal SIU investigations into suspicious claims.
CREATE TABLE IF NOT EXISTS fraud_investigations (
    investigation_id INTEGER PRIMARY KEY,
    claim_id         INTEGER NOT NULL REFERENCES claims(claim_id),
    investigator_id  INTEGER NOT NULL REFERENCES investigators(investigator_id),
    opened_date      DATE    NOT NULL,
    closed_date      DATE,
    outcome          TEXT,               -- 'Confirmed Fraud'|'No Fraud Found'|'Inconclusive'|NULL if open
    confirmed_fraud  INTEGER NOT NULL DEFAULT 0,   -- 1=confirmed, 0=not confirmed
    savings          REAL    NOT NULL DEFAULT 0.0
);

-- @desc Actuarial loss reserve calculations for open and IBNR claims.
CREATE TABLE IF NOT EXISTS reserve_estimates (
    reserve_id     INTEGER PRIMARY KEY,
    claim_id       INTEGER NOT NULL REFERENCES claims(claim_id),
    estimated_at   DATE    NOT NULL,
    reserve_amount REAL    NOT NULL,
    reserve_type   TEXT    NOT NULL,   -- 'Case Reserve'|'IBNR'|'Bulk'
    last_updated   DATE    NOT NULL
);

-- @desc State insurance department regulatory submissions and their approval status.
CREATE TABLE IF NOT EXISTS regulatory_filings (
    filing_id   INTEGER PRIMARY KEY,
    state       TEXT    NOT NULL,
    filing_date DATE    NOT NULL,
    filing_type TEXT    NOT NULL,   -- 'Rate Filing'|'Form Filing'|'Financial Statement'|'Market Conduct'
    status      TEXT    NOT NULL,   -- 'Submitted'|'Approved'|'Rejected'|'Pending'
    due_date    DATE,
    notes       TEXT
);

-- @desc Internal compliance reviews; findings count and overall result.
CREATE TABLE IF NOT EXISTS compliance_audits (
    audit_id     INTEGER PRIMARY KEY,
    audit_date   DATE    NOT NULL,
    auditor_name TEXT    NOT NULL,
    scope        TEXT    NOT NULL,   -- 'Claims Processing'|'Underwriting'|'Agent Conduct'|'Data Privacy'
    findings     INTEGER NOT NULL DEFAULT 0,
    result       TEXT    NOT NULL    -- 'Satisfactory'|'Needs Improvement'|'Unsatisfactory'
);

-- @desc Agent KPI metrics per quarter: sales volume, renewal rate, premium and commission totals.
CREATE TABLE IF NOT EXISTS agent_performance (
    perf_id           INTEGER PRIMARY KEY,
    agent_id          INTEGER NOT NULL REFERENCES agents(agent_id),
    period            TEXT    NOT NULL,   -- e.g. '2024-Q1'
    policies_sold     INTEGER NOT NULL DEFAULT 0,
    renewals          INTEGER NOT NULL DEFAULT 0,
    total_premium     REAL    NOT NULL DEFAULT 0.0,
    commission_earned REAL    NOT NULL DEFAULT 0.0
);

-- @desc Composite customer risk scores combining claims history and payment behaviour.
CREATE TABLE IF NOT EXISTS customer_risk_profiles (
    profile_id           INTEGER PRIMARY KEY,
    customer_id          INTEGER NOT NULL REFERENCES customers(customer_id),
    profile_date         DATE    NOT NULL,
    overall_score        REAL    NOT NULL,   -- 0.0 to 100.0
    claims_history_score REAL    NOT NULL,
    payment_score        REAL    NOT NULL,
    risk_tier            TEXT    NOT NULL    -- 'Preferred'|'Standard'|'Non-Standard'|'High Risk'
);

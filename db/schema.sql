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

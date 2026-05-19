-- Adjusters
INSERT OR IGNORE INTO adjusters VALUES (1, 'Sarah Mitchell', 'Northeast', 'Auto');
INSERT OR IGNORE INTO adjusters VALUES (2, 'James Okafor', 'Southeast', 'Property');
INSERT OR IGNORE INTO adjusters VALUES (3, 'Linda Chen', 'Midwest', 'Health');
INSERT OR IGNORE INTO adjusters VALUES (4, 'Robert Torres', 'West', 'Liability');
INSERT OR IGNORE INTO adjusters VALUES (5, 'Emily Watson', 'Northeast', 'Property');
INSERT OR IGNORE INTO adjusters VALUES (6, 'David Kim', 'Southeast', 'Auto');
INSERT OR IGNORE INTO adjusters VALUES (7, 'Angela Brooks', 'Midwest', 'Auto');
INSERT OR IGNORE INTO adjusters VALUES (8, 'Marcus Johnson', 'West', 'Health');
INSERT OR IGNORE INTO adjusters VALUES (9, 'Priya Patel', 'Northeast', 'Liability');
INSERT OR IGNORE INTO adjusters VALUES (10, 'Carlos Rivera', 'Southeast', 'Property');

-- Policies
INSERT OR IGNORE INTO policies VALUES (101, 'Redacted', 'Insurance', 'Auto', '2023-01-15', '2024-01-15', 1200.00, 'Expired');
INSERT OR IGNORE INTO policies VALUES (102, 'Redacted', 'Insurance', 'Property', '2023-03-01', '2024-03-01', 2500.00, 'Expired');
INSERT OR IGNORE INTO policies VALUES (103, 'Redacted', 'Insurance', 'Health', '2023-06-01', '2024-06-01', 3800.00, 'Active');
INSERT OR IGNORE INTO policies VALUES (104, 'Redacted', 'Insurance', 'Auto', '2024-01-01', '2025-01-01', 950.00, 'Active');
INSERT OR IGNORE INTO policies VALUES (105, 'Redacted', 'Insurance', 'Liability', '2024-02-15', '2025-02-15', 5200.00, 'Active');
INSERT OR IGNORE INTO policies VALUES (106, 'Redacted', 'Insurance', 'Property', '2023-09-01', '2024-09-01', 1800.00, 'Active');
INSERT OR IGNORE INTO policies VALUES (107, 'Redacted', 'Insurance', 'Auto', '2024-03-01', '2025-03-01', 1100.00, 'Active');
INSERT OR IGNORE INTO policies VALUES (108, 'Redacted', 'Insurance', 'Health', '2023-11-01', '2024-11-01', 4200.00, 'Active');
INSERT OR IGNORE INTO policies VALUES (109, 'Redacted', 'Insurance', 'Auto', '2024-04-15', '2025-04-15', 875.00, 'Active');
INSERT OR IGNORE INTO policies VALUES (110, 'Redacted', 'Insurance', 'Property', '2022-06-01', '2023-06-01', 3100.00, 'Expired');
INSERT OR IGNORE INTO policies VALUES (111, 'Redacted', 'Insurance', 'Liability', '2024-01-01', '2025-01-01', 6500.00, 'Active');
INSERT OR IGNORE INTO policies VALUES (112, 'Redacted', 'Insurance', 'Auto', '2023-07-01', '2024-07-01', 1350.00, 'Active');
INSERT OR IGNORE INTO policies VALUES (113, 'Redacted', 'Insurance', 'Health', '2024-05-01', '2025-05-01', 3200.00, 'Active');
INSERT OR IGNORE INTO policies VALUES (114, 'Redacted', 'Insurance', 'Property', '2024-02-01', '2025-02-01', 2200.00, 'Active');
INSERT OR IGNORE INTO policies VALUES (115, 'Redacted', 'Insurance', 'Auto', '2023-10-01', '2024-10-01', 990.00, 'Cancelled');
INSERT OR IGNORE INTO policies VALUES (116, 'Redacted', 'Insurance', 'Liability', '2023-04-01', '2024-04-01', 4800.00, 'Expired');
INSERT OR IGNORE INTO policies VALUES (117, 'Redacted', 'Insurance', 'Health', '2024-01-15', '2025-01-15', 5100.00, 'Active');
INSERT OR IGNORE INTO policies VALUES (118, 'Redacted', 'Insurance', 'Auto', '2024-06-01', '2025-06-01', 1050.00, 'Active');
INSERT OR IGNORE INTO policies VALUES (119, 'Redacted', 'Insurance', 'Property', '2023-08-01', '2024-08-01', 1950.00, 'Active');
INSERT OR IGNORE INTO policies VALUES (120, 'Redacted', 'Insurance', 'Auto', '2022-12-01', '2023-12-01', 800.00, 'Expired');

-- Claims
INSERT OR IGNORE INTO claims VALUES (1001, 101, 1, '2023-03-10', '2023-04-05', 8500.00, 'Approved', 'Low');
INSERT OR IGNORE INTO claims VALUES (1002, 102, 2, '2023-04-20', '2023-05-30', 42000.00, 'Approved', 'High');
INSERT OR IGNORE INTO claims VALUES (1003, 103, 3, '2023-07-15', NULL, 15200.00, 'Under Review', 'Medium');
INSERT OR IGNORE INTO claims VALUES (1004, 104, 1, '2024-02-01', '2024-02-28', 3200.00, 'Approved', 'Low');
INSERT OR IGNORE INTO claims VALUES (1005, 105, 4, '2024-03-10', NULL, 95000.00, 'Open', 'High');
INSERT OR IGNORE INTO claims VALUES (1006, 106, 5, '2023-10-05', '2023-11-20', 28000.00, 'Denied', 'High');
INSERT OR IGNORE INTO claims VALUES (1007, 107, 6, '2024-04-01', '2024-04-25', 5600.00, 'Approved', 'Low');
INSERT OR IGNORE INTO claims VALUES (1008, 108, 3, '2024-01-10', NULL, 67000.00, 'Under Review', 'High');
INSERT OR IGNORE INTO claims VALUES (1009, 109, 7, '2024-05-01', '2024-05-20', 2100.00, 'Approved', 'Low');
INSERT OR IGNORE INTO claims VALUES (1010, 110, 2, '2023-01-15', '2023-02-28', 18500.00, 'Approved', 'Medium');
INSERT OR IGNORE INTO claims VALUES (1011, 111, 4, '2024-02-15', NULL, 120000.00, 'Open', 'High');
INSERT OR IGNORE INTO claims VALUES (1012, 112, 6, '2023-08-10', '2023-09-05', 7800.00, 'Approved', 'Low');
INSERT OR IGNORE INTO claims VALUES (1013, 113, 3, '2024-06-01', NULL, 9500.00, 'Open', 'Medium');
INSERT OR IGNORE INTO claims VALUES (1014, 114, 5, '2024-03-15', '2024-04-10', 31000.00, 'Approved', 'Medium');
INSERT OR IGNORE INTO claims VALUES (1015, 115, 7, '2024-01-20', '2024-02-10', 4200.00, 'Denied', 'Low');
INSERT OR IGNORE INTO claims VALUES (1016, 116, 4, '2023-05-01', '2023-06-15', 55000.00, 'Approved', 'High');
INSERT OR IGNORE INTO claims VALUES (1017, 117, 8, '2024-02-20', NULL, 22000.00, 'Under Review', 'Medium');
INSERT OR IGNORE INTO claims VALUES (1018, 118, 1, '2024-07-01', NULL, 6800.00, 'Open', 'Low');
INSERT OR IGNORE INTO claims VALUES (1019, 119, 10, '2023-09-10', '2023-10-25', 14500.00, 'Approved', 'Medium');
INSERT OR IGNORE INTO claims VALUES (1020, 120, 6, '2023-02-05', '2023-03-01', 3900.00, 'Approved', 'Low');
INSERT OR IGNORE INTO claims VALUES (1021, 101, 9, '2023-06-12', '2023-07-20', 11200.00, 'Approved', 'Medium');
INSERT OR IGNORE INTO claims VALUES (1022, 103, 8, '2024-01-05', NULL, 38000.00, 'Under Review', 'High');
INSERT OR IGNORE INTO claims VALUES (1023, 106, 2, '2024-02-28', '2024-03-30', 19000.00, 'Approved', 'Medium');
INSERT OR IGNORE INTO claims VALUES (1024, 108, 3, '2024-03-20', NULL, 5500.00, 'Open', 'Low');
INSERT OR IGNORE INTO claims VALUES (1025, 112, 7, '2024-04-10', '2024-05-01', 8900.00, 'Denied', 'Medium');

-- Claimants
INSERT OR IGNORE INTO claimants VALUES (2001, 1001, 'Redacted', 'redacted@email.com', 'NY');
INSERT OR IGNORE INTO claimants VALUES (2002, 1002, 'Redacted', 'redacted@email.com', 'FL');
INSERT OR IGNORE INTO claimants VALUES (2003, 1003, 'Redacted', 'redacted@email.com', 'IL');
INSERT OR IGNORE INTO claimants VALUES (2004, 1004, 'Redacted', 'redacted@email.com', 'NY');
INSERT OR IGNORE INTO claimants VALUES (2005, 1005, 'Redacted', 'redacted@email.com', 'CA');
INSERT OR IGNORE INTO claimants VALUES (2006, 1006, 'Redacted', 'redacted@email.com', 'GA');
INSERT OR IGNORE INTO claimants VALUES (2007, 1007, 'Redacted', 'redacted@email.com', 'WA');
INSERT OR IGNORE INTO claimants VALUES (2008, 1008, 'Redacted', 'redacted@email.com', 'IL');
INSERT OR IGNORE INTO claimants VALUES (2009, 1009, 'Redacted', 'redacted@email.com', 'WA');
INSERT OR IGNORE INTO claimants VALUES (2010, 1010, 'Redacted', 'redacted@email.com', 'FL');
INSERT OR IGNORE INTO claimants VALUES (2011, 1011, 'Redacted', 'redacted@email.com', 'CA');
INSERT OR IGNORE INTO claimants VALUES (2012, 1012, 'Redacted', 'redacted@email.com', 'GA');
INSERT OR IGNORE INTO claimants VALUES (2013, 1013, 'Redacted', 'redacted@email.com', 'IL');
INSERT OR IGNORE INTO claimants VALUES (2014, 1014, 'Redacted', 'redacted@email.com', 'NY');
INSERT OR IGNORE INTO claimants VALUES (2015, 1015, 'Redacted', 'redacted@email.com', 'WA');
INSERT OR IGNORE INTO claimants VALUES (2016, 1016, 'Redacted', 'redacted@email.com', 'CA');
INSERT OR IGNORE INTO claimants VALUES (2017, 1017, 'Redacted', 'redacted@email.com', 'NY');
INSERT OR IGNORE INTO claimants VALUES (2018, 1018, 'Redacted', 'redacted@email.com', 'WA');
INSERT OR IGNORE INTO claimants VALUES (2019, 1019, 'Redacted', 'redacted@email.com', 'FL');
INSERT OR IGNORE INTO claimants VALUES (2020, 1020, 'Redacted', 'redacted@email.com', 'GA');
INSERT OR IGNORE INTO claimants VALUES (2021, 1021, 'Redacted', 'redacted@email.com', 'NY');
INSERT OR IGNORE INTO claimants VALUES (2022, 1022, 'Redacted', 'redacted@email.com', 'IL');
INSERT OR IGNORE INTO claimants VALUES (2023, 1023, 'Redacted', 'redacted@email.com', 'GA');
INSERT OR IGNORE INTO claimants VALUES (2024, 1024, 'Redacted', 'redacted@email.com', 'IL');
INSERT OR IGNORE INTO claimants VALUES (2025, 1025, 'Redacted', 'redacted@email.com', 'GA');

-- Fraud Flags
INSERT OR IGNORE INTO fraud_flags VALUES (3001, 1002, 'Inflated Amount', '2023-05-01', 1, 18000.00);
INSERT OR IGNORE INTO fraud_flags VALUES (3002, 1005, 'Staged Incident', '2024-03-15', 0, 0.00);
INSERT OR IGNORE INTO fraud_flags VALUES (3003, 1006, 'Duplicate', '2023-10-10', 1, 28000.00);
INSERT OR IGNORE INTO fraud_flags VALUES (3004, 1008, 'Identity Mismatch', '2024-01-20', 0, 0.00);
INSERT OR IGNORE INTO fraud_flags VALUES (3005, 1011, 'Inflated Amount', '2024-03-01', 0, 0.00);
INSERT OR IGNORE INTO fraud_flags VALUES (3006, 1016, 'Staged Incident', '2023-05-15', 1, 55000.00);
INSERT OR IGNORE INTO fraud_flags VALUES (3007, 1022, 'Duplicate', '2024-01-15', 0, 0.00);
INSERT OR IGNORE INTO fraud_flags VALUES (3008, 1003, 'Identity Mismatch', '2023-08-01', 1, 12000.00);
INSERT OR IGNORE INTO fraud_flags VALUES (3009, 1025, 'Inflated Amount', '2024-04-15', 0, 0.00);
INSERT OR IGNORE INTO fraud_flags VALUES (3010, 1017, 'Staged Incident', '2024-03-01', 0, 0.00);

-- ── New tables ───────────────────────────────────────────────────────────────

-- Coverage Types
INSERT OR IGNORE INTO coverage_types VALUES (1, 'Collision', 'Vehicle', 'Covers damage from vehicle collisions');
INSERT OR IGNORE INTO coverage_types VALUES (2, 'Comprehensive', 'Vehicle', 'Covers non-collision damage: theft, weather, fire');
INSERT OR IGNORE INTO coverage_types VALUES (3, 'Bodily Injury Liability', 'Liability', 'Covers injuries to others you cause');
INSERT OR IGNORE INTO coverage_types VALUES (4, 'Property Damage Liability', 'Liability', 'Covers damage to others property');
INSERT OR IGNORE INTO coverage_types VALUES (5, 'Medical Payments', 'Health', 'Covers medical expenses after an accident');
INSERT OR IGNORE INTO coverage_types VALUES (6, 'Building Coverage', 'Property', 'Covers the structure of the insured building');
INSERT OR IGNORE INTO coverage_types VALUES (7, 'Contents Coverage', 'Property', 'Covers personal property inside the structure');
INSERT OR IGNORE INTO coverage_types VALUES (8, 'Business Interruption', 'Property', 'Covers lost income during a repair period');

-- Loss Types
INSERT OR IGNORE INTO loss_types VALUES (1, 'Vehicle Collision', 'Vehicle');
INSERT OR IGNORE INTO loss_types VALUES (2, 'Theft', 'Vehicle');
INSERT OR IGNORE INTO loss_types VALUES (3, 'Fire Damage', 'Property');
INSERT OR IGNORE INTO loss_types VALUES (4, 'Water Damage', 'Property');
INSERT OR IGNORE INTO loss_types VALUES (5, 'Wind/Hail', 'Property');
INSERT OR IGNORE INTO loss_types VALUES (6, 'Medical Injury', 'Health');
INSERT OR IGNORE INTO loss_types VALUES (7, 'Liability Claim', 'Liability');
INSERT OR IGNORE INTO loss_types VALUES (8, 'Fraudulent Activity', 'Fraud');

-- Customers
INSERT OR IGNORE INTO customers VALUES (1, 'Redacted', 'NY', 720, '2019-03-15', 'Email');
INSERT OR IGNORE INTO customers VALUES (2, 'Redacted', 'CA', 680, '2020-07-01', 'Phone');
INSERT OR IGNORE INTO customers VALUES (3, 'Redacted', 'FL', 750, '2018-11-20', 'Email');
INSERT OR IGNORE INTO customers VALUES (4, 'Redacted', 'TX', 640, '2021-02-10', 'Mail');
INSERT OR IGNORE INTO customers VALUES (5, 'Redacted', 'IL', 700, '2017-05-30', 'Email');
INSERT OR IGNORE INTO customers VALUES (6, 'Redacted', 'WA', 760, '2022-01-15', 'Email');
INSERT OR IGNORE INTO customers VALUES (7, 'Redacted', 'GA', 620, '2019-09-01', 'Phone');
INSERT OR IGNORE INTO customers VALUES (8, 'Redacted', 'NY', 730, '2020-04-20', 'Email');

-- Agents
INSERT OR IGNORE INTO agents VALUES (1, 'Redacted', 'LIC-NE-001', 'Northeast', '2015-06-01', 0.06);
INSERT OR IGNORE INTO agents VALUES (2, 'Redacted', 'LIC-SE-002', 'Southeast', '2017-03-15', 0.055);
INSERT OR IGNORE INTO agents VALUES (3, 'Redacted', 'LIC-MW-003', 'Midwest', '2018-09-01', 0.05);
INSERT OR IGNORE INTO agents VALUES (4, 'Redacted', 'LIC-WE-004', 'West', '2016-11-20', 0.065);
INSERT OR IGNORE INTO agents VALUES (5, 'Redacted', 'LIC-NE-005', 'Northeast', '2020-01-10', 0.05);

-- Underwriters
INSERT OR IGNORE INTO underwriters VALUES (1, 'Redacted', 'CPCU', 'Auto', 1);
INSERT OR IGNORE INTO underwriters VALUES (2, 'Redacted', 'CUW', 'Property', 1);
INSERT OR IGNORE INTO underwriters VALUES (3, 'Redacted', 'ARe', 'Commercial', 1);
INSERT OR IGNORE INTO underwriters VALUES (4, 'Redacted', 'CPCU', 'Health', 1);
INSERT OR IGNORE INTO underwriters VALUES (5, 'Redacted', 'CUW', 'Auto', 0);

-- Policy Coverages
INSERT OR IGNORE INTO policy_coverages VALUES (1, 101, 1, 50000.00, 500.00);
INSERT OR IGNORE INTO policy_coverages VALUES (2, 101, 2, 50000.00, 250.00);
INSERT OR IGNORE INTO policy_coverages VALUES (3, 102, 6, 250000.00, 1000.00);
INSERT OR IGNORE INTO policy_coverages VALUES (4, 102, 7, 50000.00, 500.00);
INSERT OR IGNORE INTO policy_coverages VALUES (5, 103, 5, 10000.00, 0.00);
INSERT OR IGNORE INTO policy_coverages VALUES (6, 104, 1, 30000.00, 500.00);
INSERT OR IGNORE INTO policy_coverages VALUES (7, 104, 3, 100000.00, 0.00);
INSERT OR IGNORE INTO policy_coverages VALUES (8, 105, 3, 500000.00, 0.00);
INSERT OR IGNORE INTO policy_coverages VALUES (9, 105, 4, 100000.00, 0.00);
INSERT OR IGNORE INTO policy_coverages VALUES (10, 106, 6, 200000.00, 1000.00);
INSERT OR IGNORE INTO policy_coverages VALUES (11, 107, 1, 45000.00, 500.00);
INSERT OR IGNORE INTO policy_coverages VALUES (12, 107, 2, 45000.00, 250.00);
INSERT OR IGNORE INTO policy_coverages VALUES (13, 108, 5, 25000.00, 0.00);
INSERT OR IGNORE INTO policy_coverages VALUES (14, 113, 1, 35000.00, 500.00);
INSERT OR IGNORE INTO policy_coverages VALUES (15, 114, 6, 300000.00, 2000.00);

-- Policy Endorsements
INSERT OR IGNORE INTO policy_endorsements VALUES (1, 102, 'Flood Rider', '2023-03-01', 150.00, 'Flood coverage for coastal property');
INSERT OR IGNORE INTO policy_endorsements VALUES (2, 105, 'Umbrella', '2024-02-15', 500.00, 'Excess liability coverage $1M');
INSERT OR IGNORE INTO policy_endorsements VALUES (3, 106, 'Earthquake', '2023-09-01', 220.00, 'Seismic event coverage');
INSERT OR IGNORE INTO policy_endorsements VALUES (4, 111, 'Umbrella', '2024-01-01', 480.00, 'Excess liability coverage $2M');
INSERT OR IGNORE INTO policy_endorsements VALUES (5, 103, 'GAP', '2023-06-01', 75.00, 'Guaranteed asset protection');
INSERT OR IGNORE INTO policy_endorsements VALUES (6, 114, 'Business Interruption', '2024-02-01', 320.00, 'Lost income coverage');
INSERT OR IGNORE INTO policy_endorsements VALUES (7, 101, 'GAP', '2023-01-15', 65.00, 'Guaranteed asset protection auto');
INSERT OR IGNORE INTO policy_endorsements VALUES (8, 117, 'Flood Rider', '2024-01-15', 180.00, 'Flood coverage add-on');

-- Premium Payments
INSERT OR IGNORE INTO premium_payments VALUES (1,  101, '2023-02-15', '2023-02-14', 1200.00, 'Credit Card', 'Paid');
INSERT OR IGNORE INTO premium_payments VALUES (2,  102, '2023-04-01', '2023-03-30', 2500.00, 'ACH',         'Paid');
INSERT OR IGNORE INTO premium_payments VALUES (3,  103, '2023-07-01', '2023-07-01', 3800.00, 'ACH',         'Paid');
INSERT OR IGNORE INTO premium_payments VALUES (4,  104, '2024-02-01', '2024-01-30',  950.00, 'Credit Card', 'Paid');
INSERT OR IGNORE INTO premium_payments VALUES (5,  105, '2024-03-15', '2024-03-15', 5200.00, 'Wire',        'Paid');
INSERT OR IGNORE INTO premium_payments VALUES (6,  106, '2023-10-01', '2023-09-28', 1800.00, 'ACH',         'Paid');
INSERT OR IGNORE INTO premium_payments VALUES (7,  107, '2024-04-01', '2024-04-02', 1100.00, 'Credit Card', 'Paid');
INSERT OR IGNORE INTO premium_payments VALUES (8,  108, '2023-12-01', '2023-12-01', 4200.00, 'ACH',         'Paid');
INSERT OR IGNORE INTO premium_payments VALUES (9,  109, '2024-05-15', NULL,          875.00, 'Check',       'Overdue');
INSERT OR IGNORE INTO premium_payments VALUES (10, 110, '2022-07-01', '2022-07-01', 3100.00, 'ACH',         'Paid');
INSERT OR IGNORE INTO premium_payments VALUES (11, 111, '2024-02-01', '2024-02-01', 6500.00, 'Wire',        'Paid');
INSERT OR IGNORE INTO premium_payments VALUES (12, 112, '2023-08-01', '2023-07-30', 1350.00, 'Credit Card', 'Paid');
INSERT OR IGNORE INTO premium_payments VALUES (13, 113, '2024-06-01', NULL,         3200.00, 'ACH',         'Pending');
INSERT OR IGNORE INTO premium_payments VALUES (14, 114, '2024-03-01', '2024-02-28', 2200.00, 'Check',       'Paid');
INSERT OR IGNORE INTO premium_payments VALUES (15, 115, '2023-11-01', NULL,          990.00, 'Credit Card', 'Overdue');

-- Insured Properties
INSERT OR IGNORE INTO insured_properties VALUES (1, 102, 'Residential', 'FL', 1985, 320000.00, 'Owner-Occupied');
INSERT OR IGNORE INTO insured_properties VALUES (2, 106, 'Commercial',  'GA', 2002, 540000.00, 'Rental');
INSERT OR IGNORE INTO insured_properties VALUES (3, 110, 'Residential', 'FL', 1970, 180000.00, 'Owner-Occupied');
INSERT OR IGNORE INTO insured_properties VALUES (4, 114, 'Commercial',  'NY', 1998, 850000.00, 'Rental');
INSERT OR IGNORE INTO insured_properties VALUES (5, 119, 'Residential', 'CA', 2005, 420000.00, 'Owner-Occupied');
INSERT OR IGNORE INTO insured_properties VALUES (6, 116, 'Industrial',  'CA', 1995,1200000.00, 'Owner-Occupied');
INSERT OR IGNORE INTO insured_properties VALUES (7, 105, 'Commercial',  'NY', 2010, 650000.00, 'Rental');
INSERT OR IGNORE INTO insured_properties VALUES (8, 111, 'Commercial',  'CA', 2000, 980000.00, 'Owner-Occupied');

-- Insured Vehicles
INSERT OR IGNORE INTO insured_vehicles VALUES (1,  101, 'Toyota',    'Camry',   2021, '1HGBH41JXMN109186',  28000.00);
INSERT OR IGNORE INTO insured_vehicles VALUES (2,  104, 'Honda',     'Civic',   2022, '2T1BURHE0JC043821',  24000.00);
INSERT OR IGNORE INTO insured_vehicles VALUES (3,  107, 'Ford',      'F-150',   2020, '1FTFW1ET5DFC10312',  42000.00);
INSERT OR IGNORE INTO insured_vehicles VALUES (4,  109, 'Chevrolet', 'Malibu',  2019, '1G1ZD5ST3JF123456',  21000.00);
INSERT OR IGNORE INTO insured_vehicles VALUES (5,  112, 'BMW',       '3 Series',2021, 'WBA5R1C55KAK12345',  52000.00);
INSERT OR IGNORE INTO insured_vehicles VALUES (6,  115, 'Nissan',    'Altima',  2020, '1N4AL3AP8JC234567',  23000.00);
INSERT OR IGNORE INTO insured_vehicles VALUES (7,  118, 'Tesla',     'Model 3', 2023, '5YJ3E1EA7JF123456',  48000.00);
INSERT OR IGNORE INTO insured_vehicles VALUES (8,  120, 'Jeep',      'Wrangler',2018, '1C4BJWDG4JL876543',  32000.00);
INSERT OR IGNORE INTO insured_vehicles VALUES (9,  103, 'Subaru',    'Outback', 2022, '4S4BSANC5J3456789',  31000.00);
INSERT OR IGNORE INTO insured_vehicles VALUES (10, 113, 'Hyundai',   'Elantra', 2021, '5NPD74LF4JH567890',  22000.00);

-- Risk Assessments
INSERT OR IGNORE INTO risk_assessments VALUES (1,  101, 1, '2023-01-10', 3.2, 'Low',       NULL);
INSERT OR IGNORE INTO risk_assessments VALUES (2,  102, 2, '2023-02-15', 6.8, 'High',      'Coastal property, flood risk');
INSERT OR IGNORE INTO risk_assessments VALUES (3,  103, 4, '2023-05-20', 4.5, 'Medium',    NULL);
INSERT OR IGNORE INTO risk_assessments VALUES (4,  104, 1, '2023-12-15', 2.9, 'Low',       NULL);
INSERT OR IGNORE INTO risk_assessments VALUES (5,  105, 3, '2024-01-20', 8.1, 'Very High', 'Commercial liability exposure');
INSERT OR IGNORE INTO risk_assessments VALUES (6,  106, 2, '2023-08-10', 5.5, 'Medium',    'Aging property');
INSERT OR IGNORE INTO risk_assessments VALUES (7,  108, 4, '2023-10-15', 3.8, 'Low',       NULL);
INSERT OR IGNORE INTO risk_assessments VALUES (8,  111, 3, '2023-12-20', 7.6, 'High',      'High liability limits');
INSERT OR IGNORE INTO risk_assessments VALUES (9,  113, 1, '2024-04-10', 3.1, 'Low',       NULL);
INSERT OR IGNORE INTO risk_assessments VALUES (10, 114, 2, '2024-01-25', 5.2, 'Medium',    'Commercial property');

-- Inspection Reports
INSERT OR IGNORE INTO inspection_reports VALUES (1, 102, '2023-02-20', 'Redacted', 'Fair',      3, 1);
INSERT OR IGNORE INTO inspection_reports VALUES (2, 106, '2023-08-15', 'Redacted', 'Poor',      7, 0);
INSERT OR IGNORE INTO inspection_reports VALUES (3, 110, '2022-06-05', 'Redacted', 'Fair',      2, 1);
INSERT OR IGNORE INTO inspection_reports VALUES (4, 114, '2024-01-28', 'Redacted', 'Good',      1, 1);
INSERT OR IGNORE INTO inspection_reports VALUES (5, 119, '2023-07-30', 'Redacted', 'Excellent', 0, 1);
INSERT OR IGNORE INTO inspection_reports VALUES (6, 116, '2023-03-10', 'Redacted', 'Fair',      4, 0);
INSERT OR IGNORE INTO inspection_reports VALUES (7, 105, '2024-02-05', 'Redacted', 'Good',      2, 1);
INSERT OR IGNORE INTO inspection_reports VALUES (8, 111, '2023-12-15', 'Redacted', 'Poor',      8, 0);

-- Claim Documents
INSERT OR IGNORE INTO claim_documents VALUES (1,  1001, 'Police Report',  '2023-03-11', 1);
INSERT OR IGNORE INTO claim_documents VALUES (2,  1002, 'Photo',          '2023-04-21', 1);
INSERT OR IGNORE INTO claim_documents VALUES (3,  1002, 'Estimate',       '2023-04-25', 1);
INSERT OR IGNORE INTO claim_documents VALUES (4,  1003, 'Medical Record', '2023-07-16', 0);
INSERT OR IGNORE INTO claim_documents VALUES (5,  1004, 'Police Report',  '2024-02-02', 1);
INSERT OR IGNORE INTO claim_documents VALUES (6,  1005, 'Photo',          '2024-03-11', 1);
INSERT OR IGNORE INTO claim_documents VALUES (7,  1005, 'Affidavit',      '2024-03-15', 0);
INSERT OR IGNORE INTO claim_documents VALUES (8,  1006, 'Estimate',       '2023-10-06', 1);
INSERT OR IGNORE INTO claim_documents VALUES (9,  1008, 'Medical Record', '2024-01-11', 1);
INSERT OR IGNORE INTO claim_documents VALUES (10, 1011, 'Affidavit',      '2024-02-16', 0);
INSERT OR IGNORE INTO claim_documents VALUES (11, 1016, 'Photo',          '2023-05-02', 1);
INSERT OR IGNORE INTO claim_documents VALUES (12, 1016, 'Police Report',  '2023-05-03', 1);
INSERT OR IGNORE INTO claim_documents VALUES (13, 1022, 'Medical Record', '2024-01-06', 0);
INSERT OR IGNORE INTO claim_documents VALUES (14, 1007, 'Estimate',       '2024-04-02', 1);
INSERT OR IGNORE INTO claim_documents VALUES (15, 1014, 'Photo',          '2024-03-16', 1);

-- Claim Assessments
INSERT OR IGNORE INTO claim_assessments VALUES (1,  1001, 1,  '2023-03-15', 8200.00,  8500.00,  NULL);
INSERT OR IGNORE INTO claim_assessments VALUES (2,  1002, 2,  '2023-04-25', 45000.00, 42000.00, 'Inflated amount suspected');
INSERT OR IGNORE INTO claim_assessments VALUES (3,  1004, 1,  '2024-02-05', 3100.00,  3200.00,  NULL);
INSERT OR IGNORE INTO claim_assessments VALUES (4,  1006, 5,  '2023-10-10', 30000.00, 0.00,     'Denied - policy exclusion');
INSERT OR IGNORE INTO claim_assessments VALUES (5,  1007, 6,  '2024-04-05', 5400.00,  5600.00,  NULL);
INSERT OR IGNORE INTO claim_assessments VALUES (6,  1010, 2,  '2023-01-20', 18000.00, 18500.00, NULL);
INSERT OR IGNORE INTO claim_assessments VALUES (7,  1014, 5,  '2024-03-20', 30500.00, 31000.00, NULL);
INSERT OR IGNORE INTO claim_assessments VALUES (8,  1016, 4,  '2023-05-10', 55000.00, 55000.00, 'Staged incident confirmed by SIU');
INSERT OR IGNORE INTO claim_assessments VALUES (9,  1019, 10, '2023-09-15', 14200.00, 14500.00, NULL);
INSERT OR IGNORE INTO claim_assessments VALUES (10, 1021, 9,  '2023-06-20', 11000.00, 11200.00, NULL);

-- Claim Payments
INSERT OR IGNORE INTO claim_payments VALUES (1,  1001, '2023-04-07', 8500.00,  'ACH',   'Cleared');
INSERT OR IGNORE INTO claim_payments VALUES (2,  1002, '2023-06-05', 42000.00, 'Wire',  'Cleared');
INSERT OR IGNORE INTO claim_payments VALUES (3,  1004, '2024-03-01', 3200.00,  'Check', 'Cleared');
INSERT OR IGNORE INTO claim_payments VALUES (4,  1007, '2024-04-28', 5600.00,  'ACH',   'Cleared');
INSERT OR IGNORE INTO claim_payments VALUES (5,  1009, '2024-05-22', 2100.00,  'Check', 'Cleared');
INSERT OR IGNORE INTO claim_payments VALUES (6,  1010, '2023-03-05', 18500.00, 'Wire',  'Cleared');
INSERT OR IGNORE INTO claim_payments VALUES (7,  1012, '2023-09-10', 7800.00,  'ACH',   'Cleared');
INSERT OR IGNORE INTO claim_payments VALUES (8,  1014, '2024-04-15', 31000.00, 'Wire',  'Cleared');
INSERT OR IGNORE INTO claim_payments VALUES (9,  1016, '2023-06-20', 55000.00, 'Wire',  'Cleared');
INSERT OR IGNORE INTO claim_payments VALUES (10, 1019, '2023-10-30', 14500.00, 'ACH',   'Cleared');
INSERT OR IGNORE INTO claim_payments VALUES (11, 1020, '2023-03-05', 3900.00,  'Check', 'Cleared');
INSERT OR IGNORE INTO claim_payments VALUES (12, 1021, '2023-07-25', 11200.00, 'ACH',   'Cleared');

-- Claim Appeals
INSERT OR IGNORE INTO claim_appeals VALUES (1, 1006, '2023-12-01', 'Dispute exclusion application', 'Upheld',     '2024-01-15');
INSERT OR IGNORE INTO claim_appeals VALUES (2, 1015, '2024-03-01', 'Amount too low',                'Overturned', '2024-04-10');
INSERT OR IGNORE INTO claim_appeals VALUES (3, 1025, '2024-05-20', 'Denial unjustified',            NULL,         NULL);
INSERT OR IGNORE INTO claim_appeals VALUES (4, 1003, '2024-02-01', 'Delay in processing',           'Partial',    '2024-03-15');
INSERT OR IGNORE INTO claim_appeals VALUES (5, 1022, '2024-02-10', 'Coverage scope dispute',        NULL,         NULL);

-- Repair Vendors
INSERT OR IGNORE INTO repair_vendors VALUES (1, 'Redacted', 'Auto Body',   'Northeast', 4.5, 1);
INSERT OR IGNORE INTO repair_vendors VALUES (2, 'Redacted', 'Auto Body',   'Southeast', 4.2, 1);
INSERT OR IGNORE INTO repair_vendors VALUES (3, 'Redacted', 'Roofing',     'Southeast', 4.7, 1);
INSERT OR IGNORE INTO repair_vendors VALUES (4, 'Redacted', 'Plumbing',    'Midwest',   3.9, 1);
INSERT OR IGNORE INTO repair_vendors VALUES (5, 'Redacted', 'Electrical',  'West',      4.6, 1);
INSERT OR IGNORE INTO repair_vendors VALUES (6, 'Redacted', 'General',     'Northeast', 4.1, 1);
INSERT OR IGNORE INTO repair_vendors VALUES (7, 'Redacted', 'Auto Body',   'West',      3.8, 0);
INSERT OR IGNORE INTO repair_vendors VALUES (8, 'Redacted', 'Roofing',     'Midwest',   4.3, 1);

-- Repair Estimates
INSERT OR IGNORE INTO repair_estimates VALUES (1,  1001, 1, '2023-03-12', 8200.00,  1, 8200.00);
INSERT OR IGNORE INTO repair_estimates VALUES (2,  1004, 1, '2024-02-03', 3100.00,  1, 3100.00);
INSERT OR IGNORE INTO repair_estimates VALUES (3,  1002, 3, '2023-04-22', 46000.00, 0, NULL);
INSERT OR IGNORE INTO repair_estimates VALUES (4,  1006, 3, '2023-10-08', 29500.00, 0, NULL);
INSERT OR IGNORE INTO repair_estimates VALUES (5,  1007, 2, '2024-04-03', 5500.00,  1, 5500.00);
INSERT OR IGNORE INTO repair_estimates VALUES (6,  1010, 4, '2023-01-17', 18000.00, 1, 18000.00);
INSERT OR IGNORE INTO repair_estimates VALUES (7,  1012, 1, '2023-08-12', 7600.00,  1, 7600.00);
INSERT OR IGNORE INTO repair_estimates VALUES (8,  1014, 5, '2024-03-17', 31000.00, 1, 31000.00);
INSERT OR IGNORE INTO repair_estimates VALUES (9,  1016, 6, '2023-05-03', 58000.00, 0, NULL);
INSERT OR IGNORE INTO repair_estimates VALUES (10, 1019, 4, '2023-09-12', 14500.00, 1, 14500.00);

-- Investigators
INSERT OR IGNORE INTO investigators VALUES (1, 'Redacted', 'Auto Fraud',     'Northeast', 1);
INSERT OR IGNORE INTO investigators VALUES (2, 'Redacted', 'Property Fraud', 'Southeast', 1);
INSERT OR IGNORE INTO investigators VALUES (3, 'Redacted', 'Medical Fraud',  'Midwest',   1);
INSERT OR IGNORE INTO investigators VALUES (4, 'Redacted', 'Identity Theft', 'West',      1);
INSERT OR IGNORE INTO investigators VALUES (5, 'Redacted', 'Property Fraud', 'Northeast', 0);

-- Fraud Investigations
INSERT OR IGNORE INTO fraud_investigations VALUES (1, 1002, 2, '2023-05-01', '2023-06-30', 'Confirmed Fraud',   1, 18000.00);
INSERT OR IGNORE INTO fraud_investigations VALUES (2, 1005, 1, '2024-03-15', NULL,          NULL,               0,     0.00);
INSERT OR IGNORE INTO fraud_investigations VALUES (3, 1006, 2, '2023-10-10', '2023-12-15', 'Confirmed Fraud',   1, 28000.00);
INSERT OR IGNORE INTO fraud_investigations VALUES (4, 1008, 4, '2024-01-20', '2024-03-31', 'No Fraud Found',    0,     0.00);
INSERT OR IGNORE INTO fraud_investigations VALUES (5, 1011, 3, '2024-03-01', NULL,          NULL,               0,     0.00);
INSERT OR IGNORE INTO fraud_investigations VALUES (6, 1016, 2, '2023-05-15', '2023-08-01', 'Confirmed Fraud',   1, 55000.00);
INSERT OR IGNORE INTO fraud_investigations VALUES (7, 1022, 1, '2024-01-15', '2024-04-30', 'Inconclusive',      0,     0.00);
INSERT OR IGNORE INTO fraud_investigations VALUES (8, 1003, 4, '2023-08-01', '2023-10-20', 'Confirmed Fraud',   1, 12000.00);

-- Reserve Estimates
INSERT OR IGNORE INTO reserve_estimates VALUES (1,  1003, '2023-07-20', 15000.00,  'Case Reserve', '2023-07-20');
INSERT OR IGNORE INTO reserve_estimates VALUES (2,  1005, '2024-03-15', 100000.00, 'Case Reserve', '2024-03-15');
INSERT OR IGNORE INTO reserve_estimates VALUES (3,  1008, '2024-01-15', 70000.00,  'Case Reserve', '2024-02-01');
INSERT OR IGNORE INTO reserve_estimates VALUES (4,  1011, '2024-02-20', 125000.00, 'Case Reserve', '2024-03-01');
INSERT OR IGNORE INTO reserve_estimates VALUES (5,  1013, '2024-06-05', 9000.00,   'Case Reserve', '2024-06-05');
INSERT OR IGNORE INTO reserve_estimates VALUES (6,  1017, '2024-02-25', 22000.00,  'Case Reserve', '2024-02-25');
INSERT OR IGNORE INTO reserve_estimates VALUES (7,  1018, '2024-07-05', 6500.00,   'Case Reserve', '2024-07-05');
INSERT OR IGNORE INTO reserve_estimates VALUES (8,  1022, '2024-01-10', 40000.00,  'Case Reserve', '2024-01-10');
INSERT OR IGNORE INTO reserve_estimates VALUES (9,  1024, '2024-03-25', 5000.00,   'Case Reserve', '2024-03-25');
INSERT OR IGNORE INTO reserve_estimates VALUES (10, 1005, '2024-04-01', 95000.00,  'IBNR',         '2024-04-01');

-- Regulatory Filings
INSERT OR IGNORE INTO regulatory_filings VALUES (1, 'NY', '2024-01-15', 'Rate Filing',         'Approved',  '2024-01-31', NULL);
INSERT OR IGNORE INTO regulatory_filings VALUES (2, 'CA', '2024-02-01', 'Rate Filing',         'Pending',   '2024-03-01', 'Under DOI review');
INSERT OR IGNORE INTO regulatory_filings VALUES (3, 'FL', '2024-01-20', 'Financial Statement', 'Approved',  '2024-02-01', NULL);
INSERT OR IGNORE INTO regulatory_filings VALUES (4, 'TX', '2023-12-01', 'Market Conduct',      'Approved',  '2024-01-01', NULL);
INSERT OR IGNORE INTO regulatory_filings VALUES (5, 'IL', '2024-03-01', 'Form Filing',         'Submitted', '2024-04-01', NULL);
INSERT OR IGNORE INTO regulatory_filings VALUES (6, 'GA', '2024-02-15', 'Rate Filing',         'Rejected',  '2024-03-01', 'Rate increase denied');

-- Compliance Audits
INSERT OR IGNORE INTO compliance_audits VALUES (1, '2024-01-10', 'Redacted', 'Claims Processing', 3, 'Needs Improvement');
INSERT OR IGNORE INTO compliance_audits VALUES (2, '2023-10-15', 'Redacted', 'Underwriting',      1, 'Satisfactory');
INSERT OR IGNORE INTO compliance_audits VALUES (3, '2024-02-20', 'Redacted', 'Agent Conduct',     0, 'Satisfactory');
INSERT OR IGNORE INTO compliance_audits VALUES (4, '2023-07-05', 'Redacted', 'Data Privacy',      5, 'Unsatisfactory');
INSERT OR IGNORE INTO compliance_audits VALUES (5, '2024-03-15', 'Redacted', 'Claims Processing', 2, 'Needs Improvement');

-- Agent Performance
INSERT OR IGNORE INTO agent_performance VALUES (1,  1, '2024-Q1', 8,  12, 45000.00, 2700.00);
INSERT OR IGNORE INTO agent_performance VALUES (2,  1, '2023-Q4', 10, 15, 58000.00, 3480.00);
INSERT OR IGNORE INTO agent_performance VALUES (3,  2, '2024-Q1', 6,   9, 32000.00, 1760.00);
INSERT OR IGNORE INTO agent_performance VALUES (4,  2, '2023-Q4', 7,  11, 38000.00, 2090.00);
INSERT OR IGNORE INTO agent_performance VALUES (5,  3, '2024-Q1', 5,   8, 26000.00, 1300.00);
INSERT OR IGNORE INTO agent_performance VALUES (6,  3, '2023-Q4', 4,   7, 22000.00, 1100.00);
INSERT OR IGNORE INTO agent_performance VALUES (7,  4, '2024-Q1', 9,  14, 52000.00, 3380.00);
INSERT OR IGNORE INTO agent_performance VALUES (8,  4, '2023-Q4', 11, 16, 64000.00, 4160.00);
INSERT OR IGNORE INTO agent_performance VALUES (9,  5, '2024-Q1', 4,   6, 18000.00,  900.00);
INSERT OR IGNORE INTO agent_performance VALUES (10, 5, '2023-Q4', 3,   5, 14000.00,  700.00);

-- Customer Risk Profiles
INSERT OR IGNORE INTO customer_risk_profiles VALUES (1, 1, '2024-01-01', 72.5, 80.0, 75.0, 'Preferred');
INSERT OR IGNORE INTO customer_risk_profiles VALUES (2, 2, '2024-01-01', 58.0, 55.0, 62.0, 'Standard');
INSERT OR IGNORE INTO customer_risk_profiles VALUES (3, 3, '2024-01-01', 78.0, 82.0, 80.0, 'Preferred');
INSERT OR IGNORE INTO customer_risk_profiles VALUES (4, 4, '2024-01-01', 44.0, 40.0, 48.0, 'Non-Standard');
INSERT OR IGNORE INTO customer_risk_profiles VALUES (5, 5, '2024-01-01', 65.0, 70.0, 68.0, 'Standard');
INSERT OR IGNORE INTO customer_risk_profiles VALUES (6, 6, '2024-01-01', 81.0, 85.0, 82.0, 'Preferred');
INSERT OR IGNORE INTO customer_risk_profiles VALUES (7, 7, '2024-01-01', 38.0, 35.0, 40.0, 'High Risk');
INSERT OR IGNORE INTO customer_risk_profiles VALUES (8, 8, '2024-01-01', 70.0, 72.0, 74.0, 'Preferred');

-- Adjusters
INSERT INTO adjusters VALUES (1, 'Sarah Mitchell', 'Northeast', 'Auto');
INSERT INTO adjusters VALUES (2, 'James Okafor', 'Southeast', 'Property');
INSERT INTO adjusters VALUES (3, 'Linda Chen', 'Midwest', 'Health');
INSERT INTO adjusters VALUES (4, 'Robert Torres', 'West', 'Liability');
INSERT INTO adjusters VALUES (5, 'Emily Watson', 'Northeast', 'Property');
INSERT INTO adjusters VALUES (6, 'David Kim', 'Southeast', 'Auto');
INSERT INTO adjusters VALUES (7, 'Angela Brooks', 'Midwest', 'Auto');
INSERT INTO adjusters VALUES (8, 'Marcus Johnson', 'West', 'Health');
INSERT INTO adjusters VALUES (9, 'Priya Patel', 'Northeast', 'Liability');
INSERT INTO adjusters VALUES (10, 'Carlos Rivera', 'Southeast', 'Property');

-- Policies
INSERT INTO policies VALUES (101, 'Redacted', 'Insurance', 'Auto', '2023-01-15', '2024-01-15', 1200.00, 'Expired');
INSERT INTO policies VALUES (102, 'Redacted', 'Insurance', 'Property', '2023-03-01', '2024-03-01', 2500.00, 'Expired');
INSERT INTO policies VALUES (103, 'Redacted', 'Insurance', 'Health', '2023-06-01', '2024-06-01', 3800.00, 'Active');
INSERT INTO policies VALUES (104, 'Redacted', 'Insurance', 'Auto', '2024-01-01', '2025-01-01', 950.00, 'Active');
INSERT INTO policies VALUES (105, 'Redacted', 'Insurance', 'Liability', '2024-02-15', '2025-02-15', 5200.00, 'Active');
INSERT INTO policies VALUES (106, 'Redacted', 'Insurance', 'Property', '2023-09-01', '2024-09-01', 1800.00, 'Active');
INSERT INTO policies VALUES (107, 'Redacted', 'Insurance', 'Auto', '2024-03-01', '2025-03-01', 1100.00, 'Active');
INSERT INTO policies VALUES (108, 'Redacted', 'Insurance', 'Health', '2023-11-01', '2024-11-01', 4200.00, 'Active');
INSERT INTO policies VALUES (109, 'Redacted', 'Insurance', 'Auto', '2024-04-15', '2025-04-15', 875.00, 'Active');
INSERT INTO policies VALUES (110, 'Redacted', 'Insurance', 'Property', '2022-06-01', '2023-06-01', 3100.00, 'Expired');
INSERT INTO policies VALUES (111, 'Redacted', 'Insurance', 'Liability', '2024-01-01', '2025-01-01', 6500.00, 'Active');
INSERT INTO policies VALUES (112, 'Redacted', 'Insurance', 'Auto', '2023-07-01', '2024-07-01', 1350.00, 'Active');
INSERT INTO policies VALUES (113, 'Redacted', 'Insurance', 'Health', '2024-05-01', '2025-05-01', 3200.00, 'Active');
INSERT INTO policies VALUES (114, 'Redacted', 'Insurance', 'Property', '2024-02-01', '2025-02-01', 2200.00, 'Active');
INSERT INTO policies VALUES (115, 'Redacted', 'Insurance', 'Auto', '2023-10-01', '2024-10-01', 990.00, 'Cancelled');
INSERT INTO policies VALUES (116, 'Redacted', 'Insurance', 'Liability', '2023-04-01', '2024-04-01', 4800.00, 'Expired');
INSERT INTO policies VALUES (117, 'Redacted', 'Insurance', 'Health', '2024-01-15', '2025-01-15', 5100.00, 'Active');
INSERT INTO policies VALUES (118, 'Redacted', 'Insurance', 'Auto', '2024-06-01', '2025-06-01', 1050.00, 'Active');
INSERT INTO policies VALUES (119, 'Redacted', 'Insurance', 'Property', '2023-08-01', '2024-08-01', 1950.00, 'Active');
INSERT INTO policies VALUES (120, 'Redacted', 'Insurance', 'Auto', '2022-12-01', '2023-12-01', 800.00, 'Expired');

-- Claims
INSERT INTO claims VALUES (1001, 101, 1, '2023-03-10', '2023-04-05', 8500.00, 'Approved', 'Low');
INSERT INTO claims VALUES (1002, 102, 2, '2023-04-20', '2023-05-30', 42000.00, 'Approved', 'High');
INSERT INTO claims VALUES (1003, 103, 3, '2023-07-15', NULL, 15200.00, 'Under Review', 'Medium');
INSERT INTO claims VALUES (1004, 104, 1, '2024-02-01', '2024-02-28', 3200.00, 'Approved', 'Low');
INSERT INTO claims VALUES (1005, 105, 4, '2024-03-10', NULL, 95000.00, 'Open', 'High');
INSERT INTO claims VALUES (1006, 106, 5, '2023-10-05', '2023-11-20', 28000.00, 'Denied', 'High');
INSERT INTO claims VALUES (1007, 107, 6, '2024-04-01', '2024-04-25', 5600.00, 'Approved', 'Low');
INSERT INTO claims VALUES (1008, 108, 3, '2024-01-10', NULL, 67000.00, 'Under Review', 'High');
INSERT INTO claims VALUES (1009, 109, 7, '2024-05-01', '2024-05-20', 2100.00, 'Approved', 'Low');
INSERT INTO claims VALUES (1010, 110, 2, '2023-01-15', '2023-02-28', 18500.00, 'Approved', 'Medium');
INSERT INTO claims VALUES (1011, 111, 4, '2024-02-15', NULL, 120000.00, 'Open', 'High');
INSERT INTO claims VALUES (1012, 112, 6, '2023-08-10', '2023-09-05', 7800.00, 'Approved', 'Low');
INSERT INTO claims VALUES (1013, 113, 3, '2024-06-01', NULL, 9500.00, 'Open', 'Medium');
INSERT INTO claims VALUES (1014, 114, 5, '2024-03-15', '2024-04-10', 31000.00, 'Approved', 'Medium');
INSERT INTO claims VALUES (1015, 115, 7, '2024-01-20', '2024-02-10', 4200.00, 'Denied', 'Low');
INSERT INTO claims VALUES (1016, 116, 4, '2023-05-01', '2023-06-15', 55000.00, 'Approved', 'High');
INSERT INTO claims VALUES (1017, 117, 8, '2024-02-20', NULL, 22000.00, 'Under Review', 'Medium');
INSERT INTO claims VALUES (1018, 118, 1, '2024-07-01', NULL, 6800.00, 'Open', 'Low');
INSERT INTO claims VALUES (1019, 119, 10, '2023-09-10', '2023-10-25', 14500.00, 'Approved', 'Medium');
INSERT INTO claims VALUES (1020, 120, 6, '2023-02-05', '2023-03-01', 3900.00, 'Approved', 'Low');
INSERT INTO claims VALUES (1021, 101, 9, '2023-06-12', '2023-07-20', 11200.00, 'Approved', 'Medium');
INSERT INTO claims VALUES (1022, 103, 8, '2024-01-05', NULL, 38000.00, 'Under Review', 'High');
INSERT INTO claims VALUES (1023, 106, 2, '2024-02-28', '2024-03-30', 19000.00, 'Approved', 'Medium');
INSERT INTO claims VALUES (1024, 108, 3, '2024-03-20', NULL, 5500.00, 'Open', 'Low');
INSERT INTO claims VALUES (1025, 112, 7, '2024-04-10', '2024-05-01', 8900.00, 'Denied', 'Medium');

-- Claimants (names redacted for PII compliance)
INSERT INTO claimants VALUES (2001, 1001, 'Redacted', 'redacted@email.com', 'NY');
INSERT INTO claimants VALUES (2002, 1002, 'Redacted', 'redacted@email.com', 'FL');
INSERT INTO claimants VALUES (2003, 1003, 'Redacted', 'redacted@email.com', 'IL');
INSERT INTO claimants VALUES (2004, 1004, 'Redacted', 'redacted@email.com', 'NY');
INSERT INTO claimants VALUES (2005, 1005, 'Redacted', 'redacted@email.com', 'CA');
INSERT INTO claimants VALUES (2006, 1006, 'Redacted', 'redacted@email.com', 'GA');
INSERT INTO claimants VALUES (2007, 1007, 'Redacted', 'redacted@email.com', 'WA');
INSERT INTO claimants VALUES (2008, 1008, 'Redacted', 'redacted@email.com', 'IL');
INSERT INTO claimants VALUES (2009, 1009, 'Redacted', 'redacted@email.com', 'WA');
INSERT INTO claimants VALUES (2010, 1010, 'Redacted', 'redacted@email.com', 'FL');
INSERT INTO claimants VALUES (2011, 1011, 'Redacted', 'redacted@email.com', 'CA');
INSERT INTO claimants VALUES (2012, 1012, 'Redacted', 'redacted@email.com', 'GA');
INSERT INTO claimants VALUES (2013, 1013, 'Redacted', 'redacted@email.com', 'IL');
INSERT INTO claimants VALUES (2014, 1014, 'Redacted', 'redacted@email.com', 'NY');
INSERT INTO claimants VALUES (2015, 1015, 'Redacted', 'redacted@email.com', 'WA');
INSERT INTO claimants VALUES (2016, 1016, 'Redacted', 'redacted@email.com', 'CA');
INSERT INTO claimants VALUES (2017, 1017, 'Redacted', 'redacted@email.com', 'NY');
INSERT INTO claimants VALUES (2018, 1018, 'Redacted', 'redacted@email.com', 'WA');
INSERT INTO claimants VALUES (2019, 1019, 'Redacted', 'redacted@email.com', 'FL');
INSERT INTO claimants VALUES (2020, 1020, 'Redacted', 'redacted@email.com', 'GA');
INSERT INTO claimants VALUES (2021, 1021, 'Redacted', 'redacted@email.com', 'NY');
INSERT INTO claimants VALUES (2022, 1022, 'Redacted', 'redacted@email.com', 'IL');
INSERT INTO claimants VALUES (2023, 1023, 'Redacted', 'redacted@email.com', 'GA');
INSERT INTO claimants VALUES (2024, 1024, 'Redacted', 'redacted@email.com', 'IL');
INSERT INTO claimants VALUES (2025, 1025, 'Redacted', 'redacted@email.com', 'GA');

-- Fraud Flags
INSERT INTO fraud_flags VALUES (3001, 1002, 'Inflated Amount', '2023-05-01', 1, 18000.00);
INSERT INTO fraud_flags VALUES (3002, 1005, 'Staged Incident', '2024-03-15', 0, 0.00);
INSERT INTO fraud_flags VALUES (3003, 1006, 'Duplicate', '2023-10-10', 1, 28000.00);
INSERT INTO fraud_flags VALUES (3004, 1008, 'Identity Mismatch', '2024-01-20', 0, 0.00);
INSERT INTO fraud_flags VALUES (3005, 1011, 'Inflated Amount', '2024-03-01', 0, 0.00);
INSERT INTO fraud_flags VALUES (3006, 1016, 'Staged Incident', '2023-05-15', 1, 55000.00);
INSERT INTO fraud_flags VALUES (3007, 1022, 'Duplicate', '2024-01-15', 0, 0.00);
INSERT INTO fraud_flags VALUES (3008, 1003, 'Identity Mismatch', '2023-08-01', 1, 12000.00);
INSERT INTO fraud_flags VALUES (3009, 1025, 'Inflated Amount', '2024-04-15', 0, 0.00);
INSERT INTO fraud_flags VALUES (3010, 1017, 'Staged Incident', '2024-03-01', 0, 0.00);

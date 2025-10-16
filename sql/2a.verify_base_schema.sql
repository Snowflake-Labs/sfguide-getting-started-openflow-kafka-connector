-- ============================================================================
-- Copyright 2025 Snowflake Inc.
-- SPDX-License-Identifier: Apache-2.0
-- Licensed under the Apache License, Version 2.0 (the "License");
-- You may obtain a copy of the License at: http://www.apache.org/licenses/LICENSE-2.0
-- ============================================================================
--
-- Openflow Kafka Connector Quickstart - Phase 1: Verify Base Schema
--
-- This script verifies the initial data ingestion and base table schema.
-- Run this AFTER producing the base sample logs (sample_logs.json)
-- BEFORE producing the extended logs (sample_logs_extended.json).
-- ============================================================================

-- Set context
USE ROLE QUICKSTART_ROLE;
USE DATABASE QUICKSTART_KAFKA_CONNECTOR_DB;
USE SCHEMA PUBLIC;
USE WAREHOUSE QUICKSTART_KAFKA_CONNECTOR_WH;

/*****************************************************
| * 1. Verify Table Creation
| *****************************************************/

-- Check that the APPLICATION-LOGS table was auto-created
SHOW TABLES LIKE 'APPLICATION-LOGS';

-- Expected: You should see the APPLICATION-LOGS table created by Openflow

/*****************************************************
| * 2. Check Initial Base Schema
| *****************************************************/

-- Show columns with data types (sorted alphabetically for easy comparison)
SELECT 
  COLUMN_NAME, 
  DATA_TYPE,
  ORDINAL_POSITION
FROM QUICKSTART_KAFKA_CONNECTOR_DB.INFORMATION_SCHEMA.COLUMNS 
WHERE TABLE_NAME ILIKE 'APPLICATION-LOGS'
ORDER BY COLUMN_NAME;

-- Expected columns (from base schema, sorted alphabetically):
-- AMOUNT, DURATION_MS, ERROR, HOST, LEVEL, MESSAGE, 
-- REQUEST_ID, SERVICE, STATUS_CODE, TIMESTAMP, USER_ID
-- 
-- That's 11 base columns total.

-- 📸 IMPORTANT: Note these columns! In Phase 2, we'll run this query again
-- and see MANY NEW columns appear automatically when we ingest evolved logs!

/*****************************************************
| * 3. Basic Row Count
| *****************************************************/

-- Check how many records were ingested
SELECT COUNT(*) as TOTAL_RECORDS 
FROM "APPLICATION-LOGS";

-- Expected: Around 25 records from sample_logs.json

/*****************************************************
| * 4. View Sample Records
| *****************************************************/

-- View the base data structure
SELECT *
FROM "APPLICATION-LOGS"
LIMIT 10;

-- View specific columns
SELECT 
  TIMESTAMP,
  LEVEL,
  SERVICE,
  HOST,
  MESSAGE,
  STATUS_CODE,
  DURATION_MS,
  REQUEST_ID
FROM "APPLICATION-LOGS"
ORDER BY TIMESTAMP DESC
LIMIT 10;

/*****************************************************
| * 5. Log Level Distribution
| *****************************************************/

-- Analyze logs by level
SELECT 
  LEVEL,
  COUNT(*) as LOG_COUNT,
  ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 1) as PERCENTAGE
FROM "APPLICATION-LOGS"
GROUP BY LEVEL
ORDER BY LOG_COUNT DESC;

-- Expected: Mix of INFO, WARN, and ERROR logs

/*****************************************************
| * 6. Service Distribution
| *****************************************************/

-- See which services are logging
SELECT 
  SERVICE,
  COUNT(*) as LOG_COUNT,
  COUNT(DISTINCT HOST) as HOST_COUNT
FROM "APPLICATION-LOGS"
GROUP BY SERVICE
ORDER BY LOG_COUNT DESC;

/*****************************************************
| * 7. Error Analysis
| *****************************************************/

-- Show all error logs (using the ERROR field)
SELECT 
  TIMESTAMP,
  SERVICE,
  HOST,
  MESSAGE,
  ERROR,
  STATUS_CODE,
  DURATION_MS
FROM "APPLICATION-LOGS"
WHERE ERROR IS NOT NULL
ORDER BY TIMESTAMP DESC;

-- Count errors by type
SELECT 
  ERROR,
  COUNT(*) as ERROR_COUNT
FROM "APPLICATION-LOGS"
WHERE ERROR IS NOT NULL
GROUP BY ERROR
ORDER BY ERROR_COUNT DESC;

/*****************************************************
| * 8. Performance Analysis
| *****************************************************/

-- Find slow requests (duration > 1000ms)
SELECT 
  TIMESTAMP,
  SERVICE,
  MESSAGE,
  DURATION_MS,
  STATUS_CODE
FROM "APPLICATION-LOGS"
WHERE DURATION_MS > 1000
ORDER BY DURATION_MS DESC
LIMIT 10;

-- Average duration by service
SELECT 
  SERVICE,
  COUNT(*) as REQUEST_COUNT,
  ROUND(AVG(DURATION_MS), 2) as AVG_DURATION_MS,
  MIN(DURATION_MS) as MIN_DURATION_MS,
  MAX(DURATION_MS) as MAX_DURATION_MS
FROM "APPLICATION-LOGS"
WHERE DURATION_MS IS NOT NULL
GROUP BY SERVICE
ORDER BY AVG_DURATION_MS DESC;

/*****************************************************
| * 9. Service Health Dashboard
| *****************************************************/

-- Overall service health summary
SELECT 
  SERVICE,
  COUNT(*) as TOTAL_LOGS,
  SUM(CASE WHEN LEVEL = 'ERROR' THEN 1 ELSE 0 END) as ERROR_COUNT,
  SUM(CASE WHEN LEVEL = 'WARN' THEN 1 ELSE 0 END) as WARN_COUNT,
  SUM(CASE WHEN LEVEL = 'INFO' THEN 1 ELSE 0 END) as INFO_COUNT,
  ROUND(AVG(DURATION_MS), 2) as AVG_RESPONSE_TIME_MS
FROM "APPLICATION-LOGS"
GROUP BY SERVICE
ORDER BY ERROR_COUNT DESC, WARN_COUNT DESC;

/*****************************************************
| * 10. Payment Transactions
| *****************************************************/

-- Show payment transactions (logs with AMOUNT field)
SELECT 
  TIMESTAMP,
  SERVICE,
  MESSAGE,
  AMOUNT,
  STATUS_CODE,
  USER_ID
FROM "APPLICATION-LOGS"
WHERE AMOUNT IS NOT NULL
ORDER BY TIMESTAMP DESC;

-- Payment statistics
SELECT 
  COUNT(*) as PAYMENT_COUNT,
  ROUND(SUM(AMOUNT), 2) as TOTAL_AMOUNT,
  ROUND(AVG(AMOUNT), 2) as AVG_AMOUNT,
  ROUND(MIN(AMOUNT), 2) as MIN_AMOUNT,
  ROUND(MAX(AMOUNT), 2) as MAX_AMOUNT
FROM "APPLICATION-LOGS"
WHERE AMOUNT IS NOT NULL;

-- ============================================================================
-- Phase 1 Verification Complete!
-- 
-- ✅ Base schema columns created from initial JSON structure
-- ✅ Data successfully ingested from Kafka to Snowflake
-- ✅ Auto-schema detection working correctly
-- 
-- 🎯 NEXT STEP: Proceed to Phase 2 to see Schema Evolution in action!
--    Produce the extended logs (sample_logs_extended.json) and run
--    sql/2b.verify_schema_evolution.sql to see NEW columns appear automatically!
-- ============================================================================



-- ============================================================================
-- Copyright 2025 Snowflake Inc.
-- SPDX-License-Identifier: Apache-2.0
-- Licensed under the Apache License, Version 2.0 (the "License");
-- You may obtain a copy of the License at: http://www.apache.org/licenses/LICENSE-2.0
-- ============================================================================
--
-- Openflow Kafka Connector Quickstart - Verify Data Ingestion
--
-- This script contains queries to verify that data is flowing from Kafka
-- to Snowflake and to examine the ingested log data.
--
-- Note: The Kafka JSON SASL SCHEMAEV connector automatically flattens JSON
-- fields into individual table columns (automatic schema detection).
-- ============================================================================

-- Set context
USE ROLE QUICKSTART_ROLE;
USE DATABASE QUICKSTART_KAFKA_CONNECTOR_DB;
USE SCHEMA PUBLIC;
USE WAREHOUSE QUICKSTART_KAFKA_CONNECTOR_WH;

/*****************************************************
| * 1. Basic Row Count Check
| *****************************************************/

-- Check total number of records ingested
SELECT COUNT(*) as TOTAL_RECORDS 
FROM "APPLICATION-LOGS";

-- Expected: If data is flowing, you should see a non-zero count

/*****************************************************
| * 2. View Sample Records
| *****************************************************/

-- View the auto-detected schema (flattened columns)
SELECT *
FROM "APPLICATION-LOGS"
LIMIT 10;

-- Note: The connector automatically creates columns for each JSON field
-- You should see columns like TIMESTAMP, LEVEL, SERVICE, HOST, MESSAGE, etc.

/*****************************************************
| * 3. Check Auto-Created Columns
| *****************************************************/

-- Show what columns were automatically created from your JSON structure
SHOW COLUMNS IN "APPLICATION-LOGS";

-- Expected: You should see columns matching your JSON fields (e.g., TIMESTAMP, LEVEL, 
-- SERVICE, HOST, MESSAGE, STATUS_CODE, DURATION_MS, REQUEST_ID, etc.)

/*****************************************************
| * 4. Parse Log Content
| *****************************************************/

-- Query the schematized log fields directly (no JSON parsing needed!)
SELECT 
  TIMESTAMP as LOG_TIMESTAMP,
  LEVEL as LOG_LEVEL,
  SERVICE as SERVICE_NAME,
  HOST as HOST_NAME,
  MESSAGE as LOG_MESSAGE,
  REQUEST_ID,
  DURATION_MS,
  STATUS_CODE,
  USER_ID
FROM "APPLICATION-LOGS"
ORDER BY TIMESTAMP DESC
LIMIT 20;

-- Note: With automatic schema detection, you query columns directly
-- No need for VARIANT parsing syntax like RECORD_CONTENT:field

/*****************************************************
| * 5. Check Data Freshness
| *****************************************************/

-- View the most recent records ingested
SELECT 
  TIMESTAMP as LOG_TIMESTAMP,
  LEVEL,
  SERVICE,
  MESSAGE,
  STATUS_CODE
FROM "APPLICATION-LOGS"
ORDER BY TIMESTAMP DESC
LIMIT 20;

/*****************************************************
| * 6. Log Level Distribution
| *****************************************************/

-- Analyze logs by level across services
SELECT 
  SERVICE,
  LEVEL,
  COUNT(*) as LOG_COUNT
FROM "APPLICATION-LOGS"
GROUP BY SERVICE, LEVEL
ORDER BY LOG_COUNT DESC;

-- Expected: You should see distribution across INFO, WARN, and ERROR levels

/*****************************************************
| * 7. Performance Analysis
| *****************************************************/

-- Find slow requests (duration > 1000ms)
SELECT 
  TIMESTAMP,
  SERVICE,
  HOST,
  MESSAGE,
  DURATION_MS,
  STATUS_CODE
FROM "APPLICATION-LOGS"
WHERE DURATION_MS > 1000
ORDER BY DURATION_MS DESC
LIMIT 20;

-- Average duration by service
SELECT 
  SERVICE,
  AVG(DURATION_MS) as AVG_DURATION_MS,
  MIN(DURATION_MS) as MIN_DURATION_MS,
  MAX(DURATION_MS) as MAX_DURATION_MS,
  COUNT(*) as REQUEST_COUNT
FROM "APPLICATION-LOGS"
WHERE DURATION_MS IS NOT NULL
GROUP BY SERVICE
ORDER BY AVG_DURATION_MS DESC;

/*****************************************************
| * 8. Error Analysis
| *****************************************************/

-- Show all error logs
SELECT 
  TIMESTAMP,
  SERVICE,
  HOST,
  MESSAGE,
  ERROR,
  STATUS_CODE,
  DURATION_MS
FROM "APPLICATION-LOGS"
WHERE LEVEL = 'ERROR'
ORDER BY TIMESTAMP DESC
LIMIT 20;

-- Count errors by type
SELECT 
  ERROR,
  COUNT(*) as ERROR_COUNT,
  COUNT(DISTINCT SERVICE) as AFFECTED_SERVICES
FROM "APPLICATION-LOGS"
WHERE ERROR IS NOT NULL
GROUP BY ERROR
ORDER BY ERROR_COUNT DESC;

/*****************************************************
| * 9. Data Quality Checks
| *****************************************************/

-- Check for records with missing required fields
SELECT 
  COUNT(*) as TOTAL_RECORDS,
  SUM(CASE WHEN TIMESTAMP IS NULL THEN 1 ELSE 0 END) as MISSING_TIMESTAMP,
  SUM(CASE WHEN LEVEL IS NULL THEN 1 ELSE 0 END) as MISSING_LEVEL,
  SUM(CASE WHEN SERVICE IS NULL THEN 1 ELSE 0 END) as MISSING_SERVICE,
  SUM(CASE WHEN MESSAGE IS NULL THEN 1 ELSE 0 END) as MISSING_MESSAGE
FROM "APPLICATION-LOGS";

-- Expected: All counts should be 0 for complete data

/*****************************************************
| * 10. Schema Evolution Detection
| *****************************************************/

-- Snowflake's automatic schema detection handles schema evolution.
-- This query shows which optional/conditional fields appear in log records,
-- demonstrating how new fields are automatically added as columns.

-- Count records with optional/conditional fields
SELECT 
  COUNT(*) as TOTAL_RECORDS,
  SUM(CASE WHEN ERROR IS NOT NULL THEN 1 ELSE 0 END) as HAS_ERROR_FIELD,
  SUM(CASE WHEN AMOUNT IS NOT NULL THEN 1 ELSE 0 END) as HAS_AMOUNT_FIELD,
  SUM(CASE WHEN USER_ID IS NOT NULL THEN 1 ELSE 0 END) as HAS_USER_ID_FIELD,
  SUM(CASE WHEN TEST IS NOT NULL THEN 1 ELSE 0 END) as HAS_TEST_FIELD
FROM "APPLICATION-LOGS";

-- Show records with the 'ERROR' field (ERROR level logs only)
SELECT 
  TIMESTAMP as LOG_TIMESTAMP,
  LEVEL,
  SERVICE,
  MESSAGE,
  ERROR as ERROR_TYPE,
  STATUS_CODE
FROM "APPLICATION-LOGS"
WHERE ERROR IS NOT NULL
LIMIT 10;

-- Show records with 'TEST' field (test/health check messages)
SELECT 
  TIMESTAMP as LOG_TIMESTAMP,
  TEST as IS_TEST,
  MESSAGE,
  STATUS
FROM "APPLICATION-LOGS"
WHERE TEST = TRUE
LIMIT 10;

-- Show records with extended fields (demonstrating schema evolution)
-- These fields were added later and don't appear in all records
SELECT 
  TIMESTAMP as LOG_TIMESTAMP,
  SERVICE,
  MESSAGE,
  REGION,
  TRACE_ID,
  AUTH_METHOD,
  CURRENCY,
  PAYMENT_METHOD,
  RETRY_COUNT,
  FILE_SIZE_BYTES
FROM "APPLICATION-LOGS"
WHERE REGION IS NOT NULL 
   OR TRACE_ID IS NOT NULL
   OR AUTH_METHOD IS NOT NULL
   OR CURRENCY IS NOT NULL
   OR RETRY_COUNT IS NOT NULL
   OR FILE_SIZE_BYTES IS NOT NULL
LIMIT 10;

-- Payment transactions with extended fields
SELECT 
  TIMESTAMP,
  SERVICE,
  MESSAGE,
  AMOUNT,
  CURRENCY,
  PAYMENT_METHOD,
  USER_ID
FROM "APPLICATION-LOGS"
WHERE CURRENCY IS NOT NULL
ORDER BY TIMESTAMP DESC
LIMIT 10;

-- Note: The Kafka JSON SASL SCHEMAEV connector automatically detects new fields
-- in your JSON messages and adds them as columns to the table. This allows
-- flexible schema evolution without manual DDL changes. Fields that appear
-- conditionally (e.g., ERROR field only in ERROR logs, AMOUNT in payment logs)
-- are created as nullable columns.

/*****************************************************
| * 11. Service Health Overview
| *****************************************************/

-- Summary dashboard of service health
SELECT 
  SERVICE,
  COUNT(*) as TOTAL_LOGS,
  SUM(CASE WHEN LEVEL = 'ERROR' THEN 1 ELSE 0 END) as ERROR_COUNT,
  SUM(CASE WHEN LEVEL = 'WARN' THEN 1 ELSE 0 END) as WARN_COUNT,
  SUM(CASE WHEN LEVEL = 'INFO' THEN 1 ELSE 0 END) as INFO_COUNT,
  ROUND(AVG(DURATION_MS), 2) as AVG_RESPONSE_TIME_MS,
  MAX(TIMESTAMP) as LAST_LOG_TIME
FROM "APPLICATION-LOGS"
GROUP BY SERVICE
ORDER BY ERROR_COUNT DESC, WARN_COUNT DESC;

-- ============================================================================
-- Verification Complete!
-- 
-- If you see data in the queries above, your Kafka connector is working correctly!
-- 
-- Key Points:
-- - The Kafka JSON SASL SCHEMAEV connector automatically creates table columns
--   from your JSON message fields (automatic schema detection)
-- - New fields in JSON messages automatically become new columns (schema evolution)
-- - You can query fields directly without JSON parsing syntax
-- - Optional fields (like ERROR, AMOUNT, REGION) appear as nullable columns
-- 
-- If you don't see data:
-- 1. Check that your Kafka topic has messages (use: rpk topic consume application-logs)
-- 2. Verify Openflow processors are running (green status in Canvas)
-- 3. Check network connectivity to Kafka brokers
-- 4. Review Openflow processor logs for errors in Canvas
-- 5. Verify the table was auto-created (run: SHOW TABLES)
-- ============================================================================


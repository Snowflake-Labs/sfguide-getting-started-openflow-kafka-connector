-- ============================================================================
-- Copyright 2025 Snowflake Inc.
-- SPDX-License-Identifier: Apache-2.0
-- Licensed under the Apache License, Version 2.0 (the "License");
-- You may obtain a copy of the License at: http://www.apache.org/licenses/LICENSE-2.0
-- ============================================================================
--
-- Openflow Kafka Connector Quickstart - Phase 2: Verify Schema Evolution
--
-- This script demonstrates automatic schema evolution by showing NEW columns
-- that were automatically added when evolved log messages were ingested.
--
-- Run this AFTER producing evolved logs (sample_logs_evolved.json)
-- ============================================================================

-- Set context
USE ROLE QUICKSTART_ROLE;
USE DATABASE QUICKSTART_KAFKA_CONNECTOR_DB;
USE SCHEMA PUBLIC;
USE WAREHOUSE QUICKSTART_KAFKA_CONNECTOR_WH;

/*****************************************************
| * 1. 🎉 WOW MOMENT - Compare Schema!
| *****************************************************/

-- Run the SAME query as Phase 1 - Notice the NEW columns!
SELECT 
  COLUMN_NAME, 
  DATA_TYPE,
  ORDINAL_POSITION
FROM QUICKSTART_KAFKA_CONNECTOR_DB.INFORMATION_SCHEMA.COLUMNS 
WHERE TABLE_NAME ILIKE 'APPLICATION-LOGS'
ORDER BY COLUMN_NAME;

-- 🎯 Compare with Phase 1:
-- 
-- BASE COLUMNS (from Phase 1) - 11 columns:
--   AMOUNT, DURATION_MS, ERROR, HOST, LEVEL, MESSAGE, 
--   REQUEST_ID, SERVICE, STATUS_CODE, TIMESTAMP, USER_ID
--
-- 🆕 NEW COLUMNS (automatically added) - 26 new columns:
--   AUTH_METHOD, AVAILABLE_GB, AVAILABLE_MB, CONTENT_TYPE, CURRENCY,
--   DISK_USAGE_PERCENT, FILE_SIZE_BYTES, MEMORY_PERCENT, METRICS_COUNT,
--   PAYMENT_METHOD, PRODUCT_ID, PROVIDER, QUERY_PARAMS, RATING,
--   RECIPIENT, REGION, RESULT_COUNT, RETRY_COUNT, SESSION_DURATION,
--   SMTP_CODE, STATUS, TEST, TIME_WINDOW, TRACE_ID, 
--   VALIDATION_ERRORS, VERSION
--
-- 🎉 TOTAL: 37 columns (11 base + 26 evolved)
-- 🎉 These columns were added AUTOMATICALLY - no DDL changes required!

/*****************************************************
| * 2. Check Updated Record Count
| *****************************************************/

-- Count total records (should have ~15 more from evolved logs)
SELECT COUNT(*) as TOTAL_RECORDS 
FROM "APPLICATION-LOGS";

-- Expected: ~40 records (25 base + 15 evolved)

/*****************************************************
| * 3. Records with REGION Field (New - From Evolved Schema!)
| *****************************************************/

-- Show records with the new REGION field from evolved logs
SELECT 
  TIMESTAMP,
  SERVICE,
  MESSAGE,
  REGION,
  TRACE_ID
FROM "APPLICATION-LOGS"
WHERE REGION IS NOT NULL
ORDER BY TIMESTAMP DESC
LIMIT 10;

-- Count records by region
SELECT 
  REGION,
  COUNT(*) as RECORD_COUNT
FROM "APPLICATION-LOGS"
WHERE REGION IS NOT NULL
GROUP BY REGION
ORDER BY RECORD_COUNT DESC;

/*****************************************************
| * 4. Authentication Logs with Evolved Fields (New!)
| *****************************************************/

-- Show auth logs with new AUTH_METHOD and PROVIDER fields from evolved schema
SELECT 
  TIMESTAMP,
  SERVICE,
  MESSAGE,
  USER_ID,
  AUTH_METHOD,
  PROVIDER,
  SESSION_DURATION,
  REGION
FROM "APPLICATION-LOGS"
WHERE AUTH_METHOD IS NOT NULL
ORDER BY TIMESTAMP DESC;

-- Authentication method distribution
SELECT 
  AUTH_METHOD,
  PROVIDER,
  COUNT(*) as AUTH_COUNT
FROM "APPLICATION-LOGS"
WHERE AUTH_METHOD IS NOT NULL
GROUP BY AUTH_METHOD, PROVIDER
ORDER BY AUTH_COUNT DESC;

/*****************************************************
| * 5. Payment Logs with Currency Fields (New!)
| *****************************************************/

-- Show payment logs with new CURRENCY and PAYMENT_METHOD fields
SELECT 
  TIMESTAMP,
  SERVICE,
  MESSAGE,
  AMOUNT,
  CURRENCY,
  PAYMENT_METHOD,
  USER_ID,
  REGION
FROM "APPLICATION-LOGS"
WHERE CURRENCY IS NOT NULL
ORDER BY TIMESTAMP DESC;

-- Payment analysis by currency and method
SELECT 
  CURRENCY,
  PAYMENT_METHOD,
  COUNT(*) as TRANSACTION_COUNT,
  ROUND(SUM(AMOUNT), 2) as TOTAL_AMOUNT,
  ROUND(AVG(AMOUNT), 2) as AVG_AMOUNT
FROM "APPLICATION-LOGS"
WHERE CURRENCY IS NOT NULL
GROUP BY CURRENCY, PAYMENT_METHOD
ORDER BY TOTAL_AMOUNT DESC;

/*****************************************************
| * 6. Error Logs with Retry Information (New!)
| *****************************************************/

-- Show errors with the new RETRY_COUNT field
SELECT 
  TIMESTAMP,
  SERVICE,
  MESSAGE,
  ERROR,
  STATUS_CODE,
  RETRY_COUNT,
  REGION
FROM "APPLICATION-LOGS"
WHERE RETRY_COUNT IS NOT NULL
ORDER BY TIMESTAMP DESC;

/*****************************************************
| * 7. File Upload Logs with Metadata (New!)
| *****************************************************/

-- Show file uploads with new FILE_SIZE_BYTES and CONTENT_TYPE fields
SELECT 
  TIMESTAMP,
  SERVICE,
  MESSAGE,
  FILE_SIZE_BYTES,
  CONTENT_TYPE,
  USER_ID,
  REGION
FROM "APPLICATION-LOGS"
WHERE FILE_SIZE_BYTES IS NOT NULL
ORDER BY TIMESTAMP DESC;

-- File upload statistics
SELECT 
  CONTENT_TYPE,
  COUNT(*) as UPLOAD_COUNT,
  ROUND(SUM(FILE_SIZE_BYTES) / 1024.0 / 1024.0, 2) as TOTAL_SIZE_MB,
  ROUND(AVG(FILE_SIZE_BYTES) / 1024.0 / 1024.0, 2) as AVG_SIZE_MB
FROM "APPLICATION-LOGS"
WHERE FILE_SIZE_BYTES IS NOT NULL
GROUP BY CONTENT_TYPE;

/*****************************************************
| * 8. System Metrics with Resource Fields (New!)
| *****************************************************/

-- Show system warnings with new resource monitoring fields
-- Note: System metrics only appear in WARN logs with messages like 
-- "Memory usage above 80%" or "Disk space running low"
-- If this returns no results, produce more evolved logs:
--   python generate_logs.py --count 100 --evolved
SELECT 
  TIMESTAMP,
  SERVICE,
  MESSAGE,
  MEMORY_PERCENT,
  AVAILABLE_MB,
  DISK_USAGE_PERCENT,
  AVAILABLE_GB,
  REGION
FROM "APPLICATION-LOGS"
WHERE MEMORY_PERCENT IS NOT NULL 
   OR DISK_USAGE_PERCENT IS NOT NULL
ORDER BY TIMESTAMP DESC;

/*****************************************************
| * 9. API Query Logs with Parameters (New!)
| *****************************************************/

-- Show API queries with the new QUERY_PARAMS and RESULT_COUNT fields
SELECT 
  TIMESTAMP,
  SERVICE,
  MESSAGE,
  QUERY_PARAMS,
  RESULT_COUNT,
  DURATION_MS,
  REGION
FROM "APPLICATION-LOGS"
WHERE QUERY_PARAMS IS NOT NULL
ORDER BY TIMESTAMP DESC;

/*****************************************************
| * 10. Health Check Messages (New!)
| *****************************************************/

-- Show health check messages with the new TEST field
SELECT 
  TIMESTAMP,
  TEST,
  MESSAGE,
  STATUS,
  VERSION
FROM "APPLICATION-LOGS"
WHERE TEST = TRUE
ORDER BY TIMESTAMP DESC;

/*****************************************************
| * 11. Email Delivery Logs (New!)
| *****************************************************/

-- Show email logs with new RECIPIENT and SMTP_CODE fields
SELECT 
  TIMESTAMP,
  SERVICE,
  MESSAGE,
  ERROR,
  RECIPIENT,
  SMTP_CODE,
  REGION
FROM "APPLICATION-LOGS"
WHERE SMTP_CODE IS NOT NULL
ORDER BY TIMESTAMP DESC;

/*****************************************************
| * 12. Analytics Metrics (New!)
| *****************************************************/

-- Show analytics logs with new METRICS_COUNT and TIME_WINDOW fields
SELECT 
  TIMESTAMP,
  SERVICE,
  MESSAGE,
  METRICS_COUNT,
  TIME_WINDOW,
  DURATION_MS,
  REGION
FROM "APPLICATION-LOGS"
WHERE METRICS_COUNT IS NOT NULL
ORDER BY TIMESTAMP DESC;

/*****************************************************
| * 13. Schema Evolution Summary
| *****************************************************/

-- Count how many records have each of the new evolved fields
SELECT 
  COUNT(*) as TOTAL_RECORDS,
  SUM(CASE WHEN REGION IS NOT NULL THEN 1 ELSE 0 END) as HAS_REGION,
  SUM(CASE WHEN AUTH_METHOD IS NOT NULL THEN 1 ELSE 0 END) as HAS_AUTH_METHOD,
  SUM(CASE WHEN CURRENCY IS NOT NULL THEN 1 ELSE 0 END) as HAS_CURRENCY,
  SUM(CASE WHEN RETRY_COUNT IS NOT NULL THEN 1 ELSE 0 END) as HAS_RETRY_COUNT,
  SUM(CASE WHEN FILE_SIZE_BYTES IS NOT NULL THEN 1 ELSE 0 END) as HAS_FILE_SIZE,
  SUM(CASE WHEN MEMORY_PERCENT IS NOT NULL THEN 1 ELSE 0 END) as HAS_MEMORY_METRICS,
  SUM(CASE WHEN QUERY_PARAMS IS NOT NULL THEN 1 ELSE 0 END) as HAS_QUERY_PARAMS,
  SUM(CASE WHEN TEST IS NOT NULL THEN 1 ELSE 0 END) as HAS_TEST_FLAG
FROM "APPLICATION-LOGS";

-- ============================================================================
-- 🎉 Schema Evolution Demonstration Complete!
-- 
-- KEY TAKEAWAYS:
-- 
-- ✅ NEW columns were automatically added when evolved JSON fields appeared
-- ✅ No manual DDL changes required - Openflow handled it automatically
-- ✅ Existing records have NULL values for new columns (backward compatible)
-- ✅ New records populate the evolved fields
-- 
-- 🎯 SCHEMA EVOLUTION IN ACTION:
-- 
-- This demonstrates the power of automatic schema evolution. As your application
-- evolves and adds new fields to log messages (like region, auth_method, currency),
-- the Kafka connector automatically detects these changes and adds corresponding
-- columns to the Snowflake table. This happens transparently without:
-- 
--   ❌ Manual ALTER TABLE statements
--   ❌ Pipeline reconfiguration
--   ❌ Downtime or data loss
--   ❌ Schema migration scripts
-- 
-- ✅ Your data pipeline adapts automatically to your application's evolution!
-- 
-- This is ideal for:
-- - Microservices architectures with evolving log formats
-- - A/B testing with different log fields
-- - Gradual rollout of new instrumentation
-- - Multi-tenant systems with varying log structures
-- ============================================================================



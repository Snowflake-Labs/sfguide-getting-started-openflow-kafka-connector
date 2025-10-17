/*****************************************************
| Snowflake Openflow Kafka Connector Quickstart
| 
| Script 4: Cortex Search for Semantic Log Analysis
| 
| This script demonstrates how to create and use
| Snowflake Cortex Search for semantic search over
| log messages using natural language queries.
|*****************************************************/

USE ROLE QUICKSTART_ROLE;
USE DATABASE QUICKSTART_KAFKA_CONNECTOR_DB;
USE SCHEMA PUBLIC;
USE WAREHOUSE QUICKSTART_KAFKA_CONNECTOR_WH;

/*****************************************************
| 1. Create Cortex Search Service
|*****************************************************/

-- Create Cortex Search service on log messages
-- Includes both base and evolved schema attributes for comprehensive filtering
CREATE OR REPLACE CORTEX SEARCH SERVICE application_logs_search
  ON MESSAGE
  ATTRIBUTES LEVEL, SERVICE, ERROR, STATUS_CODE, MEMORY_PERCENT, DISK_USAGE_PERCENT, REGION
  WAREHOUSE = QUICKSTART_KAFKA_CONNECTOR_WH
  TARGET_LAG = '1 minute'
  AS (
    SELECT 
      MESSAGE,
      LEVEL,
      SERVICE,
      ERROR,
      STATUS_CODE,
      TIMESTAMP,
      REQUEST_ID,
      HOST,
      USER_ID,
      MEMORY_PERCENT::NUMBER as MEMORY_PERCENT,
      AVAILABLE_MB::NUMBER as AVAILABLE_MB,
      DISK_USAGE_PERCENT::NUMBER as DISK_USAGE_PERCENT,
      AVAILABLE_GB::NUMBER as AVAILABLE_GB,
      REGION
    FROM "APPLICATION-LOGS"
  );

/*****************************************************
| 2. Basic Semantic Search Examples
|*****************************************************/

-- Semantic search for authentication errors
-- Returns MESSAGE, LEVEL, SERVICE, TIMESTAMP, and ERROR columns
SELECT
  SNOWFLAKE.CORTEX.SEARCH_PREVIEW(
    'QUICKSTART_KAFKA_CONNECTOR_DB.PUBLIC.application_logs_search',
    '{
      "query": "authentication failed",
      "columns": ["MESSAGE", "LEVEL", "SERVICE", "TIMESTAMP", "ERROR"],
      "filter": {"@eq": {"LEVEL": "ERROR"}},
      "limit": 10
    }'
  );

-- Search for payment issues with base schema columns
SELECT
  SNOWFLAKE.CORTEX.SEARCH_PREVIEW(
    'QUICKSTART_KAFKA_CONNECTOR_DB.PUBLIC.application_logs_search',
    '{
      "query": "payment declined timeout",
      "columns": ["MESSAGE", "SERVICE", "STATUS_CODE", "TIMESTAMP", "REQUEST_ID"],
      "filter": {"@eq": {"SERVICE": "payment-service"}},
      "limit": 10
    }'
  );

-- Find database connection problems
SELECT
  SNOWFLAKE.CORTEX.SEARCH_PREVIEW(
    'QUICKSTART_KAFKA_CONNECTOR_DB.PUBLIC.application_logs_search',
    '{
      "query": "database connection timeout",
      "columns": ["MESSAGE", "LEVEL", "SERVICE", "HOST", "TIMESTAMP"],
      "filter": {"@eq": {"LEVEL": "ERROR"}},
      "limit": 10
    }'
  );

/*****************************************************
| 3. Advanced Filters with Multiple Conditions
|*****************************************************/

-- Find errors in payment OR auth services
SELECT
  SNOWFLAKE.CORTEX.SEARCH_PREVIEW(
    'QUICKSTART_KAFKA_CONNECTOR_DB.PUBLIC.application_logs_search',
    '{
      "query": "failed transaction",
      "columns": ["MESSAGE", "LEVEL", "SERVICE", "ERROR", "STATUS_CODE", "TIMESTAMP"],
      "filter": {
        "@and": [
          {"@eq": {"LEVEL": "ERROR"}},
          {"@or": [
            {"@eq": {"SERVICE": "payment-service"}},
            {"@eq": {"SERVICE": "auth-service"}}
          ]}
        ]
      },
      "limit": 20
    }'
  );

/*****************************************************
| 4. Evolved Schema Examples
|*****************************************************/

-- Search for system warnings with high memory usage (evolved schema)
SELECT
  SNOWFLAKE.CORTEX.SEARCH_PREVIEW(
    'QUICKSTART_KAFKA_CONNECTOR_DB.PUBLIC.application_logs_search',
    '{
      "query": "memory usage warning system resource",
      "columns": ["MESSAGE", "LEVEL", "SERVICE", "MEMORY_PERCENT", "AVAILABLE_MB", "REGION", "TIMESTAMP"],
      "filter": {
        "@and": [
          {"@eq": {"LEVEL": "WARN"}},
          {"@gte": {"MEMORY_PERCENT": 80}}
        ]
      },
      "limit": 15
    }'
  );

/*****************************************************
| 5. Use Cases for Different Scenarios
|*****************************************************/

-- Find all critical errors across services
SELECT
  SNOWFLAKE.CORTEX.SEARCH_PREVIEW(
    'QUICKSTART_KAFKA_CONNECTOR_DB.PUBLIC.application_logs_search',
    '{
      "query": "critical failure exception error",
      "columns": ["MESSAGE", "LEVEL", "SERVICE", "ERROR", "TIMESTAMP", "HOST"],
      "filter": {"@eq": {"LEVEL": "ERROR"}},
      "limit": 25
    }'
  );

-- Search for performance-related issues
SELECT
  SNOWFLAKE.CORTEX.SEARCH_PREVIEW(
    'QUICKSTART_KAFKA_CONNECTOR_DB.PUBLIC.application_logs_search',
    '{
      "query": "slow performance latency timeout",
      "columns": ["MESSAGE", "SERVICE", "DURATION_MS", "STATUS_CODE", "TIMESTAMP"],
      "filter": {"@gte": {"STATUS_CODE": 400}},
      "limit": 20
    }'
  );

-- Find inventory service warnings
SELECT
  SNOWFLAKE.CORTEX.SEARCH_PREVIEW(
    'QUICKSTART_KAFKA_CONNECTOR_DB.PUBLIC.application_logs_search',
    '{
      "query": "inventory stock quantity warning",
      "columns": ["MESSAGE", "LEVEL", "SERVICE", "TIMESTAMP"],
      "filter": {
        "@and": [
          {"@eq": {"SERVICE": "inventory-service"}},
          {"@eq": {"LEVEL": "WARN"}}
        ]
      },
      "limit": 15
    }'
  );

/*****************************************************
| 6. View Cortex Search Service Information
|*****************************************************/

-- Show Cortex Search service details
SHOW CORTEX SEARCH SERVICES IN SCHEMA PUBLIC;

-- Describe the search service
DESC CORTEX SEARCH SERVICE application_logs_search;

/*****************************************************
| Notes:
| - SEARCH_PREVIEW is designed for testing/validation
| - For production applications requiring low latency,
|   use the Cortex Search REST API or Python SDK
| - Evolved schema attributes (MEMORY_PERCENT, 
|   DISK_USAGE_PERCENT, REGION) provide advanced
|   operational insights
| - Use Snowflake Intelligence for natural language
|   queries without writing SQL
|*****************************************************/

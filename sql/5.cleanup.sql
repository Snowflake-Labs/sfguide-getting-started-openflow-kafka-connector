/*****************************************************
| Snowflake Openflow Kafka Connector Quickstart
| 
| Script 5: Cleanup Resources
| 
| This script removes all Snowflake objects created
| during the quickstart. Use with caution as this
| will permanently delete data.
|*****************************************************/

-- Use ACCOUNTADMIN to drop objects
USE ROLE ACCOUNTADMIN;

/*****************************************************
| 1. Drop Cortex Search Service
|*****************************************************/

-- Drop Cortex Search service (if created)
DROP CORTEX SEARCH SERVICE IF EXISTS QUICKSTART_KAFKA_CONNECTOR_DB.PUBLIC.application_logs_search;

/*****************************************************
| 2. Drop Snowflake Alerts
|*****************************************************/

-- Drop alerts (if created)
DROP ALERT IF EXISTS QUICKSTART_KAFKA_CONNECTOR_DB.PUBLIC.HIGH_ERROR_RATE_ALERT;
DROP ALERT IF EXISTS QUICKSTART_KAFKA_CONNECTOR_DB.PUBLIC.CRITICAL_SERVICE_ALERT;

/*****************************************************
| 3. Drop Database and Objects
|*****************************************************/

-- Drop database (this removes all tables and data)
DROP DATABASE IF EXISTS QUICKSTART_KAFKA_CONNECTOR_DB;

/*****************************************************
| 4. Drop Warehouse
|*****************************************************/

-- Drop warehouse
DROP WAREHOUSE IF EXISTS QUICKSTART_KAFKA_CONNECTOR_WH;

/*****************************************************
| 5. Drop External Access Integration
|*****************************************************/

-- Drop external access integration
DROP EXTERNAL ACCESS INTEGRATION IF EXISTS quickstart_kafka_connector_access;

/*****************************************************
| Notes:
| - We don't drop QUICKSTART_ROLE as it may be used 
|   by other quickstarts
| - This will permanently delete all log data and 
|   configuration
| - Make sure you've exported anything you need 
|   before running this script
| - Remember to also:
|   1. Stop and disable the Openflow connector in 
|      the Canvas
|   2. Optionally delete the Openflow runtime and 
|      deployment
|   3. Optionally delete the Kafka topic:
|      rpk topic delete application-logs
|*****************************************************/


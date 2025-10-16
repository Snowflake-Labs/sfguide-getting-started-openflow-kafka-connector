# Getting Started with Snowflake Openflow Kafka Connector

This repository contains the companion code for the [Snowflake Openflow Kafka Connector Quickstart](https://quickstarts.snowflake.com/guide/getting_started_with_openflow_kafka_connector/index.html).

## Overview

This quickstart demonstrates how to build a real-time streaming pipeline from Apache Kafka to Snowflake using the Openflow Kafka Connector. You'll learn how to:

- Set up a Kafka topic for application log streaming
- Configure Snowflake objects (database, schema, tables, network rules)
- Deploy Openflow SPCS runtime
- Configure the Kafka connector in Openflow Canvas
- Stream real-time logs from Kafka to Snowflake
- Perform powerful SQL analytics on streaming log data

## Repository Contents

```
.
├── README.md                      # This file
├── LICENSE.txt                    # Apache 2.0 license
├── env.template                   # Environment variable template for Kafka config
├── sql/
│   ├── 1.snowflake_setup.sql     # Snowflake environment setup
│   ├── 2.verify_ingestion.sql    # Data ingestion verification queries
│   └── 3.analytics_queries.sql   # Example analytics queries
└── sample-data/
    ├── sample_logs.json           # Sample application log events
    └── generate_logs.py           # Python script to produce logs to Kafka
```

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/Snowflake-Labs/sfguide-getting-started-openflow-kafka-connector.git
cd sfguide-getting-started-openflow-kafka-connector
```

### 2. Follow the Quickstart Guide

Follow the complete step-by-step guide at:
**[Getting Started with Openflow Kafka Connector](https://quickstarts.snowflake.com/guide/getting_started_with_openflow_kafka_connector/index.html)**

### 3. Setup Snowflake

Execute the SQL script in Snowsight:

```sql
-- Update network rule with your Kafka broker endpoints first!
-- Then run: sql/1.snowflake_setup.sql
```

### 4. Generate Sample Logs

Use the provided Python script to produce sample logs to Kafka:

```bash
# Install dependencies
pip install kafka-python

# Set up environment (recommended)
cp env.template .env
# Edit .env with your Kafka broker and topic settings
export $(cat .env | xargs)

# Test your Kafka connection first (recommended)
python sample-data/generate_logs.py --test-connection

# If connection test passes, produce logs
python sample-data/generate_logs.py --count 50

# Or use command-line arguments directly
python sample-data/generate_logs.py \
  --brokers YOUR-KAFKA-BROKER:9092 \
  --topic application-logs \
  --test-connection

python sample-data/generate_logs.py \
  --brokers YOUR-KAFKA-BROKER:9092 \
  --topic application-logs \
  --count 50
```

## Prerequisites

- **Snowflake Account**: Enterprise account with Openflow SPCS enabled
- **Kafka Cluster**: Access to a Kafka cluster (GCP Managed Kafka, AWS MSK, Confluent Cloud, or self-hosted)
- **Python 3.7+**: For the log generator script (optional)
- **Network Connectivity**: Kafka brokers must be accessible from Snowflake

## Use Cases

This pattern applies to:

- **Log Aggregation**: Centralize logs from distributed microservices
- **Real-time Monitoring**: Stream operational metrics for dashboards and alerting
- **Event Sourcing**: Capture application events for analytics and replay
- **Observability**: Track system health, performance, and errors
- **Incident Investigation**: Query and analyze logs with powerful SQL

## Key Features

- **Real-Time Ingestion**: Logs appear in Snowflake within seconds via Snowpipe Streaming
- **Flexible Schema**: JSON logs stored in VARIANT columns for schema flexibility
- **Scalable**: Handles high-throughput Kafka topics with automatic scaling
- **Cost-Effective**: Snowflake storage costs are lower than dedicated log platforms
- **Powerful Analytics**: Use SQL to query, aggregate, and analyze logs

## Documentation

- [Openflow Documentation](https://docs.snowflake.com/en/user-guide/data-integration/openflow/about)
- [Kafka Connector Documentation](https://docs.snowflake.com/en/user-guide/data-integration/openflow/connectors/kafka/about)
- [Kafka Connector Performance Tuning](https://docs.snowflake.com/en/user-guide/data-integration/openflow/connectors/kafka/performance-tuning)
- [All Openflow Connectors](https://docs.snowflake.com/en/user-guide/data-integration/openflow/connectors/about-openflow-connectors)

## Sample Data

The `sample-data/sample_logs.json` file contains 25 realistic application log events in JSON format, including:

- Web API requests
- Authentication events
- Database operations
- Payment processing
- Error events
- Performance metrics

## Log Generator Script

The `generate_logs.py` script produces realistic application logs with:

- Multiple services (web-API, auth-service, payment-service, etc.)
- Realistic log levels (INFO 70%, WARN 20%, ERROR 10%)
- Request IDs for tracing
- Performance metrics (duration, status codes)
- Configurable message count and rate
- **Connection testing** to verify Kafka connectivity

**Quick Start**:

```bash
# 1. Set up environment
cp env.template .env  # Edit with your Kafka settings
export $(cat .env | xargs)

# 2. Test connection (recommended first step)
python generate_logs.py --test-connection

# 3. Produce logs
python generate_logs.py --count 100
```

**Connection Test Mode**:

The `--test-connection` flag performs a comprehensive check:

- ✓ Tests broker connectivity
- ✓ Fetches cluster metadata and lists brokers
- ✓ Checks topic existence and partition count
- ✓ Verifies write permissions by sending a test message

```bash
# Test with environment variables
python generate_logs.py --test-connection

# Or test with CLI arguments
python generate_logs.py --brokers localhost:9092 --topic logs --test-connection
```

**Production Usage**:

```bash
# Basic usage
python generate_logs.py --brokers localhost:9092 --topic application-logs --count 100

# Using environment variables (recommended)
export KAFKA_BROKERS=localhost:9092
export KAFKA_TOPIC=application-logs
python generate_logs.py --count 100

# With delay between messages (throttling)
python generate_logs.py --count 50 --delay 0.5

# Continuous mode (for load testing)
python generate_logs.py --count 10 --continuous
```

**Environment Variables**:

The script supports the following environment variables for convenience:

- `KAFKA_BROKERS`: Kafka broker address(es)
- `KAFKA_TOPIC`: Target Kafka topic name
- `KAFKA_SECURITY_PROTOCOL`: Security protocol (PLAINTEXT, SSL, SASL_PLAINTEXT, SASL_SSL)
- `KAFKA_SASL_MECHANISM`: SASL mechanism (PLAIN, SCRAM-SHA-256, SCRAM-SHA-512, etc.)
- `KAFKA_SASL_USERNAME`: SASL username (required for PLAIN, SCRAM-*)
- `KAFKA_SASL_PASSWORD`: SASL password (required for PLAIN, SCRAM-*)

**SASL Authentication**:

For managed Kafka services like Confluent Cloud or secured Kafka clusters:

```bash
# Example: Confluent Cloud with SASL_SSL
export KAFKA_BROKERS=pkc-xxxxx.us-east-1.aws.confluent.cloud:9092
export KAFKA_TOPIC=application-logs
export KAFKA_SECURITY_PROTOCOL=SASL_SSL
export KAFKA_SASL_MECHANISM=PLAIN
export KAFKA_SASL_USERNAME=YOUR_API_KEY
export KAFKA_SASL_PASSWORD=YOUR_API_SECRET

# Test connection
python generate_logs.py --test-connection

# Produce logs
python generate_logs.py --count 100
```

See `env.template` for a complete configuration example with Confluent Cloud and other setups.

## Troubleshooting

If you encounter issues:

1. **Connection problems**: Run `python generate_logs.py --test-connection` to verify Kafka connectivity
2. **No data flowing**: Check Kafka topic has messages, verify network rules, ensure processors are running
3. **Connection errors**: Verify Kafka broker endpoints in network rule, check security protocol
4. **Slow ingestion**: Consider scaling Openflow runtime, check Kafka partition count

See the [quickstart guide](https://quickstarts.snowflake.com/guide/getting_started_with_openflow_kafka_connector/index.html) for detailed troubleshooting steps.

## Contributing

We welcome contributions! Please open an issue or pull request on GitHub.

## License

Copyright (c) 2025 Snowflake Inc. All rights reserved.

Licensed under the Apache License, Version 2.0. See [LICENSE.txt](LICENSE.txt) for details.

## Support

For questions or issues:

- [Open an issue](https://github.com/Snowflake-Labs/sfquickstarts/issues) on GitHub
- Visit [Snowflake Community](https://community.snowflake.com/)

## Related Quickstarts

- [Getting Started with Openflow SPCS](https://quickstarts.snowflake.com/guide/getting_started_with_openflow_spcs/index.html)
- [Getting Started with PostgreSQL CDC](https://quickstarts.snowflake.com/guide/getting_started_with_openflow_postgresql_cdc/index.html)
- [Getting Started with Unstructured Data Pipeline](https://quickstarts.snowflake.com/guide/getting_started_openflow_unstructured_data_pipeline/index.html)

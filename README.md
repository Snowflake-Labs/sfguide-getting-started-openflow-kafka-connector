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

# Produce sample logs
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

**Usage**:

```bash
# Basic usage
python generate_logs.py --brokers localhost:9092 --topic application-logs --count 100

# With delay between messages
python generate_logs.py --brokers kafka:9092 --topic logs --count 50 --delay 0.5

# Continuous mode (for load testing)
python generate_logs.py --brokers kafka:9092 --topic logs --count 10 --continuous
```

## Troubleshooting

If you encounter issues:

1. **No data flowing**: Check Kafka topic has messages, verify network rules, ensure processors are running
2. **Connection errors**: Verify Kafka broker endpoints in network rule, check security protocol
3. **Slow ingestion**: Consider scaling Openflow runtime, check Kafka partition count

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

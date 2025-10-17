#!/usr/bin/env python3
"""
Kafka Log Generator

This script produces sample application logs to a Kafka topic.
Useful for testing the Openflow Kafka Connector.

Usage:
    # Test connection first (recommended)
    python generate_logs.py --brokers localhost:9092 --topic application-logs --test-connection
    
    # Then produce logs
    python generate_logs.py --brokers localhost:9092 --topic application-logs --count 50
    
    # Or use environment variables:
    export KAFKA_BROKERS=localhost:9092
    export KAFKA_TOPIC=application-logs
    python generate_logs.py --test-connection
    python generate_logs.py --count 50
    
    # For SASL/SSL (e.g., Confluent Cloud):
    export KAFKA_BROKERS=pkc-xxxxx.region.aws.confluent.cloud:9092
    export KAFKA_TOPIC=application-logs
    export KAFKA_SECURITY_PROTOCOL=SASL_SSL
    export KAFKA_SASL_MECHANISM=PLAIN
    export KAFKA_SASL_USERNAME=YOUR_API_KEY
    export KAFKA_SASL_PASSWORD=YOUR_API_SECRET
    python generate_logs.py --test-connection

Alternative: Use rpk (Redpanda CLI) for simpler Kafka operations:
    # Produce from sample file
    rpk topic produce application-logs --brokers localhost:9092 < sample_logs.json
    
    # Or interactive produce
    rpk topic produce application-logs --brokers localhost:9092

Generate sample files for offline testing:
    # Generate base schema sample file (50 records)
    python generate_logs.py --count 50 --output sample_logs.json
    
    # Generate evolved schema sample file (30 records)
    python generate_logs.py --count 30 --evolved --output sample_logs_evolved.json
"""

import argparse
import json
import os
import random
import sys
from datetime import datetime, timezone
from time import sleep

from dotenv import load_dotenv, find_dotenv
try:
    load_dotenv(find_dotenv())
except Exception as e:
    print(f"Error loading .env file: {e}")
    sys.exit(1)


try:
    from kafka import KafkaProducer
except ImportError:
    print("Error: kafka-python library not installed")
    print("Install it with: pip install kafka-python")
    sys.exit(1)


# Sample data for generating realistic logs
SERVICES = [
    "web-api",
    "auth-service",
    "db-service",
    "payment-service",
    "inventory-service",
    "notification-service",
    "search-service",
    "analytics-service"
]

HOSTS = {
    "web-api": ["api-server-01", "api-server-02", "api-server-03"],
    "auth-service": ["auth-server-01", "auth-server-02"],
    "db-service": ["db-server-01"],
    "payment-service": ["payment-server-01", "payment-server-02"],
    "inventory-service": ["inventory-server-01", "inventory-server-02"],
    "notification-service": ["notif-server-01"],
    "search-service": ["search-server-01", "search-server-02"],
    "analytics-service": ["analytics-server-01"]
}

LOG_LEVELS = {
    "INFO": 0.70,    # 70% info logs
    "WARN": 0.20,    # 20% warnings
    "ERROR": 0.10    # 10% errors
}

INFO_MESSAGES = [
    "Request processed successfully",
    "User authentication successful",
    "GET /api/v1/products",
    "POST /api/v1/orders",
    "PUT /api/v1/cart",
    "DELETE /api/v1/cart/items",
    "GET /api/v1/users/profile",
    "Search query executed",
    "Payment processed",
    "Email notification sent",
    "SMS notification sent",
    "Daily report generated",
    "Cache refreshed successfully",
    "Session created",
    "File uploaded successfully"
]

WARN_MESSAGES = [
    "Query execution took longer than expected",
    "Low stock alert for product SKU-12345",
    "Multiple failed login attempts detected",
    "Connection pool nearly exhausted",
    "Payment declined",
    "Rate limit approaching threshold",
    "Memory usage above 80%",
    "Disk space running low"
]

ERROR_MESSAGES = [
    ("Database connection timeout", "ConnectionTimeout"),
    ("Payment gateway timeout", "GatewayTimeout"),
    ("Deadlock detected in transaction", "DeadlockDetected"),
    ("Failed to update inventory count", "ConcurrencyException"),
    ("Internal server error", "NullPointerException"),
    ("Service unavailable", "ServiceUnavailable"),
    ("Authentication failed", "AuthenticationError"),
    ("Invalid input data", "ValidationError")
]

STATUS_CODES = {
    "INFO": [200, 201, 204],
    "WARN": [200, 402],
    "ERROR": [500, 503, 504, 409]
}


def weighted_choice(choices):
    """Select item based on weighted probabilities."""
    items = list(choices.keys())
    weights = list(choices.values())
    return random.choices(items, weights=weights)[0]


def generate_log_event(evolved=False):
    """Generate a single log event with consistent schema.
    
    Args:
        evolved: If True, add evolved fields for schema evolution demonstration
    
    Note:
        This function now generates a consistent schema where all fields are always
        present (set to None if not applicable). This ensures predictable table
        schemas in Snowflake and accurate column counts for the quickstart demo.
    """
    # Select log level based on distribution
    level = weighted_choice(LOG_LEVELS)
    
    # Select service and host
    service = random.choice(SERVICES)
    host = random.choice(HOSTS[service])
    
    # Generate base log structure with ALL base fields (11 total)
    # Always initialize all base schema fields to ensure consistent schema
    log = {
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "level": level,
        "service": service,
        "host": host,
        "request_id": f"req-{random.randbytes(4).hex()}",
        "message": None,
        "duration_ms": None,
        "status_code": None,
        "user_id": None,
        "amount": None,
        "error": None
    }
    
    # Add level-specific content
    if level == "INFO":
        log["message"] = random.choice(INFO_MESSAGES)
        log["duration_ms"] = random.randint(10, 500)
        log["status_code"] = random.choice(STATUS_CODES["INFO"])
        
        # Add user_id conditionally but consistently
        if random.random() < 0.7:  # 70% chance of user_id
            log["user_id"] = f"user-{random.randint(10000, 99999)}"
        
        # Add amount for payment services
        if random.random() < 0.3 and service == "payment-service":
            log["amount"] = round(random.uniform(9.99, 999.99), 2)
            
    elif level == "WARN":
        log["message"] = random.choice(WARN_MESSAGES)
        log["status_code"] = random.choice(STATUS_CODES["WARN"])
        
        # Duration_ms may or may not be present for WARN
        if random.random() < 0.5:
            log["duration_ms"] = random.randint(500, 2000)
        
        # User_id may or may not be present for WARN
        if random.random() < 0.4:
            log["user_id"] = f"user-{random.randint(10000, 99999)}"
            
    else:  # ERROR
        message, error_type = random.choice(ERROR_MESSAGES)
        log["message"] = message
        log["error"] = error_type
        log["status_code"] = random.choice(STATUS_CODES["ERROR"])
        log["duration_ms"] = random.randint(1000, 10000)
    
    # Add evolved fields for schema evolution demonstration
    # Initialize ALL evolved fields (26 total) to ensure consistent schema
    if evolved:
        # Initialize all evolved fields as None first
        evolved_fields = {
            "region": None,
            "trace_id": None,
            "auth_method": None,
            "provider": None,
            "session_duration": None,
            "currency": None,
            "payment_method": None,
            "retry_count": None,
            "file_size_bytes": None,
            "content_type": None,
            "memory_percent": None,
            "available_mb": None,
            "disk_usage_percent": None,
            "available_gb": None,
            "query_params": None,
            "result_count": None,
            "recipient": None,
            "smtp_code": None,
            "metrics_count": None,
            "time_window": None,
            "product_id": None,
            "rating": None,
            "version": None,
            "status": None,
            "test": None,
            "validation_errors": None
        }
        
        # Add region to most logs
        if random.random() < 0.8:
            regions = ["us-east-1", "us-west-2", "us-central-1", "eu-west-1", "eu-central-1", "ap-south-1", "ap-northeast-1"]
            evolved_fields["region"] = random.choice(regions)
        
        # Add trace_id occasionally
        if random.random() < 0.3:
            evolved_fields["trace_id"] = f"trace-{random.randbytes(8).hex()}"
        
        # Add auth-specific extended fields (higher probability for demo)
        if service == "auth-service" and level == "INFO":
            if random.random() < 0.9:  # Increased from 0.6 to ensure demo queries return data
                evolved_fields["auth_method"] = random.choice(["oauth2", "saml", "basic", "api_key"])
                evolved_fields["provider"] = random.choice(["google", "okta", "azure", "aws"])
                if random.random() < 0.7:  # Increased from 0.5
                    evolved_fields["session_duration"] = random.choice([1800, 3600, 7200])
        
        # Add payment-specific extended fields (higher probability for demo)
        if service == "payment-service":
            if log.get("amount") is not None or random.random() < 0.6:  # Ensure payment logs get these fields
                if log.get("amount") is None:
                    log["amount"] = round(random.uniform(9.99, 999.99), 2)
                if random.random() < 0.9:  # Increased from 0.7 to ensure demo queries return data
                    evolved_fields["currency"] = random.choice(["USD", "EUR", "GBP", "JPY"])
                    evolved_fields["payment_method"] = random.choice(["credit_card", "debit_card", "paypal", "bank_transfer"])
        
        # Add retry count for errors
        if level == "ERROR" and random.random() < 0.5:
            evolved_fields["retry_count"] = random.randint(1, 5)
        
        # Add file upload fields for web-api (more scenarios)
        if service == "web-api":
            # Either the message contains "upload" OR randomly add for demo purposes
            if "upload" in log.get("message", "").lower() or random.random() < 0.3:
                evolved_fields["file_size_bytes"] = random.randint(10240, 10485760)  # 10KB to 10MB
                evolved_fields["content_type"] = random.choice(["image/jpeg", "image/png", "application/pdf", "text/csv"])
        
        # Add system metrics for warnings
        if level == "WARN" and ("memory" in log["message"].lower() or "disk" in log["message"].lower()):
            if "memory" in log["message"].lower():
                evolved_fields["memory_percent"] = round(random.uniform(80, 95), 1)
                evolved_fields["available_mb"] = random.randint(256, 1024)
            if "disk" in log["message"].lower():
                evolved_fields["disk_usage_percent"] = random.randint(85, 98)
                evolved_fields["available_gb"] = random.randint(10, 100)
        
        # Add query params for search/web services
        if service in ["web-api", "search-service"] and random.random() < 0.3:
            evolved_fields["query_params"] = {"category": random.choice(["electronics", "books", "clothing"]), "limit": random.choice([10, 25, 50, 100])}
            evolved_fields["result_count"] = random.randint(0, evolved_fields["query_params"]["limit"])
        
        # Add notification-specific fields
        if service == "notification-service" and level == "ERROR":
            if random.random() < 0.5:
                evolved_fields["recipient"] = f"user{random.randint(1000, 9999)}@example.com"
                evolved_fields["smtp_code"] = random.choice([550, 554, 421])
        
        # Add analytics metrics
        if service == "analytics-service" and "metrics" in log.get("message", "").lower():
            if random.random() < 0.6:
                evolved_fields["metrics_count"] = random.randint(100, 5000)
                evolved_fields["time_window"] = random.choice(["1h", "4h", "24h"])
        
        # Add web-api specific fields occasionally
        if service == "web-api" and random.random() < 0.2:
            evolved_fields["product_id"] = f"prod-{random.randint(10000, 99999)}"
            evolved_fields["rating"] = random.randint(1, 5)
        
        # Add version info occasionally
        if random.random() < 0.15:
            evolved_fields["version"] = random.choice(["1.0", "1.5", "2.0", "2.1"])
        
        # Add status field occasionally
        if random.random() < 0.1:
            evolved_fields["status"] = random.choice(["healthy", "degraded", "unhealthy"])
        
        # Add test flag occasionally
        if random.random() < 0.05:
            evolved_fields["test"] = True
        
        # Add validation errors for some ERROR logs
        if level == "ERROR" and "validation" in log.get("message", "").lower():
            evolved_fields["validation_errors"] = ["missing_field", "invalid_format"]
        
        # Merge evolved fields into log
        log.update(evolved_fields)
    
    return log


def create_producer(bootstrap_servers, security_protocol='PLAINTEXT', sasl_mechanism=None, 
                    sasl_username=None, sasl_password=None):
    """Create Kafka producer with optional SASL authentication."""
    config = {
        'bootstrap_servers': bootstrap_servers,
        'value_serializer': lambda v: json.dumps(v).encode('utf-8'),
        'key_serializer': lambda k: k.encode('utf-8') if k else None,
        'security_protocol': security_protocol
    }
    
    # Add SASL configuration if using SASL-based security
    if security_protocol in ['SASL_PLAINTEXT', 'SASL_SSL']:
        if not sasl_mechanism:
            print("Error: SASL mechanism is required when using SASL_PLAINTEXT or SASL_SSL")
            print("Set KAFKA_SASL_MECHANISM environment variable or use --sasl-mechanism")
            sys.exit(1)
        
        config['sasl_mechanism'] = sasl_mechanism
        
        if sasl_mechanism in ['PLAIN', 'SCRAM-SHA-256', 'SCRAM-SHA-512']:
            if not sasl_username or not sasl_password:
                print(f"Error: Username and password required for {sasl_mechanism}")
                print("Set KAFKA_SASL_USERNAME and KAFKA_SASL_PASSWORD environment variables")
                sys.exit(1)
            config['sasl_plain_username'] = sasl_username
            config['sasl_plain_password'] = sasl_password
    
    try:
        producer = KafkaProducer(**config)
        return producer
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"\nError creating Kafka producer: {e}")
        print("\nPlease verify your Kafka configuration:")
        print(f"  Brokers: {bootstrap_servers}")
        print(f"  Security Protocol: {security_protocol}")
        if security_protocol in ['SASL_PLAINTEXT', 'SASL_SSL']:
            print(f"  SASL Mechanism: {sasl_mechanism}")
            print(f"  SASL Username: {sasl_username if sasl_username else '(not set)'}")
        sys.exit(1)


def test_connection(bootstrap_servers, topic, security_protocol='PLAINTEXT', sasl_mechanism=None,
                    sasl_username=None, sasl_password=None):
    """Test connection to Kafka cluster and topic accessibility."""
    print("\n" + "="*60)
    print("KAFKA CONNECTION TEST")
    print("="*60)
    
    # Test 1: Create producer (tests broker connectivity)
    print(f"\n[1/4] Testing connection to Kafka brokers...")
    print(f"      Brokers: {bootstrap_servers}")
    print(f"      Security: {security_protocol}")
    if security_protocol in ['SASL_PLAINTEXT', 'SASL_SSL']:
        print(f"      SASL Mechanism: {sasl_mechanism}")
        print(f"      SASL Username: {sasl_username if sasl_username else '(not set)'}")
    
    try:
        producer = create_producer(bootstrap_servers, security_protocol, sasl_mechanism,
                                  sasl_username, sasl_password)
        print("      ✓ Successfully connected to Kafka brokers")
    except Exception as e:
        print(f"      ✗ Failed to connect: {e}")
        return False
    
    # Test 2: Check cluster metadata
    print(f"\n[2/4] Fetching cluster metadata...")
    try:
        # Give the producer a moment to fetch metadata
        sleep(1)
        
        # Access cluster metadata through the producer
        cluster = producer._metadata._partitions
        
        if cluster:
            # Get unique brokers from metadata
            brokers_found = set()
            for topic_partitions in cluster.values():
                for partition_metadata in topic_partitions.values():
                    if hasattr(partition_metadata, 'leader'):
                        brokers_found.add(partition_metadata.leader)
            
            if brokers_found:
                print(f"      ✓ Cluster metadata retrieved")
                print(f"      ✓ Found {len(brokers_found)} broker node(s): {sorted(brokers_found)}")
            else:
                print(f"      ✓ Connected to cluster (metadata available)")
        else:
            print(f"      ✓ Connected to cluster")
            
    except Exception as e:
        print(f"      ⚠ Could not fetch detailed metadata: {e}")
        print(f"      Note: This is not critical - connection was successful")
    
    # Test 3: Check topic accessibility
    print(f"\n[3/4] Checking topic accessibility...")
    print(f"      Topic: {topic}")
    
    try:
        # Use the public API to get partitions for the topic
        # This will return None if topic doesn't exist, or a set of partition IDs if it does
        partitions = producer.partitions_for(topic)
        
        if partitions is not None:
            print(f"      ✓ Topic '{topic}' exists and is accessible")
            print(f"      ✓ Topic has {len(partitions)} partition(s): {sorted(partitions)}")
        else:
            print(f"      ⚠ Topic '{topic}' not found in cluster")
            print(f"      Note: Topic may be auto-created on first write (if broker allows auto-creation)")
    except Exception as e:
        print(f"      ⚠ Could not check topic: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 4: Test write permissions (send a test message)
    print(f"\n[4/4] Testing write permissions...")
    try:
        test_log = {
            "test": True,
            "message": "Connection test from generate_logs.py",
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        }
        
        print(f"      Sending test message to topic '{topic}'...")
        future = producer.send(topic, key="test", value=test_log)
        
        # Wait for the message to be sent
        try:
            record_metadata = future.get(timeout=30)
            print(f"      ✓ Successfully sent test message")
            print(f"      ✓ Written to partition {record_metadata.partition} at offset {record_metadata.offset}")
        except Exception as send_error:
            print(f"      ✗ Failed to send test message: {send_error}")
            import traceback
            traceback.print_exc()
            producer.close()
            return False
            
    except Exception as e:
        print(f"      ✗ Error preparing test message: {e}")
        import traceback
        traceback.print_exc()
        producer.close()
        return False
    
    # Cleanup
    producer.close()
    
    # Summary
    print("\n" + "="*60)
    print("CONNECTION TEST RESULT: ✓ SUCCESS")
    print("="*60)
    print("\nYour Kafka configuration is working correctly!")
    print(f"You can now produce logs with:")
    print(f"  python generate_logs.py --count 100")
    print()
    
    return True


def write_logs_to_file(output_file, count, evolved=False):
    """Write log events to a JSONL file."""
    mode = "evolved schema" if evolved else "base schema"
    print(f"Generating {count} log events ({mode}) to file '{output_file}'...")
    
    try:
        with open(output_file, 'w') as f:
            for i in range(count):
                log = generate_log_event(evolved=evolved)
                f.write(json.dumps(log) + '\n')
                
                if (i + 1) % 10 == 0 or (i + 1) == count:
                    print(f"  Generated {i + 1}/{count} events")
        
        print(f"✓ Successfully wrote {count} log events ({mode}) to {output_file}")
        print(f"\nYou can now produce these logs to Kafka with:")
        print(f"  rpk topic produce <topic-name> -f '%v{{json}}\\n' < {output_file}")
        
    except Exception as e:
        print(f"Error writing to file: {e}")
        sys.exit(1)


def produce_logs(producer, topic, count, delay=0, evolved=False):
    """Produce log events to Kafka topic."""
    mode = "evolved schema" if evolved else "base schema"
    print(f"Producing {count} log events ({mode}) to topic '{topic}'...")
    
    for i in range(count):
        log = generate_log_event(evolved=evolved)
        
        # Use service as message key for partition distribution
        key = log.get("service", "test")
        
        try:
            # Send to Kafka
            future = producer.send(topic, key=key, value=log)
            
            # Wait for send to complete (optional, for reliability)
            record_metadata = future.get(timeout=10)
            
            if (i + 1) % 10 == 0 or (i + 1) == count:
                print(f"  Sent {i + 1}/{count} events (partition: {record_metadata.partition}, offset: {record_metadata.offset})")
            
            # Optional delay between messages
            if delay > 0 and i < count - 1:
                sleep(delay)
                
        except Exception as e:
            print(f"Error sending message {i + 1}: {e}")
    
    # Flush to ensure all messages are sent
    producer.flush()
    print(f"✓ Successfully produced {count} log events ({mode})")


def main():
    parser = argparse.ArgumentParser(
        description='Generate sample application logs and produce them to Kafka',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate sample files (no Kafka required)
  python generate_logs.py --count 50 --output sample_logs.json
  python generate_logs.py --count 30 --evolved --output sample_logs_evolved.json
  
  # Test connection to Kafka (recommended first step)
  python generate_logs.py --brokers localhost:9092 --topic application-logs --test-connection
  
  # Produce 50 logs to local Kafka
  python generate_logs.py --brokers localhost:9092 --topic application-logs --count 50
  
  # Produce 100 logs with 0.5 second delay between each
  python generate_logs.py --brokers kafka.example.com:9092 --topic app-logs --count 100 --delay 0.5
  
  # Continuous production (run until Ctrl+C)
  python generate_logs.py --brokers localhost:9092 --topic logs --count 10 --continuous
  
  # Using environment variables
  export KAFKA_BROKERS=localhost:9092 KAFKA_TOPIC=logs
  python generate_logs.py --test-connection
  python generate_logs.py --count 100

Environment Variables:
  KAFKA_BROKERS           Default Kafka broker(s) to connect to
  KAFKA_TOPIC             Default Kafka topic name
  KAFKA_SECURITY_PROTOCOL Default security protocol (default: PLAINTEXT)
  KAFKA_SASL_MECHANISM    SASL mechanism (required for SASL_* protocols)
  KAFKA_SASL_USERNAME     SASL username (required for PLAIN, SCRAM-*)
  KAFKA_SASL_PASSWORD     SASL password (required for PLAIN, SCRAM-*)
        """
    )
    
    parser.add_argument(
        '--brokers',
        default=os.environ.get('KAFKA_BROKERS'),
        help='Kafka broker(s) (comma-separated if multiple): e.g., localhost:9092 or broker1:9092,broker2:9092. Can be set via KAFKA_BROKERS env var.'
    )
    parser.add_argument(
        '--topic',
        default=os.environ.get('KAFKA_TOPIC'),
        help='Kafka topic name to produce to. Can be set via KAFKA_TOPIC env var.'
    )
    parser.add_argument(
        '--count',
        type=int,
        default=10,
        help='Number of log events to produce (default: 10)'
    )
    parser.add_argument(
        '--delay',
        type=float,
        default=0,
        help='Delay in seconds between messages (default: 0)'
    )
    parser.add_argument(
        '--continuous',
        action='store_true',
        help='Run continuously (produce COUNT events, sleep 5s, repeat)'
    )
    parser.add_argument(
        '--security-protocol',
        default=os.environ.get('KAFKA_SECURITY_PROTOCOL', 'PLAINTEXT'),
        choices=['PLAINTEXT', 'SSL', 'SASL_PLAINTEXT', 'SASL_SSL'],
        help='Security protocol (default: PLAINTEXT). Can be set via KAFKA_SECURITY_PROTOCOL env var.'
    )
    parser.add_argument(
        '--sasl-mechanism',
        default=os.environ.get('KAFKA_SASL_MECHANISM'),
        choices=['PLAIN', 'SCRAM-SHA-256', 'SCRAM-SHA-512', 'GSSAPI', 'OAUTHBEARER'],
        help='SASL mechanism (required for SASL_* protocols). Can be set via KAFKA_SASL_MECHANISM env var.'
    )
    parser.add_argument(
        '--sasl-username',
        default=os.environ.get('KAFKA_SASL_USERNAME'),
        help='SASL username (required for PLAIN, SCRAM-*). Can be set via KAFKA_SASL_USERNAME env var.'
    )
    parser.add_argument(
        '--sasl-password',
        default=os.environ.get('KAFKA_SASL_PASSWORD'),
        help='SASL password (required for PLAIN, SCRAM-*). Can be set via KAFKA_SASL_PASSWORD env var.'
    )
    parser.add_argument(
        '--test-connection',
        action='store_true',
        help='Test Kafka connection and exit (no logs produced)'
    )
    parser.add_argument(
        '--evolved',
        action='store_true',
        help='Generate logs with evolved fields for schema evolution demonstration'
    )
    parser.add_argument(
        '--output',
        help='Output file path (JSONL format). If specified, writes to file instead of Kafka. Brokers and topic are not required when using --output.'
    )
    
    args = parser.parse_args()
    
    # Validate required arguments (skip for --output mode)
    if not args.output:
        if not args.brokers:
            parser.error("--brokers is required (or set KAFKA_BROKERS environment variable)")
        if not args.topic:
            parser.error("--topic is required (or set KAFKA_TOPIC environment variable)")
    
    # Handle connection test mode
    if args.test_connection:
        if not args.brokers or not args.topic:
            parser.error("--test-connection requires --brokers and --topic")
        success = test_connection(
            args.brokers, 
            args.topic, 
            args.security_protocol,
            args.sasl_mechanism,
            args.sasl_username,
            args.sasl_password
        )
        sys.exit(0 if success else 1)
    
    # Handle file output mode
    if args.output:
        write_logs_to_file(args.output, args.count, args.evolved)
        sys.exit(0)
    
    # Create producer for Kafka mode
    print(f"Connecting to Kafka brokers: {args.brokers}")
    producer = create_producer(
        args.brokers, 
        args.security_protocol,
        args.sasl_mechanism,
        args.sasl_username,
        args.sasl_password
    )
    print("✓ Connected to Kafka")
    
    try:
        if args.continuous:
            print(f"Running in continuous mode (Ctrl+C to stop)")
            iteration = 1
            while True:
                print(f"\n--- Iteration {iteration} ---")
                produce_logs(producer, args.topic, args.count, args.delay, args.evolved)
                print("Sleeping 5 seconds before next batch...")
                sleep(5)
                iteration += 1
        else:
            produce_logs(producer, args.topic, args.count, args.delay, args.evolved)
            
    except KeyboardInterrupt:
        print("\n\nStopped by user (Ctrl+C)")
    finally:
        producer.close()
        print("✓ Producer closed")


if __name__ == "__main__":
    main()


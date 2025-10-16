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
"""

import argparse
import json
import os
import random
import sys
from datetime import datetime, timezone
from time import sleep

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


def generate_log_event():
    """Generate a single log event."""
    # Select log level based on distribution
    level = weighted_choice(LOG_LEVELS)
    
    # Select service and host
    service = random.choice(SERVICES)
    host = random.choice(HOSTS[service])
    
    # Generate base log structure
    log = {
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "level": level,
        "service": service,
        "host": host,
        "request_id": f"req-{random.randbytes(4).hex()}"
    }
    
    # Add level-specific content
    if level == "INFO":
        log["message"] = random.choice(INFO_MESSAGES)
        log["duration_ms"] = random.randint(10, 500)
        log["status_code"] = random.choice(STATUS_CODES["INFO"])
        
        # Add optional fields
        if random.random() < 0.7:  # 70% chance of user_id
            log["user_id"] = f"user-{random.randint(10000, 99999)}"
        if random.random() < 0.5 and service == "web-api":  # 50% chance of IP for web-api
            log["ip_address"] = f"192.168.{random.randint(1,255)}.{random.randint(1,255)}"
        if random.random() < 0.3 and service == "payment-service":  # Payment amounts
            log["amount"] = round(random.uniform(9.99, 999.99), 2)
            
    elif level == "WARN":
        log["message"] = random.choice(WARN_MESSAGES)
        log["status_code"] = random.choice(STATUS_CODES["WARN"])
        if random.random() < 0.5:
            log["duration_ms"] = random.randint(500, 2000)
        if random.random() < 0.4:
            log["user_id"] = f"user-{random.randint(10000, 99999)}"
            
    else:  # ERROR
        message, error_type = random.choice(ERROR_MESSAGES)
        log["message"] = message
        log["error"] = error_type
        log["status_code"] = random.choice(STATUS_CODES["ERROR"])
        log["duration_ms"] = random.randint(1000, 10000)
    
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
        metadata = producer._metadata
        # Force metadata refresh
        producer._sender._metadata.request_update()
        cluster_metadata = producer._metadata.fetch()
        
        if cluster_metadata:
            brokers = cluster_metadata.brokers()
            print(f"      ✓ Connected to {len(brokers)} broker(s):")
            for broker in brokers:
                print(f"        - {broker.host}:{broker.port} (node {broker.nodeId})")
        else:
            print("      ⚠ Could not retrieve cluster metadata")
    except Exception as e:
        print(f"      ⚠ Could not fetch metadata: {e}")
    
    # Test 3: Check topic accessibility
    print(f"\n[3/4] Checking topic accessibility...")
    print(f"      Topic: {topic}")
    
    try:
        # Get list of topics
        topics = producer._metadata.topics()
        
        if topic in topics:
            print(f"      ✓ Topic '{topic}' exists and is accessible")
            
            # Get partition info
            partitions = producer.partitions_for(topic)
            if partitions:
                print(f"      ✓ Topic has {len(partitions)} partition(s): {sorted(partitions)}")
        else:
            print(f"      ⚠ Topic '{topic}' not found in cluster")
            print(f"      Note: Topic may be auto-created on first write (if enabled)")
            print(f"      Available topics: {list(topics)[:5]}{'...' if len(topics) > 5 else ''}")
    except Exception as e:
        print(f"      ⚠ Could not check topic: {e}")
    
    # Test 4: Test write permissions (send a test message)
    print(f"\n[4/4] Testing write permissions...")
    try:
        test_log = {
            "test": True,
            "message": "Connection test from generate_logs.py",
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        }
        
        future = producer.send(topic, key="test", value=test_log)
        record_metadata = future.get(timeout=10)
        
        print(f"      ✓ Successfully sent test message")
        print(f"      ✓ Written to partition {record_metadata.partition} at offset {record_metadata.offset}")
    except Exception as e:
        print(f"      ✗ Failed to send test message: {e}")
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


def produce_logs(producer, topic, count, delay=0):
    """Produce log events to Kafka topic."""
    print(f"Producing {count} log events to topic '{topic}'...")
    
    for i in range(count):
        log = generate_log_event()
        
        # Use service as message key for partition distribution
        key = log["service"]
        
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
    print(f"✓ Successfully produced {count} log events")


def main():
    parser = argparse.ArgumentParser(
        description='Generate sample application logs and produce them to Kafka',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
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
    
    args = parser.parse_args()
    
    # Validate required arguments
    if not args.brokers:
        parser.error("--brokers is required (or set KAFKA_BROKERS environment variable)")
    if not args.topic:
        parser.error("--topic is required (or set KAFKA_TOPIC environment variable)")
    
    # Handle connection test mode
    if args.test_connection:
        success = test_connection(
            args.brokers, 
            args.topic, 
            args.security_protocol,
            args.sasl_mechanism,
            args.sasl_username,
            args.sasl_password
        )
        sys.exit(0 if success else 1)
    
    # Create producer
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
                produce_logs(producer, args.topic, args.count, args.delay)
                print("Sleeping 5 seconds before next batch...")
                sleep(5)
                iteration += 1
        else:
            produce_logs(producer, args.topic, args.count, args.delay)
            
    except KeyboardInterrupt:
        print("\n\nStopped by user (Ctrl+C)")
    finally:
        producer.close()
        print("✓ Producer closed")


if __name__ == "__main__":
    main()


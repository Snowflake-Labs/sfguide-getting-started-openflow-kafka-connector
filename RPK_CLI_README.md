# Redpanda CLI (rpk) Setup for Confluent Cloud

This guide walks you through setting up the Redpanda CLI (`rpk`) to work with Confluent Cloud
as an alternative to the Confluent CLI.

## Why Use RPK CLI

RPK is a modern, user-friendly CLI for Kafka that offers:

- Simple, intuitive commands
- Fast performance
- Kafka-compatible (works with Confluent Cloud, Apache Kafka, Redpanda)
- Better developer experience with sensible defaults

## Download and Install RPK

### Official Download

Download the latest version of RPK from the official Redpanda website:

**Download URL**: [https://docs.redpanda.com/current/get-started/rpk-install/](https://docs.redpanda.com/current/get-started/rpk-install/)

### Quick Install

**macOS (Homebrew):**

```bash
brew install redpanda-data/tap/redpanda
```

**Linux (RPM-based):**

```bash
curl -1sLf 'https://dl.redpanda.com/nzc4ZYQK3WRGd9sy/redpanda/cfg/setup/bash.rpm.sh' | sudo -E bash
sudo yum install redpanda -y
```

**Linux (Debian/Ubuntu):**

```bash
curl -1sLf 'https://dl.redpanda.com/nzc4ZYQK3WRGd9sy/redpanda/cfg/setup/bash.deb.sh' | sudo -E bash
sudo apt-get install redpanda -y
```

**Manual Download:**
Visit [Redpanda Downloads](https://github.com/redpanda-data/redpanda/releases) for direct binary downloads.

## Configure RPK for Confluent Cloud

### Prerequisites

You'll need your Confluent Cloud credentials:

- Bootstrap server address
- API Key (SASL username)
- API Secret (SASL password)

### Configuration Steps

#### 1. Create a Profile

```bash
rpk profile create confluent-cloud
```

#### 2. Configure Connection Parameters

Use the following command to set all parameters at once:

```bash
rpk profile set \
  brokers=pkc-xxxxx.us-west-2.aws.confluent.cloud:9092 \
  user=YOUR_API_KEY \
  pass=YOUR_API_SECRET \
  sasl.mechanism=PLAIN
```

> **Important Note**: Replace the values above with your own Confluent Cloud credentials.

#### 3. Enable TLS (Required for Confluent Cloud)

The `rpk profile set` command doesn't properly persist the TLS setting, so you need to manually edit the configuration file:

```bash
rpk edit profile confluent-cloud
```

Find your profile section and change `tls: {}` to:

```yaml
tls:
  enabled: true
```

Your complete profile should look like this:

```yaml
- name: confluent-cloud
  kafka_api:
    brokers:
      - pkc-xxxxx.us-west-2.aws.confluent.cloud:9092
    tls:
      enabled: true
    sasl:
      user: YOUR_API_KEY
      password: YOUR_API_SECRET
      mechanism: PLAIN
```

#### 4. Verify Configuration

Check your profile configuration:

```bash
rpk profile print
```

## Test the Connection

### List Topics

```bash
rpk topic list
```

Expected output:

```text
NAME     PARTITIONS  REPLICAS
topic_0  6           3
```

### Get Cluster Information

```bash
rpk cluster info
```

### Describe a Topic

```bash
rpk topic describe topic_0
```

## Common RPK Commands

### Topic Management

```bash
# Create a topic
rpk topic create my-topic --partitions 6 --replicas 3

# Delete a topic
rpk topic delete my-topic

# List all topics
rpk topic list

# Describe a topic
rpk topic describe my-topic
```

### Produce Messages

```bash
# Produce a single message
echo "hello world" | rpk topic produce my-topic

# Produce interactively (type messages, press Ctrl+D when done)
rpk topic produce my-topic

# Produce with key
rpk topic produce my-topic --key mykey
```

### Consume Messages

```bash
# Consume from beginning
rpk topic consume my-topic --offset start

# Consume from end (latest)
rpk topic consume my-topic --offset end

# Consume with consumer group
rpk topic consume my-topic -g my-consumer-group

# Consume and print keys
rpk topic consume my-topic --format '%k: %v\n'
```

### Consumer Groups

```bash
# List consumer groups
rpk group list

# Describe a consumer group
rpk group describe my-consumer-group

# Delete a consumer group
rpk group delete my-consumer-group
```

### ACLs (Access Control Lists)

```bash
# List ACLs
rpk acl list

# Create ACL
rpk acl create --allow-principal User:myuser --operation read --topic my-topic
```

## Troubleshooting

### Connection Issues

If you encounter connection errors:

1. **Verify TLS is enabled**: Make sure `tls.enabled: true` is in your profile
2. **Check credentials**: Ensure your API key and secret are correct
3. **Use verbose mode**: Add `-v` flag for detailed debug output

   ```bash
   rpk topic list -v
   ```

### Override Configuration

You can override any setting using the `-X` flag:

```bash
rpk topic list -X tls.enabled=true
rpk cluster info -X brokers=different-broker:9092
```

## Profile Management

```bash
# List all profiles
rpk profile list

# Switch profiles
rpk profile use confluent-cloud

# Print current profile
rpk profile print

# Delete a profile
rpk profile delete confluent-cloud
```

## Additional Resources

- [RPK Documentation](https://docs.redpanda.com/current/reference/rpk/)
- [Redpanda Console](https://docs.redpanda.com/current/manage/console/)
- [Confluent Cloud Documentation](https://docs.confluent.io/)
- [Apache Kafka Documentation](https://kafka.apache.org/documentation/)

## Configuration File Location

The RPK configuration file is located at:

- **macOS**: `~/Library/Application Support/rpk/rpk.yaml`
- **Linux**: `~/.config/rpk/rpk.yaml`
- **Windows**: `%APPDATA%\rpk\rpk.yaml`

## Security Note

⚠️ **Important**: The configuration file contains your API credentials in plain text.
Ensure proper file permissions:

```bash
chmod 600 "$HOME/Library/Application Support/rpk/rpk.yaml"  # macOS
chmod 600 ~/.config/rpk/rpk.yaml  # Linux
```

Never commit this file to version control. Add it to your `.gitignore`:

```text
rpk.yaml
```

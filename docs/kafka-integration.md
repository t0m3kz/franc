# Kafka Integration Guide

## Overview

The FRANC Service Portal now includes Kafka integration to publish service request events for downstream processing. When enabled, the portal will publish structured events to Kafka topics when users submit service requests.

## Configuration

### Environment Variables

Create a `.env` file in the project root (or set environment variables directly):

```bash
# Enable Kafka integration
KAFKA_ENABLED=true

# Kafka broker configuration
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
KAFKA_TOPIC_PREFIX=franc

# Security configuration (optional)
KAFKA_SECURITY_PROTOCOL=PLAINTEXT
KAFKA_SASL_MECHANISM=PLAIN
KAFKA_SASL_USERNAME=your_username
KAFKA_SASL_PASSWORD=your_password

# SSL configuration (optional)
KAFKA_SSL_CAFILE=/path/to/ca-cert.pem
KAFKA_SSL_CERTFILE=/path/to/client-cert.pem
KAFKA_SSL_KEYFILE=/path/to/client-key.pem
```

### Topic Structure

The integration publishes events to the following topics:

- `{KAFKA_TOPIC_PREFIX}.device.connection` - Device connection requests
- `{KAFKA_TOPIC_PREFIX}.datacenter.deployment` - Data center deployment requests  
- `{KAFKA_TOPIC_PREFIX}.pop.deployment` - PoP deployment requests
- `{KAFKA_TOPIC_PREFIX}.task.status` - Task status updates (progress, errors)
- `{KAFKA_TOPIC_PREFIX}.task.completion` - Task completion events

With the default prefix `franc`, topics will be:
- `franc.device.connection`
- `franc.datacenter.deployment`
- `franc.pop.deployment`
- `franc.task.status`
- `franc.task.completion`

## Event Schema

### Device Connection Event

```json
{
  "event_id": "conn_CHG-2024-001234_20240709_142530",
  "event_type": "device_connection",
  "change_number": "CHG-2024-001234",
  "request_id": "device_conn_CHG-2024-001234",
  "timestamp": "2024-07-09T14:25:30.123456Z",
  "user_id": null,
  "source": "franc-portal",
  "device_name": "NYC-Core-SW01",
  "device_type": "Switch",
  "location": "NYC Building A",
  "interfaces": [
    {
      "name": "Gi0/1",
      "speed": "1 Gbit",
      "role": "data",
      "vpc_group": "vPC-1"
    }
  ],
  "vpc_groups": ["vPC-1"]
}
```

### Data Center Deployment Event

```json
{
  "event_id": "dc_CHG-2024-001235_20240709_142530",
  "event_type": "datacenter_deployment",
  "change_number": "CHG-2024-001235",
  "request_id": "datacenter_CHG-2024-001235",
  "timestamp": "2024-07-09T14:25:30.123456Z",
  "user_id": null,
  "source": "franc-portal",
  "dc_name": "NYC-DC-01",
  "location": "New York Metro",
  "design_pattern": "Spine-Leaf"
}
```

### PoP Deployment Event

```json
{
  "event_id": "pop_CHG-2024-001236_20240709_142530",
  "event_type": "pop_deployment",
  "change_number": "CHG-2024-001236",
  "request_id": "pop_CHG-2024-001236",
  "timestamp": "2024-07-09T14:25:30.123456Z",
  "user_id": null,
  "source": "franc-portal",
  "pop_name": "NYC-PoP-01",
  "location": "New York Metro",
  "design_pattern": "Hub-Spoke",
  "provider": "Equinix"
}
```

### Task Status Update Event

```json
{
  "event_id": "status_CHG-2024-001234_20240709_143015",
  "event_type": "task_status_update",
  "change_number": "CHG-2024-001234",
  "request_id": "status_update_CHG-2024-001234",
  "timestamp": "2024-07-09T14:30:15.123456Z",
  "user_id": null,
  "source": "franc-portal",
  "original_request_id": "device_conn_CHG-2024-001234",
  "status": "in_progress",
  "progress_percentage": 65,
  "status_message": "Configuring interfaces on device NYC-Core-SW01",
  "error_details": null,
  "estimated_completion": "2024-07-09T14:35:00.000000Z"
}
```

### Task Completion Event

```json
{
  "event_id": "complete_CHG-2024-001234_20240709_143500",
  "event_type": "task_completion",
  "change_number": "CHG-2024-001234",
  "request_id": "completion_CHG-2024-001234",
  "timestamp": "2024-07-09T14:35:00.123456Z",
  "user_id": null,
  "source": "franc-portal",
  "original_request_id": "device_conn_CHG-2024-001234",
  "completion_status": "completed",
  "completion_message": "Device NYC-Core-SW01 successfully connected with 4 interfaces configured",
  "result_data": {
    "device_ip": "10.1.1.100",
    "management_vlan": "100",
    "configured_interfaces": ["Gi0/1", "Gi0/2", "Gi0/3", "Gi0/4"]
  },
  "error_details": null,
  "execution_duration": 180.5
}
```

## Usage

### Enabling Kafka

1. Set up your Kafka cluster or use a local Kafka instance
2. Configure the environment variables (see above)
3. Set `KAFKA_ENABLED=true`
4. Restart the FRANC portal

### User Experience

When Kafka is enabled:
- Users will see a "📡 Event successfully published to Kafka" message on successful submissions
- If Kafka publishing fails, users will see a warning but the request will still be processed
- All requests are processed normally regardless of Kafka status
- Users will see real-time task execution progress with status updates
- Task status updates and completion events are automatically published to Kafka

When Kafka is disabled (default):
- No additional messages are shown to users
- No events are published to Kafka
- The portal functions normally without any Kafka dependencies
- A simplified task completion message is shown instead of full progress tracking

### Testing Connection

You can test the Kafka connection programmatically:

```python
from kafka_integration import is_kafka_enabled, test_kafka_connection

if is_kafka_enabled():
    connection_ok = test_kafka_connection()
    print(f"Kafka connection: {'OK' if connection_ok else 'FAILED'}")
else:
    print("Kafka is disabled")
```

## Monitoring

### Message Keys

Events use the change number as the message key for consistent partitioning:
- All events for the same change number will go to the same partition
- This ensures ordering for related events

### Error Handling

The integration includes robust error handling:
- Connection failures are logged and don't block user requests
- Publish failures are logged and reported to users
- The portal continues to function even if Kafka is unavailable

### Logging

Kafka integration logs include:
- Connection status
- Successful event publications with partition and offset information
- Error details for troubleshooting

## Production Considerations

### Security

- Use SASL/SSL for production Kafka clusters
- Implement proper authentication and authorization
- Consider using service accounts for the portal

### Reliability

- Configure appropriate `acks` and `retries` settings
- Monitor partition distribution and consumer lag
- Implement dead letter queues for failed messages

### Scalability

- Use multiple partitions for high-throughput scenarios
- Consider message compression for large payloads
- Monitor broker resource usage

## Dependencies

The Kafka integration requires:
- `kafka-python>=2.0.2`
- `pydantic>=2.5.0`

These are automatically installed when you install the project dependencies.

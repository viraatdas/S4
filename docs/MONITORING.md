# S4 Monitoring and Scaling Guide

This guide provides instructions for monitoring, scaling, and maintaining the S4 service in a production environment.

## Monitoring

### Key Metrics to Monitor

For effective operation of your S4 service, monitor these key metrics:

1. **API Performance Metrics**
   - Request latency (p50, p95, p99)
   - Request count/throughput
   - Error rates (4xx, 5xx)
   - Endpoint usage patterns

2. **Resource Utilization**
   - CPU usage
   - Memory usage
   - Disk space
   - Network I/O

3. **S3 Storage Metrics**
   - Storage consumption (per tenant)
   - Request count and latency
   - Error rates

4. **Tenant-Specific Metrics**
   - Number of active tenants
   - API calls per tenant
   - File count and storage used per tenant
   - Tenant plan utilization percentage

### Monitoring Solutions

#### AWS CloudWatch (for AWS deployments)

Set up CloudWatch metrics and alarms:

```bash
# Example CloudWatch alarm for high CPU usage
aws cloudwatch put-metric-alarm \
  --alarm-name s4-high-cpu \
  --comparison-operator GreaterThanThreshold \
  --evaluation-periods 2 \
  --metric-name CPUUtilization \
  --namespace AWS/ECS \
  --period 300 \
  --threshold 80 \
  --alarm-description "Alarm when CPU exceeds 80%" \
  --alarm-actions arn:aws:sns:us-east-1:123456789012:s4-alerts \
  --dimensions Name=ServiceName,Value=s4-service Name=ClusterName,Value=s4-cluster
```

#### Google Cloud Monitoring (for GCP deployments)

Set up Cloud Monitoring dashboards and alerts:

```bash
# Example Cloud Monitoring alert policy for high memory usage
gcloud alpha monitoring policies create \
  --policy-from-file=policy.yaml
```

Example policy.yaml:
```yaml
combiner: OR
conditions:
- conditionThreshold:
    comparison: COMPARISON_GT
    duration: 300s
    filter: resource.type = "cloud_run_revision" AND
            resource.labels.service_name = "s4-service" AND
            metric.type = "run.googleapis.com/container/memory/utilizations"
    thresholdValue: 0.8
displayName: S4 Service High Memory Utilization
```

#### Prometheus + Grafana (self-hosted)

For a self-hosted monitoring solution, you can integrate Prometheus and Grafana:

1. Add Prometheus client to the S4 service
2. Expose metrics endpoints (`/metrics`)
3. Configure Prometheus to scrape these endpoints
4. Create Grafana dashboards for visualization

Example Prometheus configuration:
```yaml
scrape_configs:
  - job_name: 's4-service'
    metrics_path: '/metrics'
    static_configs:
      - targets: ['s4-service:8000']
```

## Application Logging

Implement structured logging for debugging and monitoring:

```python
# Example logging pattern in S4 code
import logging
import json

logger = logging.getLogger("s4")

def log_event(event_type, tenant_id=None, details=None):
    """Log a structured event"""
    log_data = {
        "event_type": event_type,
        "timestamp": datetime.utcnow().isoformat(),
        "tenant_id": tenant_id,
        "details": details or {}
    }
    logger.info(json.dumps(log_data))
```

Configure log aggregation services such as:
- AWS CloudWatch Logs
- Google Cloud Logging
- ELK Stack (Elasticsearch, Logstash, Kibana)
- Datadog
- Splunk

## Scaling Strategies

### Vertical Scaling

Increase resources allocated to your service:

- For Elastic Beanstalk:
  ```bash
  eb scale s4-production --instances 3
  ```

- For Google Cloud Run:
  ```bash
  gcloud run services update s4-service \
    --memory 4Gi \
    --cpu 2
  ```

### Horizontal Scaling

Add more instances of your service:

- For Elastic Beanstalk:
  ```bash
  eb scale s4-production --instances 3
  ```

- For ECS:
  ```bash
  aws ecs update-service \
    --cluster s4-cluster \
    --service s4-service \
    --desired-count 3
  ```

- For Google Cloud Run:
  ```bash
  gcloud run services update s4-service \
    --max-instances=20
  ```

### Automatic Scaling

Configure autoscaling based on metrics:

- For Elastic Beanstalk:
  ```yaml
  Resources:
    AWSEBAutoScalingGroup:
      Type: AWS::AutoScaling::AutoScalingGroup
      Properties:
        MinSize: 1
        MaxSize: 10
  ```

- For ECS:
  ```bash
  aws application-autoscaling register-scalable-target \
    --service-namespace ecs \
    --scalable-dimension ecs:service:DesiredCount \
    --resource-id service/s4-cluster/s4-service \
    --min-capacity 1 \
    --max-capacity 10
  ```

- For Google Cloud Run:
  ```bash
  gcloud run services update s4-service \
    --min-instances=1 \
    --max-instances=10
  ```

## Database/Storage Scaling

### S3 Scaling Considerations

S3 scales automatically, but consider:

1. **Request Rate**: Monitor request rates and implement rate limiting if needed
2. **Cost Optimization**: Implement lifecycle policies for old data
3. **Performance**: Use appropriate S3 storage classes based on access patterns

### Managing Tenant Data Growth

1. **Implement Storage Quotas**: Enforce storage limits based on tenant plans
2. **Data Archiving**: Automatically archive old data to cheaper storage
3. **Data Cleanup**: Implement data retention policies

## Backup and Disaster Recovery

### Regular Backups

Create automated backups of tenant data:

```bash
#!/bin/bash
# Example backup script
TIMESTAMP=$(date +%Y%m%d%H%M%S)
BACKUP_BUCKET="s4-backups"

# Backup tenant configuration data
aws s3 cp s3://your-s4-bucket/tenants/ s3://$BACKUP_BUCKET/backups/$TIMESTAMP/tenants/ --recursive

# Backup indices
aws s3 cp s3://your-s4-bucket/indices/ s3://$BACKUP_BUCKET/backups/$TIMESTAMP/indices/ --recursive
```

### Disaster Recovery Plan

1. **Recovery Point Objective (RPO)**: Define maximum acceptable data loss
2. **Recovery Time Objective (RTO)**: Define maximum acceptable downtime
3. **Multi-Region Deployment**: Consider deploying to multiple regions for high availability
4. **Regular Restore Testing**: Test your restore procedures regularly

## Security Monitoring

1. **API Authentication Logs**: Monitor failed authentication attempts
2. **Admin API Logs**: Closely monitor all admin API calls
3. **AWS CloudTrail** or **GCP Cloud Audit Logs**: Monitor infrastructure changes
4. **Regular Security Scanning**: Implement automated vulnerability scanning

## Performance Optimization

1. **API Rate Limiting**: Implement tenant-specific rate limits
2. **Caching**: Add caching for frequently accessed data
3. **Query Optimization**: Optimize S3 queries by implementing efficient prefixes
4. **Embedding Optimization**: Cache embeddings to reduce OpenAI API costs

## Maintenance Procedures

### Deployment with Zero Downtime

Implement blue-green deployment or rolling updates:

- For Elastic Beanstalk:
  ```
  eb deploy --staged
  ```

- For Google Cloud Run:
  ```
  # Google Cloud Run handles this automatically with new revisions
  ```

### Regular Maintenance Checklist

1. **Dependency Updates**: Regularly update S4 dependencies
2. **Security Patches**: Apply security patches promptly
3. **Performance Review**: Review performance metrics monthly
4. **Cost Review**: Monitor and optimize AWS/GCP costs
5. **Backup Verification**: Verify backup integrity regularly

## Tenant Management Best Practices

1. **Tenant Onboarding Automation**: Automate tenant provisioning
2. **Tenant Monitoring**: Create dashboards per tenant
3. **Communication Plan**: Establish communication channels for maintenance windows
4. **SLA Monitoring**: Track performance against defined SLAs

## Troubleshooting Common Issues

### API Performance Degradation

1. Check CPU and memory usage
2. Review logs for error patterns
3. Check S3 access patterns
4. Review tenant usage patterns

### Storage Issues

1. Check S3 error logs
2. Verify tenant storage quotas
3. Check permissions and IAM roles
4. Verify encryption settings

### Tenant Isolation Problems

1. Review tenant ID handling in code
2. Check authorization middleware
3. Verify S3 key prefixing is working correctly
4. Test tenant isolation with automated tests 
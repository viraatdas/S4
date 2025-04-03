# S4 Troubleshooting Guide

This guide provides solutions for common issues you might encounter when deploying, configuring, or using S4.

## Table of Contents

- [Installation and Deployment Issues](#installation-and-deployment-issues)
- [Authentication Problems](#authentication-problems)
- [API Errors](#api-errors)
- [Document Processing Issues](#document-processing-issues)
- [Search Functionality Issues](#search-functionality-issues)
- [Admin Portal Issues](#admin-portal-issues)
- [Performance Problems](#performance-problems)
- [Tenant Management Issues](#tenant-management-issues)
- [Storage and S3 Integration](#storage-and-s3-integration)
- [Logging and Diagnostics](#logging-and-diagnostics)

## Installation and Deployment Issues

### Docker Deployment Fails

**Symptoms:**
- Docker containers fail to start
- Error messages in Docker logs

**Solutions:**
1. Check Docker version:
   ```bash
   docker --version
   docker-compose --version
   ```
   Ensure you have Docker 20.10+ and Docker Compose 2.0+.

2. Verify port availability:
   ```bash
   sudo lsof -i :8000
   sudo lsof -i :80
   ```
   If these ports are in use, modify the `docker-compose.yml` file or stop the conflicting services.

3. Check disk space:
   ```bash
   df -h
   ```
   Ensure you have at least 2GB of free space.

4. Inspect container logs:
   ```bash
   docker-compose logs s4
   docker-compose logs s4-ui
   ```
   Look for specific error messages to diagnose the issue.

### AWS Deployment Failure

**Symptoms:**
- AWS Elastic Beanstalk deployment fails
- Amplify frontend deployment fails

**Solutions:**
1. Verify AWS CLI configuration:
   ```bash
   aws configure list
   ```
   Ensure you have valid credentials and the correct region is selected.

2. Check IAM permissions:
   ```bash
   aws iam get-user
   ```
   Ensure your user has the necessary permissions for S3, Elastic Beanstalk, and Amplify.

3. Validate the deployment script:
   ```bash
   cat deploy_amplify.sh
   ```
   Ensure there are no syntax errors in the script.

4. Check AWS service status:
   ```bash
   aws health describe-events
   ```
   Verify AWS services are operational.

### Missing Environment Variables

**Symptoms:**
- Application starts but immediately exits
- Error messages about missing configuration

**Solutions:**
1. Verify the `.env` file exists:
   ```bash
   ls -la .env
   ```

2. Check the contents of the `.env` file:
   ```bash
   cat .env | grep -v PASSWORD | grep -v KEY
   ```
   Ensure all required variables are set.

3. For Docker deployment, ensure environment variables are passed to containers:
   ```bash
   docker-compose config
   ```
   Verify that the `environment` section contains the necessary variables.

4. For AWS deployment, check environment variables in the AWS console.

## Authentication Problems

### Admin API Key Not Working

**Symptoms:**
- 401 Unauthorized responses from admin endpoints
- Cannot access Admin Portal

**Solutions:**
1. Verify the admin key format:
   ```bash
   cat .env | grep ADMIN_API_KEY
   ```
   Ensure the key is correctly formed (typically starting with `s4_admin_`).

2. Check for whitespace or special characters:
   ```bash
   echo -n "$S4_ADMIN_API_KEY" | hexdump -C
   ```
   Ensure there are no trailing spaces or invisible characters.

3. Reset the admin API key:
   ```bash
   # Generate a new key
   NEW_KEY=$(openssl rand -hex 16)
   echo "New admin key: $NEW_KEY"
   
   # Update .env file
   sed -i "s/S4_ADMIN_API_KEY=.*/S4_ADMIN_API_KEY=$NEW_KEY/" .env
   
   # Restart the application
   docker-compose restart
   ```

### Tenant API Key Issues

**Symptoms:**
- Tenant cannot authenticate
- 401 responses for tenant endpoints

**Solutions:**
1. Verify the tenant exists:
   ```bash
   curl -X GET http://localhost:8000/api/admin/tenants \
     -H "X-Admin-Key: your_admin_key" | grep tenant_id
   ```

2. Regenerate the tenant API key from the Admin Portal or API:
   ```bash
   curl -X POST http://localhost:8000/api/admin/tenants/tenant_id/regenerate-key \
     -H "X-Admin-Key: your_admin_key"
   ```

3. Check tenant status:
   ```bash
   curl -X GET http://localhost:8000/api/admin/tenants/tenant_id \
     -H "X-Admin-Key: your_admin_key"
   ```
   Ensure the tenant is not suspended.

## API Errors

### Rate Limiting

**Symptoms:**
- 429 Too Many Requests responses
- Tenant operations fail intermittently

**Solutions:**
1. Check tenant's current usage:
   ```bash
   curl -X GET http://localhost:8000/api/admin/tenants/tenant_id \
     -H "X-Admin-Key: your_admin_key"
   ```
   Look for the `api_calls_count` value.

2. Upgrade the tenant to a higher plan:
   ```bash
   curl -X PUT http://localhost:8000/api/admin/tenants/tenant_id/plan \
     -H "X-Admin-Key: your_admin_key" \
     -H "Content-Type: application/json" \
     -d '{"plan_id": "premium"}'
   ```

3. Adjust rate limits in system configuration (if possible).

### Invalid Request Errors (400)

**Symptoms:**
- 400 Bad Request responses
- Client-side validation errors

**Solutions:**
1. Check request payload format:
   ```bash
   curl -v -X POST http://localhost:8000/api/documents \
     -H "X-Tenant-Key: tenant_key" \
     -F "file=@/path/to/document.pdf"
   ```
   Ensure all required fields are included and properly formatted.

2. Verify file types and sizes:
   ```bash
   file /path/to/document.pdf
   du -h /path/to/document.pdf
   ```
   Ensure the file is a valid document and within size limits.

3. Review API documentation for correct endpoint usage:
   ```bash
   curl http://localhost:8000/docs
   ```

### Internal Server Errors (500)

**Symptoms:**
- 500 Internal Server Error responses
- Backend service crashes

**Solutions:**
1. Check application logs:
   ```bash
   docker-compose logs s4 --tail=100
   ```
   Look for error stacktraces or exception messages.

2. Verify the OpenAI API key is valid:
   ```bash
   curl https://api.openai.com/v1/engines \
     -H "Authorization: Bearer $OPENAI_API_KEY"
   ```

3. Check system resources:
   ```bash
   docker stats
   ```
   Ensure the container has sufficient CPU and memory.

## Document Processing Issues

### Document Upload Failures

**Symptoms:**
- Document uploads fail
- Error responses during upload

**Solutions:**
1. Check file size limits:
   ```bash
   du -h /path/to/document.pdf
   ```
   Ensure the file is within the configured size limits.

2. Verify supported file types:
   ```bash
   file /path/to/document.pdf
   ```
   Ensure the file is of a supported type (PDF, DOCX, TXT, etc.).

3. Check S3 bucket permissions:
   ```bash
   aws s3 ls s3://your-s4-bucket
   ```
   Ensure the application has write access to the S3 bucket.

4. Verify environment variables for S3:
   ```bash
   cat .env | grep S3
   ```
   Ensure S3 bucket and region are correctly configured.

### Documents Stuck in Processing

**Symptoms:**
- Documents remain in "processing" status
- Documents never become searchable

**Solutions:**
1. Check processing queue status:
   ```bash
   docker-compose logs s4 | grep "Processing document"
   ```
   Look for processing logs or errors.

2. Verify OpenAI API access:
   ```bash
   curl https://api.openai.com/v1/engines \
     -H "Authorization: Bearer $OPENAI_API_KEY"
   ```
   Ensure the OpenAI API is accessible and the key is valid.

3. For large documents, increase processing timeout:
   ```bash
   # Edit the docker-compose.yml file
   nano docker-compose.yml
   
   # Add or modify the processing timeout
   environment:
     - S4_PROCESSING_TIMEOUT=300
   ```

4. Restart the processing service:
   ```bash
   docker-compose restart s4
   ```

## Search Functionality Issues

### No Search Results

**Symptoms:**
- Searches return empty results
- Documents are uploaded but not searchable

**Solutions:**
1. Verify documents are processed:
   ```bash
   curl -X GET http://localhost:8000/api/documents \
     -H "X-Tenant-Key: tenant_key"
   ```
   Check that document status is "ready".

2. Verify search query format:
   ```bash
   curl -X POST http://localhost:8000/api/search \
     -H "X-Tenant-Key: tenant_key" \
     -H "Content-Type: application/json" \
     -d '{"query": "your search query", "limit": 5}'
   ```
   Ensure the query is properly formatted.

3. Check embedding model configuration:
   ```bash
   cat .env | grep EMBEDDING_MODEL
   ```
   Ensure the embedding model matches the one used during document processing.

### Poor Search Results Quality

**Symptoms:**
- Search results are not relevant
- Expected documents are not returned

**Solutions:**
1. Adjust search parameters:
   ```bash
   curl -X POST http://localhost:8000/api/search \
     -H "X-Tenant-Key: tenant_key" \
     -H "Content-Type: application/json" \
     -d '{"query": "your search query", "limit": 10, "min_score": 0.6}'
   ```
   Try lowering the `min_score` value or increasing the `limit`.

2. Try different query formulations:
   ```bash
   curl -X POST http://localhost:8000/api/search \
     -H "X-Tenant-Key: tenant_key" \
     -H "Content-Type: application/json" \
     -d '{"query": "alternative phrasing", "limit": 5}'
   ```
   Use more specific or different phrasing.

3. Check for document processing issues:
   ```bash
   docker-compose logs s4 | grep "Error processing"
   ```
   Ensure documents were correctly processed.

## Admin Portal Issues

### Cannot Access Admin Portal

**Symptoms:**
- Admin Portal login page doesn't load
- Network error when accessing Admin Portal

**Solutions:**
1. Check if frontend service is running:
   ```bash
   docker ps | grep s4-ui
   ```
   Ensure the UI container is running.

2. Verify network connectivity:
   ```bash
   curl -I http://localhost
   ```
   Check if the frontend is accessible.

3. Clear browser cache and cookies, then try again.

4. Ensure the frontend UI is properly deployed:
   ```bash
   docker-compose logs s4-ui
   ```
   Look for any startup errors.

### Admin Portal Features Not Working

**Symptoms:**
- Some Admin Portal features fail
- API errors in browser console

**Solutions:**
1. Check browser console for errors:
   Press F12 in your browser to open developer tools, then check the console for error messages.

2. Verify API connectivity from the frontend:
   ```bash
   curl -I http://localhost:8000/api/health
   ```
   Ensure the API is accessible from the frontend.

3. Check CORS configuration:
   ```bash
   cat .env | grep CORS
   ```
   Ensure CORS settings allow the frontend to access the API.

4. Update the Admin Portal:
   ```bash
   docker-compose pull s4-ui
   docker-compose up -d s4-ui
   ```
   Ensure you have the latest version.

## Performance Problems

### Slow API Response Times

**Symptoms:**
- API requests take a long time to complete
- Timeouts during API calls

**Solutions:**
1. Check system resources:
   ```bash
   docker stats
   ```
   Monitor CPU, memory, and I/O usage.

2. Optimize search queries:
   ```bash
   curl -X POST http://localhost:8000/api/search \
     -H "X-Tenant-Key: tenant_key" \
     -H "Content-Type: application/json" \
     -d '{"query": "specific query", "limit": 3}'
   ```
   Reduce the `limit` value or use more specific queries.

3. Check for database bottlenecks:
   ```bash
   docker-compose logs s4 | grep "query time"
   ```
   Look for slow database operations.

4. Scale the resources:
   ```bash
   # Edit docker-compose.yml
   nano docker-compose.yml
   
   # Increase memory and CPU limits
   services:
     s4:
       deploy:
         resources:
           limits:
             cpus: '2'
             memory: 2G
   ```

### High Resource Usage

**Symptoms:**
- High CPU/memory consumption
- Container restarts due to OOM errors

**Solutions:**
1. Monitor resource usage:
   ```bash
   docker stats --no-stream
   ```
   Identify which container is using the most resources.

2. Optimize document processing:
   ```bash
   # Edit .env file to adjust chunk size
   S4_CHUNK_SIZE=1000
   S4_CHUNK_OVERLAP=100
   ```
   Adjust chunking parameters for more efficient processing.

3. Implement rate limiting:
   ```bash
   # Edit .env file
   S4_RATE_LIMIT_REQUESTS=10
   S4_RATE_LIMIT_WINDOW=60
   ```
   Limit the number of concurrent operations.

4. Scale horizontally (for production deployments):
   For AWS deployments, increase the number of instances or container count.

## Tenant Management Issues

### Cannot Create New Tenants

**Symptoms:**
- Tenant creation fails
- Error responses when adding tenants

**Solutions:**
1. Verify admin API key permissions:
   ```bash
   curl -X GET http://localhost:8000/api/admin/health \
     -H "X-Admin-Key: your_admin_key"
   ```
   Ensure the admin key has proper permissions.

2. Check tenant creation payload:
   ```bash
   curl -X POST http://localhost:8000/api/admin/tenants \
     -H "X-Admin-Key: your_admin_key" \
     -H "Content-Type: application/json" \
     -d '{"name": "Test Tenant", "email": "test@example.com", "company": "Test Inc", "plan_id": "basic"}'
   ```
   Ensure all required fields are provided.

3. Verify the plan ID exists:
   ```bash
   curl -X GET http://localhost:8000/api/admin/plans \
     -H "X-Admin-Key: your_admin_key"
   ```
   Ensure the specified plan ID is valid.

### Tenant Usage Tracking Issues

**Symptoms:**
- Incorrect usage reporting
- Discrepancies between actual and reported usage

**Solutions:**
1. Verify current tenant usage:
   ```bash
   curl -X GET http://localhost:8000/api/admin/tenants/tenant_id \
     -H "X-Admin-Key: your_admin_key"
   ```
   Check the reported `storage_used` and `api_calls_count`.

2. Verify actual storage usage:
   ```bash
   aws s3 ls s3://your-s4-bucket/tenants/tenant_id --recursive | wc -l
   aws s3 ls s3://your-s4-bucket/tenants/tenant_id --recursive --summarize
   ```
   Compare actual storage usage with reported usage.

3. Reset usage counters (if necessary):
   ```bash
   curl -X POST http://localhost:8000/api/admin/tenants/tenant_id/reset-usage \
     -H "X-Admin-Key: your_admin_key"
   ```
   This is a drastic measure and should be used with caution.

## Storage and S3 Integration

### S3 Connectivity Issues

**Symptoms:**
- Error messages about S3 access
- Document uploads fail with storage errors

**Solutions:**
1. Verify AWS credentials:
   ```bash
   aws s3 ls
   ```
   Ensure the AWS CLI can access S3.

2. Check S3 bucket existence and permissions:
   ```bash
   aws s3 ls s3://your-s4-bucket
   ```
   Ensure the bucket exists and is accessible.

3. Verify bucket policy:
   ```bash
   aws s3api get-bucket-policy --bucket your-s4-bucket
   ```
   Ensure the policy allows necessary operations.

4. Check environment variables:
   ```bash
   cat .env | grep AWS
   cat .env | grep S3
   ```
   Ensure all S3-related variables are correctly set.

### Storage Limit Exceeded

**Symptoms:**
- Document uploads fail with quota errors
- Error messages about storage limits

**Solutions:**
1. Check tenant's storage usage:
   ```bash
   curl -X GET http://localhost:8000/api/admin/tenants/tenant_id \
     -H "X-Admin-Key: your_admin_key"
   ```
   Look for the `storage_used` value.

2. Upgrade the tenant's plan:
   ```bash
   curl -X PUT http://localhost:8000/api/admin/tenants/tenant_id/plan \
     -H "X-Admin-Key: your_admin_key" \
     -H "Content-Type: application/json" \
     -d '{"plan_id": "premium"}'
   ```
   Move the tenant to a plan with higher storage limits.

3. Clean up old or unused documents:
   ```bash
   curl -X GET http://localhost:8000/api/documents \
     -H "X-Tenant-Key: tenant_key"
   ```
   Identify old documents that can be deleted to free up space.

## Logging and Diagnostics

### Insufficient Logging

**Symptoms:**
- Cannot diagnose issues
- Missing important information in logs

**Solutions:**
1. Enable debug logging:
   ```bash
   # Edit .env file
   S4_DEBUG=true
   
   # Restart the service
   docker-compose restart s4
   ```

2. View detailed logs:
   ```bash
   docker-compose logs s4 --tail=100
   ```

3. Enable API request logging:
   ```bash
   # Edit .env file
   S4_LOG_API_REQUESTS=true
   
   # Restart the service
   docker-compose restart s4
   ```

4. Check log formatting:
   ```bash
   # Edit .env file
   S4_LOG_FORMAT=json
   
   # Restart the service
   docker-compose restart s4
   ```
   JSON format can be easier to parse for automated analysis.

### Log Analysis

**Symptoms:**
- Need to analyze logs for troubleshooting
- Looking for patterns in errors

**Solutions:**
1. Extract error messages:
   ```bash
   docker-compose logs s4 | grep "ERROR" > errors.log
   ```
   Collect all error messages for analysis.

2. Find specific errors:
   ```bash
   docker-compose logs s4 | grep "ConnectionError"
   ```
   Look for specific error types.

3. Analyze API usage patterns:
   ```bash
   docker-compose logs s4 | grep "API call" | cut -d ' ' -f 5- | sort | uniq -c | sort -nr
   ```
   Identify the most common API calls.

4. Track document processing times:
   ```bash
   docker-compose logs s4 | grep "Processing time" | awk '{print $NF}' | sort -n
   ```
   Analyze document processing performance.

## Additional Resources

- [API Documentation](./API_USAGE.md)
- [Deployment Guide](./DEPLOYMENT.md)
- [Admin Portal Guide](./ADMIN_PORTAL.md)
- [GitHub Issues](https://github.com/your-org/s4/issues)

If you encounter an issue not covered in this guide, please:

1. Check the application logs:
   ```bash
   docker-compose logs s4 > s4_logs.txt
   docker-compose logs s4-ui > s4_ui_logs.txt
   ```

2. Collect system information:
   ```bash
   docker version
   docker-compose version
   aws --version
   cat .env | grep -v PASSWORD | grep -v KEY > env_redacted.txt
   ```

3. Submit an issue on GitHub with:
   - Detailed description of the problem
   - Steps to reproduce
   - Logs and system information
   - Expected vs. actual behavior 
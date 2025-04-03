#!/bin/bash

ADMIN_API_KEY="21c806de42ea8c37087d23487f86cd3c"
BACKEND_URL="http://production.eba-ermuim2e.us-east-1.elasticbeanstalk.com"
MAX_RETRIES=20
RETRY_INTERVAL=30

echo "Waiting for S4 backend to become available..."
for i in $(seq 1 $MAX_RETRIES); do
  echo "Attempt $i of $MAX_RETRIES..."
  HEALTH_STATUS=$(curl -s "$BACKEND_URL/health" || echo "failed")
  
  if [[ "$HEALTH_STATUS" == *"ok"* ]]; then
    echo "Backend is ready!"
    echo "Creating a tenant..."
    
    RESPONSE=$(curl -s -X POST "$BACKEND_URL/api/admin/tenants" \
      -H "X-Admin-Key: $ADMIN_API_KEY" \
      -H "Content-Type: application/json" \
      -d '{"name": "Example Company", "email": "admin@example.com", "company": "Example Inc", "plan_id": "basic"}')
    
    echo "Tenant creation response:"
    echo "$RESPONSE"
    
    # Extract the tenant key
    TENANT_KEY=$(echo "$RESPONSE" | grep -o '"key":"[^"]*' | cut -d'"' -f4)
    
    if [ ! -z "$TENANT_KEY" ]; then
      echo ""
      echo "===================================================="
      echo "Deployment successful!"
      echo "===================================================="
      echo "S4 Backend URL: $BACKEND_URL"
      echo "S4 UI URL: http://s4-ui-bucket.s3-website-us-east-1.amazonaws.com"
      echo "Admin API Key: $ADMIN_API_KEY"
      echo "Tenant Key: $TENANT_KEY"
      echo ""
      echo "To use the UI, go to: http://s4-ui-bucket.s3-website-us-east-1.amazonaws.com"
      echo "Login with the tenant key: $TENANT_KEY"
      echo "===================================================="
      
      exit 0
    else
      echo "Failed to extract tenant key from the response. Please check manually."
      exit 1
    fi
  else
    echo "Backend is not ready yet, waiting $RETRY_INTERVAL seconds before retry..."
    sleep $RETRY_INTERVAL
  fi
done

echo "Backend did not become available after $MAX_RETRIES attempts."
echo "Please check the Elastic Beanstalk environment status and logs."
echo "S4 Backend URL: $BACKEND_URL"
echo "S4 UI URL: http://s4-ui-bucket.s3-website-us-east-1.amazonaws.com"
echo "Admin API Key: $ADMIN_API_KEY"
exit 1

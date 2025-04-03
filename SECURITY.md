# S4 Security Guide

This document outlines security best practices for the S4 application, focusing on credential management, authentication, and secure deployment.

## Credential Management

### Environment Variables

All sensitive credentials must be stored as environment variables and never committed to the repository:

- **Authentication Credentials**:
  - `SUPERTOKENS_CONNECTION_URI`
  - `SUPERTOKENS_API_KEY`
  - `GOOGLE_CLIENT_ID`
  - `GOOGLE_CLIENT_SECRET`

- **API Keys**:
  - `OPENAI_API_KEY`
  - `AWS_ACCESS_KEY_ID`
  - `AWS_SECRET_ACCESS_KEY`

- **Database Credentials**:
  - `DB_CONNECTION_STRING`
  - `DB_USERNAME`
  - `DB_PASSWORD`

Use the provided `env-unified-template.txt` as a reference for required variables.

### Local Development

For local development:

1. Create a `.env` file based on the template
2. Add `.env` to `.gitignore`
3. Use a secure method to share credentials among team members (e.g., password manager)

### Production Deployment

For production environments:

1. Use environment variable management in your deployment platform:
   - AWS Parameter Store or Secrets Manager for AWS deployments
   - Docker secrets for container deployments
   - Environment configuration in CI/CD pipelines

2. Rotate credentials regularly
3. Use the principle of least privilege for all service accounts

## Cleaning Repository History

If sensitive credentials were previously committed to the repository:

1. Use the provided `git_clean_credentials.sh` script to clean the Git history
2. Force push the cleaned history to the repository
3. Revoke and rotate all exposed credentials immediately

**Important**: After cleaning the repository history, all team members must clone a fresh copy of the repository.

## Authentication Security

### SuperTokens Configuration

Ensure the SuperTokens configuration follows these security practices:

1. Use HTTPS for all SuperTokens connections
2. Set appropriate cookie security options:
   - `secure: true` in production
   - `httpOnly: true` for session cookies
   - Proper CORS configuration

3. Configure session timeouts appropriately:
   - `sessionExpiredStatusCode: 401`
   - Reasonable session lifetime

### API Authentication

For API authentication:

1. Validate all tokens on the server side
2. Use short-lived access tokens
3. Implement proper refresh token rotation
4. Add rate limiting for authentication endpoints

## API Security

1. Implement rate limiting for all API endpoints
2. Validate all input data
3. Use HTTPS for all API communications
4. Implement proper CORS configuration
5. Add security headers to API responses

## Frontend Security

1. Sanitize all user inputs
2. Implement Content Security Policy (CSP)
3. Use HTTPS for all communications
4. Store tokens securely (preferably in HttpOnly cookies)
5. Implement proper CSRF protection

## S3 Security

1. Configure S3 buckets with proper access controls:
   - Block public access
   - Use bucket policies to restrict access
   - Enable encryption at rest

2. Use pre-signed URLs for temporary access
3. Implement proper IAM roles with least privilege
4. Enable S3 access logging

## Monitoring and Incident Response

1. Enable CloudTrail logging for AWS services
2. Set up alerts for suspicious activities
3. Create an incident response plan
4. Regularly review access logs

## Security Checklist

Before deployment, verify:

- [ ] All credentials are stored as environment variables
- [ ] No sensitive data in repository history
- [ ] HTTPS is enforced for all communications
- [ ] Authentication is properly configured
- [ ] Input validation is implemented
- [ ] Rate limiting is in place
- [ ] S3 buckets are properly secured
- [ ] Logging and monitoring are configured

## Regular Security Tasks

- [ ] Rotate credentials quarterly
- [ ] Review IAM permissions monthly
- [ ] Update dependencies weekly
- [ ] Run security scans before major releases
- [ ] Conduct security training for new team members

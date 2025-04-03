# S4 Admin Portal Guide

This guide provides detailed information about using the S4 Admin Portal to manage the semantic search service.

## Introduction

The S4 Admin Portal is a web-based interface designed for system administrators to manage tenants, monitor system performance, and configure system-wide settings. It provides a user-friendly alternative to the Admin API for common administrative tasks.

## Accessing the Admin Portal

Access the Admin Portal at:

- **Local Development**: `http://localhost/admin/login`
- **Production**: `https://your-frontend-url/admin/login`

You'll need your Admin API key to log in, which was generated during system deployment.

## Dashboard

The Admin Dashboard provides an overview of your S4 deployment:

### Key Features:

- **System Overview**: Real-time metrics on API calls, storage usage, and active tenants
- **Recent Activity**: Latest tenant registrations and document uploads
- **Tenant Distribution**: Breakdown of tenants by plan and status
- **Usage Trends**: Graphs showing API usage and storage consumption over time

## Tenant Management

The Tenant Management section allows you to create, view, edit, and delete tenants.

### Tenant List

The tenant list displays all tenants with key information:

- **Tenant Name**: The name of the tenant organization
- **Email**: Primary contact email
- **Company**: Company or organization name
- **Plan**: Current subscription plan
- **Status**: Active or suspended
- **Created Date**: When the tenant was created
- **API Key**: Masked API key (can be revealed or regenerated)

### Actions:

1. **Create Tenant**:
   - Click the "Add Tenant" button
   - Fill in the required information:
     - Name
     - Email
     - Company name
     - Subscription plan
   - Click "Create" to generate a new tenant with an API key

2. **Edit Tenant**:
   - Click the edit icon next to a tenant
   - Modify tenant details
   - Click "Save Changes"

3. **Change Tenant Plan**:
   - Click the "Change Plan" button for a tenant
   - Select the new plan from the dropdown
   - Confirm the change

4. **Regenerate API Key**:
   - Click the "Regenerate Key" button
   - Confirm the action
   - Copy the new key to share with the tenant

5. **Suspend/Activate Tenant**:
   - Toggle the status switch
   - Confirm the action

6. **Delete Tenant**:
   - Click the delete icon
   - Confirm the deletion (this will permanently remove all tenant data)

## Analytics

The Analytics section provides detailed insights into system usage and performance.

### System Analytics

View system-wide metrics:

- **API Calls**: Total calls, breakdown by endpoint, and time-based trends
- **Storage Usage**: Total usage, growth over time, and projected needs
- **Tenant Activity**: Active vs. inactive tenants, new registrations
- **Document Processing**: Upload volumes, processing times, and success rates
- **Search Performance**: Query volumes, response times, and most frequent queries

### Tenant Analytics

View tenant-specific metrics:

- **Top Tenants**: Ranked by API usage, storage, or document count
- **Usage Patterns**: Peak usage times and common operations
- **Plan Distribution**: Number of tenants on each subscription plan
- **Tenant Growth**: New tenant registrations over time

### Data Filtering

Filter analytics data by:

- **Time Period**: Last 24 hours, 7 days, 30 days, or custom range
- **Tenant Group**: All tenants, specific plans, or individual tenants
- **Operation Type**: API calls, document uploads, searches

### Export

Export analytics data in various formats:

- **CSV**: For spreadsheet analysis
- **JSON**: For integration with other tools
- **PDF Reports**: For sharing with stakeholders

## System Configuration

The Configuration section allows you to manage system-wide settings.

### Subscription Plans

Manage available subscription plans:

1. **View Plans**: See all available plans with their limits and features
2. **Create Plan**: Define new subscription tiers
3. **Edit Plan**: Modify existing plan details
4. **Delete Plan**: Remove plans (will not affect existing tenants)

### API Settings

Configure API behavior:

- **Rate Limiting**: Set global rate limits
- **CORS Settings**: Configure allowed origins
- **Authentication Settings**: Adjust token expiration times

### Storage Settings

Configure document storage:

- **S3 Settings**: Update bucket configuration
- **File Type Restrictions**: Set allowed file types
- **Size Limits**: Configure maximum file sizes

### Embedding Settings

Configure the semantic search capabilities:

- **Embedding Model**: Select the OpenAI embedding model
- **Chunk Size**: Configure document chunking parameters
- **Vector Dimensions**: View embedding dimensions

## Alerts and Notifications

Configure system alerts:

- **Usage Alerts**: Set thresholds for system resource usage
- **Error Alerts**: Get notified of system errors or failures
- **Tenant Alerts**: Monitor tenant-specific issues
- **Notification Methods**: Configure email, Slack, or webhook notifications

## User Management

Manage admin users (for systems with multiple administrators):

- **Add Admin**: Create additional admin accounts
- **Edit Permissions**: Set access levels for different admins
- **Reset Credentials**: Handle password resets or key regeneration

## Audit Logs

View system audit logs:

- **Admin Actions**: Track all administrative actions
- **System Events**: Monitor automatic system events
- **Authentication Events**: Track login attempts and failures
- **Filter Logs**: Search for specific events or actions

## Best Practices

### Security

- Regularly rotate your Admin API key
- Limit admin portal access to trusted networks
- Monitor audit logs for suspicious activity
- Use strong, unique passwords for admin accounts

### Tenant Management

- Document tenant onboarding processes
- Establish clear criteria for plan upgrades/downgrades
- Create templates for common tenant communications
- Regularly review inactive tenants

### System Monitoring

- Set up alerts for abnormal usage patterns
- Schedule regular reviews of system analytics
- Monitor storage growth and plan accordingly
- Check error logs daily

## Troubleshooting

### Common Issues

1. **Login Problems**:
   - Verify Admin API key is correct
   - Check for network connectivity issues
   - Clear browser cache and cookies

2. **Missing Tenant Data**:
   - Check tenant status (may be suspended)
   - Verify tenant API key is active
   - Check for storage or database issues

3. **Performance Problems**:
   - Review system analytics for usage spikes
   - Check server resources
   - Verify OpenAI API is functioning correctly

4. **API Errors**:
   - Check error logs for specific error codes
   - Verify tenant hasn't exceeded plan limits
   - Test API endpoints directly

## Getting Help

If you encounter issues with the Admin Portal:

- Check the [Troubleshooting Guide](./TROUBLESHOOTING.md)
- Review system logs for error messages
- Contact support at support@your-org.com
- Visit the community forum at https://community.your-org.com/s4

## Keyboard Shortcuts

The Admin Portal supports the following keyboard shortcuts:

| Shortcut | Action |
|----------|--------|
| `Alt+D` | Go to Dashboard |
| `Alt+T` | Go to Tenant Management |
| `Alt+A` | Go to Analytics |
| `Alt+C` | Go to Configuration |
| `Alt+N` | Create New Tenant |
| `Alt+S` | Open Search |
| `Alt+L` | View Logs |
| `Alt+H` | Open Help |
| `Esc` | Close modal or cancel action |

## Customization

The Admin Portal can be customized with your organization's branding:

- **Logo**: Upload your company logo
- **Colors**: Adjust the color scheme
- **Domain**: Use a custom domain
- **Email Templates**: Customize tenant communications

Contact your implementation team for assistance with customization options. 
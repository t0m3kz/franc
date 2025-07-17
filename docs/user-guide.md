# FRANC - Service Portal User Guide

## Overview

FRANC (Streamlit connection and utilities for Infrahub) is a web-based service portal that provides a self-service interface for network operations teams. The portal offers a mobile-friendly interface for requesting common network services including device connections, data center deployments, and point-of-presence (PoP) deployments.


## Getting Started

### Accessing the Portal

The Service Portal is a web application accessible through your browser. Once launched, you'll see:

- **🛠️ Service Portal** header with "Network Operations Self-Service" subtitle
- **Home** and **Service Catalogue** navigation tabs (bottom navigation bar style for mobile)
- Mobile-responsive design that adapts to your device

### Navigation

The portal uses a two-tab navigation:

1. **Home**: Welcome page with service overview cards and quick help
2. **Service Catalogue**: Access all available services via a selectbox

**Mobile Optimization:**
- Navigation tabs are styled for thumb access
- All forms and controls are touch-friendly


## Available Services

### 1. Deploy Data Center

Request deployment of a new data center infrastructure.

**Required Information:**
- **Change Number**: Approved change management number (required)
- **Data Center Name**: Unique identifier for the new data center
- **Location**: Geographic location (select from available metros or enter manually if options are unavailable)
- **Design Pattern**: Infrastructure design template (filtered for DC-specific patterns)

**Process:**
1. Obtain approved change number from your change management team
2. Go to **Service Catalogue**
3. Select **"Deploy Data Center"** from the service dropdown
4. Enter your change number as the first field
5. Fill in all required fields
6. Click **"🚀 Submit Data Center Request"**
7. Confirmation message will display change number and details upon successful submission

### 2. Deploy Point of Presence (PoP)

Request deployment of a new point-of-presence location.

**Required Information:**
- **Change Number**: Approved change management number (required)
- **PoP Name**: Unique identifier for the new PoP
- **Location**: Geographic location (select from available metros or enter manually if options are unavailable)
- **Design Pattern**: Infrastructure design template (filtered for PoP-specific patterns)
- **Provider**: Network service provider for the PoP

**Process:**
1. Obtain approved change number from your change management team
2. Go to **Service Catalogue**
3. Select **"Deploy PoP"** from the service dropdown
4. Enter your change number as the first field
5. Fill in all required fields including provider selection
6. Click **"🚀 Submit PoP Request"**
7. Confirmation message will display change number and details upon successful submission

### 3. Connection Request (Device Connection)

Request network connection for a device with interface configuration.

**Required Information:**
- **Change Number**: Approved change management number (required)
- **Device Name**: Unique identifier for the device
- **Device Type**: Device role/type (select from available options or enter manually if options are unavailable)
- **Location**: Physical location (select from available buildings or enter manually if options are unavailable)
- **Interface Configuration**: One or more network interfaces

**Interface Configuration Details:**
For each interface, specify:
- **Interface Name**: Unique name for the interface
- **Speed**: Connection speed (1 Gbit, 10 Gbit, 40 Gbit, or 100 Gbit)
- **Role**: Interface purpose (data or management)
- **vPC Group**: Virtual port channel grouping (optional)

**Advanced Features:**
- **Dynamic Interface Management**: Add or remove interfaces as needed
- **vPC Group Configuration**: Configure virtual port channels with automatic validation
- **Duplicate Name Detection**: Prevents duplicate interface names
- **Interface Summary**: Real-time preview of configuration

**Process:**
1. Obtain approved change number from your change management team
2. Go to **Service Catalogue**
3. Select **"Connection Request"** from the service dropdown
4. Enter your change number as the first field
5. Fill in device information
6. Configure the number of interfaces needed
7. Set up vPC groups if required
8. Configure each interface (name, speed, role, vPC assignment)
9. Click **"🚀 Submit Connection Request"**
10. Confirmation message will display change number and interface details upon successful submission


## Form Validation & Help

All service forms include comprehensive validation and built-in help:

### Common Validations
- **Change Number**: Required for all service requests, must not be empty
- **Required Fields**: All mandatory fields must be completed
- **Selection Validation**: When options are available, a selection must be made
- **Text Input Fallback**: Manual entry available when external data is unavailable

### Connection Request Specific Validations
- **Minimum Interface Count**: At least one named interface required
- **Unique Interface Names**: No duplicate interface names allowed
- **vPC Group Validation**: Each vPC group must contain at least two interfaces
- **Complete Interface Configuration**: All interface fields must be filled

### Help Integration
- Help icons and expandable sections are available for every service and field
- Quick Help is always available on the Home tab
- Interface configuration help is available in the Connection Request form


## Error Handling

The portal provides clear, actionable error messages and guidance:

- **Field-Level Errors**: Specific guidance for each invalid field
- **Real-Time Validation**: Immediate feedback as you fill forms
- **Success Confirmation**: Clear confirmation when requests are submitted successfully
- **Validation Tips**: Expandable help sections provide tips for fixing errors


## Mobile Optimization

The Service Portal is designed for mobile use:

- **Responsive Layout**: Adapts to different screen sizes
- **Touch-Friendly Controls**: Large buttons and touch targets
- **Optimized Navigation**: Bottom navigation bar style for easy thumb access
- **Readable Typography**: Appropriate font sizes for mobile devices
- **Landscape Mode**: Recommended for complex forms


## Data Integration

The portal integrates with your organization's infrastructure management system:

- **Dynamic Option Loading**: Service options loaded from Infrahub or other infrastructure database
- **Fallback Support**: Manual entry available when external systems are unavailable
- **Real-Time Data**: Information pulled from live infrastructure management systems


## Support and Troubleshooting

### Common Issues

**"No options available" in dropdown menus:**
- This occurs when Infrahub or external infrastructure system is unavailable
- Use the manual text input field that appears automatically
- Contact support if this persists

**Form validation errors:**
- Read error messages carefully - they provide specific guidance
- Ensure all required fields are completed
- Check for duplicate interface names in connection requests
- Verify vPC groups have at least two interfaces

**Interface configuration issues:**
- Use the interface summary to verify your configuration
- Ensure interface names are unique
- Check that vPC group assignments are correct

### Getting Help

For technical support or feature requests:
- Contact your network operations team
- Include specific error messages and screenshots when reporting issues
- Mention which service you were trying to use


## Tips for Efficient Use

1. **Bookmark the Portal**: Save the portal URL for quick access
2. **Use Descriptive Names**: Choose clear, descriptive names for devices and interfaces
3. **Plan Interface Configuration**: Know your interface requirements before starting
4. **Review Before Submitting**: Use the interface summary to verify complex configurations
5. **Mobile Access**: The portal works well on phones and tablets for quick requests
6. **Expand Help Sections**: Use help icons and expandable sections for guidance


## Security and Data Privacy

- All form data is validated before submission
- Integration with existing infrastructure management systems maintains data consistency
- Form submissions are logged for audit purposes
- No sensitive data is stored in browser sessions
- Validation and error handling prevent common security issues


## Change Management Requirements

**All network service requests require a valid change management number.**

### Before You Begin

1. **Obtain Change Approval**: Contact your change management team to get an approved change number
2. **Change Number Format**: Typically follows CHG-YYYY-XXXXXX format (e.g., CHG-2024-001234)
3. **Have Information Ready**: Ensure your change has been approved before submitting service requests

### Why Change Numbers Are Required

- **Compliance**: Ensures all network changes follow proper approval processes
- **Tracking**: Links service requests to approved changes for audit purposes
- **Coordination**: Helps coordinate changes across teams and systems
- **Documentation**: Maintains proper record-keeping for network modifications

**Important**: Service requests cannot be processed without a valid change number.

---

*For technical questions or feature requests, contact your network operations team.*

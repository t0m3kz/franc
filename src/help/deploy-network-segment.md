# Deploy Network Segment

This service allows you to provision a new network segment at a selected site. You can specify the segment name, VLAN or VNI number, and choose whether the segment is Layer 2 (L2) or Layer 3 (L3).

## Form Fields

- **Site**: Select the site where the network segment will be deployed.
- **Network Segment Name**: Enter a descriptive name for the segment.
- **VLAN or VNI Number**: Enter the VLAN (for L2) or VNI (for L3) number.
- **Segment Type**: Choose between L2 (Layer 2) or L3 (Layer 3).
- **Assigned Ports**: Specify the number of ports to assign to this segment. This will dynamically show fields for each port.
- **Switch & Port Assignment**: For each assigned port, select the switch and port to be used.

## Tips
- Ensure the VLAN/VNI number is unique and not already in use at the selected site.
- For L3 segments, additional routing configuration may be required.
- Use the dynamic port assignment to map each port to a specific switch and port.

## Troubleshooting
- If you do not see available sites or switches, check your Infrahub connection and schema configuration.
- Validation errors will be shown if required fields are missing or invalid.

For more details, see the [Developer Guide](../developer-guide.md) or contact your network administrator.

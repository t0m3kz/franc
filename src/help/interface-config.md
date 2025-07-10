**Interface Configuration Guide:**
- **Name**: Use descriptive names like 'Gi0/1', 'eth0', 'mgmt0'
- **Speed**: Select the appropriate port speed for your needs
- **Role**:
  - `data` - Production traffic interfaces
  - `management` - Out-of-band management interfaces
- **vPC Group**: Assign interfaces to virtual port channels for redundancy
  - Each vPC group needs at least 2 interfaces
  - Use 'none' for standalone interfaces

**Tips:**
- Start with management interfaces, then add data interfaces
- Group related interfaces using consistent naming
- Consider redundancy requirements when planning vPC groups

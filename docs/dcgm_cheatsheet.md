DCGMI CLI COMMAND REFERENCE
Service Management
Copy# Start DCGM host engine (standalone mode)
sudo systemctl start nvidia-dcgm
sudo systemctl enable nvidia-dcgm

# Or start manually
sudo nv-hostengine

# Check status
systemctl status nvidia-dcgm

# Stop service
sudo systemctl stop nvidia-dcgm
Discovery Commands
Copy# List all GPUs
dcgmi discovery -l

# List all GPUs with detailed info
dcgmi discovery -i

# List supported GPUs only
dcgmi discovery -c
Group Management
Copy# Create a GPU group
dcgmi group -c "MyGPUs" -a 0,1,2,3

# List all groups
dcgmi group -l

# Show group info
dcgmi group -g 1 -i

# Delete a group
dcgmi group -d 1

# Add GPU to group
dcgmi group -g 1 --add 4

# Remove GPU from group
dcgmi group -g 1 --remove 4
Health Monitoring
Copy# Quick health check (all GPUs)
dcgmi health -c

# Set health watches
dcgmi health -s a    # All watches
dcgmi health -s p    # PCIe health
dcgmi health -s m    # Memory health
dcgmi health -s i    # Inforom health
dcgmi health -s t    # Thermal health
dcgmi health -s P    # Power health
dcgmi health -s n    # NVLink health

# Check health for specific group
dcgmi health -g 1 -c

# Fetch health results
dcgmi health -f
Real-Time Monitoring (dmon)
Copy# Monitor default metrics (1 second interval)
dcgmi dmon

# Monitor specific GPUs
dcgmi dmon -i 0,1

# Monitor specific fields
dcgmi dmon -e 155,150,203,204
# 155 = Power usage
# 150 = GPU temp
# 203 = GPU utilization
# 204 = Memory utilization

# List available field IDs
dcgmi dmon -l

# Custom interval (milliseconds)
dcgmi dmon -d 500

# Monitor for specific duration (seconds)
dcgmi dmon -c 60

# Output to file
dcgmi dmon -e 155,150 > gpu_metrics.csv
Field Value Queries
Copy# Get latest field values
dcgmi fieldgroup -l

# Create custom field group
dcgmi fieldgroup -c "PowerTemp" -f 155,150,203

# Watch fields for a group
dcgmi fieldgroup -g 1 -w "PowerTemp"

# Get field values
dcgmi introspect -F 155    # Power usage
dcgmi introspect -F 150    # Temperature
Configuration
Copy# Get current configuration
dcgmi config -g 1 --get

# Set power limit (Watts)
dcgmi config -g 1 --set -P 300

# Set compute mode
dcgmi config -g 1 --set -c 0   # 0=Default, 1=Exclusive Thread

# Enforce configuration
dcgmi config -g 1 --enforce
Topology
Copy# Show GPU topology
dcgmi topo --gpus

# Show NVLink topology
dcgmi nvlink -s
Diagnostics
Copy# Run Level 1 diagnostics (quick, ~1 min)
dcgmi diag -r 1

# Run Level 2 diagnostics (medium, ~2 min)
dcgmi diag -r 2

# Run Level 3 diagnostics (long, ~12 min)
dcgmi diag -r 3

# Run Level 4 diagnostics (extended, ~60 min)
dcgmi diag -r 4

# Run specific tests
dcgmi diag -r "pcie,diagnostic"
dcgmi diag -r "memory"
dcgmi diag -r "stress"

# Run on specific GPUs
dcgmi diag -r 2 -i 0,1

# Run on group
dcgmi diag -r 2 -g 1

# JSON output
dcgmi diag -r 2 -j

# Verbose output
dcgmi diag -r 2 -v
Stats & Profiling
Copy# Enable job stats
dcgmi stats -e

# Start watching a job
dcgmi stats -s "job123"

# Stop watching and get stats
dcgmi stats -x "job123"

# View job stats
dcgmi stats -j "job123"

# Disable stats
dcgmi stats -d
Policy Management
Copy# Set policy for thermal violations
dcgmi policy -g 1 --set 0,0 -T 85

# Set policy for power violations
dcgmi policy -g 1 --set 0,0 -P 300

# Set policy for ECC errors
dcgmi policy -g 1 --set 0,0 -e 1

# Get current policies
dcgmi policy -g 1 --get
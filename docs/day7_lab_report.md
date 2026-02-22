# Day 7 Lab Report - Hands-On GPU Practice

**Date:** [TODAY'S DATE]
**Platform:** [RunPod / Colab / Lambda]
**GPU:** [GPU Model]
**Duration:** [X hours]
**Cost:** $[X.XX]

## Environment Details

- **GPU:** [nvidia-smi output - GPU name]
- **Driver Version:** [X.X.X]
- **CUDA Version:** [X.X]
- **Memory:** [XX GB]

## Exercises Completed

### 1. nvidia-smi Exploration
- [x] Basic output interpretation
- [x] Continuous monitoring
- [x] Query specific metrics
- [x] Process monitoring
- [x] Topology check

### 2. Python Script Testing
- [x] gpu_monitor.py on real hardware
- [x] Stress test execution
- [x] Memory allocation test

### 3. Advanced Monitoring
- [x] nvtop installation and usage
- [ ] DCGM testing (if available)

## Key Observations

### Idle State Metrics
- Temperature: [X]°C
- Power Draw: [X]W
- Utilization: [X]%
- Memory Used: [X] MB

### Under Load Metrics (stress test)
- Temperature: [X]°C (peak)
- Power Draw: [X]W (peak)
- Utilization: [X]%
- Memory Used: [X] GB

### Temperature Behavior
- Idle → Load time: ~[X] seconds
- Peak temperature: [X]°C
- Cooling after load: ~[X] seconds to idle

## Screenshots / Evidence

[Paste nvidia-smi output here]

## Lessons Learned

1. [Key learning #1]
2. [Key learning #2]
3. [Key learning #3]

## Commands Reference (Personal Cheat Sheet)

```bash
# My most useful commands:
nvidia-smi -l 1                    # Continuous monitoring
nvidia-smi --query-gpu=... --format=csv  # Custom queries
nvtop                              # Interactive monitoring

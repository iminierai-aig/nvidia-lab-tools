#!/usr/bin/env python3
"""
Mock GPU Monitor - For testing without actual GPU
"""

import csv
import datetime
import time
import random
import argparse


def get_mock_gpu_metrics(num_gpus=8):
    """Generate mock GPU data for testing."""
    gpus = []
    for i in range(num_gpus):
        gpu = {
            'index': i,
            'name': f'NVIDIA B200',
            'temperature': random.uniform(35, 85),
            'gpu_util': random.uniform(0, 100),
            'mem_util': random.uniform(0, 100),
            'mem_used': random.uniform(0, 192000),
            'mem_total': 192000,
            'power_draw': random.uniform(100, 1000),
            'power_limit': 1000,
        }
        gpus.append(gpu)
    return gpus


# ... rest of the code same as above, but use get_mock_gpu_metrics()


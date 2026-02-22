#!/usr/bin/env python3
"""
T4 Stress Test
Optimized stress testing for NVIDIA T4 GPU.

The T4 is optimized for inference (INT8/FP16), so we test:
1. FP32 compute (standard)
2. FP16 compute (tensor cores)
3. Memory bandwidth
4. Memory capacity
"""

import torch
import time
import argparse
from typing import Optional

def check_cuda():
    """Verify CUDA is available."""
    if not torch.cuda.is_available():
        print("ERROR: CUDA not available!")
        print("Check: nvidia-smi")
        print("Check: python3 -c 'import torch; print(torch.cuda.is_available())'")
        exit(1)
    
    print(f"GPU: {torch.cuda.get_device_name(0)}")
    print(f"CUDA Version: {torch.version.cuda}")
    print(f"PyTorch Version: {torch.__version__}")
    print("-" * 50)


def fp32_stress(duration: int = 60, size: int = 4096):
    """
    FP32 matrix multiplication stress test.
    Tests standard GPU compute performance.
    """
    check_cuda()
    device = torch.device('cuda')
    
    print(f"FP32 Stress Test")
    print(f"Matrix size: {size}x{size}")
    print(f"Duration: {duration}s")
    print("-" * 50)
    
    # Create matrices
    a = torch.randn(size, size, device=device, dtype=torch.float32)
    b = torch.randn(size, size, device=device, dtype=torch.float32)
    
    # Warmup
    for _ in range(5):
        c = torch.matmul(a, b)
    torch.cuda.synchronize()
    
    # Stress test
    start_time = time.time()
    iterations = 0
    
    print("Running... (monitor with nvidia-smi -l 1)")
    
    try:
        while (time.time() - start_time) < duration:
            c = torch.matmul(a, b)
            torch.cuda.synchronize()
            iterations += 1
            
            if iterations % 50 == 0:
                elapsed = time.time() - start_time
                print(f"  Progress: {elapsed:.1f}s / {duration}s ({iterations} iterations)")
    
    except KeyboardInterrupt:
        print("\nInterrupted")
    
    elapsed = time.time() - start_time
    tflops = (2 * size**3 * iterations) / (elapsed * 1e12)
    
    print("-" * 50)
    print(f"Results:")
    print(f"  Iterations: {iterations}")
    print(f"  Time: {elapsed:.2f}s")
    print(f"  Rate: {iterations/elapsed:.2f} iter/s")
    print(f"  Performance: {tflops:.2f} TFLOPS (FP32)")
    print(f"  T4 Spec: 8.1 TFLOPS (FP32)")
    
    # Cleanup
    del a, b, c
    torch.cuda.empty_cache()


def fp16_stress(duration: int = 60, size: int = 8192):
    """
    FP16 matrix multiplication stress test.
    Tests Tensor Core performance (T4's strength).
    """
    check_cuda()
    device = torch.device('cuda')
    
    print(f"FP16 Stress Test (Tensor Cores)")
    print(f"Matrix size: {size}x{size}")
    print(f"Duration: {duration}s")
    print("-" * 50)
    
    # Create FP16 matrices
    a = torch.randn(size, size, device=device, dtype=torch.float16)
    b = torch.randn(size, size, device=device, dtype=torch.float16)
    
    # Warmup
    for _ in range(5):
        c = torch.matmul(a, b)
    torch.cuda.synchronize()
    
    # Stress test
    start_time = time.time()
    iterations = 0
    
    print("Running... (monitor with nvidia-smi -l 1)")
    
    try:
        while (time.time() - start_time) < duration:
            c = torch.matmul(a, b)
            torch.cuda.synchronize()
            iterations += 1
            
            if iterations % 100 == 0:
                elapsed = time.time() - start_time
                print(f"  Progress: {elapsed:.1f}s / {duration}s ({iterations} iterations)")
    
    except KeyboardInterrupt:
        print("\nInterrupted")
    
    elapsed = time.time() - start_time
    tflops = (2 * size**3 * iterations) / (elapsed * 1e12)
    
    print("-" * 50)
    print(f"Results:")
    print(f"  Iterations: {iterations}")
    print(f"  Time: {elapsed:.2f}s")
    print(f"  Rate: {iterations/elapsed:.2f} iter/s")
    print(f"  Performance: {tflops:.2f} TFLOPS (FP16)")
    print(f"  T4 Spec: 65 TFLOPS (FP16 Tensor)")
    
    # Cleanup
    del a, b, c
    torch.cuda.empty_cache()


def memory_bandwidth(duration: int = 30):
    """
    Memory bandwidth stress test.
    T4 has 320 GB/s memory bandwidth.
    """
    check_cuda()
    device = torch.device('cuda')
    
    print(f"Memory Bandwidth Test")
    print(f"Duration: {duration}s")
    print("-" * 50)
    
    # Create large tensors (1GB each)
    size = 256 * 1024 * 1024  # 256M floats = 1GB
    
    a = torch.randn(size, device=device, dtype=torch.float32)
    b = torch.zeros(size, device=device, dtype=torch.float32)
    
    # Warmup
    for _ in range(3):
        b.copy_(a)
    torch.cuda.synchronize()
    
    # Test
    start_time = time.time()
    iterations = 0
    total_bytes = 0
    
    print("Running... (monitor with nvidia-smi -l 1)")
    
    try:
        while (time.time() - start_time) < duration:
            b.copy_(a)
            torch.cuda.synchronize()
            iterations += 1
            total_bytes += size * 4 * 2  # Read + Write
            
            if iterations % 20 == 0:
                elapsed = time.time() - start_time
                bandwidth = total_bytes / (elapsed * 1e9)
                print(f"  Progress: {elapsed:.1f}s, Bandwidth: {bandwidth:.1f} GB/s")
    
    except KeyboardInterrupt:
        print("\nInterrupted")
    
    elapsed = time.time() - start_time
    bandwidth = total_bytes / (elapsed * 1e9)
    
    print("-" * 50)
    print(f"Results:")
    print(f"  Data Transferred: {total_bytes / 1e9:.2f} GB")
    print(f"  Time: {elapsed:.2f}s")
    print(f"  Bandwidth: {bandwidth:.2f} GB/s")
    print(f"  T4 Spec: 320 GB/s")
    print(f"  Efficiency: {(bandwidth/320)*100:.1f}%")
    
    # Cleanup
    del a, b
    torch.cuda.empty_cache()


def memory_fill(target_gb: Optional[float] = None):
    """
    Memory capacity test.
    Allocate GPU memory to test monitoring.
    """
    check_cuda()
    device = torch.device('cuda')
    
    total_memory = torch.cuda.get_device_properties(0).total_memory / (1024**3)
    
    if target_gb is None:
        target_gb = total_memory * 0.8  # 80% = ~12.8GB for T4
    
    print(f"Memory Fill Test")
    print(f"Total Memory: {total_memory:.2f} GB")
    print(f"Target: {target_gb:.2f} GB")
    print("-" * 50)
    
    # Calculate elements needed
    elements = int((target_gb * 1024**3) / 4)  # float32 = 4 bytes
    
    print(f"Allocating {target_gb:.2f} GB...")
    
    try:
        tensor = torch.zeros(elements, device=device, dtype=torch.float32)
        
        allocated = torch.cuda.memory_allocated(0) / (1024**3)
        print(f"Allocated: {allocated:.2f} GB")
        print("\nMemory held. Check with: nvidia-smi")
        print("Press Enter to release...")
        input()
        
    except RuntimeError as e:
        print(f"Allocation failed: {e}")
    
    finally:
        torch.cuda.empty_cache()
        print("Memory released")


def full_stress(duration: int = 120):
    """
    Combined stress test.
    Cycles through different stress patterns.
    """
    check_cuda()
    
    print("=" * 50)
    print("FULL T4 STRESS TEST")
    print(f"Total Duration: {duration}s")
    print("=" * 50)
    
    segment = duration // 4
    
    print(f"\n[1/4] FP32 Compute ({segment}s)")
    fp32_stress(duration=segment, size=3072)
    
    print(f"\n[2/4] FP16 Tensor Core ({segment}s)")
    fp16_stress(duration=segment, size=6144)
    
    print(f"\n[3/4] Memory Bandwidth ({segment}s)")
    memory_bandwidth(duration=segment)
    
    print(f"\n[4/4] Memory Capacity ({segment}s)")
    print("Allocating 12GB for {segment}s...")
    device = torch.device('cuda')
    elements = int((12 * 1024**3) / 4)
    tensor = torch.zeros(elements, device=device, dtype=torch.float32)
    time.sleep(segment)
    del tensor
    torch.cuda.empty_cache()
    print("Released")
    
    print("\n" + "=" * 50)
    print("FULL STRESS TEST COMPLETE")
    print("=" * 50)


def main():
    parser = argparse.ArgumentParser(description='T4 GPU Stress Test')
    subparsers = parser.add_subparsers(dest='command', help='Test type')
    
    # FP32 test
    fp32_parser = subparsers.add_parser('fp32', help='FP32 compute stress')
    fp32_parser.add_argument('-d', '--duration', type=int, default=60)
    fp32_parser.add_argument('-s', '--size', type=int, default=4096)
    
    # FP16 test
    fp16_parser = subparsers.add_parser('fp16', help='FP16 tensor core stress')
    fp16_parser.add_argument('-d', '--duration', type=int, default=60)
    fp16_parser.add_argument('-s', '--size', type=int, default=8192)
    
    # Memory bandwidth
    bw_parser = subparsers.add_parser('bandwidth', help='Memory bandwidth test')
    bw_parser.add_argument('-d', '--duration', type=int, default=30)
    
    # Memory fill
    mem_parser = subparsers.add_parser('memory', help='Memory fill test')
    mem_parser.add_argument('-g', '--gb', type=float, help='Target GB')
    
    # Full test
    full_parser = subparsers.add_parser('full', help='Full stress test')
    full_parser.add_argument('-d', '--duration', type=int, default=120)
    
    args = parser.parse_args()
    
    if not args.command:
        # Default: quick FP32 test
        fp32_stress(duration=30, size=3072)
    elif args.command == 'fp32':
        fp32_stress(duration=args.duration, size=args.size)
    elif args.command == 'fp16':
        fp16_stress(duration=args.duration, size=args.size)
    elif args.command == 'bandwidth':
        memory_bandwidth(duration=args.duration)
    elif args.command == 'memory':
        memory_fill(target_gb=args.gb)
    elif args.command == 'full':
        full_stress(duration=args.duration)


if __name__ == '__main__':
    main()

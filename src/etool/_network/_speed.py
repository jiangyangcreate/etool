"""
系统性能测试工具 (System Performance Test Tool)

该模块提供了一个全面的系统性能测试工具，用于测试和监控计算机系统的各项性能指标。
包括网络速度、硬盘读写速度、内存性能以及GPU状态的测试。

功能特性:
- 网络测试：测量下载速度、上传速度和网络延迟
- 硬盘测试：评估磁盘读写性能
- 内存测试：测量内存读写速度
- GPU测试：监控GPU使用状态、内存占用等指标

依赖项:
- speedtest-cli: 网络速度测试
- pynvml: NVIDIA GPU监控
- python 3.6+

作者: Allen
版本: 1.0.1
创建日期: 2024-12-07
最后更新: 2024-12-14
"""

import speedtest
import time
import os
import tempfile
import random
import pynvml
import numpy as np
from numba import cuda

class ManagerSpeed:
    results = {}

    @classmethod
    def network(cls):
        """测试网络速度"""
        try:
            st = speedtest.Speedtest()
            st.get_best_server()
            
            download_speed = st.download() / 1_000_000
            upload_speed = st.upload() / 1_000_000
            ping = st.results.ping
            
            cls.results['network'] = {
                'download_speed': f"{download_speed:.2f} Mbps",
                'upload_speed': f"{upload_speed:.2f} Mbps",
                'ping': f"{ping:.2f} ms"
            }
            info = f'''\n网络测试结果:
下载速度: {cls.results['network']['download_speed']}
上传速度: {cls.results['network']['upload_speed']}
延迟: {cls.results['network']['ping']}
'''
            print(info)
            return info

        except Exception as e:
            print(f"网络测试失败: {str(e)}")
            cls.results['network'] = None
            return f"网络测试失败: {str(e)}"


    @classmethod
    def disk(cls, file_size_mb=100):
        """测试硬盘读写速度"""
        try:
            # 创建临时测试文件
            temp_file = tempfile.NamedTemporaryFile(delete=False)
            file_path = temp_file.name
            
            # 写入测试
            data = os.urandom(1024 * 1024)  # 1MB 随机数据
            start_time = time.time()
            
            for _ in range(file_size_mb):
                temp_file.write(data)
            temp_file.close()
            
            write_time = time.time() - start_time
            write_speed = file_size_mb / write_time  # MB/s
            
            # 读取测试
            start_time = time.time()
            with open(file_path, 'rb') as f:
                while f.read(1024 * 1024):
                    pass
            
            read_time = time.time() - start_time
            read_speed = file_size_mb / read_time  # MB/s
            
            # 清理临时文件
            os.unlink(file_path)
            
            cls.results['disk'] = {
                'read_speed': f"{read_speed:.2f} MB/s",
                'write_speed': f"{write_speed:.2f} MB/s"
            }
            info = f'''\n硬盘测试结果:
读取速度: {cls.results['disk']['read_speed']}
写入速度: {cls.results['disk']['write_speed']}
'''
            print(info)
            return info
        except Exception as e:
            print(f"硬盘测试失败: {str(e)}")
            cls.results['disk'] = None
            return f"硬盘测试失败: {str(e)}"

    @classmethod
    def memory(cls, size_mb=1000):
        """测试内存读写速度"""
        try:
            # 写入测试
            start_time = time.time()
            data = [random.random() for _ in range(size_mb * 1024 * 1024 // 8)]  # 创建指定大小的列表
            write_time = time.time() - start_time
            write_speed = size_mb / write_time
            
            # 读取测试
            start_time = time.time()
            _ = [x for x in data]  # 遍历列表
            read_time = time.time() - start_time
            read_speed = size_mb / read_time
            
            cls.results['memory'] = {
                'read_speed': f"{read_speed:.2f} MB/s",
                'write_speed': f"{write_speed:.2f} MB/s"
            }
            info = f'''\n内存测试结果:
读取速度: {cls.results['memory']['read_speed']}
写入速度: {cls.results['memory']['write_speed']}
'''
            print(info)
            return info
        except Exception as e:
            print(f"内存测试失败: {str(e)}")
            cls.results['memory'] = None
            return f"内存测试失败: {str(e)}"

    @classmethod
    def gpu_memory(cls):
        """测试GPU显存使用情况"""
        try:
            pynvml.nvmlInit()
            deviceCount = pynvml.nvmlDeviceGetCount()
            gpu_results = []
            
            for i in range(deviceCount):
                handle = pynvml.nvmlDeviceGetHandleByIndex(i)
                name = pynvml.nvmlDeviceGetName(handle)
                memory = pynvml.nvmlDeviceGetMemoryInfo(handle)
                utilization = pynvml.nvmlDeviceGetUtilizationRates(handle)


                size_bytes = 1000 * 1024 * 1024

                # Generate random data
                host_data = np.random.rand(size_bytes // 4).astype(np.float32)

                # Write test: Host to Device
                start_time = time.time()
                device_data = cuda.to_device(host_data)
                write_time = time.time() - start_time
                write_speed = 1000 / write_time

                # 读取显存测试
                start_time = time.time()
                device_data.copy_to_host()
                read_time = time.time() - start_time
                read_speed = 1000 / read_time

                gpu_info = {
                    'name': name,
                    'total_memory': f"{memory.total / (1024**2):.2f} MB",
                    'used_memory': f"{memory.used / (1024**2):.2f} MB",
                    'free_memory': f"{memory.free / (1024**2):.2f} MB",
                    'gpu_utilization': f"{utilization.gpu}%",
                    'memory_utilization': f"{utilization.memory}%",
                    'write_speed': f"{write_speed:.2f} MB/s",
                    'read_speed': f"{read_speed:.2f} MB/s"
                }
                gpu_results.append(gpu_info)
            
            cls.results['gpu'] = gpu_results
            pynvml.nvmlShutdown()
            info = f'''\nGPU测试结果:'''
            for i, gpu in enumerate(cls.results['gpu']):
                info += f'''\nGPU {i+1}:
名称: {gpu['name']}
总内存: {gpu['total_memory']}
已用内存: {gpu['used_memory']}
可用内存: {gpu['free_memory']}
GPU使用率: {gpu['gpu_utilization']}
显存使用率: {gpu['memory_utilization']}
写入速度: {gpu['write_speed']}
读取速度: {gpu['read_speed']}'''
            print(info)
            return info
        except Exception as e:
            print(f"GPU测试失败: {str(e)}")
            cls.results['gpu'] = None
            return f"GPU测试失败: {str(e)}"



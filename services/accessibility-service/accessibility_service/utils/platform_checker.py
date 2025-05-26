#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
跨平台兼容性检查工具
用于检测和处理不同操作系统和环境的兼容性问题
"""

import os
import sys
import platform
import subprocess
import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class PlatformType(Enum):
    """平台类型枚举"""
    WINDOWS = "windows"
    MACOS = "macos"
    LINUX = "linux"
    UNKNOWN = "unknown"


class ArchitectureType(Enum):
    """架构类型枚举"""
    X86_64 = "x86_64"
    ARM64 = "arm64"
    ARM = "arm"
    I386 = "i386"
    UNKNOWN = "unknown"


@dataclass
class SystemInfo:
    """系统信息"""
    platform_type: PlatformType
    architecture: ArchitectureType
    os_version: str
    python_version: str
    is_virtual_env: bool
    available_memory_gb: float
    cpu_count: int
    has_gpu: bool
    gpu_info: Optional[str] = None


@dataclass
class CompatibilityIssue:
    """兼容性问题"""
    severity: str  # "error", "warning", "info"
    component: str
    description: str
    solution: Optional[str] = None
    workaround: Optional[str] = None


@dataclass
class PlatformInfo:
    """Platform information data class."""
    system: str
    release: str
    version: str
    machine: str
    processor: str
    architecture: str
    python_version: str
    python_implementation: str


class PlatformChecker:
    """Utility class for checking platform capabilities and requirements."""
    
    def __init__(self):
        """Initialize the platform checker."""
        self._platform_info = None
        self._capabilities = None
    
    def get_platform_info(self) -> PlatformInfo:
        """Get detailed platform information."""
        if self._platform_info is None:
            self._platform_info = PlatformInfo(
                system=platform.system(),
                release=platform.release(),
                version=platform.version(),
                machine=platform.machine(),
                processor=platform.processor(),
                architecture=platform.architecture()[0],
                python_version=platform.python_version(),
                python_implementation=platform.python_implementation()
            )
        return self._platform_info
    
    def is_windows(self) -> bool:
        """Check if running on Windows."""
        return platform.system().lower() == 'windows'
    
    def is_linux(self) -> bool:
        """Check if running on Linux."""
        return platform.system().lower() == 'linux'
    
    def is_macos(self) -> bool:
        """Check if running on macOS."""
        return platform.system().lower() == 'darwin'
    
    def is_unix_like(self) -> bool:
        """Check if running on Unix-like system."""
        return self.is_linux() or self.is_macos()
    
    def get_python_version(self) -> tuple:
        """Get Python version as tuple."""
        return sys.version_info[:3]
    
    def check_python_version(self, min_version: tuple = (3, 8, 0)) -> bool:
        """Check if Python version meets minimum requirements."""
        return self.get_python_version() >= min_version
    
    def get_available_memory(self) -> Optional[int]:
        """Get available system memory in bytes."""
        try:
            if self.is_linux():
                with open('/proc/meminfo', 'r') as f:
                    for line in f:
                        if line.startswith('MemAvailable:'):
                            return int(line.split()[1]) * 1024
            elif self.is_macos():
                result = subprocess.run(
                    ['vm_stat'],
                    capture_output=True,
                    text=True,
                    check=True
                )
                # Parse vm_stat output (simplified)
                lines = result.stdout.split('\n')
                for line in lines:
                    if 'Pages free:' in line:
                        free_pages = int(line.split(':')[1].strip().rstrip('.'))
                        return free_pages * 4096  # Assuming 4KB page size
            elif self.is_windows():
                import psutil
                return psutil.virtual_memory().available
        except Exception:
            pass
        return None
    
    def get_cpu_count(self) -> int:
        """Get number of CPU cores."""
        return os.cpu_count() or 1
    
    def check_disk_space(self, path: str = '.', min_space_gb: float = 1.0) -> bool:
        """Check if sufficient disk space is available."""
        try:
            if self.is_windows():
                import shutil
                total, used, free = shutil.disk_usage(path)
            else:
                statvfs = os.statvfs(path)
                free = statvfs.f_frsize * statvfs.f_bavail
            
            free_gb = free / (1024 ** 3)
            return free_gb >= min_space_gb
        except Exception:
            return False
    
    def check_network_connectivity(self, host: str = "8.8.8.8", timeout: int = 5) -> bool:
        """Check network connectivity."""
        try:
            import socket
            socket.setdefaulttimeout(timeout)
            socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, 53))
            return True
        except Exception:
            return False
    
    def get_environment_variables(self) -> Dict[str, str]:
        """Get relevant environment variables."""
        relevant_vars = [
            'PATH', 'PYTHONPATH', 'HOME', 'USER', 'LANG', 'LC_ALL',
            'VIRTUAL_ENV', 'CONDA_DEFAULT_ENV', 'CUDA_VISIBLE_DEVICES'
        ]
        
        env_vars = {}
        for var in relevant_vars:
            value = os.environ.get(var)
            if value:
                env_vars[var] = value
        
        return env_vars
    
    def check_gpu_availability(self) -> Dict[str, Any]:
        """Check GPU availability and capabilities."""
        gpu_info = {
            'cuda_available': False,
            'cuda_version': None,
            'gpu_count': 0,
            'gpu_names': [],
            'total_memory': 0
        }
        
        try:
            # Check for CUDA
            import torch
            if torch.cuda.is_available():
                gpu_info['cuda_available'] = True
                gpu_info['cuda_version'] = torch.version.cuda
                gpu_info['gpu_count'] = torch.cuda.device_count()
                
                for i in range(gpu_info['gpu_count']):
                    gpu_name = torch.cuda.get_device_name(i)
                    gpu_memory = torch.cuda.get_device_properties(i).total_memory
                    gpu_info['gpu_names'].append(gpu_name)
                    gpu_info['total_memory'] += gpu_memory
        except ImportError:
            pass
        
        return gpu_info
    
    def check_dependencies(self, dependencies: List[str]) -> Dict[str, bool]:
        """Check if required dependencies are available."""
        results = {}
        
        for dep in dependencies:
            try:
                __import__(dep)
                results[dep] = True
            except ImportError:
                results[dep] = False
        
        return results
    
    def get_system_capabilities(self) -> Dict[str, Any]:
        """Get comprehensive system capabilities."""
        if self._capabilities is None:
            platform_info = self.get_platform_info()
            
            self._capabilities = {
                'platform': {
                    'system': platform_info.system,
                    'release': platform_info.release,
                    'architecture': platform_info.architecture,
                    'python_version': platform_info.python_version,
                },
                'resources': {
                    'cpu_count': self.get_cpu_count(),
                    'available_memory': self.get_available_memory(),
                    'disk_space_ok': self.check_disk_space(),
                },
                'connectivity': {
                    'network_available': self.check_network_connectivity(),
                },
                'gpu': self.check_gpu_availability(),
                'python': {
                    'version_ok': self.check_python_version(),
                    'implementation': platform_info.python_implementation,
                },
                'environment': self.get_environment_variables(),
            }
        
        return self._capabilities
    
    def validate_requirements(self, requirements: Dict[str, Any]) -> Dict[str, bool]:
        """Validate system against requirements."""
        capabilities = self.get_system_capabilities()
        results = {}
        
        # Check Python version
        if 'python_version' in requirements:
            min_version = tuple(requirements['python_version'])
            results['python_version'] = self.check_python_version(min_version)
        
        # Check memory
        if 'min_memory_gb' in requirements:
            available_memory = capabilities['resources']['available_memory']
            if available_memory:
                available_gb = available_memory / (1024 ** 3)
                results['memory'] = available_gb >= requirements['min_memory_gb']
            else:
                results['memory'] = False
        
        # Check disk space
        if 'min_disk_space_gb' in requirements:
            results['disk_space'] = self.check_disk_space(
                min_space_gb=requirements['min_disk_space_gb']
            )
        
        # Check dependencies
        if 'dependencies' in requirements:
            dep_results = self.check_dependencies(requirements['dependencies'])
            results['dependencies'] = all(dep_results.values())
            results['dependency_details'] = dep_results
        
        # Check network
        if 'network_required' in requirements and requirements['network_required']:
            results['network'] = capabilities['connectivity']['network_available']
        
        # Check GPU
        if 'gpu_required' in requirements and requirements['gpu_required']:
            results['gpu'] = capabilities['gpu']['cuda_available']
        
        return results
    
    def get_compatibility_report(self) -> Dict[str, Any]:
        """Get a comprehensive compatibility report."""
        capabilities = self.get_system_capabilities()
        
        # Define minimum requirements for accessibility service
        min_requirements = {
            'python_version': (3, 8, 0),
            'min_memory_gb': 2.0,
            'min_disk_space_gb': 1.0,
            'dependencies': [
                'pydantic', 'fastapi', 'uvicorn', 'sqlalchemy',
                'redis', 'numpy', 'pillow'
            ],
            'network_required': True,
            'gpu_required': False
        }
        
        validation_results = self.validate_requirements(min_requirements)
        
        return {
            'platform_info': capabilities['platform'],
            'system_resources': capabilities['resources'],
            'requirements_check': validation_results,
            'recommendations': self._get_recommendations(validation_results),
            'compatibility_score': self._calculate_compatibility_score(validation_results)
        }
    
    def _get_recommendations(self, validation_results: Dict[str, bool]) -> List[str]:
        """Get recommendations based on validation results."""
        recommendations = []
        
        if not validation_results.get('python_version', True):
            recommendations.append("Upgrade Python to version 3.11 or higher")
        
        if not validation_results.get('memory', True):
            recommendations.append("Increase available system memory (minimum 2GB recommended)")
        
        if not validation_results.get('disk_space', True):
            recommendations.append("Free up disk space (minimum 1GB required)")
        
        if not validation_results.get('dependencies', True):
            recommendations.append("Install missing Python dependencies")
        
        if not validation_results.get('network', True):
            recommendations.append("Ensure network connectivity for external services")
        
        if not recommendations:
            recommendations.append("System meets all requirements")
        
        return recommendations
    
    def _calculate_compatibility_score(self, validation_results: Dict[str, bool]) -> float:
        """Calculate compatibility score (0-100)."""
        if not validation_results:
            return 0.0
        
        passed = sum(1 for result in validation_results.values() if result)
        total = len(validation_results)
        
        return (passed / total) * 100.0


def check_platform_compatibility() -> Dict[str, Any]:
    """便捷函数：检查平台兼容性"""
    checker = PlatformChecker()
    return checker.get_compatibility_report()


if __name__ == "__main__":
    # 运行兼容性检查
    checker = PlatformChecker()
    report = checker.get_compatibility_report()
    
    print("🔍 索克生活无障碍服务 - 平台兼容性检查报告")
    print("=" * 60)
    
    # 平台信息
    platform_info = report['platform_info']
    print("\n📋 平台信息:")
    print(f"  操作系统: {platform_info['system']} ({platform_info['release']})")
    print(f"  架构: {platform_info['architecture']}")
    print(f"  Python版本: {platform_info['python_version']}")
    
    # 系统资源
    system_resources = report['system_resources']
    print("\n📋 系统资源:")
    print(f"  可用内存: {system_resources['available_memory'] / (1024 ** 3):.2f} GB")
    print(f"  CPU核心数: {system_resources['cpu_count']}")
    print(f"  磁盘空间: {'可用' if system_resources['disk_space_ok'] else '不足'}")
    
    # 兼容性检查结果
    requirements_check = report['requirements_check']
    print("\n📋 兼容性检查结果:")
    for requirement, result in requirements_check.items():
        print(f"  {requirement}: {'通过' if result else '未通过'}")
    
    # 兼容性评分
    compatibility_score = report['compatibility_score']
    print(f"\n📊 兼容性评分: {compatibility_score:.1f}/100")
    
    # 建议
    recommendations = report['recommendations']
    if recommendations:
        print("\n💡 改进建议:")
        for rec in recommendations:
            print(f"  • {rec}")
    
    print("\n" + "=" * 60) 
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


class PlatformChecker:
    """平台兼容性检查器"""
    
    def __init__(self):
        self.system_info = self._detect_system_info()
        self.compatibility_issues: List[CompatibilityIssue] = []
    
    def _detect_system_info(self) -> SystemInfo:
        """检测系统信息"""
        # 检测平台类型
        system = platform.system().lower()
        if system == "windows":
            platform_type = PlatformType.WINDOWS
        elif system == "darwin":
            platform_type = PlatformType.MACOS
        elif system == "linux":
            platform_type = PlatformType.LINUX
        else:
            platform_type = PlatformType.UNKNOWN
        
        # 检测架构
        machine = platform.machine().lower()
        if machine in ["x86_64", "amd64"]:
            architecture = ArchitectureType.X86_64
        elif machine in ["arm64", "aarch64"]:
            architecture = ArchitectureType.ARM64
        elif machine.startswith("arm"):
            architecture = ArchitectureType.ARM
        elif machine in ["i386", "i686"]:
            architecture = ArchitectureType.I386
        else:
            architecture = ArchitectureType.UNKNOWN
        
        # 检测虚拟环境
        is_virtual_env = (
            hasattr(sys, 'real_prefix') or
            (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix) or
            os.environ.get('VIRTUAL_ENV') is not None or
            os.environ.get('CONDA_DEFAULT_ENV') is not None
        )
        
        # 检测内存
        try:
            if platform_type == PlatformType.LINUX:
                with open('/proc/meminfo', 'r') as f:
                    meminfo = f.read()
                    for line in meminfo.split('\n'):
                        if line.startswith('MemTotal:'):
                            memory_kb = int(line.split()[1])
                            available_memory_gb = memory_kb / 1024 / 1024
                            break
                    else:
                        available_memory_gb = 0.0
            elif platform_type == PlatformType.MACOS:
                result = subprocess.run(['sysctl', 'hw.memsize'], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    memory_bytes = int(result.stdout.split(':')[1].strip())
                    available_memory_gb = memory_bytes / 1024 / 1024 / 1024
                else:
                    available_memory_gb = 0.0
            elif platform_type == PlatformType.WINDOWS:
                import psutil
                available_memory_gb = psutil.virtual_memory().total / 1024 / 1024 / 1024
            else:
                available_memory_gb = 0.0
        except Exception:
            available_memory_gb = 0.0
        
        # 检测GPU
        has_gpu, gpu_info = self._detect_gpu()
        
        return SystemInfo(
            platform_type=platform_type,
            architecture=architecture,
            os_version=platform.platform(),
            python_version=platform.python_version(),
            is_virtual_env=is_virtual_env,
            available_memory_gb=available_memory_gb,
            cpu_count=os.cpu_count() or 1,
            has_gpu=has_gpu,
            gpu_info=gpu_info
        )
    
    def _detect_gpu(self) -> Tuple[bool, Optional[str]]:
        """检测GPU信息"""
        try:
            # 尝试检测NVIDIA GPU
            result = subprocess.run(['nvidia-smi', '--query-gpu=name', '--format=csv,noheader'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0 and result.stdout.strip():
                return True, f"NVIDIA: {result.stdout.strip()}"
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        
        try:
            # 尝试检测AMD GPU (Linux)
            system = platform.system().lower()
            if system == "linux":
                result = subprocess.run(['lspci'], capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    for line in result.stdout.split('\n'):
                        if 'VGA' in line and ('AMD' in line or 'ATI' in line):
                            return True, f"AMD: {line.split(':')[-1].strip()}"
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        
        try:
            # 尝试检测Intel GPU
            system = platform.system().lower()
            if system == "darwin":
                result = subprocess.run(['system_profiler', 'SPDisplaysDataType'], 
                                      capture_output=True, text=True, timeout=10)
                if result.returncode == 0 and 'Intel' in result.stdout:
                    return True, "Intel Integrated Graphics"
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        
        return False, None
    
    def check_python_compatibility(self) -> List[CompatibilityIssue]:
        """检查Python兼容性"""
        issues = []
        
        # 检查Python版本
        python_version = tuple(map(int, platform.python_version().split('.')))
        if python_version < (3, 8):
            issues.append(CompatibilityIssue(
                severity="error",
                component="python",
                description=f"Python版本 {platform.python_version()} 过低，需要3.8+",
                solution="升级Python到3.8或更高版本",
                workaround="使用pyenv或conda管理Python版本"
            ))
        elif python_version >= (3, 12):
            issues.append(CompatibilityIssue(
                severity="warning",
                component="python",
                description=f"Python版本 {platform.python_version()} 较新，某些依赖可能不兼容",
                solution="确保所有依赖都支持当前Python版本",
                workaround="考虑使用Python 3.11"
            ))
        
        # 检查虚拟环境
        if not self.system_info.is_virtual_env:
            issues.append(CompatibilityIssue(
                severity="warning",
                component="environment",
                description="未检测到虚拟环境，可能导致依赖冲突",
                solution="创建并激活虚拟环境",
                workaround="使用 python -m venv venv && source venv/bin/activate"
            ))
        
        return issues
    
    def check_system_requirements(self) -> List[CompatibilityIssue]:
        """检查系统要求"""
        issues = []
        
        # 检查内存
        if self.system_info.available_memory_gb < 4:
            issues.append(CompatibilityIssue(
                severity="warning",
                component="memory",
                description=f"可用内存 {self.system_info.available_memory_gb:.1f}GB 可能不足",
                solution="增加系统内存到8GB或更多",
                workaround="关闭其他应用程序释放内存"
            ))
        
        # 检查CPU核心数
        if self.system_info.cpu_count < 2:
            issues.append(CompatibilityIssue(
                severity="warning",
                component="cpu",
                description=f"CPU核心数 {self.system_info.cpu_count} 较少，可能影响性能",
                solution="使用多核CPU",
                workaround="减少并发处理数量"
            ))
        
        return issues
    
    def check_platform_specific_issues(self) -> List[CompatibilityIssue]:
        """检查平台特定问题"""
        issues = []
        
        if self.system_info.platform_type == PlatformType.MACOS:
            # macOS特定检查
            if self.system_info.architecture == ArchitectureType.ARM64:
                issues.append(CompatibilityIssue(
                    severity="info",
                    component="macos_arm",
                    description="检测到Apple Silicon (M1/M2)，某些依赖可能需要特殊处理",
                    solution="使用支持ARM64的依赖版本",
                    workaround="使用Rosetta 2运行x86_64版本"
                ))
            
            # 检查Xcode命令行工具
            try:
                subprocess.run(['xcode-select', '--version'], 
                             capture_output=True, check=True, timeout=5)
            except (subprocess.CalledProcessError, FileNotFoundError):
                issues.append(CompatibilityIssue(
                    severity="warning",
                    component="xcode",
                    description="未安装Xcode命令行工具，编译某些依赖可能失败",
                    solution="安装Xcode命令行工具",
                    workaround="xcode-select --install"
                ))
        
        elif self.system_info.platform_type == PlatformType.LINUX:
            # Linux特定检查
            # 检查必要的系统库
            required_libs = ['libgl1-mesa-glx', 'libglib2.0-0']
            for lib in required_libs:
                try:
                    result = subprocess.run(['dpkg', '-l', lib], 
                                          capture_output=True, timeout=5)
                    if result.returncode != 0:
                        issues.append(CompatibilityIssue(
                            severity="warning",
                            component="system_libs",
                            description=f"缺少系统库 {lib}",
                            solution=f"安装系统库: sudo apt-get install {lib}",
                            workaround="使用包管理器安装缺失的库"
                        ))
                except (subprocess.TimeoutExpired, FileNotFoundError):
                    pass
        
        elif self.system_info.platform_type == PlatformType.WINDOWS:
            # Windows特定检查
            # 检查Visual C++运行时
            try:
                import winreg
                # 这里可以添加更多Windows特定的检查
            except ImportError:
                pass
        
        return issues
    
    def check_audio_video_support(self) -> List[CompatibilityIssue]:
        """检查音视频支持"""
        issues = []
        
        # 检查音频设备
        try:
            if self.system_info.platform_type == PlatformType.LINUX:
                # 检查ALSA/PulseAudio
                result = subprocess.run(['aplay', '-l'], 
                                      capture_output=True, timeout=5)
                if result.returncode != 0:
                    issues.append(CompatibilityIssue(
                        severity="warning",
                        component="audio",
                        description="未检测到音频设备或ALSA配置问题",
                        solution="检查音频驱动和ALSA配置",
                        workaround="使用sudo apt-get install alsa-utils"
                    ))
            elif self.system_info.platform_type == PlatformType.MACOS:
                # macOS通常有内置音频支持
                pass
            elif self.system_info.platform_type == PlatformType.WINDOWS:
                # Windows通常有内置音频支持
                pass
        except (subprocess.TimeoutExpired, FileNotFoundError):
            issues.append(CompatibilityIssue(
                severity="info",
                component="audio",
                description="无法检测音频设备状态",
                solution="手动验证音频设备工作正常",
                workaround="测试系统音频播放功能"
            ))
        
        # 检查摄像头支持
        try:
            import cv2
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                issues.append(CompatibilityIssue(
                    severity="warning",
                    component="camera",
                    description="无法访问摄像头设备",
                    solution="检查摄像头连接和权限",
                    workaround="确保摄像头未被其他应用占用"
                ))
            cap.release()
        except ImportError:
            issues.append(CompatibilityIssue(
                severity="info",
                component="camera",
                description="OpenCV未安装，无法检测摄像头",
                solution="安装OpenCV: pip install opencv-python",
                workaround="手动验证摄像头功能"
            ))
        except Exception as e:
            issues.append(CompatibilityIssue(
                severity="warning",
                component="camera",
                description=f"摄像头检测失败: {str(e)}",
                solution="检查摄像头驱动和权限",
                workaround="重启系统或重新连接摄像头"
            ))
        
        return issues
    
    def check_network_connectivity(self) -> List[CompatibilityIssue]:
        """检查网络连接"""
        issues = []
        
        # 检查基本网络连接
        try:
            import socket
            socket.create_connection(("8.8.8.8", 53), timeout=3)
        except OSError:
            issues.append(CompatibilityIssue(
                severity="error",
                component="network",
                description="无法连接到互联网",
                solution="检查网络连接和防火墙设置",
                workaround="使用离线模式或配置代理"
            ))
        
        # 检查HTTPS连接
        try:
            import ssl
            import urllib.request
            urllib.request.urlopen("https://www.google.com", timeout=5)
        except Exception:
            issues.append(CompatibilityIssue(
                severity="warning",
                component="https",
                description="HTTPS连接可能有问题",
                solution="检查SSL证书和代理设置",
                workaround="配置证书或使用HTTP代理"
            ))
        
        return issues
    
    def run_comprehensive_check(self) -> Dict[str, Any]:
        """运行全面的兼容性检查"""
        all_issues = []
        
        # 运行各项检查
        all_issues.extend(self.check_python_compatibility())
        all_issues.extend(self.check_system_requirements())
        all_issues.extend(self.check_platform_specific_issues())
        all_issues.extend(self.check_audio_video_support())
        all_issues.extend(self.check_network_connectivity())
        
        # 统计问题
        error_count = sum(1 for issue in all_issues if issue.severity == "error")
        warning_count = sum(1 for issue in all_issues if issue.severity == "warning")
        info_count = sum(1 for issue in all_issues if issue.severity == "info")
        
        # 计算兼容性评分
        total_checks = len(all_issues) + 10  # 假设总共有10个基础检查
        compatibility_score = max(0, (total_checks - error_count * 3 - warning_count) / total_checks * 100)
        
        return {
            "system_info": self.system_info,
            "issues": all_issues,
            "summary": {
                "total_issues": len(all_issues),
                "errors": error_count,
                "warnings": warning_count,
                "info": info_count,
                "compatibility_score": round(compatibility_score, 1)
            },
            "recommendations": self._generate_recommendations(all_issues)
        }
    
    def _generate_recommendations(self, issues: List[CompatibilityIssue]) -> List[str]:
        """生成改进建议"""
        recommendations = []
        
        # 基于问题生成建议
        error_issues = [issue for issue in issues if issue.severity == "error"]
        if error_issues:
            recommendations.append("🚨 发现严重兼容性问题，建议优先解决错误级别的问题")
        
        warning_issues = [issue for issue in issues if issue.severity == "warning"]
        if warning_issues:
            recommendations.append("⚠️ 发现兼容性警告，建议在生产环境部署前解决")
        
        # 基于系统信息生成建议
        if self.system_info.available_memory_gb < 8:
            recommendations.append("💾 建议增加系统内存到8GB以获得更好的性能")
        
        if not self.system_info.has_gpu:
            recommendations.append("🎮 考虑使用GPU加速以提升AI模型性能")
        
        if not self.system_info.is_virtual_env:
            recommendations.append("🐍 强烈建议使用虚拟环境隔离依赖")
        
        return recommendations
    
    def print_report(self):
        """打印兼容性报告"""
        result = self.run_comprehensive_check()
        
        print("🔍 索克生活无障碍服务 - 平台兼容性检查报告")
        print("=" * 60)
        
        # 系统信息
        print("\n📋 系统信息:")
        info = result["system_info"]
        print(f"  操作系统: {info.platform_type.value} ({info.os_version})")
        print(f"  架构: {info.architecture.value}")
        print(f"  Python版本: {info.python_version}")
        print(f"  虚拟环境: {'是' if info.is_virtual_env else '否'}")
        print(f"  内存: {info.available_memory_gb:.1f} GB")
        print(f"  CPU核心: {info.cpu_count}")
        print(f"  GPU: {'是' if info.has_gpu else '否'} {info.gpu_info or ''}")
        
        # 兼容性评分
        print(f"\n📊 兼容性评分: {result['summary']['compatibility_score']}/100")
        
        # 问题列表
        if result["issues"]:
            print(f"\n⚠️ 发现的问题 ({result['summary']['total_issues']} 个):")
            for issue in result["issues"]:
                icon = "🚨" if issue.severity == "error" else "⚠️" if issue.severity == "warning" else "ℹ️"
                print(f"  {icon} [{issue.component}] {issue.description}")
                if issue.solution:
                    print(f"     解决方案: {issue.solution}")
                if issue.workaround:
                    print(f"     临时方案: {issue.workaround}")
                print()
        else:
            print("\n✅ 未发现兼容性问题")
        
        # 建议
        if result["recommendations"]:
            print("💡 改进建议:")
            for rec in result["recommendations"]:
                print(f"  • {rec}")
        
        print("\n" + "=" * 60)


def check_platform_compatibility() -> Dict[str, Any]:
    """便捷函数：检查平台兼容性"""
    checker = PlatformChecker()
    return checker.run_comprehensive_check()


if __name__ == "__main__":
    # 运行兼容性检查
    checker = PlatformChecker()
    checker.print_report() 
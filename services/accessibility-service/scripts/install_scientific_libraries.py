#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
科学计算库自动安装脚本
自动检测系统环境并安装所需的科学计算库
"""

import os
import sys
import subprocess
import platform
import argparse
from typing import List, Dict, Tuple
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ScientificLibraryInstaller:
    """科学计算库安装器"""
    
    def __init__(self):
        """初始化安装器"""
        self.system = platform.system().lower()
        self.python_version = sys.version_info
        self.installation_results = {}
        
        # 核心科学计算库
        self.core_libraries = [
            'numpy>=1.24.0',
            'scipy>=1.11.0',
            'pandas>=2.1.0',
            'matplotlib>=3.8.0',
            'seaborn>=0.13.0',
            'plotly>=5.17.0'
        ]
        
        # 机器学习库
        self.ml_libraries = [
            'scikit-learn>=1.3.0',
            'xgboost>=2.0.0',
            'lightgbm>=4.1.0',
            'catboost>=1.2.0'
        ]
        
        # 计算机视觉库
        self.cv_libraries = [
            'opencv-python>=4.8.0',
            'Pillow>=10.1.0',
            'imageio>=2.33.0',
            'scikit-image>=0.22.0'
        ]
        
        # 音频处理库
        self.audio_libraries = [
            'librosa>=0.10.0',
            'sounddevice>=0.4.6',
            'pydub>=0.25.0'
        ]
        
        # 信号处理库
        self.signal_libraries = [
            'filterpy>=1.4.5',
            'pywavelets>=1.4.1'
        ]
        
        # 地理信息库
        self.geo_libraries = [
            'geopy>=2.4.0',
            'shapely>=2.0.0',
            'folium>=0.15.0',
            'haversine>=2.8.0'
        ]
        
        # 性能优化库
        self.performance_libraries = [
            'numba>=0.58.0',
            'joblib>=1.3.0'
        ]
        
        # 数据存储库
        self.storage_libraries = [
            'h5py>=3.10.0'
        ]
        
        # 开发工具
        self.dev_libraries = [
            'jupyter>=1.0.0',
            'ipython>=8.17.0',
            'notebook>=7.0.0'
        ]
    
    def check_python_version(self) -> bool:
        """检查Python版本"""
        logger.info(f"检查Python版本: {self.python_version}")
        
        if self.python_version < (3, 8):
            logger.error("需要Python 3.8或更高版本")
            return False
        
        logger.info("✅ Python版本检查通过")
        return True
    
    def install_system_dependencies(self) -> bool:
        """安装系统依赖"""
        logger.info("安装系统依赖...")
        
        try:
            if self.system == 'darwin':  # macOS
                self._install_macos_dependencies()
            elif self.system == 'linux':
                self._install_linux_dependencies()
            elif self.system == 'windows':
                self._install_windows_dependencies()
            else:
                logger.warning(f"未知系统: {self.system}")
                return False
            
            logger.info("✅ 系统依赖安装完成")
            return True
            
        except Exception as e:
            logger.error(f"系统依赖安装失败: {e}")
            return False
    
    def _install_macos_dependencies(self):
        """安装macOS系统依赖"""
        dependencies = [
            'brew install portaudio',  # 音频处理
            'brew install pkg-config',  # 包配置
            'brew install hdf5',  # HDF5支持
            'brew install geos',  # 地理信息系统
            'brew install proj',  # 地图投影
            'brew install gdal',  # 地理数据抽象库
        ]
        
        for cmd in dependencies:
            try:
                subprocess.run(cmd.split(), check=True, capture_output=True)
                logger.info(f"✅ 执行成功: {cmd}")
            except subprocess.CalledProcessError as e:
                logger.warning(f"⚠️ 执行失败: {cmd} - {e}")
            except FileNotFoundError:
                logger.warning("⚠️ Homebrew未安装，跳过系统依赖安装")
                break
    
    def _install_linux_dependencies(self):
        """安装Linux系统依赖"""
        # 检测包管理器
        if self._command_exists('apt-get'):
            dependencies = [
                'sudo apt-get update',
                'sudo apt-get install -y python3-dev',
                'sudo apt-get install -y portaudio19-dev',
                'sudo apt-get install -y libhdf5-dev',
                'sudo apt-get install -y libgeos-dev',
                'sudo apt-get install -y libproj-dev',
                'sudo apt-get install -y libgdal-dev',
                'sudo apt-get install -y libblas-dev liblapack-dev',
                'sudo apt-get install -y gfortran'
            ]
        elif self._command_exists('yum'):
            dependencies = [
                'sudo yum install -y python3-devel',
                'sudo yum install -y portaudio-devel',
                'sudo yum install -y hdf5-devel',
                'sudo yum install -y geos-devel',
                'sudo yum install -y proj-devel',
                'sudo yum install -y gdal-devel',
                'sudo yum install -y blas-devel lapack-devel',
                'sudo yum install -y gcc-gfortran'
            ]
        else:
            logger.warning("未检测到支持的包管理器")
            return
        
        for cmd in dependencies:
            try:
                subprocess.run(cmd.split(), check=True, capture_output=True)
                logger.info(f"✅ 执行成功: {cmd}")
            except subprocess.CalledProcessError as e:
                logger.warning(f"⚠️ 执行失败: {cmd} - {e}")
    
    def _install_windows_dependencies(self):
        """安装Windows系统依赖"""
        logger.info("Windows系统建议使用Anaconda或Miniconda来安装科学计算库")
        logger.info("请访问: https://www.anaconda.com/products/distribution")
    
    def _command_exists(self, command: str) -> bool:
        """检查命令是否存在"""
        try:
            subprocess.run(['which', command], check=True, capture_output=True)
            return True
        except subprocess.CalledProcessError:
            return False
    
    def install_libraries(self, library_groups: List[str]) -> Dict[str, bool]:
        """安装指定的库组"""
        results = {}
        
        for group in library_groups:
            if group == 'core':
                results.update(self._install_library_group('核心科学计算库', self.core_libraries))
            elif group == 'ml':
                results.update(self._install_library_group('机器学习库', self.ml_libraries))
            elif group == 'cv':
                results.update(self._install_library_group('计算机视觉库', self.cv_libraries))
            elif group == 'audio':
                results.update(self._install_library_group('音频处理库', self.audio_libraries))
            elif group == 'signal':
                results.update(self._install_library_group('信号处理库', self.signal_libraries))
            elif group == 'geo':
                results.update(self._install_library_group('地理信息库', self.geo_libraries))
            elif group == 'performance':
                results.update(self._install_library_group('性能优化库', self.performance_libraries))
            elif group == 'storage':
                results.update(self._install_library_group('数据存储库', self.storage_libraries))
            elif group == 'dev':
                results.update(self._install_library_group('开发工具', self.dev_libraries))
            else:
                logger.warning(f"未知的库组: {group}")
        
        return results
    
    def _install_library_group(self, group_name: str, libraries: List[str]) -> Dict[str, bool]:
        """安装一组库"""
        logger.info(f"安装 {group_name}...")
        results = {}
        
        for library in libraries:
            try:
                logger.info(f"  安装 {library}...")
                subprocess.run([
                    sys.executable, '-m', 'pip', 'install', library, '--upgrade'
                ], check=True, capture_output=True)
                
                results[library] = True
                logger.info(f"  ✅ {library} 安装成功")
                
            except subprocess.CalledProcessError as e:
                results[library] = False
                logger.error(f"  ❌ {library} 安装失败: {e}")
        
        return results
    
    def verify_installation(self) -> Dict[str, bool]:
        """验证安装结果"""
        logger.info("验证安装结果...")
        
        verification_imports = {
            'numpy': 'import numpy',
            'scipy': 'import scipy',
            'pandas': 'import pandas',
            'matplotlib': 'import matplotlib.pyplot',
            'seaborn': 'import seaborn',
            'plotly': 'import plotly.graph_objects',
            'sklearn': 'import sklearn',
            'cv2': 'import cv2',
            'PIL': 'import PIL',
            'librosa': 'import librosa',
            'filterpy': 'import filterpy',
            'geopy': 'import geopy',
            'numba': 'import numba',
            'h5py': 'import h5py'
        }
        
        results = {}
        for lib_name, import_statement in verification_imports.items():
            try:
                subprocess.run([
                    sys.executable, '-c', import_statement
                ], check=True, capture_output=True)
                results[lib_name] = True
                logger.info(f"✅ {lib_name} 验证成功")
            except subprocess.CalledProcessError:
                results[lib_name] = False
                logger.warning(f"⚠️ {lib_name} 验证失败")
        
        return results
    
    def generate_report(self, installation_results: Dict[str, bool], 
                       verification_results: Dict[str, bool]) -> str:
        """生成安装报告"""
        report = []
        report.append("=" * 60)
        report.append("科学计算库安装报告")
        report.append("=" * 60)
        
        # 系统信息
        report.append(f"系统: {platform.system()} {platform.release()}")
        report.append(f"Python版本: {sys.version}")
        report.append(f"安装时间: {__import__('datetime').datetime.now()}")
        report.append("")
        
        # 安装结果
        report.append("安装结果:")
        total_attempted = len(installation_results)
        successful_installs = sum(installation_results.values())
        
        for library, success in installation_results.items():
            status = "✅ 成功" if success else "❌ 失败"
            report.append(f"  {library}: {status}")
        
        report.append(f"\n安装成功率: {successful_installs}/{total_attempted} ({successful_installs/total_attempted*100:.1f}%)")
        report.append("")
        
        # 验证结果
        report.append("验证结果:")
        total_verified = len(verification_results)
        successful_verifications = sum(verification_results.values())
        
        for library, success in verification_results.items():
            status = "✅ 可用" if success else "❌ 不可用"
            report.append(f"  {library}: {status}")
        
        report.append(f"\n验证成功率: {successful_verifications}/{total_verified} ({successful_verifications/total_verified*100:.1f}%)")
        report.append("")
        
        # 建议
        if successful_verifications < total_verified:
            report.append("建议:")
            report.append("- 检查系统依赖是否正确安装")
            report.append("- 尝试使用conda安装失败的库")
            report.append("- 查看具体错误信息并手动安装")
        
        report.append("=" * 60)
        
        return "\n".join(report)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='科学计算库自动安装脚本')
    parser.add_argument('--core-only', action='store_true', 
                       help='只安装核心库')
    parser.add_argument('--no-system-deps', action='store_true',
                       help='跳过系统依赖安装')
    parser.add_argument('--groups', nargs='+', 
                       choices=['core', 'ml', 'cv', 'audio', 'signal', 'geo', 'performance', 'storage', 'dev'],
                       default=['core', 'ml', 'cv', 'audio', 'signal'],
                       help='要安装的库组')
    
    args = parser.parse_args()
    
    installer = ScientificLibraryInstaller()
    
    # 检查Python版本
    if not installer.check_python_version():
        sys.exit(1)
    
    # 安装系统依赖
    if not args.no_system_deps:
        installer.install_system_dependencies()
    
    # 确定要安装的库组
    if args.core_only:
        library_groups = ['core']
    else:
        library_groups = args.groups
    
    logger.info(f"将安装以下库组: {', '.join(library_groups)}")
    
    # 安装库
    installation_results = installer.install_libraries(library_groups)
    
    # 验证安装
    verification_results = installer.verify_installation()
    
    # 生成报告
    report = installer.generate_report(installation_results, verification_results)
    print(report)
    
    # 保存报告到文件
    report_file = 'scientific_libraries_installation_report.txt'
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    logger.info(f"安装报告已保存到: {report_file}")
    
    # 返回适当的退出码
    total_verified = len(verification_results)
    successful_verifications = sum(verification_results.values())
    
    if successful_verifications == total_verified:
        logger.info("🎉 所有库安装和验证成功！")
        sys.exit(0)
    elif successful_verifications >= total_verified * 0.8:
        logger.warning("⚠️ 大部分库安装成功，但有一些失败")
        sys.exit(0)
    else:
        logger.error("❌ 多数库安装失败")
        sys.exit(1)


if __name__ == '__main__':
    main() 
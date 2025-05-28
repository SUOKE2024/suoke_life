#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
索克生活 - Python版本统一更新脚本
将所有微服务的Python版本统一更新为3.13.3
"""

import os
import re
import glob
from pathlib import Path
from typing import List, Dict, Any
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 目标Python版本
TARGET_PYTHON_VERSION = "3.13.3"
TARGET_PYTHON_MAJOR_MINOR = "3.13"

class PythonVersionUpdater:
    """Python版本更新器"""
    
    def __init__(self, root_dir: str = "."):
        self.root_dir = Path(root_dir)
        self.updated_files = []
        self.errors = []
    
    def update_all(self):
        """更新所有配置文件"""
        logger.info(f"开始将Python版本统一更新为 {TARGET_PYTHON_VERSION}")
        
        # 更新pyproject.toml文件
        self.update_pyproject_files()
        
        # 更新Dockerfile文件
        self.update_dockerfile_files()
        
        # 更新requirements.txt文件中的Python版本注释
        self.update_requirements_files()
        
        # 更新CI/CD配置文件
        self.update_ci_files()
        
        # 更新Makefile文件
        self.update_makefile_files()
        
        # 生成报告
        self.generate_report()
    
    def update_pyproject_files(self):
        """更新所有pyproject.toml文件"""
        logger.info("更新pyproject.toml文件...")
        
        pyproject_files = list(self.root_dir.rglob("pyproject.toml"))
        
        for file_path in pyproject_files:
            try:
                self.update_pyproject_file(file_path)
            except Exception as e:
                self.errors.append(f"更新 {file_path} 失败: {e}")
                logger.error(f"更新 {file_path} 失败: {e}")
    
    def update_pyproject_file(self, file_path: Path):
        """更新单个pyproject.toml文件"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # 更新requires-python (处理多种格式)
        content = re.sub(
            r'requires-python\s*=\s*"[^"]*"',
            f'requires-python = ">={TARGET_PYTHON_VERSION}"',
            content
        )
        
        # 更新poetry风格的python版本 (^3.13 -> >=3.13.3)
        content = re.sub(
            r'python\s*=\s*"\^3\.\d+(\.\d+)?"',
            f'python = ">={TARGET_PYTHON_VERSION}"',
            content
        )
        
        # 更新其他python版本格式
        content = re.sub(
            r'python\s*=\s*">=3\.\d+(\.\d+)?"',
            f'python = ">={TARGET_PYTHON_VERSION}"',
            content
        )
        
        # 确保添加Python 3.13分类器
        if f'"Programming Language :: Python :: {TARGET_PYTHON_MAJOR_MINOR}"' not in content:
            if 'classifiers = [' in content:
                # 已有classifiers部分，添加Python 3.13分类器
                lines = content.split('\n')
                new_lines = []
                in_classifiers = False
                python_classifier_added = False
                
                for line in lines:
                    if 'classifiers = [' in line:
                        in_classifiers = True
                        new_lines.append(line)
                    elif in_classifiers and line.strip() == ']':
                        # 在结束前添加Python 3.13分类器
                        if not python_classifier_added:
                            new_lines.append(f'    "Programming Language :: Python :: {TARGET_PYTHON_MAJOR_MINOR}",')
                        new_lines.append(line)
                        in_classifiers = False
                    elif in_classifiers and '"Programming Language :: Python :: 3.' in line:
                        # 替换旧的Python版本分类器
                        if TARGET_PYTHON_MAJOR_MINOR not in line:
                            new_lines.append(f'    "Programming Language :: Python :: {TARGET_PYTHON_MAJOR_MINOR}",')
                            python_classifier_added = True
                        else:
                            new_lines.append(line)
                            python_classifier_added = True
                    else:
                        new_lines.append(line)
                
                content = '\n'.join(new_lines)
            else:
                # 没有classifiers部分，在[project]部分后添加
                lines = content.split('\n')
                new_lines = []
                project_section_found = False
                classifiers_added = False
                
                for i, line in enumerate(lines):
                    new_lines.append(line)
                    
                    if line.strip() == '[project]':
                        project_section_found = True
                    elif project_section_found and not classifiers_added:
                        # 检查是否到了下一个section或文件结束
                        next_line = lines[i + 1] if i + 1 < len(lines) else ""
                        if (next_line.strip().startswith('[') and next_line.strip() != '[project]') or i == len(lines) - 1:
                            # 在当前行后添加classifiers
                            new_lines.append('classifiers = [')
                            new_lines.append(f'    "Programming Language :: Python :: {TARGET_PYTHON_MAJOR_MINOR}",')
                            new_lines.append(']')
                            classifiers_added = True
                
                content = '\n'.join(new_lines)
        
        # 更新tool.black的target-version
        content = re.sub(
            r"target-version\s*=\s*\[[^\]]*\]",
            f"target-version = ['py{TARGET_PYTHON_MAJOR_MINOR.replace('.', '')}']",
            content
        )
        
        # 更新tool.mypy的python_version
        content = re.sub(
            r'python_version\s*=\s*"[^"]*"',
            f'python_version = "{TARGET_PYTHON_MAJOR_MINOR}"',
            content
        )
        
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            self.updated_files.append(str(file_path))
            logger.info(f"已更新: {file_path}")
    
    def update_dockerfile_files(self):
        """更新所有Dockerfile文件"""
        logger.info("更新Dockerfile文件...")
        
        dockerfile_patterns = [
            "**/Dockerfile",
            "**/Dockerfile.*",
            "**/*.dockerfile"
        ]
        
        dockerfile_files = []
        for pattern in dockerfile_patterns:
            dockerfile_files.extend(self.root_dir.rglob(pattern))
        
        for file_path in dockerfile_files:
            try:
                self.update_dockerfile_file(file_path)
            except Exception as e:
                self.errors.append(f"更新 {file_path} 失败: {e}")
                logger.error(f"更新 {file_path} 失败: {e}")
    
    def update_dockerfile_file(self, file_path: Path):
        """更新单个Dockerfile文件"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # 更新FROM python:版本
        content = re.sub(
            r'FROM python:\d+\.\d+(\.\d+)?(-\w+)?',
            f'FROM python:{TARGET_PYTHON_VERSION}-slim',
            content
        )
        
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            self.updated_files.append(str(file_path))
            logger.info(f"已更新: {file_path}")
    
    def update_requirements_files(self):
        """更新requirements.txt文件中的Python版本注释"""
        logger.info("更新requirements.txt文件...")
        
        requirements_files = list(self.root_dir.rglob("requirements*.txt"))
        
        for file_path in requirements_files:
            try:
                self.update_requirements_file(file_path)
            except Exception as e:
                self.errors.append(f"更新 {file_path} 失败: {e}")
                logger.error(f"更新 {file_path} 失败: {e}")
    
    def update_requirements_file(self, file_path: Path):
        """更新单个requirements.txt文件"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # 更新Python版本注释
        content = re.sub(
            r'# .*Python \d+\.\d+.*',
            f'# Python {TARGET_PYTHON_VERSION} 兼容版本',
            content
        )
        
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            self.updated_files.append(str(file_path))
            logger.info(f"已更新: {file_path}")
    
    def update_ci_files(self):
        """更新CI/CD配置文件"""
        logger.info("更新CI/CD配置文件...")
        
        ci_files = []
        ci_files.extend(self.root_dir.rglob(".github/workflows/*.yml"))
        ci_files.extend(self.root_dir.rglob(".github/workflows/*.yaml"))
        ci_files.extend(self.root_dir.rglob(".gitlab-ci.yml"))
        
        for file_path in ci_files:
            try:
                self.update_ci_file(file_path)
            except Exception as e:
                self.errors.append(f"更新 {file_path} 失败: {e}")
                logger.error(f"更新 {file_path} 失败: {e}")
    
    def update_ci_file(self, file_path: Path):
        """更新单个CI配置文件"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # 更新Python版本
        content = re.sub(
            r'python-version:\s*["\']?\d+\.\d+(\.\d+)?["\']?',
            f'python-version: "{TARGET_PYTHON_VERSION}"',
            content
        )
        
        content = re.sub(
            r'python-version:\s*\[\s*["\']?\d+\.\d+["\']?\s*\]',
            f'python-version: ["{TARGET_PYTHON_VERSION}"]',
            content
        )
        
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            self.updated_files.append(str(file_path))
            logger.info(f"已更新: {file_path}")
    
    def update_makefile_files(self):
        """更新Makefile文件"""
        logger.info("更新Makefile文件...")
        
        makefile_files = []
        makefile_files.extend(self.root_dir.rglob("Makefile"))
        makefile_files.extend(self.root_dir.rglob("makefile"))
        
        for file_path in makefile_files:
            try:
                self.update_makefile_file(file_path)
            except Exception as e:
                self.errors.append(f"更新 {file_path} 失败: {e}")
                logger.error(f"更新 {file_path} 失败: {e}")
    
    def update_makefile_file(self, file_path: Path):
        """更新单个Makefile文件"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # 更新PYTHON变量
        content = re.sub(
            r'PYTHON\s*:?=\s*python\d+\.\d+',
            f'PYTHON := python{TARGET_PYTHON_MAJOR_MINOR}',
            content
        )
        
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            self.updated_files.append(str(file_path))
            logger.info(f"已更新: {file_path}")
    
    def generate_report(self):
        """生成更新报告"""
        logger.info("\n" + "="*60)
        logger.info("Python版本更新完成报告")
        logger.info("="*60)
        
        logger.info(f"目标版本: Python {TARGET_PYTHON_VERSION}")
        logger.info(f"成功更新文件数: {len(self.updated_files)}")
        logger.info(f"错误数: {len(self.errors)}")
        
        if self.updated_files:
            logger.info("\n已更新的文件:")
            for file_path in sorted(self.updated_files):
                logger.info(f"  ✓ {file_path}")
        
        if self.errors:
            logger.info("\n错误列表:")
            for error in self.errors:
                logger.error(f"  ✗ {error}")
        
        # 生成更新摘要文件
        summary_file = self.root_dir / "PYTHON_VERSION_UPDATE_SUMMARY.md"
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(f"# Python版本更新摘要\n\n")
            f.write(f"**更新时间**: {self._get_current_time()}\n")
            f.write(f"**目标版本**: Python {TARGET_PYTHON_VERSION}\n")
            f.write(f"**更新文件数**: {len(self.updated_files)}\n")
            f.write(f"**错误数**: {len(self.errors)}\n\n")
            
            if self.updated_files:
                f.write("## 已更新的文件\n\n")
                for file_path in sorted(self.updated_files):
                    f.write(f"- `{file_path}`\n")
                f.write("\n")
            
            if self.errors:
                f.write("## 错误列表\n\n")
                for error in self.errors:
                    f.write(f"- {error}\n")
                f.write("\n")
            
            f.write("## 更新内容\n\n")
            f.write("1. **pyproject.toml**: 更新 `requires-python`、`classifiers`、`tool.black.target-version`、`tool.mypy.python_version`\n")
            f.write("2. **Dockerfile**: 更新 `FROM python:` 基础镜像版本\n")
            f.write("3. **requirements.txt**: 更新Python版本注释\n")
            f.write("4. **CI/CD配置**: 更新GitHub Actions、GitLab CI等配置中的Python版本\n")
            f.write("5. **Makefile**: 更新PYTHON变量\n\n")
            
            f.write("## 验证步骤\n\n")
            f.write("1. 检查所有微服务是否能正常启动\n")
            f.write("2. 运行测试套件确保兼容性\n")
            f.write("3. 更新开发环境和CI/CD环境\n")
            f.write("4. 更新文档中的Python版本要求\n")
        
        logger.info(f"\n更新摘要已保存到: {summary_file}")
    
    def _get_current_time(self):
        """获取当前时间字符串"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def main():
    """主函数"""
    updater = PythonVersionUpdater()
    updater.update_all()


if __name__ == "__main__":
    main() 
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
索克生活 - Python版本验证脚本
验证所有微服务的Python版本是否统一为3.13.3
"""

import re
import sys
import json
from pathlib import Path
from typing import Dict, List, Tuple, Any
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

def verify_python_versions():
    """验证Python版本统一性"""
    root_dir = Path(".")

    logger.info(f"开始验证Python版本是否统一为 {TARGET_PYTHON_VERSION}")

    # 统计结果
    total_files = 0
    passed_files = 0
    failed_files = 0
    issues = []

    # 验证pyproject.toml文件
    pyproject_files = list(root_dir.rglob("pyproject.toml"))
    for file_path in pyproject_files:
        total_files += 1
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            file_issues = []

            # 检查requires-python
            requires_python_match = re.search(r'requires-python\s*=\s*"([^"]*)"', content)
            if requires_python_match:
                requires_python = requires_python_match.group(1)
                if TARGET_PYTHON_VERSION not in requires_python:
                    file_issues.append(f"requires-python版本不匹配: {requires_python}")

            # 检查classifiers
            if f'"Programming Language :: Python :: {TARGET_PYTHON_MAJOR_MINOR}"' not in content:
                file_issues.append(f"缺少Python {TARGET_PYTHON_MAJOR_MINOR}分类器")

            if file_issues:
                failed_files += 1
                issues.append(f"❌ {file_path}: {', '.join(file_issues)}")
            else:
                passed_files += 1
                logger.info(f"✅ {file_path}")

        except Exception as e:
            failed_files += 1
            issues.append(f"❌ {file_path}: 读取失败 - {e}")

    # 验证Dockerfile文件
    dockerfile_patterns = ["**/Dockerfile", "**/Dockerfile.*"]
    dockerfile_files = []
    for pattern in dockerfile_patterns:
        dockerfile_files.extend(root_dir.rglob(pattern))

    for file_path in dockerfile_files:
        total_files += 1
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            file_issues = []

            # 检查FROM python:版本
            from_python_matches = re.findall(r'FROM python:(\d+\.\d+(?:\.\d+)?(?:-\w+)?)', content)

            if from_python_matches:
                for version in from_python_matches:
                    if not version.startswith(TARGET_PYTHON_VERSION):
                        file_issues.append(f"Python基础镜像版本不匹配: {version}")

            if file_issues:
                failed_files += 1
                issues.append(f"❌ {file_path}: {', '.join(file_issues)}")
            else:
                passed_files += 1
                logger.info(f"✅ {file_path}")

        except Exception as e:
            failed_files += 1
            issues.append(f"❌ {file_path}: 读取失败 - {e}")

    # 打印摘要
    success_rate = (passed_files / total_files * 100) if total_files > 0 else 0

    logger.info("\n" + "="*60)
    logger.info("Python版本验证报告")
    logger.info("="*60)
    logger.info(f"目标版本: Python {TARGET_PYTHON_VERSION}")
    logger.info(f"验证文件总数: {total_files}")
    logger.info(f"通过验证: {passed_files}")
    logger.info(f"验证失败: {failed_files}")
    logger.info(f"成功率: {success_rate:.1f}%")

    if issues:
        logger.info("\n问题列表:")
        for issue in issues:
            logger.error(issue)

    if failed_files == 0:
        logger.info("\n🎉 所有文件的Python版本验证通过！")
        return True
    else:
        logger.error(f"\n❌ 发现 {failed_files} 个文件存在版本问题")
        return False

if __name__ == "__main__":
    success = verify_python_versions()
    sys.exit(0 if success else 1)
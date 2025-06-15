#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试运行脚本
用于运行单元测试和集成测试，并自动设置正确的环境

使用方法:
    # 运行单元测试
    python3 scripts/run_tests.py unit
    
    # 运行集成测试
    python3 scripts/run_tests.py integration
    
    # 运行所有测试
    python3 scripts/run_tests.py all
    
    # 运行指定测试文件
    python3 scripts/run_tests.py file test/unit/repository/test_oauth_repository.py
"""

import os
import sys
import subprocess
import argparse
import logging
from pathlib import Path

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)8s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# 获取项目根目录
ROOT_DIR = Path(__file__).parent.parent.absolute()


def set_python_path():
    """设置Python路径，确保所有模块可以正确导入"""
    # 将服务根目录添加到Python路径
    sys.path.insert(0, str(ROOT_DIR))
    os.environ['PYTHONPATH'] = f"{ROOT_DIR}:{os.environ.get('PYTHONPATH', '')}"
    logger.info(f"Python路径设置为: {os.environ['PYTHONPATH']}")


def setup_test_environment():
    """设置测试环境变量"""
    # 设置测试环境变量
    os.environ['ENVIRONMENT'] = 'test'
    os.environ['TEST_DB_HOST'] = os.environ.get('TEST_DB_HOST', 'localhost')
    os.environ['TEST_DB_PORT'] = os.environ.get('TEST_DB_PORT', '5432')
    os.environ['TEST_DB_NAME'] = os.environ.get('TEST_DB_NAME', 'auth_test')
    os.environ['TEST_DB_USER'] = os.environ.get('TEST_DB_USER', 'postgres')
    os.environ['TEST_DB_PASSWORD'] = os.environ.get('TEST_DB_PASSWORD', 'postgres')
    os.environ['TEST_REDIS_HOST'] = os.environ.get('TEST_REDIS_HOST', 'localhost')
    os.environ['TEST_REDIS_PORT'] = os.environ.get('TEST_REDIS_PORT', '6379')
    os.environ['TEST_REDIS_DB'] = os.environ.get('TEST_REDIS_DB', '1')
    os.environ['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'test_jwt_secret_for_testing_only')
    
    # 设置集成测试服务地址
    os.environ['TEST_SERVER_HOST'] = os.environ.get('TEST_SERVER_HOST', 'localhost')
    os.environ['TEST_SERVER_HTTP_PORT'] = os.environ.get('TEST_SERVER_HTTP_PORT', '8080')
    os.environ['TEST_SERVER_GRPC_PORT'] = os.environ.get('TEST_SERVER_GRPC_PORT', '50051')
    
    logger.info("测试环境变量设置完成")


def run_unit_tests(specific_file=None, coverage=True):
    """运行单元测试"""
    os.chdir(ROOT_DIR)
    logger.info("开始运行单元测试...")
    
    cmd = ['python3', '-m', 'pytest']
    
    if specific_file:
        cmd.append(specific_file)
    else:
        cmd.append('test/unit')
    
    if coverage:
        cmd.extend(['--cov=internal', '--cov-report=term'])
    
    cmd.extend(['-v'])
    
    result = subprocess.run(cmd)
    return result.returncode


def run_integration_tests(specific_file=None):
    """运行集成测试"""
    os.chdir(ROOT_DIR)
    logger.info("开始运行集成测试...")
    
    cmd = ['python3', '-m', 'pytest']
    
    if specific_file:
        cmd.append(specific_file)
    else:
        cmd.append('test/integration')
    
    cmd.extend(['-v'])
    
    result = subprocess.run(cmd)
    return result.returncode


def check_test_dependencies():
    """检查测试依赖是否可用"""
    missing_deps = []
    
    # 检查PostgreSQL
    try:
        import asyncpg
        logger.info("PostgreSQL客户端库已安装")
    except ImportError:
        missing_deps.append("asyncpg")
    
    # 检查Redis
    try:
        import redis
        logger.info("Redis客户端库已安装")
    except ImportError:
        missing_deps.append("redis")
    
    # 检查测试库
    try:
        import pytest
        logger.info(f"Pytest版本: {pytest.__version__}")
    except ImportError:
        missing_deps.append("pytest")
    
    if missing_deps:
        logger.warning(f"缺少依赖: {', '.join(missing_deps)}")
        return False
    
    return True


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='运行测试套件')
    parser.add_argument('test_type', choices=['unit', 'integration', 'all', 'file'], 
                        help='测试类型: unit(单元测试), integration(集成测试), all(全部测试), file(指定文件)')
    parser.add_argument('file_path', nargs='?', help='测试文件路径 (当test_type为file时需提供)')
    parser.add_argument('--no-coverage', action='store_true', help='不生成覆盖率报告')
    
    args = parser.parse_args()
    
    # 设置环境
    set_python_path()
    setup_test_environment()
    
    # 检查依赖
    if not check_test_dependencies():
        logger.error("测试依赖检查失败，请安装缺失的依赖后重试")
        return 1
    
    # 根据测试类型运行测试
    if args.test_type == 'unit':
        return run_unit_tests(coverage=not args.no_coverage)
    elif args.test_type == 'integration':
        return run_integration_tests()
    elif args.test_type == 'all':
        unit_result = run_unit_tests(coverage=not args.no_coverage)
        integration_result = run_integration_tests()
        return max(unit_result, integration_result)
    elif args.test_type == 'file':
        if not args.file_path:
            logger.error("使用file选项时必须提供文件路径")
            return 1
        
        if 'unit' in args.file_path:
            return run_unit_tests(args.file_path, coverage=not args.no_coverage)
        else:
            return run_integration_tests(args.file_path)


if __name__ == "__main__":
    sys.exit(main()) 
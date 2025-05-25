#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试运行脚本
方便执行所有测试，包括单元测试、集成测试、性能测试和端到端测试
"""

import os
import sys
import subprocess
import argparse
import time
from pathlib import Path


def run_command(command, description):
    """运行命令并显示结果"""
    print(f"\n{'='*60}")
    print(f"🚀 {description}")
    print(f"{'='*60}")
    
    start_time = time.time()
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        if result.returncode == 0:
            print(f"✅ {description} 成功完成 (耗时: {duration:.2f}s)")
            if result.stdout:
                print("\n📋 输出:")
                print(result.stdout)
        else:
            print(f"❌ {description} 失败 (耗时: {duration:.2f}s)")
            if result.stderr:
                print("\n🚨 错误:")
                print(result.stderr)
            if result.stdout:
                print("\n📋 输出:")
                print(result.stdout)
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ 执行 {description} 时发生异常: {e}")
        return False


def run_unit_tests():
    """运行单元测试"""
    return run_command(
        "python3 -m pytest test/test_service_implementations.py -v --tb=short",
        "单元测试"
    )


def run_integration_tests():
    """运行集成测试"""
    return run_command(
        "python3 -m pytest test/test_integration.py -v --tb=short",
        "集成测试"
    )


def run_performance_tests():
    """运行性能测试"""
    return run_command(
        "python3 -m pytest test/test_performance.py -v --tb=short -s",
        "性能测试"
    )


def run_e2e_tests():
    """运行端到端测试"""
    return run_command(
        "python3 -m pytest test/test_e2e.py -v --tb=short -s",
        "端到端测试"
    )


def run_all_tests():
    """运行所有测试"""
    return run_command(
        "python3 -m pytest test/ -v --tb=short",
        "所有测试"
    )


def run_coverage_tests():
    """运行测试覆盖率分析"""
    return run_command(
        "python3 -m pytest test/ --cov=internal --cov-report=html --cov-report=term",
        "测试覆盖率分析"
    )


def run_specific_test(test_file, test_function=None):
    """运行特定测试"""
    if test_function:
        command = f"python3 -m pytest {test_file}::{test_function} -v --tb=short -s"
        description = f"特定测试: {test_file}::{test_function}"
    else:
        command = f"python3 -m pytest {test_file} -v --tb=short -s"
        description = f"特定测试文件: {test_file}"
    
    return run_command(command, description)


def check_dependencies():
    """检查测试依赖"""
    print("🔍 检查测试依赖...")
    
    required_packages = [
        'pytest',
        'pytest-asyncio',
        'pytest-cov',
        'psutil'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} (缺失)")
    
    if missing_packages:
        print(f"\n🚨 缺失依赖包: {', '.join(missing_packages)}")
        print("请运行以下命令安装:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    print("\n✅ 所有依赖包已安装")
    return True


def generate_test_report():
    """生成测试报告"""
    print("\n📊 生成测试报告...")
    
    # 生成HTML报告
    html_report = run_command(
        "python3 -m pytest test/ --html=test_report.html --self-contained-html",
        "生成HTML测试报告"
    )
    
    # 生成JUnit XML报告
    junit_report = run_command(
        "python3 -m pytest test/ --junitxml=test_results.xml",
        "生成JUnit XML报告"
    )
    
    if html_report:
        print("📄 HTML报告已生成: test_report.html")
    
    if junit_report:
        print("📄 XML报告已生成: test_results.xml")
    
    return html_report and junit_report


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="无障碍服务测试运行器")
    
    parser.add_argument(
        '--type', '-t',
        choices=['unit', 'integration', 'performance', 'e2e', 'all', 'coverage'],
        default='all',
        help='测试类型 (默认: all)'
    )
    
    parser.add_argument(
        '--file', '-f',
        help='运行特定测试文件'
    )
    
    parser.add_argument(
        '--function', '-fn',
        help='运行特定测试函数 (需要与 --file 一起使用)'
    )
    
    parser.add_argument(
        '--report', '-r',
        action='store_true',
        help='生成测试报告'
    )
    
    parser.add_argument(
        '--check-deps',
        action='store_true',
        help='检查测试依赖'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='详细输出'
    )
    
    args = parser.parse_args()
    
    print("🧪 索克生活 - 无障碍服务测试运行器")
    print("=" * 60)
    
    # 检查依赖
    if args.check_deps or not check_dependencies():
        if not check_dependencies():
            sys.exit(1)
        return
    
    success = True
    
    # 运行特定测试
    if args.file:
        success = run_specific_test(args.file, args.function)
    
    # 运行测试类型
    elif args.type == 'unit':
        success = run_unit_tests()
    
    elif args.type == 'integration':
        success = run_integration_tests()
    
    elif args.type == 'performance':
        success = run_performance_tests()
    
    elif args.type == 'e2e':
        success = run_e2e_tests()
    
    elif args.type == 'coverage':
        success = run_coverage_tests()
    
    elif args.type == 'all':
        print("🎯 运行完整测试套件...")
        
        # 按顺序运行所有测试
        tests = [
            ("单元测试", run_unit_tests),
            ("集成测试", run_integration_tests),
            ("性能测试", run_performance_tests),
            ("端到端测试", run_e2e_tests)
        ]
        
        results = {}
        
        for test_name, test_func in tests:
            print(f"\n🔄 开始 {test_name}...")
            result = test_func()
            results[test_name] = result
            
            if not result:
                print(f"⚠️  {test_name} 失败，但继续执行其他测试...")
                success = False
        
        # 显示总结
        print("\n" + "="*60)
        print("📋 测试总结")
        print("="*60)
        
        for test_name, result in results.items():
            status = "✅ 通过" if result else "❌ 失败"
            print(f"{test_name}: {status}")
        
        overall_status = "✅ 全部通过" if success else "❌ 部分失败"
        print(f"\n总体结果: {overall_status}")
    
    # 生成报告
    if args.report:
        generate_test_report()
    
    # 退出状态
    if success:
        print("\n🎉 测试完成！")
        sys.exit(0)
    else:
        print("\n💥 测试失败！")
        sys.exit(1)


if __name__ == "__main__":
    main() 
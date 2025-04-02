#!/usr/bin/env python3
"""
负载测试结果分析脚本
"""

import json
import argparse
import sys
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='分析K6负载测试结果')
    parser.add_argument('-f', '--file', required=True, help='K6 JSON结果文件路径')
    parser.add_argument('-t', '--threshold', type=int, default=1000, 
                         help='响应时间阈值(毫秒)，默认1000ms')
    parser.add_argument('-o', '--output', help='输出报告目录，默认为load_test_results')
    return parser.parse_args()


def load_k6_results(file_path):
    """加载K6 JSON格式测试结果"""
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        return data
    except Exception as e:
        print(f"加载结果文件失败: {e}")
        sys.exit(1)


def analyze_results(data, threshold):
    """分析测试结果，生成关键指标"""
    metrics = {}
    
    # 提取HTTP指标
    http_reqs = data.get('metrics', {}).get('http_reqs', {})
    http_req_duration = data.get('metrics', {}).get('http_req_duration', {})
    http_req_failed = data.get('metrics', {}).get('http_req_failed', {})
    
    # 计算基本指标
    metrics['total_requests'] = http_reqs.get('values', {}).get('count', 0)
    metrics['rps'] = http_reqs.get('values', {}).get('rate', 0)
    metrics['failure_rate'] = http_req_failed.get('values', {}).get('rate', 0) * 100
    
    # 响应时间指标
    metrics['avg_response_time'] = http_req_duration.get('values', {}).get('avg', 0)
    metrics['min_response_time'] = http_req_duration.get('values', {}).get('min', 0)
    metrics['max_response_time'] = http_req_duration.get('values', {}).get('max', 0)
    metrics['p90_response_time'] = http_req_duration.get('values', {}).get('p(90)', 0)
    metrics['p95_response_time'] = http_req_duration.get('values', {}).get('p(95)', 0)
    
    # 特定于RAG的指标
    rag_query_duration = data.get('metrics', {}).get('rag_query_duration', {})
    rag_success_rate = data.get('metrics', {}).get('rag_success_rate', {})
    
    if rag_query_duration:
        metrics['avg_rag_query_time'] = rag_query_duration.get('values', {}).get('avg', 0)
        metrics['p95_rag_query_time'] = rag_query_duration.get('values', {}).get('p(95)', 0)
    
    if rag_success_rate:
        metrics['rag_success_rate'] = rag_success_rate.get('values', {}).get('rate', 0) * 100
    
    # 阈值检查
    metrics['pct_over_threshold'] = sum(1 for t in data.get('metrics', {})
                                         .get('http_req_duration', {})
                                         .get('values', {})
                                         .get('raw', []) if t > threshold) / metrics['total_requests'] * 100
    
    return metrics


def generate_report(metrics, threshold, output_dir):
    """生成测试报告，包括文本和图表"""
    output_path = Path(output_dir) if output_dir else Path('load_test_results')
    output_path.mkdir(exist_ok=True, parents=True)
    
    # 生成文本报告
    report_path = output_path / f"load_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    
    with open(report_path, 'w') as f:
        f.write("=========================================\n")
        f.write("        RAG服务负载测试报告            \n")
        f.write("=========================================\n")
        f.write(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"总请求数: {metrics['total_requests']:.0f}\n")
        f.write(f"每秒请求数(RPS): {metrics['rps']:.2f}\n")
        f.write(f"失败率: {metrics['failure_rate']:.2f}%\n")
        f.write("\n----- 响应时间指标(ms) -----\n")
        f.write(f"平均响应时间: {metrics['avg_response_time']:.2f} ms\n")
        f.write(f"最小响应时间: {metrics['min_response_time']:.2f} ms\n")
        f.write(f"最大响应时间: {metrics['max_response_time']:.2f} ms\n")
        f.write(f"90%响应时间: {metrics['p90_response_time']:.2f} ms\n")
        f.write(f"95%响应时间: {metrics['p95_response_time']:.2f} ms\n")
        f.write(f"超过{threshold}ms的请求比例: {metrics['pct_over_threshold']:.2f}%\n")
        
        f.write("\n----- RAG特定指标 -----\n")
        if 'avg_rag_query_time' in metrics:
            f.write(f"平均RAG查询时间: {metrics['avg_rag_query_time']:.2f} ms\n")
            f.write(f"95% RAG查询时间: {metrics['p95_rag_query_time']:.2f} ms\n")
        if 'rag_success_rate' in metrics:
            f.write(f"RAG查询成功率: {metrics['rag_success_rate']:.2f}%\n")
        
        f.write("\n----- 性能评估 -----\n")
        if metrics['p95_response_time'] < threshold and metrics['failure_rate'] < 5:
            f.write("✅ 性能测试通过: 服务在当前负载下表现良好\n")
        else:
            f.write("⚠️ 性能测试需注意: 服务在当前负载下可能需要优化\n")
            
            if metrics['p95_response_time'] >= threshold:
                f.write(f"  - 95%响应时间({metrics['p95_response_time']:.2f}ms)超过阈值({threshold}ms)\n")
            if metrics['failure_rate'] >= 5:
                f.write(f"  - 失败率({metrics['failure_rate']:.2f}%)超过5%\n")
    
    print(f"报告已生成: {report_path}")
    return report_path


def main():
    """主函数"""
    args = parse_args()
    data = load_k6_results(args.file)
    metrics = analyze_results(data, args.threshold)
    report_path = generate_report(metrics, args.threshold, args.output)
    
    # 打印关键指标到控制台
    print("\n=== 负载测试关键指标 ===")
    print(f"总请求数: {metrics['total_requests']:.0f}")
    print(f"每秒请求数(RPS): {metrics['rps']:.2f}")
    print(f"失败率: {metrics['failure_rate']:.2f}%")
    print(f"平均响应时间: {metrics['avg_response_time']:.2f} ms")
    print(f"95%响应时间: {metrics['p95_response_time']:.2f} ms")
    print(f"超过{args.threshold}ms的请求比例: {metrics['pct_over_threshold']:.2f}%")
    
    # 返回码基于测试结果
    if metrics['p95_response_time'] < args.threshold and metrics['failure_rate'] < 5:
        print("✅ 性能测试通过")
        return 0
    else:
        print("⚠️ 性能测试需注意")
        return 1


if __name__ == "__main__":
    sys.exit(main())
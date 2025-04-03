#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RAG服务负载测试脚本
使用Locust进行性能测试
"""

import json
import os
import random
import time
from typing import Dict, List, Any

from locust import HttpUser, task, between, events

# 测试查询样本
SAMPLE_QUERIES = [
    "中医四诊合参的基本理论是什么？",
    "阴阳五行学说在中医中的应用有哪些？",
    "针灸的基本原理是什么？",
    "如何通过舌诊辨别体质类型？",
    "中医治未病的核心理念是什么？",
    "食疗对于健康养生有什么作用？",
    "经络和穴位的关系是什么？",
    "如何根据四季变化调整养生方法？",
    "中医如何看待亚健康状态？",
    "情志对健康的影响有哪些？",
]

# 负载测试配置
class RAGServiceUser(HttpUser):
    """模拟RAG服务用户"""
    
    # 用户行为间隔为1-5秒
    wait_time = between(1, 5)
    
    def on_start(self):
        """用户启动时执行"""
        self.client.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        
        # 记录结果目录
        self.results_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "load_test_results"
        )
        os.makedirs(self.results_dir, exist_ok=True)
    
    @task(1)
    def health_check(self):
        """检查服务健康状态"""
        self.client.get("/health")
    
    @task(1)
    def status_check(self):
        """检查服务状态"""
        self.client.get("/api/v1/status")
    
    @task(5)
    def basic_query(self):
        """基本查询测试"""
        query = random.choice(SAMPLE_QUERIES)
        payload = {
            "query": query,
            "max_results": 3,
            "threshold": 0.7
        }
        
        with self.client.post(
            "/api/v1/query",
            json=payload,
            catch_response=True
        ) as response:
            try:
                if response.status_code != 200:
                    response.failure(f"状态码错误: {response.status_code}")
                    return
                
                data = response.json()
                if "results" not in data:
                    response.failure("响应中缺少results字段")
                elif len(data["results"]) == 0:
                    response.failure("没有返回任何结果")
                else:
                    response.success()
            except Exception as e:
                response.failure(f"响应处理异常: {str(e)}")
    
    @task(3)
    def advanced_query(self):
        """高级查询测试，包含更多参数"""
        query = random.choice(SAMPLE_QUERIES)
        payload = {
            "query": query,
            "max_results": 5,
            "threshold": 0.6,
            "include_metadata": True,
            "filter": {
                "source_type": random.choice(["article", "book", "research"]),
                "min_date": "2010-01-01"
            }
        }
        
        with self.client.post(
            "/api/v1/query",
            json=payload,
            catch_response=True
        ) as response:
            try:
                if response.status_code != 200:
                    response.failure(f"状态码错误: {response.status_code}")
                    return
                
                data = response.json()
                if "results" not in data:
                    response.failure("响应中缺少results字段")
                else:
                    response.success()
            except Exception as e:
                response.failure(f"响应处理异常: {str(e)}")

# 测试事件处理
@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """测试开始时的处理函数"""
    print("开始RAG服务性能测试")

@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """测试结束时的处理函数"""
    print("RAG服务性能测试完成")
    
    # 保存测试数据摘要
    results_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        "load_test_results"
    )
    os.makedirs(results_dir, exist_ok=True)
    
    stats = environment.stats
    
    # 收集统计数据
    summary_stats = {
        "timestamp": time.time(),
        "duration": environment.runner.time(),
        "num_requests": stats.num_requests,
        "num_failures": stats.num_failures,
        "total_response_time": stats.total_response_time,
        "endpoints": {}
    }
    
    # 处理各个端点的统计信息
    for name, value in stats.entries.items():
        endpoint_stats = {
            "method": name[1] if len(name) > 1 else "GET",
            "name": name[0],
            "num_requests": value.num_requests,
            "num_failures": value.num_failures,
            "median_response_time": value.median_response_time,
            "avg_response_time": value.avg_response_time,
            "min_response_time": value.min_response_time,
            "max_response_time": value.max_response_time,
            "percentile_95": value.get_response_time_percentile(0.95),
            "percentile_99": value.get_response_time_percentile(0.99),
        }
        summary_stats["endpoints"][name[0]] = endpoint_stats
    
    # 写入结果文件
    filename = os.path.join(results_dir, f"locust_summary_{int(time.time())}.json")
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(summary_stats, f, indent=2, ensure_ascii=False)
    
    print(f"测试结果已保存到 {filename}") 